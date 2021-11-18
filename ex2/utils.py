import os
import sys

def delete(path):
    os.remove(path)

def moveRen(srcPath,dstPath):
    os.rename(srcPath,dstPath)

def changeFile(filePath,data):
    with open(filePath,'w') as f:
        f.write(data)
        f.close()

def createFile(filePath):
    os.makedirs(filePath,exist_ok=True)

def handleNewModify(command):
    cmd, path = command.split(' ',1)
    if (cmd == "created"):
        createFile(path)
    elif (cmd == "moved"):
        src,dst=path.split('\n',1)
        moveRen(src,dst)
    elif (cmd=="deleted"):
        delete(path)
    elif (cmd=="modified"):
        pass