import cv2
import pyshine as ps #  pip3 install pyshine==0.0.9
import sys
import os

def video_broadcasting():
    HTML="""
    <html>
    <head>
    <title>Rasberrypi Streaming</title>
    </head>

    <body>
    <center><h1>Robot cam</h1></center>
    <center><img src="stream.mjpg" width='640' height='480' autoplay playsinline></center>

    </body>
    </html>
    """

    StreamProps = ps.StreamProps
    StreamProps.set_Page(StreamProps,HTML)
    address = ('192.168.233.251',5050) # Enter PI? address 
    try:
        StreamProps.set_Mode(StreamProps,'cv2')
        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_BUFFERSIZE,4)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        capture.set(cv2.CAP_PROP_FPS,10)
        StreamProps.set_Capture(StreamProps,capture)
        StreamProps.set_Quality(StreamProps,90)
        server = ps.Streamer(address,StreamProps)
        print('[VIDEO_BROADCASTING]Started at','http://'+address[0]+':'+str(address[1]))
        server.serve_forever()
        
            
    except KeyboardInterrupt:       #press ctrl+c to exit
        print('[VIDEO_BROADCASTING]Terminated')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
        
video_broadcasting()
