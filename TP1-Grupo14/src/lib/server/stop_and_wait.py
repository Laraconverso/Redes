from ..utils.exceptions import ServerDisconnected
from ..utils import serializer
from ..utils.logger import get_logger
from queue import Empty

logger = get_logger("Server")

TIMEOUT = 0.5
MAX_RETRIES = 5


def sv_sw_receive(client_socket, queue, client_addr):
    received_packets = []
    expected_seg_num = 1
    packet_generator = serializer.PacketGenerator("SW")
    while True:
        try:
            packet = queue.get(timeout=TIMEOUT)
        except Empty:
            raise ServerDisconnected("El servidor se ha desconectado")

        seg_num = serializer.get_seg_num(packet)

        if seg_num != expected_seg_num:
            packet_generator.set_ack_number(expected_seg_num - 1)
            packet_generator.set_ack()
            last_ack = packet_generator.create_packet()
            client_socket.sendto(last_ack, client_addr)
            continue
        received_packets.append(packet)

        packet_generator.set_ack_number(seg_num)
        packet_generator.set_ack()
        if serializer.get_fin(packet):
            packet_generator.set_fin()
            client_socket.sendto(packet_generator.create_packet(), client_addr)
            break
        client_socket.sendto(packet_generator.create_packet(), client_addr)
        expected_seg_num += 1

    return received_packets


def sv_sw_send(packets, server_socket, queue, client_addr):
    for packet in packets:
        retries = 0
        while retries < MAX_RETRIES:
            try:
                seg_num = serializer.get_seg_num(packet)

                server_socket.sendto(packet, client_addr)

                ack = queue.get(timeout=TIMEOUT)
                ack_num = serializer.get_ack_num(ack)
                if ack_num == seg_num:
                    break
            except Empty:
                retries += 1
        if retries >= MAX_RETRIES:
            logger.error("Máximos intentos realizados")
            raise ServerDisconnected(
                "El servidor no ha respondido los %d envios", MAX_RETRIES
            )
    return True
