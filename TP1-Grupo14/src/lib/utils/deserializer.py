
"""
Funciones asociadas al rearmado de archivos.
Util en el lado receptor de la red.
"""
from . import serializer as p_tools

# MISC
BIN_WRITE_MODE = "wb"
FIST_PACKET = 0


def _build_file(
        file_name: str,
        file_size: int,
        file_chunks: list[bytes]) -> bool:
    """
    [Uso privado] Crea el archivo en el directorio ____
    y lo escribe de forma binaria.
    :param file_name: Nombre del archivo a crear/escribir.
    :param file_size: Size en bytes del archivo a crear/escribir.
    :param file_chunks: Lista de chunks a escribir en el archivo.
    :return: Verdadero si el archivo se escribió correctamente.
    """
    total = 0
    with open(file_name, BIN_WRITE_MODE) as f:
        for chunk in file_chunks:
            written = f.write(chunk)
            if written != len(chunk):
                return False
        total = f.tell()
    return True if total == file_size else False


def deserialize(file_packets: list[bytes], path, file_name, file_size) -> bool:
    """
    Dado un conjunto de paquetes, genera el archivo correspondiente.
    :param file_packets: Lista de paquetes.
    :return: Verdadero en caso de archivo creado correctamente.
    """
    file_chunks = []
    for packet in file_packets:
        payload = p_tools.get_payload(packet)
        file_chunks.append(payload)
    return _build_file(f"{path}/{file_name}", file_size, file_chunks)
