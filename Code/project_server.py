import numpy as np
import cv2
import socket
import threading
import time

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 1776))
server_socket.listen(10)
(client_socket, address) = server_socket.accept()

cap = cv2.VideoCapture(0)

while cap.isOpened() :
    # Capture frame-by-frame
    ret,frame = cap.read()
    # Our operations on the frame come here
    color = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    #cv2.imshow('frame',color)
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
    result,encimg=cv2.imencode('.jpg',color,encode_param)
    client_socket.sendall(encimg)      #threads
    # Display the resulting frame
    #color1=client_socket.recv(3000000)
    
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cap.destroyAllWindows()
client_socket.close()
server_socket.close()
