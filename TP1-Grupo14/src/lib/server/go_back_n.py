import time
from ..utils.exceptions import ServerDisconnected
from ..utils import serializer as p_tools
from queue import Empty
from ..utils.logger import get_logger

logger = get_logger("Server")

SIZE_PACKET = 1024
TIMEOUT_QUEUE = 10
TIMEOUT_LOST_PK = 2
WINDOW_SIZE = 10


def sv_gbn_send(file_packets, client_socket, queue, addr):
    base = 0
    next_seqnum = 0
    total_packets = len(file_packets)
    timer_start = None  # Temporizador solo para el paquete 'base'
    retries = [0 for _ in file_packets]  # Lista para contar reintentos
    SENDING_LIMIT = 3  # Límite de reintentos por paquete

    while base < total_packets:
        # Se quiere enviar un paquete
        if next_seqnum < base + WINDOW_SIZE and next_seqnum < total_packets:
            if retries[next_seqnum] > SENDING_LIMIT:
                raise ServerDisconnected(
                    f"Client hasn't acknowledged packet {next_seqnum + 1}"
                    f" after {SENDING_LIMIT} retries.")

            # Enviar paquete
            client_socket.sendto(file_packets[next_seqnum], addr)
            retries[next_seqnum] += 1  # Incrementar contador de reintentos
            if base == next_seqnum:
                timer_start = time.time()  # Iniciar temporizador
            next_seqnum += 1

        # Llega un ACK
        try:
            ack_packet = queue.get(timeout=TIMEOUT_QUEUE)
            if p_tools.get_ack(ack_packet):
                ack_seq = p_tools.get_seg_num(ack_packet)
                # Como el ack_seq empieza en 1, y file_packets está en base 0:
                ack_index = ack_seq - 1

                if ack_index >= base:
                    base = ack_index + 1

                    if base == next_seqnum:
                        timer_start = None  # Ventana vacía, detener timer
                    else:
                        timer_start = time.time()  # Reiniciar timer
        except Empty:
            pass  # No llegó ningún ACK en este ciclo

        # Timeout del paquete base
        if timer_start and (time.time() - timer_start >= TIMEOUT_LOST_PK):
            for i in range(base, next_seqnum):
                if retries[i] > SENDING_LIMIT:
                    raise ServerDisconnected(
                        f"Client hasn't acknowledged packet {i + 1} "
                        f"after {SENDING_LIMIT} retries."
                        )
                client_socket.sendto(file_packets[i], addr)
                retries[i] += 1  # Incrementar contador de reintentos
            timer_start = time.time()  # Reiniciar timer


def sv_gbn_receive(client_socket, queue, addr):
    expected_seq = 1
    received_packets = []
    last_ack = 0

    while True:
        try:
            # Obtener paquete de este cliente
            packet = queue.get(timeout=TIMEOUT_QUEUE)
        except Empty:
            raise ServerDisconnected("Client has disconnected")

        seq = p_tools.get_seg_num(packet)
        is_end = p_tools.get_fin(packet)

        ack = p_tools.PacketGenerator("GBN")
        ack.set_ack()

        if seq != expected_seq:
            ack.set_ack_number(last_ack)
            client_socket.sendto(ack.create_packet(), addr)
            continue

        received_packets.append(packet)

        # ACK packet actual
        ack.set_ack()
        ack.set_ack_number(seq)
        expected_seq += 1

        if is_end:
            ack.set_fin()
            ack_packet = ack.create_packet()
            client_socket.sendto(ack_packet, addr)
            break

        ack_packet = ack.create_packet()
        last_ack = p_tools.get_ack_num(ack_packet)
        client_socket.sendto(ack_packet, addr)

    return received_packets
