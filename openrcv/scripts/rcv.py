
"""
The rcv command for counting ballots.

"""

import argparse
import logging
import os
import sys

import yaml

from openrcv import counting
from openrcv.scripts.argparse import ArgParser, HelpAction
from openrcv.scripts.argparser import create_argparser
from openrcv.scripts.run import main
from openrcv.utils import logged_open


log = logging.getLogger(__name__)


def run_main():
    main(run_rcv)


# TODO: unit-test this.
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
