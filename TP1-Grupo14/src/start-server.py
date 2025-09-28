from lib.server.server_parser import parse_args
from lib.socket_manager import start_connections_manager
from lib.utils.logger import setup_logger, get_logger


def main():
    args = parse_args()
    setup_logger(verbose=args.verbose, quiet=args.quiet, name="Server")
    logger = get_logger("Server")
    logger.info("Iniciando servidor")
    start_connections_manager(
        args.host, args.port, args.protocol, args.storage
    )


if __name__ == '__main__':
    main()
