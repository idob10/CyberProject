import os
import socket
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from server import sendMsg
from server import getMsg

# protocol constant
PROTOCOL_ACK = "ACK"
PROTOCOL_END_OF_FILE ="DONE"
PROTOCOL_END_OF_MODIFICATION = "FINISH"

class DirectoryObserver(FileSystemEventHandler):
    def __init__(self, modify_queue):
        self._modify_queue = modify_queue

    def on_moved(self, event):
        self._modify_queue.append(event.event_type + ',' + event.src_path + ',' + event.dest_path+','+event.is_directory)

    def on_modified(self, event):
        if (event.is_directory):
            return

        self._modify_queue.append(event.event_type + ',' + event.src_path)

    def on_deleted(self, event):
        self._modify_queue.append(event.event_type + ',' + event.src_path+','+event.is_directory)

    def on_created(self, event):
        self._modify_queue.append(event.event_type + ',' + event.src_path+','+str(event.is_directory))

    def get_modify_queue(self):
        return self._modify_queue

class DirectoryApplayer:
    def __init__(self, folder_path, sock):
        self._folder_path = folder_path
        self._sock = sock

    def delete(self, path):
        os.remove(self._folder_path + '\\' + path)

    def moveRename(self, paths):
        srcPath,dstPath = paths.split('\n', 1)
        os.rename(self._folder_path + '\\' + srcPath, self._folder_path + '\\' + dstPath)

    def copy_file(self, filePath):
        with open(self._folder_path + '\\' + filePath,'wb') as f:
            data = self._sock.recv(1024)
            print("recv:" + data.decode())
            while data.decode() != PROTOCOL_END_OF_FILE:
                f.write(data)
                self._sock.send(PROTOCOL_ACK.encode())
                print("send:" + PROTOCOL_ACK)
                data = self._sock.recv(1024)

            self._sock.send(PROTOCOL_ACK.encode())
            f.close()

    def createFile(self, filePath,isDir):
        if isDir == "False":
            self.copy_file(filePath)
        else:
            os.makedirs(self._folder_path + "\\" + filePath, exist_ok=True)

    def handleNewModify(self, command):
        command = command.split(',',3)
        if (command[0] == "created"):
            self.createFile(command[1],command[2])
        elif (command[0] == "moved"):
            self.moveRename(command[1])
        elif (command[0]=="deleted"):
            self.delete(command[1])
        
    def sendDir(self,dirName):
        listOfFiles = []
        listOfDirs = []
        for (dirpath, dirnames, filenames) in os.walk(dirName):
            listOfDirs += ([dirname for dirname in dirnames])
            listOfFiles += [file for file in filenames]
        
        for filePath in listOfFiles:
            sendMsg(self._sock, "created,"+filePath+",False")
            sendFile(os.path.join(dirName,filePath),self._sock)

        for filePath in listOfDirs:
            sendMsg(self._sock, "created,"+filePath+",True")

def sendFile(filePath, sock):
    try:
        with open(filePath, 'r') as f:
            data = f.read(1024)
            while len(data) != 0:
                sendMsg(sock, data)
                data = f.read(1024)

            sendMsg(sock, PROTOCOL_END_OF_FILE)
            f.close()
    except Exception:
        sendMsg(sock, PROTOCOL_END_OF_FILE)