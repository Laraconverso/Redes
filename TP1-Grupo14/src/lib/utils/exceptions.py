"""
Excepciones utilizadas.
"""


class ServerDisconnected(Exception):
    """
    Error, el servidor se desconectó durante la carga/descarga de datos.
    """
    pass


class WrongDataReceived(Exception):
    """
    Error en donde el socket no recibió un ACK.
    """
    pass


class NoServerEnoughMemory(Exception):
    """
    Error el servidor no tiene espacio suficiente.
    """
    pass


class FullStorageError(Exception):
    """
    Error no hay suficiente espacio en disco para guardar el archivo.
    """
    pass


class FileNotFound(Exception):
    """
    Error archivo no encontrado.
    """
    pass
