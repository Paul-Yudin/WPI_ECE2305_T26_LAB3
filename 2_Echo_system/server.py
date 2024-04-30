import socket

HOST = '127.0.0.1'
PORT = 2000
addr = (HOST, PORT)

s = socket.socket()
print("Socket Created")

s.bind(addr)
print("Socket bind complete")

s.listen(5)
print("Socket is now listening")

con, adr = s.accept()
print(f"Accepted connection with {':'.join(map(str, adr))}\n")

con.send(b"Welcome to the server, please enter a message:")

def echo():
    msg_bin = con.recv(2048)
    msg_str = msg_bin.decode('utf-8')
    print(f"Client Message: {msg_str}")
    con.send(msg_bin)

while True:
    echo()
