import wave
import winsound as ws
from piper import PiperVoice
import speech_recognition as sr
import sys
from multiprocessing import Process,shared_memory
import pygame as pg
import time
import random as rd
import serial as ps
import pyttsx3
import sounddevice as sd
import os 
import tempfile
import subprocess

r = sr.Recognizer()
ser = ps.Serial(port="COM3", baudrate=115200, timeout=1)
time.sleep(2)
pg.init()
pg.mixer.init()
window = pg.display.set_mode((80,80))   
recog = sr.Recognizer()
# global history
existing_shm = shared_memory.SharedMemory(name="ai_output")

def speak_on_device(text):
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    try:
        render_code = (
            "import sys, pyttsx3; "
            "engine = pyttsx3.init(); "
            "engine.setProperty('rate', 100); "
            "engine.setProperty('volume', 1.0); "
            "voices = engine.getProperty('voices'); "
            "engine.setProperty('voice', voices[0].id); "
            "engine.save_to_file(sys.argv[2], sys.argv[1]); "
            "engine.runAndWait(); "
            "engine.stop()"
        )
        subprocess.run(
            [sys.executable, "-c", render_code, temp_file, text],
            check=True,
            timeout=30,
        )

        if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
            raise RuntimeError(f"Speech audio was not created: {temp_file}")
        # PlaySound is synchronous by default, so it waits for the WAV to finish.
        ws.PlaySound(temp_file, ws.SND_FILENAME)
    finally:
        try:
            os.remove(temp_file)
        except OSError:
            pass
    
class RPS:
    allitems = []
    def __init__(self, beats,losses,name):
        self.beats = beats
        self.losses = losses
        self.name = name
        RPS.allitems.append(name)
        pass
    def getName(self):
        return self.name
    @classmethod
    def random(cls):
        return cls.allitems
    def play(self,op):
        print(self)
        if self.name == "scissors":
            ser.write(b"g1 h2 y30 z50 v-70 w80  \n")
            time.sleep(8)
            speak_on_device("scissors")
            
        if self.name == "rock":
            ser.write(b"g1 h2 y30 z50  w80 v-80 \n")
            time.sleep(8)
            speak_on_device("rock")
        if self.name == "paper":
            ser.write(b"g1 h2 y30 z50 v170 w200 \n")
            time.sleep(8)
            speak_on_device("paper")
        # count down and release for robot animation
        if op == self.beats:
            
            return "Win"
        if op == self.losses:
            
            return "Loss"
        if op == self.name:
            
            return "Draw"
def rps():
    time.sleep(5)
    ser.write(b"m17\n")

    rock = RPS("scissors","paper","rock")
    scissors = RPS("paper","rock","scissors")
    paper = RPS("rock","scissors","paper")
    list = [rock,paper,scissors]
    
    while True:
        existing_shm = shared_memory.SharedMemory(name="ai_output")
        raw_data= bytes(existing_shm.buf[:20])
        data = raw_data.decode('utf-8').strip().strip('\x00')
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_l:
                    print("L")
                        # raw_data1= bytes(existing_shm.buf[:20])
                        # data = raw_data1.decode('utf-8')
                    
                   
                    choosen = list[rd.randrange(0,2)]
                    print(choosen.getName)
                    data = data.lower()
                    print(data)
                    outcome = choosen.play(data)
                    print("outcome:", repr(outcome))
                    
                    ser.write(b"g1 h2 x0 y0 z0 u0 w0 v0\n")
                    
                    if outcome== "Win":
                        speak_on_device("u lost to a clanker")
                        print("you lost")
                            
                            
                    if outcome== "Loss":
                        speak_on_device("aww I lost")
                                                        
                        print("congrats you won")
                        
                    if outcome== "Draw":
                        speak_on_device("we drew lets go again")
                        print("it was a draw lets go again")
                            
                            
                    
                    
                    time.sleep(4)
                            
                            



if __name__ == "__main__":
    
    
    rps()
   