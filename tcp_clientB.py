import socket

SERVER_IP = "127.0.0.1"    # The remote host
SERVER_PORT = 9000             # The same port as used by the server

print("Waiting for Secret Message....")
clientB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientB.connect((SERVER_IP, SERVER_PORT))
data = clientB.recv(1024)
secret_message=data.decode()
clientB.close()
print('Secret Message Recieved:', repr(secret_message))
print()
print("Goodbye..")
print()