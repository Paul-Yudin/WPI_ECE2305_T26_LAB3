#Server

import socket

STOP_WORDS = ["quit", "bye", "leave"]

HOST = '127.0.0.1'
PORT = 2000
addr = (HOST, PORT)

print("Note: The communication is one way, you will only be able to send a message upon recieving a message\n")

s = socket.socket()
s.bind(addr)
s.listen(5)

con, adr = s.accept()
print(f"Accepted connection with {':'.join(map(str, adr))}\n")

con.send(b"Success...")

def send_msg():
    msg_str = input("Server Message: ")
    msg_bin = msg_str.encode('utf-8')
    con.send(msg_bin)
    
    if msg_str in STOP_WORDS:
        stop_chat()

def recv_msg():
    msg_bin = con.recv(2048)
    msg_str = msg_bin.decode('utf-8')
    print(f"Client Message: {msg_str}")
    
    if msg_str in STOP_WORDS:
        stop_chat()
    
def stop_chat():
    con.close()
    s.close()
    exit()

while True:
    recv_msg()
    send_msg()

