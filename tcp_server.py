#TCP server coded by Anthony Wilkinson
#Cyber550 Assignment 2
#Used code references from http://pycryptodome.readthedocs.io/en/latest/src/examples.html
#Used code references from https://docs.python.org/3.3/library/socket.html#socket.socket.settimeout

import socket
import sys
from Crypto.Cipher import AES

SERVER_IP = "127.0.0.1" #Server IP using Loopback for testing
SERVER_PORT = 9000   #Server Port
CIPHER_KEY=b'bQeThWmZq4t7w!z%C*F-JaNdRfUjXn2r' #Shared Key 32 bytes for 256-bit encryption
TCP_BUFFER= 1024 #Buffer for receiving data
NONCE=b'dRgUkXp2s5v8y/B?E(G+KbPeShVmYq3t' #shared nonce key for validation. 
          
TCPserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #initialize TCP stream
TCPserver.bind((SERVER_IP, SERVER_PORT)) #Bind TCP Stream connectoin
TCPserver.listen(2) #Listen for two TCP connections

conn, addr = TCPserver.accept() #connection 1 which is clientA
print('Client A Connected From:', addr)
print()
conn1, addr2 = TCPserver.accept() #connection 2 which is clientB
print('Client B Connected From:', addr)
print()


while True:
	print("Receiving Secret Encrypted Message...")
	print()
	data=conn.recv(TCP_BUFFER) #ClientA sending cipher message
	ciphertext=data
	print("Received Encrypted Message:",ciphertext)
	print()
	cipher = AES.new(CIPHER_KEY, AES.MODE_EAX,NONCE) #AES encryption using EAX mode -Encrypt/authenticate/translate
	plaintext = cipher.decrypt(ciphertext) #decryption of cipher message passed from client A
	print("Decrypting using Shared Key...")
	#print(plaintext)
	#print("data:", data)
	conn1.sendall(plaintext)
	print()
	print("Decrypted Message Sent to ClientB!")
	break

print("Goodbye!")
TCPserver.close()