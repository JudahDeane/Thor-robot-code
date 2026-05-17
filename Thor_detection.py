from hand_highlight import  hand_main
from multiprocessing import Process,shared_memory




def handtracking():
    
    existing_shm = shared_memory.SharedMemory(name="ai_output")
    existing_shm2 = shared_memory.SharedMemory(name="cords")

    data = ""
    try:
        while True:
            
            prevdata = data
            raw_data= bytes(existing_shm.buf[:20])
            data = raw_data.decode('utf-8').strip().strip('\x00')
            raw_data= bytes(existing_shm2.buf[:3])
            data = raw_data.decode('utf-8')
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