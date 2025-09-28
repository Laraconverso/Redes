import os
import socket
import threading


from .server.go_back_n import sv_gbn_send, sv_gbn_receive
from .server.stop_and_wait import sv_sw_send, sv_sw_receive
from .utils import deserializer
from .utils import serializer
from .utils.serializer import PacketGenerator
from .utils.exceptions import FileNotFound
from queue import Queue
from .utils.logger import get_logger

PACKET_SIZE = 1024*2

MAX_STORAGE, MAX_LIMIT = 100000000000, 10000000

client_pool = {}

logger = get_logger("Server")


def client_thread(address, queue, socket, sv_protocol, storage):

    packet_generator = PacketGenerator(sv_protocol)
    dato = queue.get()
    if serializer.get_upl(dato):  # Al sv le llego solicitud de subida
        # -> CLIENTE QUIERE SUBIR/MANDARNOS ALGO
        file_name, file_size = serializer.get_file_data(dato)
        if file_size > MAX_LIMIT or file_size > MAX_STORAGE:
            packet_generator.set_upl()
            socket.sendto(packet_generator.create_packet(), address)
            return

        packet_generator.set_upl()
        packet_generator.set_ack()
        socket.sendto(packet_generator.create_packet(), address)

        res_packets = []
        match serializer.get_protocol(dato):
            case 1:  # SW
                res_packets = sv_sw_receive(socket, queue, address)
            case 2:  # GO BACK
                res_packets = sv_gbn_receive(socket, queue, address)
            case _:
                logger.error("Error in protocol")

        deserializer.deserialize(res_packets, storage, file_name, file_size)
    elif serializer.get_dwl(dato):
        file_name, _ = serializer.get_file_data(dato)
        for root, dirs, files in os.walk(storage):
            if file_name in files:
                break

        if file_name in files:

            file_size = os.path.getsize(storage + "/" + file_name)
            packet_generator.set_ack()
            packet_generator.set_dwl()
            size_confirmation_packet = packet_generator.create_packet(
                file_size.to_bytes(4, byteorder="big"))
            socket.sendto(size_confirmation_packet, address)

            res_packet = queue.get()  # Debería llegar el READY
            if (
                serializer.get_dwl(res_packet)
                and serializer.get_ack(res_packet)
            ):
                file_packets = serializer.serialize(
                    f"{storage}/{file_name}", sv_protocol)
                match serializer.get_protocol(dato):
                    case 1:  # SW
                        sv_sw_send(file_packets, socket, queue, address)
                    case 2:  # GO BACK N
                        sv_gbn_send(file_packets, socket, queue, address)
                    case _:
                        logger.error("Error, protocolos no matchean")

            if (
                serializer.get_dwl(res_packet)
                and not serializer.get_ack(res_packet)
            ):
                socket.close()
        else:
            logger.error("File not found")
            return


def start_connections_manager(host, port, protocol, path):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # Socket UDP
    server.bind((host, port))

    while True:
        try:
            package, addr = server.recvfrom(PACKET_SIZE)

            # Validacion
            modo = serializer.get_protocol(package)

            if modo != serializer.get_protocol_mode(protocol):
                # No match en protocolos -> ignoro
                packet_generator = PacketGenerator("ERR")
                server.sendto(packet_generator.create_packet(), addr)
                continue

            # (ip, port)
            if addr not in client_pool:
                queue = Queue()
                queue.put(package)
                thread = threading.Thread(
                    target=client_thread,
                    args=(addr, queue, server, protocol, path), daemon=True)
                client_pool[addr] = queue
                thread.start()
            else:
                client_pool[addr].put(package)
        except KeyboardInterrupt:
            logger.info("Cerrando servidor...")
            break
