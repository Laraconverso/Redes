import socket
from ..utils import serializer as p_tools
from ..utils.exceptions import ServerDisconnected
from ..utils.logger import get_logger

logger = get_logger("Client")

# Constantes
TIMEOUT = 0.5  # Tiempo de espera para retransmisión (en segundos)
MAX_RETRIES = 5  # Número máximo de retransmisiones
PACKET_SIZE = 1024


def stop_and_wait_send(sock, packets, server_address):
    """
    Implementación del protocolo Stop-and-Wait
    para enviar una lista de paquetes.
    """
    for packet in packets:
        retries = 0
        while retries < MAX_RETRIES:
            try:
                # Enviar paquete
                sock.sendto(packet, server_address)

                # Configurar timeout para esperar el ACK
                sock.settimeout(TIMEOUT)

                # Esperar ACK
                ack, _ = sock.recvfrom(PACKET_SIZE)
                if not ack:
                    raise ServerDisconnected("El servidor no respondió"
                                             " al paquete enviado.")
                ack_num = p_tools.get_ack_num(ack)

                # Verificar si el ACK es válido
                if ack_num == p_tools.get_seg_num(packet):
                    break  # Salir del bucle de retransmisión
            except socket.timeout:
                retries += 1
        else:
            logger.error("Máximos intentos de envio realizados.")
            return False  # Fallo en el envío
    return True  # Todos los paquetes enviados exitosamente


def stop_and_wait_receive(sock):
    """
    Implementación del protocolo Stop-and-Wait
    para recibir una lista de paquetes.
    """
    received_packets = []
    expected_seq_num = 1

    while True:
        try:
            # Configurar timeout para evitar bloqueos
            sock.settimeout(TIMEOUT)

            # Recibir paquete
            packet, server_address = sock.recvfrom(PACKET_SIZE)
            if not packet:
                raise ServerDisconnected("El servidor no envió más paquetes.")
            seq_num = p_tools.get_seg_num(packet)

            # Verificar si es el paquete esperado
            if seq_num == expected_seq_num:
                received_packets.append(packet)

                # Enviar ACK
                ack_packet = p_tools.PacketGenerator("SW")
                ack_packet.set_ack_number(seq_num)
                sock.sendto(ack_packet.create_packet(), server_address)

                # Incrementar el número de secuencia esperado
                expected_seq_num += 1

                # Verificar si es el último paquete (FIN flag)
                if p_tools.get_fin(packet):
                    break
            else:
                # Enviar ACK del último paquete correctamente recibido
                ack_packet = p_tools.PacketGenerator("SW")
                ack_packet.set_ack_number(expected_seq_num - 1)
                sock.sendto(ack_packet.create_packet(), server_address)
        except socket.timeout:
            break
    return received_packets
