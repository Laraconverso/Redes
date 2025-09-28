"""
Funciones, clase y métodos relacionados con la configuración
de la estructura del paquete.
::
    +--------------------- Paquete ---------------------+
    | Número de segmento (32 bits)                      |
    |---------------------------------------------------|
    | Número de ACK (32 bits)                           |
    |---------------------------------------------------|
    | U | D | A | F |                                   |
    | P | W | C | I |   Protocolo de error (4 bits)     |
    | L | N | K | N |                                   |
    |---------------------------------------------------|
    | Longitud del payload (16 bits)                    |
    |---------------------------------------------------|
    | Payload (hasta 1013 bytes)                        |
    +---------------------------------------------------+
    MMU: 1024 bytes
"""

# LONGITUDES E ÍNDICES EN BYTES
LEN_SEG_NUM, LEN_ACK_NUM, LEN_FLAGS, LEN_PAYLOAD_LEN = 4, 4, 1, 2
START_ACK_NUM, START_P_LEN, START_P_INDEX = 4, 9, 11
PAYLOAD_SIZE, PACKET_SIZE = 1013, 1024

# LONGITUDES E ÍNDICES EN BITS
POS_BIT_PACKET_UPL, POS_BIT_PACKET_DWL = 64, 65
POS_BIT_PACKET_ACK, POS_BIT_PACKET_FIN = 66, 67
POS_UPL, POS_DWL, POS_ACK, POS_FIN = 7, 6, 5, 4  # Posiciones dentro del byte

# FLAGS INFO
INITIAL_FLAG_STATE, INITIAL_NUM_STATE = 0, 0
ON, OFF = 1, 0
UPL, DWL, ACK, FIN, PROTOCOL = range(5)
PROTOCOL_MASK = 0b00001111

# CÓDIGOS DE PROTOCOLOS DE RECUPERACIÓN DE ERRORES
STOP_AND_WAIT_CODE, GO_BACK_N_CODE, ERROR_CODE = 1, 2, 0

# MISC
LAST_PAYLOAD = -1
INFO_SEPARATOR = "\r\n"
BIN_READ_MODE = "rb"


def _get_err_recv_code(mode: str) -> int:
    """
    [Uso privado] Dado un protocolo de recuperación de errores pasado por
    parámetro, devuelvo el código asociado para usarse en los headers de
    los paquetes.
    :param mode: El protocolo de recuperación de error.
    :return: El código en cuestión.
    :raises Exception: Si el modo elegido no existe.
    """
    match mode.upper():
        case "SW":
            return STOP_AND_WAIT_CODE
        case "GBN":
            return GO_BACK_N_CODE
        case "ERR":
            return ERROR_CODE
        case _:
            raise Exception("Wrong error recovery mode")


def get_seg_num(packet: bytes) -> int:
    """
    Permite obtener el número de segmento asociado a un paquete.
    :param packet: Paquete a analizar.
    :return: Valor del número de segmento.
    """
    return int.from_bytes(packet[0: LEN_SEG_NUM], byteorder="big")


def get_ack_num(packet: bytes) -> int:
    """
    Permite obtener el número de acknowledge asociado a un paquete.
    :param packet: Paquete a analizar.
    :return: Valor del número de acknowledge.
    """
    return int.from_bytes(
        packet[START_ACK_NUM: START_ACK_NUM + LEN_ACK_NUM],
        byteorder="big")


def _get_bit_value(data: bytes, index: int) -> int:
    """
    [Uso privado] Permite obtener el valor del bit en una posición
    específica del byte.
    :param data: Byte a analizar.
    :param index: Posición del bit a buscar.
    :return: Valor del bit (0/1).
    """
    byte_index = index // 8
    bit_position = 7 - (index % 8)
    return (data[byte_index] >> bit_position) & 1


def get_upl(packet: bytes) -> int:
    """
    Devuelve el estado del flag UPLOAD.
    :param packet: Paquete a analizar.
    :return: Estado del flag UPLOAD.
    """
    return _get_bit_value(packet, POS_BIT_PACKET_UPL)


def get_dwl(packet: bytes) -> int:
    """
    Devuelve el estado del flag UPLOAD.
    :param packet: Paquete a analizar.
    :return: Estado del flag UPLOAD.
    """
    return _get_bit_value(packet, POS_BIT_PACKET_DWL)


def get_ack(packet: bytes) -> int:
    """
    Devuelve el estado del flag ACKNOWLEDGE.
    :param packet: Paquete a analizar.
    :return: Estado del flag ACKNOWLEDGE.
    """
    return _get_bit_value(packet, POS_BIT_PACKET_ACK)


def get_fin(packet: bytes) -> int:
    """
    Devuelve el estado del flag FIN.
    :param packet: Paquete a analizar.
    :return: Estado del flag FIN.
    """
    return _get_bit_value(packet, POS_BIT_PACKET_FIN)


def get_protocol(packet: bytes) -> int:
    byte8 = packet[8]
    second_nibble = byte8 & 0x0F
    return second_nibble


def get_protocol_mode(mode: str) -> int:
    return _get_err_recv_code(mode)


def get_payload_len(packet: bytes) -> int:
    """
    Devuelve la longitud en bytes del payload.
    :param packet: Paquete a analizar.
    :return: Longitud del payload.
    """
    return int.from_bytes(
        packet[START_P_LEN:START_P_LEN+LEN_PAYLOAD_LEN],
        byteorder="big")


def get_payload(packet: bytes) -> bytes:
    """
    Devuelve el payload asociado al packet.
    :param packet: Paquete a analizar.
    :return: Información contenida en el payload.
    """
    return packet[START_P_INDEX:]


def get_file_data(packet: bytes) -> tuple[str, int]:
    """
    Útil para los paquetes que mueven información sobre el archivo.

    NOTA: Durante el envío de información del archivo, se agrega la
    data como payload con la siguiente sintaxís, ``file_name\\r\\nfile_size``.

    :param packet: Paquete a analizar.
    :return: Nombre del archivo, tamaño en bytes.
    """
    payload = packet[11:].decode("utf-8")
    res = payload.split(INFO_SEPARATOR)
    if len(res) > 1:
        name, size = res
    else:
        name = res[0]
        size = -1
    if not size:  # Caso flag dwl
        size = '-1'
    return name, int(size)


class PacketGenerator:
    """
    Clase encargada del manejo y creación de los paquetes a enviar
    a través de los sockets. Permite al usuario:

    - Delegar el manejo de número de secuencias.
    - Setear flags a medida.
    - Setear número de acknowledgement,
    - Crear el paquete en bytes listo para enviar por sockets.

    :raises Exception: Si el modo de recuperación de errores no existe.
    """

    def __init__(self, error_rec_mode: str, initial_seg_num=1):
        self.seg_num = initial_seg_num
        self.ack_num = 0
        self.flags = []
        self.set_initial_state(_get_err_recv_code(error_rec_mode))

    def set_initial_state(self, code: int):
        """
        Setea (y reinicia, en el caso) el comportamiento original
        de la instancia generadora.
        :param code: El protocolo a usar por el generador.
        """
        self.ack_num = INITIAL_NUM_STATE
        self.flags = [
            INITIAL_FLAG_STATE,
            INITIAL_FLAG_STATE,
            INITIAL_FLAG_STATE,
            INITIAL_FLAG_STATE,
            code
        ]

    def set_ack_number(self, number: int):
        """
        Setea el número de acknowledgement del próximo paquete a generar.
        :param number: Número de paquete a reconocer.
        """
        self.ack_num = number

    def set_upl(self):
        """
        Setea el valor del flag UPL del próximo paquete a generar.
        """
        self.flags[UPL] = ON

    def set_dwl(self):
        """
        Setea el valor del flag DWL del próximo paquete a generar.
        """
        self.flags[DWL] = ON

    def set_ack(self):
        """
        Setea el valor del flag ACK del próximo paquete a generar.
        """
        self.flags[ACK] = ON

    def set_fin(self):
        """
        Setea el valor del flag FIN del próximo paquete a generar.
        """
        self.flags[FIN] = ON

    def create_packet(self, payload=b'') -> bytes:
        """
        Método de clase para generar paquetes a partir de la información
        presente en el generador. Cada paquete contiene en los bytes:

        - 0:3, Número de segmento
        - 4:7,
        - 8, Flags (1er bit, UPL; 2do bit, DWL; 3er bit,
          ACK; 4to bit, FIN; 5:8 bits, Protocolo)
        - 9:11, Longitud del payload (en bytes también)
        - 11+, Payload.

        Una vez creado el paquete, los valores internos se resetean a
        un estado inicial, se aumenta el número de segmento y la instancia
        se puede volver a reutilizar para crear más paquetes.

        :param payload: Información a transmitir mediante el paquete.
        :return: Paquete codificado.
        """
        header_seg_num = self.seg_num.to_bytes(LEN_SEG_NUM, byteorder="big")
        header_ack_num = self.ack_num.to_bytes(LEN_ACK_NUM, byteorder="big")

        header_flags = (
                (self.flags[UPL] << POS_UPL) |
                (self.flags[DWL] << POS_DWL) |
                (self.flags[ACK] << POS_ACK) |
                (self.flags[FIN] << POS_FIN) |
                (self.flags[PROTOCOL] & PROTOCOL_MASK)
        ).to_bytes(LEN_FLAGS, byteorder="big")

        len_file_bits = len(payload).to_bytes(LEN_PAYLOAD_LEN, byteorder="big")
        header = (header_seg_num +
                  header_ack_num +
                  header_flags +
                  len_file_bits +
                  payload)

        self.seg_num += 1

        self.set_initial_state(self.flags[PROTOCOL])
        return header


def _get_file_data(file_path: str) -> tuple[int, list[bytes]]:
    """
    [Uso privado] Realiza la lectura del archivo obteniendo información,
    obteniendo:

    - Tamaño en bytes
    - Arreglo de byte chunks del archivo, siendo cada chunk de 1013 bytes.

    :param file_path: Directorio del archivo a leer.
    :return: Tamaño del archivo, arreglo de chunks.
    """
    data = []
    with open(file_path, BIN_READ_MODE) as f:
        while True:
            load = f.read(PAYLOAD_SIZE)
            if not load:
                break
            data.append(load)
        size = f.tell()
    return size, data


def _add_last_packet(
        generator: PacketGenerator,
        data: list[bytes],
        packets: list[bytes]):
    """
    [Uso privado] Agrega el último paquete a la lista asegurando la
    presencia del flag FIN.
    :param generator: Generador de paquetes, para no perder el
    orden de secuencia.
    :param data: Lista de chunks del archivo.
    :param packets: Lista de paquetes a usar.
    """
    generator.set_fin()
    packets.append(generator.create_packet(data[LAST_PAYLOAD]))


def serialize(file_path: str, mode: str) -> list[bytes]:
    """
    Crea la lista de paquetes a usar para el envío de información entre
    los nodos del programa respetando el protocolo elegido.
    Todos los items de la lista, salvo el primero, que contiene solo el
    nombre y el tamaño del archivo, así como el último que contiene el flag
    FIN activado, son paquetes comunes.
    :param file_path: Directorio del archivo a transferir.
    :param mode: Modo de recuperación de errores.
    :return: Lista de paquetes generados.
    :raises ValueError: Si el archivo no existe.
    :raises Exception: Si el modo de recuperación elegido no existe,
    """
    _, data = _get_file_data(file_path)
    gen = PacketGenerator(mode)
    packets = []
    if len(data) < abs(LAST_PAYLOAD-1):
        # Caso especial, un único paquete.
        _add_last_packet(gen, data, packets)
        return packets

    packets += [gen.create_packet(payload) for payload in data[:LAST_PAYLOAD]]
    _add_last_packet(gen, data, packets)
    return packets
