from hand_highlight import  hand_main
from multiprocessing import Process,shared_memory
from voice_test import rps
import time

def handtracking():
    
    existing_shm = shared_memory.SharedMemory(name="ai_output")
    existing_shm2 = shared_memory.SharedMemory(name="cords")

    data = ""
    data1 = ""
    try:
        while True:
            
            prevdata = data
            prevdata1 = data1
            raw_data= bytes(existing_shm.buf[:20])
            data = raw_data.decode('utf-8').strip().strip('\x00')
            raw_data1= bytes(existing_shm2.buf[:3])
            data1 = raw_data1.decode('utf-8')
            if data:
                if prevdata == data:
                    pass
                else:
                    print(f"{data}")
            if data1:
                if prevdata1 == data1:
                    pass
                else:
                    print(f"{data1}")
            
                
    except KeyboardInterrupt:
        print("stop")
    finally:
        existing_shm.close



if __name__ == "__main__":
    p1 = Process(target=hand_main)
    p2 = Process(target=handtracking)
    p3 = Process(target=rps)
    p1.start()
    p2.start()
   
    p3.start()
    
    p1.join()
    p2.join()
    
    p3.join()

