import socket

HOST = '127.0.0.1'
PORT = 2000
addr = (HOST, PORT)

r = socket.socket()
r.connect(addr)

r.send(b"Hello World")

r.close()

print("Client Done")
