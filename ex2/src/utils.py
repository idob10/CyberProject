import os
from watchdog.events import FileSystemEventHandler
from server import sendBytesMsg, sendMsg

# protocol constant
PROTOCOL_ACK = "ACK"
PROTOCOL_END_OF_FILE ="DONE"
PROTOCOL_END_OF_MODIFICATION = "FINISH"

class DirectoryObserver(FileSystemEventHandler):
    def __init__(self, modify_queue, filePath):
        self._modify_queue = modify_queue
        self._filePath = filePath

    def on_moved(self, event):
        if event.is_directory == True and len(os.listdir(event.dest_path))!=0:
            return
        # saving the massage
        self._modify_queue.append(event.event_type + ',' + event.src_path[len(self._filePath) + 1 : ]
                                  + ',' + event.dest_path[len(self._filePath) + 1 : ]+','+str(event.is_directory))

    def on_modified(self, event):
        if (event.is_directory):
            return
        # saving the massage
        self._modify_queue.append("modified" + ',' + event.src_path[len(self._filePath) + 1 : ] + ',' + "False")
        # self._modify_queue.append("modified" + ',' + event.src_path[len(self._filePath) + 1 : ]+',' + "False")

    def on_deleted(self, event):
        # saving the massage
        self._modify_queue.append(event.event_type + ',' + event.src_path[len(self._filePath) + 1 : ] +','+str(event.is_directory))

    def on_created(self, event):
        # saving the massage
        self._modify_queue.append(event.event_type + ',' + event.src_path[len(self._filePath) + 1 : ]
                                  + ',' + str(event.is_directory))

    def get_modify_queue(self):
        return self._modify_queue

# updating a folder
class DirectoryApplayer:
    def __init__(self, folder_path, sock):
        self._folder_path = folder_path
        self._sock = sock
        self._cmdServer = []

    def set_sock(self, sock):
        self._sock = sock

    def delete(self, path):
        # cecking if it a folder
        if os.path.isdir(os.path.join(self._folder_path,path)):
            os.rmdir(os.path.join(self._folder_path,path))
        else:
            os.remove(os.path.join(self._folder_path,path))

    def moveRename(self, srcPath,dstPath):
        #os.makedirs(os.path.dirname(os.path.join(self._folder_path, dstPath)), exist_ok=True)
        os.renames(os.path.join(self._folder_path,srcPath), os.path.join(self._folder_path,dstPath))
        os.makedirs(os.path.dirname(os.path.join(self._folder_path,srcPath)), exist_ok=True)

    def copy_file(self, filePath):
        with open(os.path.join(self._folder_path, filePath),'wb') as f:
            data = self._sock.recv(1024)
            print("recv bytes")

            # getting the data from the socket
            while True:
                try:
                    # check if it the end of f
                    if data.decode() == PROTOCOL_END_OF_FILE:
                        break
                    self.writeSliceData(data,f)
                    data = self._sock.recv(1024)
                except:
                    self.writeSliceData(data,f)
                    data = self._sock.recv(1024)

            self._sock.send(PROTOCOL_ACK.encode())
            f.close()
    
    def writeSliceData(self,data,f):
        f.write(data)
        self._sock.send(PROTOCOL_ACK.encode())
        print("send:" + PROTOCOL_ACK)

    def createFile(self, filePath,isDir):
        if isDir == "False":
            self.copy_file(filePath)
        else:
            os.makedirs(os.path.join(self._folder_path,filePath), exist_ok=True)

    def handleNewModify(self, command):
        self._cmdServer.append(command)

        # handle a modification to a folder
        command = command.split(',',4)
        if (command[0] == "created"):
            self.createFile(command[1],command[2])
        elif (command[0] == "moved"):
            self._cmdServer.append("created,"+command[2]+","+command[3])
            self._cmdServer.append("deleted,"+command[1]+","+command[3])
            self.moveRename(command[1], command[2])
        elif (command[0]=="deleted"):
            self.delete(command[1])
        elif (command[0]=="modified"):
            self.delete(command[1])
            self.createFile(command[1],command[2])
            self._cmdServer.append("created,"+command[1]+","+command[2])
            self._cmdServer.append("deleted,"+command[1]+","+command[2])

    def getCmdServer(self):
        return self._cmdServer
    
    def clear(self):
        self._cmdServer = []
        
    def sendDir(self,dirName):
        listOfFiles = []
        listOfDirs = []
        # going throw the folder and saving all the files and folders in a list
        for (dirpath, dirnames, filenames) in os.walk(dirName):
            if dirpath == self._folder_path:
                listOfDirs+=dirnames
            else:
                listOfDirs += ([os.path.join(os.path.relpath(dirpath,self._folder_path),dirname) for dirname in dirnames])
            if dirpath == self._folder_path:
                listOfFiles += filenames
            else:
                listOfFiles += [os.path.join(os.path.relpath(dirpath,self._folder_path),file) for file in filenames]

        # sending the files and folders
        for filePath in listOfDirs:
            sendMsg(self._sock, "created,"+filePath+",True")

        for filePath in listOfFiles:
            sendMsg(self._sock, "created,"+filePath+",False")
            sendFile(os.path.join(self._folder_path ,filePath),self._sock)


def sendFile(filePath, sock):
    with open(filePath, 'rb') as f:
        data = f.read(1024)
        while len(data) != 0:
            sendBytesMsg(sock, data)
            data = f.read(1024)

        sendMsg(sock, PROTOCOL_END_OF_FILE)
        f.close()