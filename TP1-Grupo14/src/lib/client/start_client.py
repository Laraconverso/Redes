import socket
import os
from ..utils import serializer as p_tools
from ..utils.deserializer import deserialize
from .stop_and_wait import stop_and_wait_send, stop_and_wait_receive
from ..utils.exceptions import ServerDisconnected, WrongDataReceived
from ..utils.exceptions import FullStorageError, NoServerEnoughMemory
from ..utils.logger import get_logger
from .go_back_n import cl_gnb_receive, cl_gbn_send

PACKET_SIZE = 1024

logger = get_logger("Client")


def start_client(command, host, port, file_path, file_name, protocol):
    server_address = (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    generator = p_tools.PacketGenerator(protocol)

    try:
        if command == "upload":
            # Primer paquete: UPLOAD + tamaño del archivo
            logger.info(file_path)
            for root, dirs, files in os.walk(file_path):
                if file_name in files:
                    break
            if file_name in files:
                file_size = os.path.getsize(file_path)

                generator.set_upl()
                prop = f"{file_name}\r\n{file_size}"
                packet = generator.create_packet(prop.encode())
                sock.sendto(packet, server_address)

                # Respuesta del servidor
                response, _ = sock.recvfrom(PACKET_SIZE)
                if not response:
                    raise ServerDisconnected("El servidor no respondió "
                                             "durante el handshake.")
                if p_tools.get_ack(response) and p_tools.get_upl(response):
                    logger.info("El servidor aceptó el archivo. "
                                "Iniciando transferencia...")
                elif p_tools.get_upl(response):
                    raise NoServerEnoughMemory("El servidor no tiene el"
                                               "espacio necesario")
                else:
                    raise WrongDataReceived("Respuesta inesperada del servidor"
                                            " durante el handshake.")

                # Serializar y enviar paquetes
                packets = p_tools.serialize(
                    f"{file_path}/{file_name}", protocol)
                logger.debug("Paquetes a enviar %d", len(packets))
                if protocol == "sw":
                    stop_and_wait_send(sock, packets, server_address)
                elif protocol == "gbn":
                    cl_gbn_send(sock, packets, server_address)
            else:
                logger.error("Archivo no está presente en el sistema,"
                             " cerrando sesión...")

        elif command == "download":
            # Primer paquete: DOWNLOAD + nombre del archivo
            generator.set_dwl()
            packet = generator.create_packet(file_name.encode())
            sock.sendto(packet, server_address)

            # Respuesta del servidor
            response, _ = sock.recvfrom(PACKET_SIZE)
            if not response:
                raise ServerDisconnected("El servidor no respondió"
                                         " durante el handshake.")

            if p_tools.get_ack(response) and p_tools.get_dwl(response):
                file_size = int.from_bytes(
                    p_tools.get_payload(response), byteorder="big")
                logger.info(f"El servidor confirmó el archivo."
                            f" Tamaño: {file_size} bytes.")
                # Verificar espacio en disco
                if file_size > (
                    os.statvfs("/").f_bavail * os.statvfs("/").f_frsize
                ):
                    generator.set_dwl()
                    sock.sendto(generator.create_packet(), server_address)
                    raise FullStorageError("No hay suficiente"
                                           " espacio en memoria")
                else:
                    generator.set_dwl()
                    generator.set_ack()
                    sock.sendto(generator.create_packet(), server_address)
            elif p_tools.get_dwl(response):
                raise FileNotFoundError("Servidor no posee el archivo")
            else:
                raise WrongDataReceived("Respuesta inesperada del servidor"
                                        " durante el handshake.")

            # Recibir y deserializar paquetes
            packets = []
            if protocol == "sw":
                packets = stop_and_wait_receive(sock)
            elif protocol == "gbn":
                packets = cl_gnb_receive(sock)
            deserialize(packets, file_path, file_name, file_size)
        else:
            raise ValueError("Comando no reconocido. "
                             "Use 'upload' o 'download'.")

    except (ServerDisconnected, WrongDataReceived, FileNotFoundError,
            FullStorageError, NoServerEnoughMemory) as e:
        logger.error(f"Error: {e}")
    finally:
        sock.close()
