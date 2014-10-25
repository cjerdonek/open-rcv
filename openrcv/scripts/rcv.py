
"""
The rcv command for counting ballots.

"""

import argparse
import logging
import os
import sys

import yaml

from openrcv import counting
from openrcv.scripts.main import main, ArgParser, HelpAction
from openrcv.utils import logged_open


log = logging.getLogger(__name__)

DESCRIPTION = """\
Tally the contests specified by the file at INPUT_PATH.

"""


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


def run_main():
    main(run_rcv)


def run_rcv(argv):
    if argv is None:
        argv = sys.argv
    parser = create_argparser()
    ns = parser.parse_args(args=argv[1:])  # Namespace object
    input_path = ns.input_path
    with logged_open(input_path) as f:
        config = yaml.load(f)
    # TODO: use a common pattern for accessing config values.
    base_dir = os.path.dirname(input_path)
    config = config['openrcv']
    contests = config['contests']
    contest = contests[0]
    blt_path = os.path.join(base_dir, contest['file'])
    counting.count_irv(blt_path)
