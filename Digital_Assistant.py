import pyttsx3
import speech_recognition as sr
import datetime
import ctypes
import wikipedia
import webbrowser
import time
import os
import wolframalpha
import random
import sys
import subprocess
import GoogleNews
import cv2
import win32com.client
from fuzzywuzzy import fuzz
from desktop_use import DesktopUseClient, Locator, sleep
import requests
from groq import Groq
import threading
from pynput.keyboard import Key,Controller
import tempfile
from PIL import Image
import pytesseract
import requests
from plyer import notification
import tkinter as tk
from tkinter import messagebox
import speedtest
import re

text_queue = []  # This will store queries coming from GUI


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

keyboard = Controller()


client_groq = Groq(api_key="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")
client = DesktopUseClient(base_url="http://127.0.0.1:9375")

wolfram = wolframalpha.Client('5Y76K7-WXLQ4ALRHA')

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

output_callback = None  # Global variable to store the callback function

def set_output_callback(callback):
    """Set the callback function for output."""
    global output_callback
    output_callback = callback

def print_output(message):
    """print output using the callback or fallback to print_output."""
    if output_callback:
        output_callback(message)  # Call the GUI's callback function
    else:
        print(message)  # Fallback to standard print_output



def ask_groq(query):
    headers = {
        "Authorization": f"Bearer {client_groq}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",  # Replace with your chosen model ID
        "messages": [{"role": "user", "content": query}]
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    except requests.exceptions.HTTPError as http_err:
        print_output(f"HTTP error occurred: {http_err} - {response.text}")
        return "There was an error reaching Groq's server."
    except Exception as err:
        print_output(f"Other error occurred: {err}")
        return "Something went wrong while talking to Groq."


# respond according to sentiments
def analyze_sentiment(text):
    headers = {
        "Authorization": f"Bearer {client_groq}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a sentiment analysis expert. Analyze the user's mood from this sentence."},
            {"role": "user", "content": f"What is the mood of this sentence: '{text}'? Respond with one word: happy, sad, angry, excited, tired, anxious, or neutral."}
        ]
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
        response.raise_for_status()
        sentiment = response.json()['choices'][0]['message']['content'].strip().lower()
        return sentiment
    except Exception as e:
        print_output("Sentiment analysis error:", e)
        return "neutral"

def respond_to_sentiment(sentiment):
    mood_responses = {
        "happy": "That's wonderful to hear! Keep smiling.",
        "sad": "I'm here for you. Would you like to hear a joke or some music?",
        "angry": "It’s okay to feel that way. Deep breaths can help.",
        "excited": "Yay! I love your energy!",
        "tired": "You should rest a bit. Want me to play something relaxing?",
        "anxious": "I understand. Want me to help calm you down with some music or breathing tips?",
        "neutral": "Got it. Let me know if you need anything."
    }

    response = mood_responses.get(sentiment, "I'm not sure how you're feeling, but I'm here for you.")
    speak(response)
    print_output(response)


def type_into_field_desktop(app_name, field_role, text):
    try:
        field = client.locator(f'window:{app_name}').locator(f'role:{field_role}')
        field.type_text(text)
        speak("Typed your text successfully.")
    except Exception as e:
        print_output(f"Typing failed: {e}")
        speak("Couldn't type into the field.")


def volumeup():
    for i in range(5):
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
        sleep(0.1)

def volumedown():
    for i in range(5):
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)
        sleep(0.1)

def openappweb(query):
    speak("Launching sir")
    if ".com" in query or ".co.in" in query or ".org" in query:
        query = query.replace("open","")
        query = query.replace("launch","")
        query = query.replace("website","")
        query = query.replace(" ","")
        webbrowser.open(f"https://www.{query}")


def closeappweb(query):
    import pyautogui
    n = int(input("tell number of tabs to close: "))
    speak("closing sir")
    for i in range(n):
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
    speak("All tab close")


def set_alarm(alarm_time):
    try:
        alarm_hour, alarm_minute = map(int, alarm_time.split(":"))
        now = datetime.datetime.now()
        alarm_datetime = now.replace(hour=alarm_hour, minute=alarm_minute, second=0, microsecond=0)

        if alarm_datetime < now:
            alarm_datetime += datetime.timedelta(days=1)

        time_diff = (alarm_datetime - now).total_seconds()
        speak(f"Alarm set for {alarm_time}. I will wake you up!")
        print_output(f"Alarm set for {alarm_time}. Waiting...")

        def alarm_trigger():
            time.sleep(time_diff)
            speak("Time to wake up!")
            os.startfile('C:\\Users\\hp\\Music\\Ashes Remain - On My Own.mp3')  # Change path if needed

        threading.Thread(target=alarm_trigger).start()

    except Exception as e:
        print_output(f"[ERROR] Alarm error: {e}")
        speak("Sorry, I could not set the alarm. Please try again.")


# It returns OCR'd text directly (not a screenshot).
def get_text_from_capture_screen():

    try:
        response = requests.post("http://127.0.0.1:9375/capture_screen", json={})
        if response.status_code == 200:
            data = response.json()
            if "text" in data:
                return data["text"]
            else:
                print_output("[WARN] No 'text' in capture_screen response.")
                return ""
        else:
            print_output(f"[ERROR] capture_screen failed with status: {response.status_code}")
            return ""
    except Exception as e:
        print_output(f"[ERROR] Exception in capture_screen OCR: {e}")
        return ""

# summarize screen Text Using Groq LLM API
def summarize_screen_content_with_groq(text):
    if not text or len(text.strip()) < 10:
        return "Screen content is too minimal to summarize."

    prompt = f"""You are an assistant. Here's the user's screen content:
{text}

Summarize the screen content in simple English. Mention what the user might be seeing."""

    try:
        response = client_groq.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300,
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print_output(f"[ERROR] Groq summarization failed: {e}")
        return "Could not generate a summary due to an error."


def read_and_summarize_screen():
    print_output("Reading screen using capture_screen OCR...")
    ocr_text = get_text_from_capture_screen()

    if not ocr_text or ocr_text.strip() == "":
        print_output("[INFO] No text was read from the screen.")
        speak("There doesn't seem to be any readable text on the screen.")
        return

    print_output(f"OCR result:\n{ocr_text[:500]}")
    summary = summarize_screen_content_with_groq(ocr_text)
    print_output("\n[Summary]")
    print_output(summary)
    speak(summary)

# Takes OCR Of the screen and clicks visual button In Websites Too
def smart_click_web_button(button_label: str):
        import pyautogui

        # Step 1: Focus browser window using Terminator (YouTube or ChatGPT)
        print_output("Trying to activate browser window...")
        try:
            client.activate_browser_window_by_title("YouTube")
        except:
            client.activate_browser_window_by_title("ChatGPT")

        # Step 2: Take screenshot using pyautogui
        img = pyautogui.screenshot()

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img_path = tmp.name
            img.save(img_path)

        # Step 3: OCR with bounding boxes
        boxes = pytesseract.image_to_data(Image.open(img_path), output_type=pytesseract.Output.DICT)

        for i in range(len(boxes['text'])):
            word = boxes['text'][i]
            if button_label.lower() in word.lower():
                x, y, w, h = boxes['left'][i], boxes['top'][i], boxes['width'][i], boxes['height'][i]
                pyautogui.moveTo(x + w / 2, y + h / 2)
                pyautogui.click()
                speak(f"Clicked the '{button_label}' button.")
                return

        speak(f"Could not find the '{button_label}' button on screen.")



def click_all_occurrences_on_screen(target_text: str):
    import pyautogui

    try:
        screenshot = pyautogui.screenshot()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            screenshot_path = tmp.name
            screenshot.save(screenshot_path)

        # Step 2: OCR with bounding box extraction
        data = pytesseract.image_to_data(Image.open(screenshot_path), output_type=pytesseract.Output.DICT)
        os.remove(screenshot_path)
        clicks_done = 0
        target_text = target_text.lower()

        for i in range(len(data['text'])):
            word = data['text'][i].strip().lower()
            if target_text in word:
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                center_x = x + w // 2
                center_y = y + h // 2

                pyautogui.moveTo(center_x, center_y)
                pyautogui.click()
                print_output(f"[✓] Clicked at: ({center_x}, {center_y}) for match: {word}")
                clicks_done += 1
                time.sleep(0.3)

        if clicks_done == 0:
            speak(f"No occurrences of '{target_text}' found.")
        else:
            speak(f"Clicked on {clicks_done} occurrences of '{target_text}'.")

    except Exception as e:
        print_output(f"[ERROR] click_all_occurrences_on_screen: {e}")
        speak("Something went wrong while scanning the screen.")



def run_flappy_bird():
    global pause_listening
    pause_listening = True
    print_output("Pausing listening... launching game.")
    subprocess.run(["python", r"flappy_Bird\main.py"])
    print_output("Game closed. Resuming listening.")
    pause_listening = False
    # Start listening in a background thread
    listener_thread = threading.Thread(target=listen)
    listener_thread.daemon = True
    listener_thread.start()


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


# def snd(msg,ph,hr,min):
#     pywhatkit.sendwhatmsg(ph, msg, hr, min)


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
        print_output("Good Morning!")

    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")
        print_output("Good Afternoon!")

    else:
        speak("Good Evening!")
        print_output("Good Evening!")

    speak("I am Digital Dave Sir. Please tell me how may I help you")
    print_output("I am Digital Dave Sir. Please tell me how may I help you")


def smart_search_and_open(query):
    try:
        print_output(f"Trying indexed search for: {query}")
        connection = win32com.client.Dispatch("ADODB.Connection")
        recordset = win32com.client.Dispatch("ADODB.Recordset")

        connection.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
        search_query = f"SELECT System.ItemPathDisplay FROM SYSTEMINDEX WHERE FREETEXT('{query}')"
        recordset.Open(search_query, connection)

        indexed_results = []
        while not recordset.EOF:
            path = recordset.Fields.Item("System.ItemPathDisplay").Value
            filename = os.path.basename(path).lower()
            if path and any(path.lower().endswith(ext) for ext in
                            ['.pdf', '.txt', '.docx', '.xlsx', '.pptx']) and fuzz.partial_ratio(query.lower(),
                                                                                                filename) > 70:
                indexed_results.append(path)
            recordset.MoveNext()

        recordset.Close()
        connection.Close()

        if indexed_results:
            print_output(f"Found via index: {indexed_results[0]}")
            speak(f"Opening {query}")
            os.startfile(indexed_results[0])
            return

    except Exception as e:
        print_output(f"Index search failed: {e}")

    # Fallback: file system search for .exe/.lnk
    speak("Trying file system search for applications")
    print_output("Falling back to manual directory scan...")
    fallback_dirs = [
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        os.path.expanduser("~\\AppData\\Local"),
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Downloads"),
    ]

    matches = []
    for directory in fallback_dirs:
        for root, dirs, files in os.walk(directory):
            for name in files:
                if query.lower() in name.lower() and name.lower().endswith(('.exe', '.lnk')):
                    matches.append(os.path.join(root, name))

    if matches:
        print_output(f"Found via fallback: {matches[0]}")
        speak(f"Launching {query}")
        os.startfile(matches[0])
    else:
        print_output("No file found via index or fallback.")
        speak(f"Sorry, I couldn't find any file or app named {query}.")


def listen():
    global pause_listening
    while True:
        if pause_listening:
            continue
        else:
            break

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def focus_mode():
    if is_admin():
        current_time = datetime.datetime.now().strftime("%H:%M")
        stop_time = input("Enter the time eg:- [11:12]: ")
    
        host_path = "C:\Windows\System32\drivers\etc\hosts"
        redirect = "127.0.0.1"
        print_output(current_time)
        time.sleep(2)
        website_list = ["www.facebook.com","facebook.com","www.instagram.com","instagram.com","www.youtube.com","youtube.com"]
    
        if (current_time<stop_time):
            with open(host_path,"r+") as file:  #r+ is for reading and writing
                content = file.read()
                print_output(content)
                time.sleep(1)
                for website in website_list:
                    if website in content:
                        pass
                    else:
                        file.write(f"{redirect} {website}\n")
                        print_output("done")
                        time.sleep(1)
                print_output("Websites are blocked || focus mode turned on")
    
        while True:
            current_time = datetime.datetime.now().strftime("%H:%M")
            if current_time >= stop_time:
                with open(host_path, "r+") as file:
                    content = file.readlines()
                    file.seek(0)
                    for line in content:
                        if not any(website in line for website in website_list):
                            file.write(line)
                    file.truncate()
                print_output("Websites are unblocked || focus mode turned off")
                break
            else:
                print_output(f"Still in focus mode. Current time: {current_time}, waiting until: {stop_time}")
                time.sleep(30)  # Wait before checking again
    
    
    else:
        ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable," ".join(sys.argv),None,-1)


def takeCommand():
    #It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print_output("Listening...")
        speak("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print_output("Recognizing...")
        speak("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print_output(f"User said: {query}\n")

    except Exception as e:
        # print_output(e)
        print_output("Say that again please...")
        speak("Say that again please...")
        return "None"
    return query
    server.close()

def submit_query(query=None):
    if query:
        text_queue.append(query.lower())


def main(mode):
    time.sleep(1)
    wishMe()
    # Flags
    game_running = False
    pause_listening = False
    text_mode = mode
    ama_mode = False
    should_exit = False
    while not should_exit:
        # import pyautogui
        # Get input based on active mode
        if text_mode:
            if text_queue:
                query = text_queue.pop(0)
            else:
                continue  # No input yet, keep waiting
        else:
            query = takeCommand().lower()


        # Exit command detection
        if any(exit_phrase in query for exit_phrase in
               ['stop', 'abort', 'nothing', 'go to sleep', 'bye', 'exit dave']):
            speak("Okay. Shutting down now. Bye Sir, have a nice day.")
            print_output("Shutting down Digital Dave...")
            should_exit = True
            tk.window.destroy()  # Close the GUI window if it exists
            continue
        # Enter or exit AMA mode
        # Just say activate ask me anything mode to ask directly to groq server and say exit to exit the feature
        # You can directly connect to groq to ask some basic questions
        if 'activate ask me anything' in query:
            ama_mode = True
            speak("Ask Me Anything mode activated. I'm ready for your questions.")
            continue
        if ama_mode:
            response = ask_groq(query)
            print_output(response)
            speak(response)
            continue  # Go to next loop iteration
        elif 'exit ask me anything ' in query:
            ama_mode = False
            speak("Exiting Ask Me Anything mode.")
            continue
        # Toggle text input mode
        elif 'activate text' in query:
            text_mode = True
            speak("Text input mode activated. You can now type your commands.")
            continue
        elif 'deactivate text' in query:
            text_mode = False
            speak("Text input mode deactivated. Resuming voice commands.")
            continue
        # Check for emotional input
        elif "i feel" in query or "i am feeling" in query or "i'm feeling" in query:
            sentiment = analyze_sentiment(query)
            print_output(f"Detected sentiment: {sentiment}")
            respond_to_sentiment(sentiment)
            continue
        # you have to mention the topic and dave will automatically open the resource in youtube
        elif 'play something on youtube' in query:
            mood = query.replace("play something", "").strip()
            speak(f"Looking for {mood} music. Let me find something for you.")
            search = f"{mood} relaxing music on YouTube"
            webbrowser.open(f"https://www.youtube.com/results?search_query={search}")

        elif 'play namespace on youtube' in query:
            webbrowser.open(f"https://www.youtube.com/@namespacecomm")
        # Schedule
        elif 'set my schedule' in query:
            tasks = []  # empty list
            speak("do you want to clear old task yes or no?")
            query = takeCommand().lower()
            if 'yes' in query:
                file = open("tasks.txt", "w")
                file.write(f"")
                file.close()
                task_no = int(input("enter number of tasks: "))
                i = 0
                for i in range(task_no):
                    tasks.append(input("enter the task:"))
                    file = open("tasks.txt", "a")
                    file.write(f"{i}.{tasks[i]}\n")
                    file.close()
            elif 'no' in query:
                task_no = int(input("enter number of tasks: "))
                i = 0
                for i in range(task_no):
                    tasks.append(input("enter the task:"))
                    file = open("tasks.txt", "a")
                    file.write(f"{i}.{tasks[i]}\n")
                    file.close()
        elif 'show my schedule' in query:
            from pygame import mixer #for music
            try:
                with open("tasks.txt", "r") as file:
                    content = file.read().strip()
                if not content:
                    speak("Your schedule is currently empty.")
                    print_output("No tasks found in tasks.txt.")
                else:
                    print_output("Your Schedule:\n", content)
                    mixer.init()
                    try:
                        mixer.music.load("notification.wav")
                        mixer.music.play()
                    except Exception as e:
                        print_output("Error playing sound:", e)
                    # Show schedule in popup
                    root = tk.Tk()
                    root.withdraw()  # Hide main window
                    messagebox.showinfo("My Schedule", content)
            except FileNotFoundError:
                speak("I couldn't find your schedule file.")
                print_output("tasks.txt not found.")
        # control youtube
        # drawback: youtube should be on
        elif 'pause' in query:
            import pyautogui
            pyautogui.press("k")
            speak("video pause")
        elif 'mute' in query:
            import pyautogui
            pyautogui.press("m")
            speak("video muted")
        elif 'volume up' in query:
            speak("Turning volume up sir")
            volumeup()
        elif 'volume up' in query:
            speak("Turning volume down sir")
            volumedown()
        # Dave will use Groq to generate a summary of your dictated
        elif 'summarise this' in query:
            speak("Please tell me the note you want to summarize.")
            note = takeCommand()
            summary = ask_groq(f"Summarize this: {note}")
            speak("Here's a short summary:")
            print_output(summary)
            speak(summary)
        # this will open any website but mention extension
        elif 'open website' in query:
            openappweb(query)
            should_exit = True
        # open all system apps
        elif 'open app' in query:
            import pyautogui
            query = query.replace("open", "")
            query = query.replace("app", "")
            query = query.replace(" ", "")
            pyautogui.hotkey("ctrl", "esc")
            pyautogui.typewrite(query)
            pyautogui.sleep(2)
            pyautogui.press("enter")
        elif 'click my photo' in query:
            import pyautogui
            pyautogui.hotkey("ctrl", "esc")
            pyautogui.typewrite("camera")
            pyautogui.press("enter")
            pyautogui.sleep(2)
            speak("smile")
            pyautogui.press("enter")
        # close tabs
        # drawback: the required browers should be on
        elif 'close tab' in query:
            closeappweb(query)
        elif 'internet speed' in query:
            wifi = speedtest.Speedtest()
            upload_net = wifi.upload() / 1048576
            download_net = wifi.download() / 1048576
            print_output("Wifi upload speed is", upload_net)
            print_output("Wifi download speed is", download_net)
            speak(f"Wifi download speed is{download_net}")
            speak(f"Wifi upload speed is{upload_net}")
        # Logic for executing tasks based on query
        elif 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print_output(results)
            speak(results)

        elif 'open youtube' in query:
            webbrowser.open("youtube.com")
            speak("opening youtube")
            print_output("Opening Youtube...")

        elif 'open google' in query:
            webbrowser.open("google.com")
            speak("opening google")
            print_output("Opening google...")

        # focus mode
        elif 'focus mode' in query:
            a = int(input("are you sure that you want to enter focus mode : [1 for yes / 0 for no]: "))
            if (a==1):
                speak("Entering focus mode......")
                # os.startfile("E:\\Project\\AI_chatbot\\focusmode.py")
                subprocess.call(["powershell", "-Command","Start-Process python -ArgumentList 'E:\\Project\\AI_chatbot\\focusmode.py' -Verb RunAs"])
                exit()
            else:
                pass

        elif 'open google sign in' in query:
            print_output('okay, opening Google Account')
            speak('okay, opening Google Account')
            webbrowser.open(
                'https://accounts.google.com/signin/chrome/sync?ssp=1&continue=https%3A%2F%2Fwww.google.com%2F')

        elif 'open new tab in google' in query:
            print_output('okay, opening new tab')
            speak('okay, opening new tab')
            webbrowser.open('chrome://newtab')

        elif 'latest news' in query:
            googlenews = GoogleNews()
            googlenews.setlang('en')
            googlenews.search('latest News')
            googlenews.getpage(1)
            result = googlenews.gettext()
            speak(result)
            print_output(result)

        elif 'time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")
            print_output(f"Sir, the time is {strTime}")

        elif 'open command prompt' in query:
            os.system("start cmd")

        elif 'open camera' in query:
            cap = cv2.VideoCapture(0)
            while True:
                ret, img = cap.read()
                cv2.imshow('webcam', img)
                k = cv2.waitKey(50)
                if k == 27:
                    break
            cap.release()
            cv2.destroyAllWindows()

        elif 'my ip address' in query:
            ip = webbrowser.get('https://api.ipify.org').text
            print_output(ip)
            speak(f"your ip address is {ip}")
            print_output("Your ip address is", {ip})

        elif "shut down the system" in query:
            os.system("shutdown /s /t 5")

        elif "restart the system" in query:
            os.system("shutdown /r /t 5")

        elif "Lock the system" in query:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

        elif 'close notepad' in query:
            os.system("taskkill /f /im notepad.exe")
            speak('closing notepad')
            print_output("Closing Notepad")


        elif 'close code' in query:
            os.system("taskkill /f /im Microsoft VS Code.exe")
            speak('closing vs code')
            print_output("Closing vs code")


        elif 'open youtube' in query:
            import pywhatkit
            speak("what you will like to watch ?")
            query = takeCommand().lower()
            pywhatkit.playonyt(f"{query}")


        elif "what's up" in query or 'how are you' in query:
            Msgs = ['Just doing my thing!', 'I am fine!', 'Nice!', 'I am nice and full of energy']
            print_output(random.choice(Msgs))
            speak(random.choice(Msgs))

        elif 'nothing' in query or 'abort' in query or 'stop' in query or "go to sleep" in query or "bye" in query:
            print_output('Okay')
            speak('okay')
            print_output('Bye Sir, have a nice day.')
            speak('Bye Sir, have a nice day.')
            tk.window.destroy()  # Close the GUI window if it exists
            sys.exit()

        elif 'hello' in query:
            print_output('Hello Sir')
            speak('Hello Sir')

        elif 'hey ai' in query:
            print_output('Hello Sir')
            speak('Hello Sir')

        elif 'what is your name' in query:
            print_output('My name is Dave')
            speak('My name is Dave')

        elif 'how are you' in query:
            print_output('I am fine and full of energy and how you?')
            speak('I am fine and full of energy and how you?')

        elif 'i am fine' in query:
            print_output('Thats nice')
            speak('Thats nice')

        elif 'bye' in query:
            print_output('Bye ' + 'Sir' + ', have a nice day.')
            speak('Bye ' + 'Sir' + ', have a nice day.')
            tk.window.destroy()
            break

        elif "take screenshot" in query:
            import pyautogui
            speak('tell me a name for the file')
            name = takeCommand().lower()
            time.sleep(3)
            img = pyautogui.screenshot()
            img.save(f"{name}.png")
            speak("screenshot saved")

        elif 'open new window' in query:
            import pyautogui
            pyautogui.hotkey('ctrl', 'n')

        elif 'minimise this window' in query:
            import pyautogui
            pyautogui.hotkey('alt', 'space')
            time.sleep(1)
            pyautogui.press('n')

        elif 'open history' in query:
            import pyautogui
            pyautogui.hotkey('ctrl', 'h')

        elif 'open downloads' in query:
            import pyautogui
            pyautogui.hotkey('ctrl', 'j')

        elif 'previous tab' in query:
            import pyautogui
            pyautogui.hotkey('ctrl', 'shift', 'tab')

        elif 'next tab' in query:
            import pyautogui
            pyautogui.hotkey('ctrl', 'tab')

        elif 'close tab' in query:
            import pyautogui
            pyautogui.hotkey('ctrl', 'w')

        elif 'close window' in query:
            import pyautogui
            pyautogui.hotkey('ctrl', 'shift', 'w')

        elif 'open stackoverflow' in query:
            webbrowser.open("stackoverflow.com")
            speak("opening StackOverflow")
            print_output("Opening StackOverflow...")

        elif 'shutdown' in query:
            print_output("Okay,Shutting Down")
            speak("Okay,Shutting Down")
            os.system('shutdown-s')


        elif "what's going on" in query or "what's up" in query or "how are you?" in query:
            Msgs = ['Just doing my thing!', 'I am fine!', 'Nice!', 'I am nice and full of energy']
            print_output(random.choice(Msgs))
            speak(random.choice(Msgs))

        elif 'play flappy bird' in query or "play game" in query or "play offline game" in query:
            game_running = True
            run_flappy_bird()


        elif "reset chat".lower() in query.lower():
            chatStr = ""

        elif "summarize screen" in query or "what's on screen" in query or "read screen" in query:
            read_and_summarize_screen()


        elif "click button" in query or "click everywhere" in query:
            speak("What text should I click on?")
            label = takeCommand().lower()
            click_all_occurrences_on_screen(label)

        elif "click web button" in query or "click browser button" in query:
            speak("What button should I click on the web page?")
            button_label = takeCommand().lower()
            smart_click_web_button(button_label)

        elif 'set alarm' in query:
            speak("Please tell me the time to set alarm, like 7:30 or 18:45")
            alarm_input = takeCommand().lower()

            # Extract digits using regex or simple parsing
            match = re.search(r'(\d{1,2}):(\d{2})', alarm_input)
            if match:
                alarm_time = f"{int(match.group(1)):02d}:{int(match.group(2)):02d}"
                set_alarm(alarm_time)
            else:
                speak("I didn't understand the time format. Please say it like 7:30 or 18:45")
        elif 'open notes app' in query:
            try:
                speak("Opening the notes app.")
                os.startfile(r"Websites\notes-app\index.html")
            except Exception as e:
                print_output(f"Failed to open the notes app: {e}")
                speak("Sorry, I couldn't open the notes app.")

        elif'open password generator' in query:
            try:
                speak("Opening the password generator.")
                os.startfile(r"Websites\password-generator\index.html")
            except Exception as e:
                print_output(f"Failed to open the password generator: {e}")
                speak("Sorry, I couldn't open the password generator.")

        elif 'open todo app' in query:
            try:
                speak("Opening the todo app.")
                os.startfile(r"Websites\todo-app\index.html")
            except Exception as e:
                print_output(f"Failed to open the todo app: {e}")
                speak("Sorry, I couldn't open the todo app.")

        elif 'open drawing app' in query:
            try:
                speak("Opening the drawing app.")
                os.startfile(r"Websites\drawing-app\index.html")
            except Exception as e:
                print_output(f"Failed to open the drawing app: {e}")
                speak("Sorry, I couldn't open the drawing app.")

        elif 'open github profiler' in query:
            try:
                speak("Opening the GitHub profiler.")
                os.startfile(r"Websites\github-profiles\index.html")
            except Exception as e:
                print_output(f"Failed to open the GitHub profiler: {e}")
                speak("Sorry, I couldn't open the GitHub profiler.")

        elif 'open car game' in query:
            try:
                speak("Opening the car game.")
                os.startfile(r"Websites\Game1\index.html")
            except Exception as e:
                print_output(f"Failed to open the car game: {e}")
                speak("Sorry, I couldn't open the car game.")

        elif 'open dino game' in query:
            try:
                speak("Opening the dinosaur game.")
                os.startfile(r"Websites\Game2\JavaScript Dragon Game\index.html")
            except Exception as e:
                print_output(f"Failed to open the dinosaur game: {e}")
                speak("Sorry, I couldn't open the dinosaur game.")

        else:
            try:
                try:
                    res = wolfram.query(query)
                    results = next(res.results).text
                    print_output('according to my sources-')
                    speak('according to my sources')
                    print_output(results)
                    speak(results)
                except:
                    results = wikipedia.summary(query, sentences=2)
                    print_output('according to wikipedia-')
                    speak('according to wikipedia')
                    print_output(results)
                    speak(results)

            except:
                speak('I don\'t know Sir! Google is smarter than me!')
                print_output('I don\'t know Sir! Google is smarter than me!')
                webbrowser.open('www.google.com')


if __name__ == "__main__":
    main(True)