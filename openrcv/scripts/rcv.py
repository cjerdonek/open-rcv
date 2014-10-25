
"""
The rcv command for counting ballots.

"""

import logging
import sys

from openrcv import counting
from openrcv.scripts.main import main, ArgParser

log = logging.getLogger(__name__)

DESCRIPTION = """\
Tally the contests specified by the file at INPUT_PATH.

"""


def create_argparser():
    """
    Return an ArgumentParser object.

    """
    parser = ArgParser(description=DESCRIPTION)
    parser.add_argument('input_path', metavar='INPUT_PATH',
                        help="path to a contests configuration file. "
                             "Supported file formats are JSON (*.json) and "
                             "YAML (*.yaml or *.yml).")
    return parser


def run_main():
    main(run_rcv)


# TODO: unit-test --help.
def run_rcv(argv):
    if argv is None:
        argv = sys.argv
    parser = create_argparser()
    ns = parser.parse_args()  # Namespace object
    input_path = ns.input_path
    # TODO: read BLT path from input_path.
    blt_path = input_path
    counting.count_irv(blt_path)
