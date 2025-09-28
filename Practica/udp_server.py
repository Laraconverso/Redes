from socket import *

BUFF_SIZE = 1024

host = "127.0.0.1" #IP adress or domain name #usamos localhost para el ejemplo
port = 12000
serv_addr = (host, port)

serv_socket = socket(AF_INET, SOCK_DGRAM) 
serv_socket.bind(serv_addr) #vicnulamos ese puerto a ese socket, ya nadie puede utilizarlo

print("The server is ready")

while True: 
    payload, client_addr = serv_socket.recvfrom(BUFF_SIZE)
    msg=payload.decode().upper()
    serv_socket.sendto(msg.encode(), client_addr)