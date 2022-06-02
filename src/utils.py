import os
from watchdog.events import FileSystemEventHandler
from Crypto.Cipher import AES
import virusTotal
import threading
# protocol constant
PROTOCOL_ACK = "ACK"
PROTOCOL_END_OF_FILE ="DONE"
PROTOCOL_END_OF_MODIFICATION = "FINISH"
# protocol constant
NEW_CLIENT_MASSAGE = "new client"
CLOSE_CONNECTION = "close connection"
CIPHER_KEY=b'bQeThWmZq4t7w!z%C*F-JaNdRfUjXn2r' #Shared Key 32 bytes for 256-bit encryption
NONCE=b'dRgUkXp2s5v8y/B?E(G+KbPeShVmYq3t' #shared nonce key for validation. 

def encrypt(msg):
    CIPHER = AES.new(CIPHER_KEY, AES.MODE_EAX, NONCE) #AES encryption using EAX mode with predefined cipher key and nonce key for validation
    ciphertext, tag = CIPHER.encrypt_and_digest(msg)
    return ciphertext

def decrypt(msg):
    cipher = AES.new(CIPHER_KEY, AES.MODE_EAX,NONCE) #AES encryption using EAX mode -Encrypt/authenticate/translate
    plaintext = cipher.decrypt(msg) #decryption of cipher message passed from client A
    return plaintext

def sendMsg(sock,msg):
    messageToSend = encrypt(msg.encode())
    sock.send(messageToSend)
    r = sock.recv(8192)

def sendBytesMsg(sock,msg):
    messageToSend = encrypt(msg)
    sock.send(messageToSend)
    r = sock.recv(8192)

def getMsg(sock):
    msg = sock.recv(8192)
    msg = decrypt(msg).decode()
    sock.send(PROTOCOL_ACK.encode())
    return msg


class DirectoryObserver(FileSystemEventHandler):
    def __init__(self, modify_queue, filePath):
        self._modify_queue = modify_queue
        self._filePath = filePath

    def on_moved(self, event):
        '''if event.is_directory == True and len(os.listdir(event.dest_path))!=0:
            return'''
        createEvent = "created" + ',' + event.src_path[len(self._filePath) + 1 : ] + ','+str(event.is_directory)
        modifiedEvent = "modified" + ',' + event.src_path[len(self._filePath) + 1 : ] + ','+str(event.is_directory)

        created = False
        modified = False
        for index in range(len(self._modify_queue)):
            if createEvent == self._modify_queue[index]:
                created = True
                self._modify_queue[index] = self._modify_queue[index].replace(event.src_path[len(self._filePath) + 1 : ],
                                                                                event.dest_path[len(self._filePath) + 1 : ])
            elif modifiedEvent == self._modify_queue[index]:
                if modified == False and created == False:
                    self._modify_queue.insert(index,event.event_type + ',' + event.src_path[len(self._filePath) + 1 : ]
                                  + ',' + event.dest_path[len(self._filePath) + 1 : ]+','+str(event.is_directory))
                    self._modify_queue[index+1] = self._modify_queue[index+1].replace(event.src_path[len(self._filePath) + 1 : ],
                                                                                event.dest_path[len(self._filePath) + 1 : ])
                else:
                    self._modify_queue[index] = self._modify_queue[index].replace(event.src_path[len(self._filePath) + 1 : ],
                                                                                event.dest_path[len(self._filePath) + 1 : ])
                modified = True

            
        # saving the massage
        if created == False and modified == False:
            self._modify_queue.append(event.event_type + ',' + event.src_path[len(self._filePath) + 1 : ]
                                  + ',' + event.dest_path[len(self._filePath) + 1 : ]+','+str(event.is_directory))

    def on_modified(self, event):
        if (event.is_directory):
            return
        # saving the massage
        modifiedEvent = "modified" + ',' + event.src_path[len(self._filePath) + 1 : ] + ',' + "False"
        if modifiedEvent in self._modify_queue:
            return
        self._modify_queue.append(modifiedEvent)
        # self._modify_queue.append("modified" + ',' + event.src_path[len(self._filePath) + 1 : ]+',' + "False")

    def on_deleted(self, event):
        # saving the massage
        createEvent = "created" + ',' + event.src_path[len(self._filePath) + 1 : ] +','+str(event.is_directory)
        modifiedEvent = "modified" + ',' + event.src_path[len(self._filePath) + 1 : ] +','+str(event.is_directory)
        created = False
        if createEvent in self._modify_queue:
            self._modify_queue.remove(createEvent)
            created = True

        if modifiedEvent in self._modify_queue:
            self._modify_queue.remove(modifiedEvent)
        
        if created == False:
            self._modify_queue.insert(0,event.event_type + ',' + event.src_path[len(self._filePath) + 1 : ] +','+str(event.is_directory))

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
        self.lastPath = "randomPath"

    def set_sock(self, sock):
        self._sock = sock

    def delete(self, path):
        try:
        # cecking if it a folder
            if os.path.isdir(os.path.join(self._folder_path,path)):
                self.lastPath = path
                os.system(f'rmdir /q /s \"{os.path.join(self._folder_path,path)}\"')
            else:
                os.remove(os.path.join(self._folder_path,path))
        except:
            pass

    def moveRename(self, srcPath,dstPath):
        try:
            os.rename(os.path.join(self._folder_path,srcPath), os.path.join(self._folder_path,dstPath))
        except:
            pass

    def copy_file(self, filePath):
        with open(os.path.join(self._folder_path, filePath),'wb') as f:
            data = self._sock.recv(8192)
            data = decrypt(data)
            # getting the data from the socket
            while True:
                try:
                    # check if it the end of f
                    if data.decode() == PROTOCOL_END_OF_FILE:
                        break
                    self.writeSliceData(data,f)
                    data = self._sock.recv(8192)
                    data = decrypt(data)
                except:
                    self.writeSliceData(data,f)
                    data = self._sock.recv(8192)
                    data = decrypt(data)

            self._sock.send(PROTOCOL_ACK.encode())
        f.close()
        #t = threading.Thread(target=virusTotal.handleChange,args=(os.path.join(self._folder_path,filePath),))
        #t.start()
        # virusTotal.handleChange(os.path.join(self._folder_path,filePath))
    
    def writeSliceData(self,data,f):
        f.write(data)
        self._sock.send(PROTOCOL_ACK.encode())

    def createFile(self, filePath,isDir):
        if isDir == "False":
            self.copy_file(filePath)
        else:
            os.makedirs(os.path.join(self._folder_path,filePath), exist_ok=True)

    def handleNewModify(self, command):
        tempCmd = command
        try:
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
        except:
            while (virusTotal.FLAG_IN_USE['state']):
                continue
            self.handleNewModify(tempCmd)


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
        data = f.read(8192)
        while len(data) != 0:
            sendBytesMsg(sock, data)
            data = f.read(8192)

        sendMsg(sock, PROTOCOL_END_OF_FILE)
    f.close()
