from multiprocessing import dummy
from operator import le
from queue import Queue
import cv2
import numpy as np
import socket 
import threading
import time


q=Queue()
qf=Queue()

HEADER = 64
PORT = 5051
#SERVER = "192.168.43.17"     #server = "192.168.1.10"
FORMAT = 'utf-8'
DISCONNECT_MESSAGE="!DIS"




def process_img(q,qf):

    net = cv2.dnn.readNet(r'C:\Users\Muhammed\Desktop\yolov3_training_last (3).weights',r'C:\Users\Muhammed\Desktop\yolov3_training.cfg')
    classes = ["Ripe","Unripe","Rotten"]

    # get webcam stream
    def arm_XYZ(x, y, w, h):        #at 10cm apple width(w)=500
        #arm_z=10*500/w#cm        #arm_z
        ref_x=width/2
        ref_y=height-height*0.0
        arm_x=(x+w/2-ref_x)              #x limit from arm needed??
        arm_y=(ref_y-y-h/2)-160
        cv2.line(img,(int(ref_x),int(ref_y)),(int(x+w/2),int(y +h/2)),[204,0,204],1)
        d=5.2                         #d is average apple width in cm
        z=width*d/w
        #print(z)
        return [arm_x,arm_y,w,h]


    
    N=1
    while True:

        if qf.get()=="scan":
            boxesN=[]
            
            try:
                layer_names = net.getLayerNames()
                output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
                colors = np.random.uniform(0, 255, size=(len(classes), 3))


                webcam = cv2.VideoCapture("http://192.168.233.100:5050/stream.mjpg")    #index 0 ==> laptop cam "http://192.168.43.54:5049/stream.mjpg"
                # Loading image
                ret,img = webcam.read()
                #img = cv2.resize(img, (800, 600))
                height, width, channels = img.shape
                #print(height, width)
                # Detecting objects
                blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

                net.setInput(blob)
                outs = net.forward(output_layers)

                # Showing informations on the screen
                class_ids = []
                confidences = []
                boxes = []
                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        
                        class_id = np.argmax(scores)
                        
                        confidence = scores[class_id]
                        if confidence > 0.5:
                            #print("confidence="+str(confidence))
                            # Object detected
                            #print(class_id)
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)

                            # Rectangle coordinates
                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)

                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)

                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
                #print(indexes)
                font = cv2.FONT_HERSHEY_PLAIN




                for i in range(len(boxes)):
                    if i in indexes:
                        #print(x, y, w, h)
                        x, y, w, h = boxes[i]

                        
                        q.put(np.round_(np.multiply(arm_XYZ(x, y, w, h),0.3125)))
                        
                            
                       
                        

                        
                        


                        
                        label = str(classes[class_ids[i]])
                        if(class_ids[i]==0):
                            color = [102, 102, 255]
                        elif(class_ids[i]==1):
                            color = [102, 255, 102]
                        else:
                            color = [0, 25, 51]
                        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                        cv2.circle(img,(x+int(w/2),y+int(h/2)),3,[0, 179, 255],-1)
                        cv2.putText(img, label, (x, y + 30), font, 3, color, 2)
                        

                        


                cv2.imshow("Stream", img)
                #key = cv2.waitKey(0)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                #print("class_id="+str(class_id))
                #print("scores="+str(scores))
            except:
                pass
            webcam.release()
            q.put("empty")


            

        


    
##############################################################################################
def cord_sender(q):
    ADDR = ("192.168.233.100" ,PORT)                                        #PI IP
    #print(ADDR)
    client= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    while True:
        try:
            client.connect(ADDR)
            break
        except:
            print("[COORDINATES_SERVER]ERROR:Can't connect (Re-enter IP or port),(an another server exists on port),(server didn't start)")
            #time.sleep(1)

    print ("[COORDINATES_SERVER]connected to PI")
    
    def send(msg):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)
        print("[COORDINATES_SERVER]sent msg to PI:"+msg)
    #send("test")
    

    while True:
        if q.empty():
            #print("pass")
            time.sleep(0.5)
            pass
        else:
            x=str(q.get())
            send(x)

##############################################################################################
def flag_listener(qf):
    port=PORT+1
    ADDR= ("192.168.233.251" ,port)                                #laptop IP
    #print(ADDR)
    server= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        server.bind(ADDR)
    except:
        print("[FLAG_SERVER]ERROR:Another connection on port")
        

    def handle_client(conn, addr):
        print("[FLAG_SERVER]PI "+str(addr)+" is connected")
        connected = True
        while connected:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)      #The recived msg
                if msg == DISCONNECT_MESSAGE:
                    connected=False
                    print("[FLAG_SERVER]PI "+str(addr)+" DISCONNECTED")
                    quit()
                else:
                    print("[FLAG_SERVER]msg recived from PI "+str(addr)+": "+msg)
                    if msg == "scan":
                        qf.put(msg)

        conn.close

    def start():
        server.listen()
        print("[FLAG_SERVER]server is listening on "+str(ADDR))
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args= (conn, addr))
            thread.start()
            #print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


    print("[FLAG_SERVER]server is starting")
    start()
    




thread1 = threading.Thread(target=process_img, args=(q,qf,))
thread2 = threading.Thread(target=cord_sender, args=(q,))
thread3 = threading.Thread(target=flag_listener, args=(qf,))

thread1.start()
thread2.start()
thread3.start()