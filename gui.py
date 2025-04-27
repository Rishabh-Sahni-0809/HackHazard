from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, StringVar, Label, Frame, scrolledtext
import sys
import subprocess
import threading
import os

# Import necessary functions from Digital_Assistant.py
from Digital_Assistant import set_output_callback,main,submit_query
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"Design\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)  # Temporary folder used by PyInstaller
    else:
        base_path = Path(__file__).parent
    return base_path / "Design/build/assets/frame0" / Path(path)


def open_gui(script_name):
    window.destroy()  # Close current window
    subprocess.Popen([sys.executable, script_name])

# Function to handle updating the chat display with assistant responses
def update_chat_display(message):
    chat_box.config(state='normal')
    chat_box.insert('end', f"DAVE: {message}\n\n", 'assistant')
    chat_box.see('end')  # Auto-scroll to the bottom
    chat_box.config(state='disabled')

# Process the user's query and handle responses
def process_query(query):
    submit_query(query)  # Call the function to process the query

# Function to submit user's query to the assistant
def submit_message():
    query = entry_1.get()
    if query.strip():
        # Clear entry field
        entry_1.delete(0, 'end')
        
        # Add user message to chat box
        chat_box.config(state='normal')
        chat_box.insert('end', f"You: {query}\n", 'user')
        chat_box.see('end')  # Auto-scroll to the bottom
        chat_box.config(state='disabled')
        
        # Process the query in a separate thread to avoid freezing the GUI
        threading.Thread(target=process_query, args=(query,), daemon=True).start()

# Initialize the assistant
def initialize_assistant():
    set_output_callback(update_chat_display)
    main(True)  # Start the assistant in non-voice mode

# Make a thread-safe wrapper
def safe_initialize_assistant():
    threading.Thread(target=initialize_assistant, daemon=True).start()

# Instead of calling initialize_assistant directly


    
    

window = Tk()
window.geometry("750x680")
window.configure(bg="#1C1C1C")
window.title("DAVE AI Assistant")

canvas = Canvas(
    window,
    bg="#1C1C1C",
    height=680,
    width=750,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

# Create chat box for conversation
chat_frame = Frame(window, bg="#1C1C1C")
chat_frame.place(x=30, y=90, width=680, height=515)

chat_box = scrolledtext.ScrolledText(
    chat_frame,
    bg="#1C1C1C",
    fg="#FFFFFF",
    font=("Inter", 12),
    wrap='word'
)
chat_box.pack(fill='both', expand=True)
chat_box.tag_configure('user', foreground='#CCCCCC')
chat_box.tag_configure('assistant', foreground='#FFFFFF')
chat_box.config(state='disabled')

# Add welcome message
chat_box.config(state='normal')
chat_box.insert('end', "DAVE: Hello! I'm DAVE, your Digital Assistant. How can I help you today?\n\n", 'assistant')
chat_box.config(state='disabled')

image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(378.0, 641.0, image=image_image_1)

entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(393.0, 640.5, image=entry_image_1)
entry_1 = Entry(
    bd=0,
    bg="#EDEDED",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=78.0,
    y=627.0,
    width=630.0,
    height=25.0
)
# Bind Enter key to submit
entry_1.bind("<Return>", lambda event: submit_message())

button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=submit_message,
    relief="flat"
)
button_1.place(
    x=689.0,
    y=630.0,
    width=14.0,
    height=17.0
)

placeholder_text = StringVar()
placeholder_text.set("Type message")
placeholder_label = Label(
    window,
    textvariable=placeholder_text,
    bg="#EDEDED",
    fg="#2C2C2C",
    font=("Inter", 14 * -1)
)
placeholder_label.place(
    x=72.0,
    y=631.0
)

def on_entry_click(event):
    if placeholder_text.get() == "Type message":
        placeholder_text.set("")
        
def on_focus_out(event):
    if entry_1.get() == "":
        placeholder_text.set("Type message")

entry_1.bind("<FocusIn>", on_entry_click)
entry_1.bind("<FocusOut>", on_focus_out)

button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: open_gui("gui2.py"),
    relief="flat"
)
button_2.place(
    x=47.0,
    y=633.0,
    width=13.0,
    height=18.0
)

button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: open_gui("gui1.py"),
    relief="flat"
)
button_3.place(
    x=13.0,
    y=30.0,
    width=210.0,
    height=49.0
)

canvas.create_text(
    345.0,
    40.0,
    anchor="nw",
    text="DAVE AI",
    fill="#FFFFFF",
    font=("PlayfairDisplay Medium", 40 * -1)
)

image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(47.0, 144.0, image=image_image_2)

# Set the output callback and initialize the assistant
set_output_callback(update_chat_display)
window.after(1000, safe_initialize_assistant)

window.resizable(False, False)
window.mainloop()