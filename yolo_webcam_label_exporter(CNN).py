import cv2
import numpy as np
import glob
import random

# Images & labels export path
export_path=r"C:\Users\Muhammed\Desktop\New folder\grad. code\code 1\yolo_custom_detection\saved_images"
export_path=export_path+"\\"
    
#create total_number.txt if non existent
file_total = open(export_path + r"total_number.txt","a")
file_total.close
#reading the total number of saved images
file = open(export_path + "total_number.txt","r+")
if(file.read()==""):
    img_id=0
else:
    file.seek(0)
    img_id=int(file.read())
    
def export_label(xMin,yMin,wBox,hBox,width,height,export_path):
    
    #exporting labels
    yolo_label_txt = open(export_path+"labels.txt","a")
    bBox="["+str(xMin)+","+str(yMin)+","+str(wBox)+","+str(hBox)+"]"
    line=str(img_id)+" "+str(width)+" "+str(height)+" "+str(bBox)+"\n"
    yolo_label_txt.write(line)
    yolo_label_txt.close

# Load Yolo
net = cv2.dnn.readNet("yolov3_training_last.weights", "yolov3_testing.cfg")

# Name custom object
classes = ["apple"]

# get webcam stream
webcam = cv2.VideoCapture(0)    #index 0 ==> laptop cam

#box color
color =[200, 99, 243]

while True:
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    # Loading image
    ret,img = webcam.read()
    #img = cv2.resize(img, (800, 600))
    height, width, channels = img.shape

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
            if confidence > 0.3:
                # Object detected
                print(class_id)
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
                
                #export the detected image
                cv2.imwrite(export_path+str(img_id)+".jpg", img)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    print(indexes)
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            export_label(x,y,w,h,width,height,export_path)
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y + 30), font, 3, color, 2)
        
        #updating the total number of saved images
        if i==len(boxes)-1:
            img_id=img_id+1
    
    #updating the total number of saved images in txt
    file.seek(0)
    file.write(str(img_id))
    file.close


    cv2.imshow("Stream", img)
    #key = cv2.waitKey(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

webcam.release()
cv2.destroyAllWindows()


