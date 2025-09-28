import sys
import argparse
from lib.client import start_client  # import directo
from lib.utils.exceptions import (
    ServerDisconnected, WrongDataReceived,
    NoServerEnoughMemory, FullStorageError
)
from lib.utils.logger import setup_logger, get_logger


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print("\nError: Comando inválido. Use -h para ver la ayuda y"
              " asegúrese de llenar todos los argumentos requeridos.\n")
        sys.exit(1)


def main():
    parser = CustomArgumentParser(
        description="Comando para descargar un archivo del servidor.",
        usage="download [-h] [-v | -q] [-H ADDR] [-p PORT]"
        " [-d FILEPATH] [-n FILENAME] [-r protocol]"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="aumenta la verbosidad")
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="reduce la verbosidad")
    parser.add_argument(
        "-H", "--host", type=str,
        required=True, help="dirección IP del servidor"
    )
    parser.add_argument(
        "-p", "--port", type=int, required=True, help="puerto del servidor")
    parser.add_argument(
        "-d", "--dst", type=str,
        required=True, help="ruta donde guardar el archivo"
    )
    parser.add_argument(
        "-n", "--name", type=str,
        required=True, help="nombre del archivo en el servidor"
    )
    parser.add_argument(
        "-r", "--protocol", type=str,
        required=True, choices=["gbn", "sw", "GBN", "SW"],
        help="protocolo de recuperación de errores"
    )

    args = parser.parse_args()
    setup_logger(verbose=args.verbose, quiet=args.quiet, name="Client")
    logger = get_logger("Client")
    logger.info("=== Cliente: DOWNLOAD ===")
    try:
        start_client.start_client(
            command="download",
            host=args.host,
            port=args.port,
            file_path=args.dst,
            file_name=args.name,
            protocol=args.protocol
        )
    except (
        ServerDisconnected,
        WrongDataReceived,
        NoServerEnoughMemory,
        FullStorageError
    ) as e:
        logger.error(f"Error: {e}")
    except KeyboardInterrupt:
        logger.error("Sesión terminada...")


if __name__ == "__main__":
    main()
