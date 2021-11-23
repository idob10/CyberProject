import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 12345))
s.send('new client'.encode())
data = s.recv(100)
#s.send('created,../src/N1NI76B4SOsG1NP7E16KP5FkvoZ0QP7M07EZXfpXGYloFZV78UTiutGaJLPlvKxXJUu9Jz6PvomSoXbMsFsC4eaOWSbIT4OaXCUJaLMwxzS6KvXigOb5lfBGPZEH1yhZ/New folder,True'.encode())
print("Server sent: ", data)
s.close()