from socket import *

BUFF_SIZE = 1024

port = 7070

serv_socket = socket(AF, SOCK_STREAM)
serv_socket.bind(("", port))
serv_socket.listen(1)
print("Server is listenint on port [{}]".format(port))

while True:
    conn_socket, addr = serv_socket.accept() #llamada bloqueante
    msg = conn_socket.recv(BUFF_SIZE).decode()
    res = msg.upper()
    conn_socket.send(res.enconde())
    conn_socket.close()



