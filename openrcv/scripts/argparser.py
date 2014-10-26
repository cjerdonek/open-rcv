
from openrcv.scripts.argparse import ArgParser, HelpAction, Option


DESCRIPTION = """\
Tally the contests specified by the file at INPUT_PATH.

"""

OPTION_HELP = Option(('-h', '--help'))


# TODO: unit-test print_help().
def create_argparser(prog="rcv"):
    """
    Return an ArgumentParser object.

    """
    parser = ArgParser(prog=prog, description=DESCRIPTION, add_help=False)
    parser.add_argument('input_path', metavar='INPUT_PATH',
        help=("path to a contests configuration file. Supported file "
              "formats are JSON (*.json) and YAML (*.yaml or *.yml)."))
    # The add_argument() call for help is modeled after how argparse does it.
    parser.add_argument('-h', '--help', action=HelpAction,
        help='show this help message and exit.')
    return parser
