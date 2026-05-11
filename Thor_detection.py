import argparse
import os
import time
import cv2
import mediapipe as mp
import numpy as np
import pickle
from collections import deque
from hand_highlight import parse_args, hand_main
from multiprocessing import Process,shared_memory

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
except Exception:
    RandomForestClassifier = None


def handtracking():
    
    existing_shm = shared_memory.SharedMemory(name="ai_output")

    data = ""
    try:
        while True:
            prevdata = data
            raw_data= bytes(existing_shm.buf[:20])
            data = raw_data.decode('utf-8').strip().strip('\x00')
            if data:
                if prevdata == data:
                    pass
                else:
                    print(f"{data}")
            
                
    except KeyboardInterrupt:
        print("stop")
    finally:
        existing_shm.close



if __name__ == "__main__":
    p1 = Process(target=hand_main)
    p2 = Process(target=handtracking)
    p1.start()
    p2.start()
   
    p1.join()
    p2.join()