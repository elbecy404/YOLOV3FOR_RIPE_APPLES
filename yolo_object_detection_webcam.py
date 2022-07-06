import cv2
import numpy as np



# Load Yolo
net = cv2.dnn.readNet("yolov3_tiny_training_last.weights", "yolov3_tiny.cfg")

# Name custom object
classes = ["apple"]

# get webcam stream
webcam = cv2.VideoCapture(0)    #index 0 ==> laptop cam

while True:
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))



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
                #print("confidence="+str(confidence))
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

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    print(indexes)
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            print(x, y, w, h)
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = colors[class_ids[i]]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y + 30), font, 3, color, 2)


    cv2.imshow("Stream", img)
    #key = cv2.waitKey(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    print("class_id="+str(class_id))
    print("scores="+str(scores))
webcam.release()
cv2.destroyAllWindows()


def arm_XYZ(x, y, w):        #at 10cm apple width(w)=500
    arm_z=10*w/500#cm        #arm_z
    arm_x=x-w/2              #x limit from arm needed??
    arm_y=y
    return arm_x,arm_y,arm_z