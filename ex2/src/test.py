from utils import *
import socket

d = DirectoryApplayer("../",socket.socket())
print(d.downloadDir("../"))

