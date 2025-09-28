#udp_client.py
# ejemplo udp, se envia un mensaje y lo imprime por consola.
from socket import *

BUFF_SIZE = 1024

host = "localhost"  #IP adress or domain name #usamos localhost para el ejemplo
port = 12000
serv_addr = (host, port)

client_socket = socket(AF_INET, SOCK_DGRAM) #Ipv4 network, UDP socket
#suele consultar que so los parametros en los examenes. 
msg = "less is more"

client_socket.sendto(msg.encode(), serv_addr) 
#pasamos el mensaje a bytes y le psamos la direccion de red

response, sender_addr = client_socket.recvfrom(BUFF_SIZE)
#funcion bloqueante hasta que no recibo nada se bloquea el hilo de ejecucion 
#UDP (no orientado a la conexion) pensamos que enviamos y recibimos un paquete. 
#la sender_address sirve para validar venga del host que esperás y no de cualquier otro


print(response.decode())
#imprimo por pantalla con decode paso de btes a string

client_socket.close()
