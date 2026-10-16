import speech_recognition as sr
import pyautogui as pag
import time
import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt,QTimer,Signal,QObject
from PySide6.QtGui import QFont,QPixmap
import os
import subprocess
import platform

class Signals(QObject):
    react = Signal()

signals = Signals()
global on
on = True
app = QApplication(sys.argv)
label = QLabel("Chat log:\nJarvis ready")
max_n = 5
messages = []
imlabel=QLabel()
PM= QPixmap(r"Image\Jarvis.jpeg").scaled(1920, 1080, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
imlabel.setPixmap(PM)

imlabel.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
imlabel.move(0,0)
imlabel.resize(1920,1080)

def react():
    imlabel.show()
    QTimer.singleShot(1000,imlabel.hide)
signals.react.connect(react)
def open_app(app_path):
    os_name = platform.system()
    if os_name == "Windows":
        # Use 'start' command in Windows command prompt
        subprocess.Popen(['start', app_path], shell=True)
def add_message(msg):
    global messages
    messages.append(msg)
    messages = messages[-max_n:]
    label.setText("Chat log:\n" + "\n".join(messages))
recog = sr.Recognizer()
def callback(recog,audio):
    try:
        words = recog.recognize_google(audio)
        print("You said: " + words)
        add_message(words)
        if 'jarvis clip that' in words.lower():
            print("yes sir")
            add_message("Jarvis: Yes sir!")
            pag.press('f8')
        if 'jarvis shutdown' in words.lower():
            print("ending")
            add_message("Jarvis: Ending session. Goodbye!")
            time.sleep(2)
            os._exit(0)
        if 'jarvis open roblox' in words.lower():
            open_app(r'c:\Users\light\AppData\Local\Roblox\Versions\version-1588a9c58c674e38\RobloxPlayerBeta.exe')
            add_message("Jarvis: Yes sir")
        if 'jarvis open autoclicker' in words.lower():
            open_app(r'c:\Users\light\AppData\Roaming\OP Auto Clicker\AutoClicker.exe')
            add_message("Jarvis: Yes sir")
        if 'jarvis rage quit and smash my keyboard' in words.lower():
            add_message("Jarvis: On the double sir")
            pag.keyDown("alt")
            pag.keyDown("f4")
            pag.keyUp("alt")
        if 'jarvis react to this' in words.lower():
            add_message("Jarvis: On the double sir")
            signals.react.emit()

    except sr.UnknownValueError:
        pass 

label.setFont(QFont("Arial", 14))
label.setStyleSheet("color: white; background: transparent;")
label.resize(800,200)
label.setWindowFlags(
    Qt.FramelessWindowHint |
    Qt.WindowStaysOnTopHint |
    Qt.Tool
)

label.setAttribute(Qt.WA_TranslucentBackground)
label.setAttribute(Qt.WA_TransparentForMouseEvents)

label.move(20, 20)
label.show()

with sr.Microphone() as source:
    print("Please say something:")
    recog.adjust_for_ambient_noise(source)
    audio = recog.listen(source)


recog.listen_in_background(sr.Microphone(), callback,phrase_time_limit=5)
sys.exit(app.exec())