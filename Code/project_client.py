import numpy as np
import cv2
import socket
import threading
import time
my_socket = socket.socket()
my_socket.connect(('127.0.0.1', 1776))

#cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    #ret, frame = cap.read()
    # Our operations on the frame come here
    #color = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    # Display the resulting frame
    data=my_socket.recv(640*480*24)
    print data
    decoded=cv2.imdecode(data,1)
    cv2.imshow('image',decoded)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
#cap.release()
cv2.destroyAllWindows()
my_socket.close()
