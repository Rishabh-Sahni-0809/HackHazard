from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


import subprocess
import sys
import os


# Start server.py silently
def run_server():
    server_path = os.path.join(os.getcwd(), 'desktop_use\server.exe')  # Path to server.exe
    if os.path.exists(server_path):
        if sys.platform == "win32":
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen([server_path], creationflags=CREATE_NO_WINDOW)
        else:
            subprocess.Popen([server_path])
    else:
        print("server.exe not found!")

run_server()


def open_gui(script_name):
    window.destroy()  # Close current window
    subprocess.Popen([sys.executable, script_name])


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"Design\build\assets\frame1")


def relative_to_assets(path: str) -> Path:
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)  # Temporary folder used by PyInstaller
    else:
        base_path = Path(__file__).parent
    return base_path / "Design/build/assets/frame1" / Path(path)


window = Tk()

window.geometry("750x680")
window.configure(bg = "#1C1C1C")


canvas = Canvas(
    window,
    bg = "#1C1C1C",
    height = 680,
    width = 750,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
canvas.create_text(
    285.0,
    63.0,
    anchor="nw",
    text="DAVE AI",
    fill="#FFFFFF",
    font=("PlayfairDisplay Medium", 48 * -1)
)

canvas.create_text(
    190.0,
    149.0,
    anchor="nw",
    text="Welcome to DAVE AI",
    fill="#FFFFFF",
    font=("Inter Medium", 40 * -1)
)

image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    99.0,
    321.0,
    image=image_image_1
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    385.0,
    290.0,
    image=image_image_2
)

image_image_3 = PhotoImage(
    file=relative_to_assets("image_3.png"))
image_3 = canvas.create_image(
    632.0,
    288.0,
    image=image_image_3
)

canvas.create_text(
    512.0,
    433.0,
    anchor="nw",
    text="Limitations",
    fill="#FFFFFF",
    font=("Inter SemiBold", 18 * -1)
)

image_image_4 = PhotoImage(
    file=relative_to_assets("image_4.png"))
image_4 = canvas.create_image(
    557.0,
    409.0,
    image=image_image_4
)

image_image_5 = PhotoImage(
    file=relative_to_assets("image_5.png"))
image_5 = canvas.create_image(
    378.0,
    412.0,
    image=image_image_5
)

canvas.create_text(
    152.0,
    433.0,
    anchor="nw",
    text="Examples",
    fill="#FFFFFF",
    font=("Inter SemiBold", 18 * -1)
)

image_image_6 = PhotoImage(
    file=relative_to_assets("image_6.png"))
image_6 = canvas.create_image(
    190.0,
    413.0,
    image=image_image_6
)

canvas.create_text(
    326.0,
    433.0,
    anchor="nw",
    text="Capabilities",
    fill="#FFFFFF",
    font=("Inter SemiBold", 18 * -1)
)

image_image_7 = PhotoImage(
    file=relative_to_assets("image_7.png"))
image_7 = canvas.create_image(
    376.0,
    627.0,
    image=image_image_7
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    391.0,
    626.5,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#EDEDED",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=76.0,
    y=613.0,
    width=630.0,
    height=25.0
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: open_gui("gui.py"),
    relief="flat"
)
button_1.place(
    x=687.0,
    y=618.0,
    width=14.0,
    height=17.0
)

canvas.create_text(
    84.0,
    617.0,
    anchor="nw",
    text="Type message",
    fill="#2C2C2C",
    font=("Inter", 14 * -1)
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: open_gui("gui2.py"),
    relief="flat"
)
button_2.place(
    x=45.0,
    y=619.0,
    width=13.0,
    height=18.0
)
window.resizable(False, False)
window.mainloop()
