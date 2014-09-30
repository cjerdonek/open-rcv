#!/usr/bin/env python
#
# **THIS SCRIPT IS WRITTEN FOR PYTHON 3.4.**
#

"""
Usage: python3.4 count.py ELECTION.blt OUTPUT.txt

"""

import sys

from openrcv.parsing import BLTParser

FILE_ENCODING = "utf-8"


def main(argv=None):
    if argv is None:
        argv = sys.argv
    # TODO: use argparse.
    print(repr(argv))
    ballots_path = argv[1]
    parser = BLTParser()
    info = parser.parse_path(ballots_path)
    print(repr(info))


if __name__ == "__main__":
    main(sys.argv)
