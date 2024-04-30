#Client

import socket

HOST = '127.0.0.1'
PORT = 2000
addr = (HOST, PORT)

r = socket.socket()
print("Socket Created")

r.connect(addr)
print("Connecting...\n")

def send_msg():
    msg_str = input("Client Message: ")
    msg_bin = msg_str.encode('utf-8')
    r.send(msg_bin)

def recv_msg():
    msg_bin = r.recv(2048)
    msg_str = msg_bin.decode('utf-8')
    print(f"Server Message: {msg_str}")

while True:
    recv_msg()
    send_msg()
