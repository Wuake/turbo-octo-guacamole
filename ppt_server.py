import socket
import os
import os.path
import win32com.client as win32
import time
import win32com.client

#message box
import ctypes

import tkinter as tk
from tkinter import messagebox


#https://medium.com/@chasekidder/controlling-powerpoint-w-python-52f6f6bf3f2d
#https://pypi.org/project/ppt-control/
def server_program():
    # get the hostname
    host = '127.0.0.1'
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind(('', port))  # bind host address and port together
    
    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    print("server running :: \n")
    while True:
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            if not data:
                break
            print("from connected user: " + str(data))
            smsg = str(data)  # initiate port no above 1024
            print(smsg.split("@")[0])
            if smsg.split("@")[0] == "open_ppt": 
                msg = "server ok "
                ppt = smsg.split("@")[1] # "C:\\wamp64\\www\\test.pptx"
                conn.send(msg.encode())  # send data to the client
                #os.system('start /max "" "POWERPNT.EXE" /c '+ppt)  # /s slide show C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\
                #
                print("ppt file ", ppt)
                app = win32.gencache.EnsureDispatch("PowerPoint.Application")
                
                if os.path.isfile(ppt) :
                    ppt =  str(ppt.replace("\\", "\\\\"))   
                    presentation = app.Presentations.Open(FileName=ppt,  ReadOnly=0) # Untitled=0,WithWindow=1
                    presentation.SlideShowSettings.ShowType = win32.constants.ppShowTypeSpeaker
                    presentation.SlideShowSettings.Run()
                    print("ppt file ______after run_____________ ", ppt)
                    time.sleep(10)
                   
                else : print("File not exist : ", ppt)
                    #ctypes.windll.user32.MessageBoxExW(0, text, title, 0x1000)
                
                #close ppt
                presentation.Close()
                app.Quit()
                del app
                os.system('taskkill /F /IM POWERPNT.EXE')
                
        conn.close()  # close the connection
        print("client disconnected")
        
        #exit()                    

if __name__ == '__main__':
    server_program()
