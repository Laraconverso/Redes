from socket import *

#TCP orientado a la conexion, comunicacion uno a uno
#entonces se conecta desde ambos lados
#Una vez que esta la conexion hecha sabemos univocamente con quien nos estamos conectando.
BUFF_SIZE = 1024

host = "localhost" #IP adress or domain name #usamos localhost para el ejemplo
port = 12000
serv_addr = (host, port)

client_socket = socket(AF_INET, SOCK_STREAM) #IPv4 network, TCP socket
client_socket.connect(host, port)

msg = "small is beautiful"
client_socket.send()
