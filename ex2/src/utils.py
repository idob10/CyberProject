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
        self._modify_queue.append(event.event_type + ',' + event.src_path + ',' + event.dest_path)

    def on_modified(self, event):
        if (event.is_directory):
            return

        self._modify_queue.append(event.event_type + ',' + event.src_path)

    def on_deleted(self, event):
        self._modify_queue.append(event.event_type + ',' + event.src_path)

    def on_created(self, event):
        self._modify_queue.append(event.event_type + ',' + event.src_path)

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

    def createFile(self, filePath):
        os.makedirs(filePath,exist_ok=True)
        self.copy_file(filePath)

    def handleNewModify(self, command):
        cmd, param = command.split(' ',1)
        if (cmd == "created"):
            self.createFile(param)
        elif (cmd == "moved"):
            self.moveRename(param)
        elif (cmd=="deleted"):
            self.delete(param)

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