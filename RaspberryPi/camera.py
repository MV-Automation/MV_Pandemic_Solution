import cv2
import time
import multiprocessing as mp

#Camera class to load the rtsp stream into another process with multiprocessing
#in order to increase performance
class camera():

    def __init__(self,rtsp_url):        
        #load pipe for data transmittion to the process
        self.parent_conn, child_conn = mp.Pipe()
        #load process
        self.p = mp.Process(target=self.update, args=(child_conn,rtsp_url))        
        #start process
        self.p.daemon = True
        self.p.start()

    def end(self):
        #send closure request to process
        self.parent_conn.send(2)

    def update(self,conn,rtsp_url):
        #load cam into seperate process
        print("Camera Loading")
        cap = cv2.VideoCapture(rtsp_url,cv2.CAP_FFMPEG)   
        print("Camera Loaded")
        run = True

        while run:

            #grab frames from the buffer
            cap.grab()

            #recieve input data
            rec_dat = conn.recv()


            if rec_dat == 1:
                #if frame requested
                _, frame = cap.retrieve()
                conn.send(frame)

            elif rec_dat == 2:
                #if close requested
                cap.release()
                run = False

        print("Camera Connection Closed")        
        conn.close()
        cv2.destroyAllWindows()
        return

    def get_frame(self,resize=None):
        ###used to grab frames from the cam connection process

        #send request
        self.parent_conn.send(1)
        frame = self.parent_conn.recv()

        #reset request 
        self.parent_conn.send(0)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #resize if needed
        if resize == None:            
            return frame
        else:
            return self.rescale_frame(frame)

    def rescale_frame(self,frame):
        return cv2.resize(frame,(800, 480), interpolation = cv2.INTER_AREA) 

# Based on the code provided by Lewis Morris at 
# https://stackoverflow.com/questions/60816436/open-cv-rtsp-camera-buffer-lag