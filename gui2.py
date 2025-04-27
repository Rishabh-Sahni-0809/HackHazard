from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage
from PIL import Image, ImageTk, ImageSequence
import sys
import subprocess
import Digital_Assistant # Import the Digital_Assistant module


def open_gui(script_name):
    window.destroy()
    subprocess.Popen([sys.executable, script_name])


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"Design\build\assets\frame2")


def relative_to_assets(path: str) -> Path:
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)  # Temporary folder used by PyInstaller
    else:
        base_path = Path(__file__).parent
    return base_path / "Design/build/assets/frame2" / Path(path)



from Digital_Assistant import set_output_callback  # Import the callback setter

def update_response_text(message):
    """Update the response text in the GUI."""
    canvas.itemconfig(response_text, text=message)
    window.update()

# Set the callback function for Digital_Assistant
set_output_callback(update_response_text)

import io
import contextlib


def listen_and_respond():
    canvas.itemconfig(response_text, text="How May I Help You")
    window.update()

    # Redirect stdout temporarily to capture prints
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        Digital_Assistant.main(False)  # Run normally, but capture what it prints

    output = buffer.getvalue().strip()  # Get the printed output
    if output:
        canvas.itemconfig(response_text, text=output)
    else:
        canvas.itemconfig(response_text, text="Sorry, I didn't catch that!")


window = Tk()
window.geometry("750x680")
window.configure(bg="#1C1C1C")

canvas = Canvas(window, bg="#1C1C1C", height=680, width=750, bd=0,
                highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

# Background mic area images
image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(376.0, 639.0, image=image_image_1)

entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
canvas.create_image(391.0, 638.5, image=entry_image_1)

entry_1 = Entry(bd=0, bg="#EDEDED", fg="#000716", highlightthickness=0)
entry_1.place(x=76.0, y=625.0, width=630.0, height=25.0)

# Buttons
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
Button(window, image=button_image_1, borderwidth=0, highlightthickness=0,
       command=lambda: open_gui("gui.py"), relief="flat").place(x=687.0, y=630.0, width=14.0, height=17.0)

button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
Button(window, image=button_image_2, borderwidth=0, highlightthickness=0,
       command=listen_and_respond, relief="flat").place(x=45.0, y=631.0, width=13.0, height=18.0)

button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
Button(window, image=button_image_3, borderwidth=0, highlightthickness=0,
       command=lambda: open_gui("gui.py"), relief="flat").place(x=11.0, y=28.0, width=210.0, height=49.0)

canvas.create_text(375.0, 38.0, anchor="nw", text="DAVE AI", fill="#FFFFFF", font=("PlayfairDisplay Medium", 40 * -1))
canvas.create_text(250.0, 95.0, anchor="nw", text="Welcome to DAVE AI", fill="#FFFFFF", font=("Inter Medium", 40 * -1))

# Response Text (dynamic)
response_text = canvas.create_text(299.0, 458.0, anchor="nw",
                                   text="HOW CAN I HELP YOU", fill="#FFFFFF", font=("Roboto", 14 * -1))


# Mic animation
class AnimatedGIF:
    def __init__(self, canvas, gif_path, x, y):
        self.canvas = canvas
        self.gif_path = gif_path
        self.frames = []
        self.load_frames()
        self.index = 0
        self.image_obj = self.canvas.create_image(x, y, image=self.frames[0])
        self.animate()

    def load_frames(self):
        gif = Image.open(self.gif_path)
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert("RGBA")
            self.frames.append(ImageTk.PhotoImage(frame))

    def animate(self):
        self.canvas.itemconfig(self.image_obj, image=self.frames[self.index])
        self.index = (self.index + 1) % len(self.frames)
        window.after(100, self.animate)


# Load mic animation
mic_anim = AnimatedGIF(canvas, relative_to_assets("MicAni.gif"), 450.0, 323.0)


# Start by listening immediately once when GUI opens
window.after(1000, listen_and_respond)  # Call listen_and_respond after 100ms

window.resizable(False, False)
window.mainloop()
