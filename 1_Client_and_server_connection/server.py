import socket

HOST = '127.0.0.1'
PORT = 2000
addr = (HOST, PORT)


s = socket.socket()
s.bind(addr)

s.listen(5)
con, adr = s.accept()

data = con.recv(2048)

print(data)

con.close()
s.close()

print("Server Done")
