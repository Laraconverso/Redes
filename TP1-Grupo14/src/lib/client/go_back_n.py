"""
Funciones relacionadas con el envío y descarga de paquetes con
modo de recuperación de errores GO BACK N.
"""
from ..utils import serializer as p_tools
from ..utils.exceptions import ServerDisconnected
from ..utils.logger import get_logger
import socket
import time

# LONGITUDES EN BYTES
PACKET_SIZE = 1024

# TIEMPO EN MS
MS_LENGTH = 1000
ACK_TIME_LIMIT = 2000

# TIEMPO EN S
AUX_TIMEOUT = 0.05
TIMEOUT = 0.1
TIMEOUT_LOST_PK = 2

# GO BACK N PACKET SETTINGS
WINDOW_SIZE = 10
SENDING_LIMIT = 2
PACKET, TIME_SENT, TIMES_SENT = 0, 1, 2
INITIAL_TIME_SENT, INITIAL_TIMES_SENT = None, 0

logger = get_logger("Client")


def cl_gnb_receive(src_socket: socket) -> list[bytes]:
    """
    Función que maneja la llegada de datos **desde un servidor que
    implementa el protocolo de recuperación de errores GO-BACK-N**.
    La función tiene la responsabilidad de:

    - Guardar en orden los paquetes recibidos por el socket.
    - Enviar acknowledges al servidor cuando se recibe el paquete esperado.
    :param src_socket: El socket desde donde se recibe data.
    :param address: La dirección del servidor que envía los datos.
    :return: Lsita de todos los paquetes recibidos en orden.
    :raises: ServerDisconnected: Si el servidor se desconectó.
    """
    recv_buffer = []
    packet = p_tools.PacketGenerator("GBN")
    exp_seg_num = 1  # 1. DWL, 2. ACK DWL, 3. Primer paquete de datos.
    while True:
        src_socket.settimeout(TIMEOUT)
        try:
            data, address = src_socket.recvfrom(PACKET_SIZE)

        except socket.timeout:
            raise ServerDisconnected("Servidor desconectado "
                                     "durante la transferencia")
        cur_seg_num = p_tools.get_seg_num(data)
        if not data:
            break
        if exp_seg_num != cur_seg_num:
            packet.set_ack()
            packet.set_ack_number(exp_seg_num-1)
            src_socket.sendto(data, address)
            continue
        recv_buffer.append(data)

        if p_tools.get_fin(data):

            packet.set_fin()
            packet.set_ack_number(cur_seg_num)
            packet.set_ack()
            fin_req = packet.create_packet(data)
            src_socket.sendto(fin_req, address)
            src_socket.close()
            break

        packet.set_ack()
        packet.set_ack_number(cur_seg_num)
        ack_res = packet.create_packet()
        src_socket.sendto(ack_res, address)
        exp_seg_num += 1

    return recv_buffer


def cl_gbn_send(client_socket, packets, address):
    roof, floor = 0, 0
    timers = [0.0 for _ in packets]
    retries = [0 for _ in packets]
    exp_ack_num = 1
    client_socket.setblocking(False)

    cantidad = 0
    while len(packets) > roof >= floor:
        while roof - floor < WINDOW_SIZE and roof < len(packets):
            if retries[roof] > SENDING_LIMIT:
                raise ServerDisconnected(f"server hasn't sent any "
                                         f"ack for packet {exp_ack_num}")
            client_socket.sendto(packets[roof], address)
            cantidad += 1
            timers[roof] = time.monotonic()
            retries[roof] += 1
            roof += 1
            continue

        if time.monotonic() - timers[floor] > TIMEOUT_LOST_PK:
            roof = floor
            continue

        try:
            ack = client_socket.recv(PACKET_SIZE)
        except BlockingIOError:
            # Socket estaba vacío -> espero, sigo...
            time.sleep(AUX_TIMEOUT)
            continue

        if exp_ack_num != p_tools.get_ack_num(ack):
            # Si ack recibido es dis -> ignoro
            continue
        floor += 1
        exp_ack_num += 1
