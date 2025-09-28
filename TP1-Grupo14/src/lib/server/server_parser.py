import argparse


class CustomHelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            return super()._format_action_invocation(action)
        return ' , '.join(action.option_strings)


def get_parser():
    parser = argparse.ArgumentParser(
        prog='start-server',
        description="Comando para iniciar el servidor.",
        usage="start-server [-h] [-v | -q] [-H ADDR] [-p PORT] "
        "[-s DIRPATH] [-r protocol]",
        formatter_class=CustomHelpFormatter
    )

    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        '-v', '--verbose', action='store_true', help='aumenta la verbosidad')
    verbosity_group.add_argument(
        '-q', '--quiet', action='store_true', help='reduce la verbosidad')

    parser.add_argument(
        '-H', '--host', type=str, help='dirección IP del servidor')
    parser.add_argument(
        '-p', '--port', type=int, help='puerto del servidor')
    parser.add_argument(
        '-s', '--storage', type=str, help='ruta de almacenamiento de archivos')
    parser.add_argument(
        '-r', '--protocol', type=str, help='protocolo de recuperación "'
        '"de errores (gbn o stopandwait)')

    return parser


def parse_args():
    parser = get_parser()
    return parser.parse_args()
