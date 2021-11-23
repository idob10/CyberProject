import os
import socket
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
        self._modify_queue.append(event.event_type + ',' + event.src_path+','+event.is_directory)

    def get_modify_queue(self):
        return self._modify_queue

class DirectoryApplayer:
    def __init__(self, folder_id, sock):
        self._folder_id = folder_id
        self._sock = sock

    def delete(self, path):
        os.remove(self._folder_id + '\\' + path)

    def moveRename(self, paths):
        srcPath,dstPath = paths.split('\n', 1)
        os.rename(self._folder_id + '\\' + srcPath, self._folder_id + '\\' + dstPath)

    def copy_file(self, filePath):
        with open(self._folder_id + '\\' + filePath,'w') as f:
            data = self._sock.recv(1024)
            while data.decode() != PROTOCOL_END_OF_FILE:
                f.write(data)
                self._sock.send(PROTOCOL_ACK.encode())
                data = self._sock.recv(1024)
            f.close()

    def createFile(self, filePath,isDir):
        os.makedirs(filePath,exist_ok=True)
        if (not bool(isDir)):
            self.copy_file(filePath)

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
            listOfDirs += ([os.path.join(dirpath,dirname) for dirname in dirnames])
            listOfFiles += [os.path.join(dirpath, file) for file in filenames]
        
        for filePath in listOfFiles:
            self._sock.send(("created"+filePath+",False").encode())
            sendFile(filePath,self._sock)

        for filePath in listOfDirs:
            self._sock.send(("created"+filePath+",True").encode())

def sendFile(filePath, sock):
    try:
        with open(filePath, 'r') as f:
            data = f.read(1024)
            while len(data) != 0:
                sock.send(data)
                sock.recv(1024) #getting the ack
                data = f.read(1024)

            sock.send(PROTOCOL_END_OF_FILE.encode())
            f.close()
    except Exception:
        sock.send(PROTOCOL_END_OF_FILE.encode())
