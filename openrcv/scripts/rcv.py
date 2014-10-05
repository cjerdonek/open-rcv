
"""
The rcv command for counting ballots.

"""

import logging
import sys

from openrcv import counting
from openrcv.scripts.main import main

log = logging.getLogger(__name__)


def run_main():
    main(run_rcv)

def run_rcv(argv):
    if argv is None:
        argv = sys.argv
    # TODO: use argparse.
    blt_path = argv[1]
    counting.count_irv(blt_path)
