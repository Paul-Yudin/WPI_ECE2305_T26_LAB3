#Client

import socket

STOP_WORDS = ["quit", "bye", "leave"]

HOST = '127.0.0.1'
PORT = 2000
addr = (HOST, PORT)

print("Note: The communication is one way, you will only be able to send a message upon recieving a message\n")

r = socket.socket()

r.connect(addr)
print("Connecting...\n")

def send_msg():
    msg_str = input("Client Message: ")
    msg_bin = msg_str.encode('utf-8')
    r.send(msg_bin)
    
    if msg_str in STOP_WORDS:
        stop_chat()

def recv_msg():
    msg_bin = r.recv(2048)
    msg_str = msg_bin.decode('utf-8')
    print(f"Server Message: {msg_str}")
    
    if msg_str in STOP_WORDS:
        stop_chat()

def stop_chat():
    r.close()
    exit()

while True:
    recv_msg()
    send_msg()
