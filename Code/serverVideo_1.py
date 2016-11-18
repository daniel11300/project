import socket
import cv2
#from PIL import Image
#from PIL import ImageTk
import os, sys, Tkinter
import time
import cv2

server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 9001))
server_socket.listen(1)
client_socket, address = server_socket.accept()

while True:
    data=client_socket.recv(3000000)
    
    f=open(r'd:\img1.jpg','wb')
    f.write(data)
    f.close()
    
    img=cv2.imread(r'd:\img1.jpg',1)
    cv2.imshow('image',img)
    cv2.waitKey(100)
  
    
client_socket.close()
server_socket.close()
