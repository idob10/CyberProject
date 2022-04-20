import socket
import sys
import re
import getpass
from Crypto.Cipher import AES

SERVER_IP = "127.0.0.1"    #server IP of 127.0.0.1 LOOPBACK used for testing
SERVER_PORT = 9000         # server Port
CIPHER_KEY=b'bQeThWmZq4t7w!z%C*F-JaNdRfUjXn2r' #Shared Encryption/decryption Key
NONCE=b'dRgUkXp2s5v8y/B?E(G+KbPeShVmYq3t' #shared NONCE key for validity

clientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP socket creation
clientA.connect((SERVER_IP, SERVER_PORT)) #TCP connection


while True:
	Secret_Message_Input= getpass.getpass(prompt='Enter Secret Message.. : ' )
	print("Message will Encrypt with AES")
	print()
	raw_message=Secret_Message_Input.encode() #Encode message to bytes
	CIPHER = AES.new(CIPHER_KEY, AES.MODE_EAX, NONCE) #AES encryption using EAX mode with predefined cipher key and nonce key for validation
	ciphertext, tag = CIPHER.encrypt_and_digest(raw_message)
	print("Sending Encrypted Message:",ciphertext)
	clientA.send(ciphertext) #send ciphertext of raw message
	clientA.close()#close socket
	print()
	break

clientA.close()
print('Message Sent..Goodbye')
print()