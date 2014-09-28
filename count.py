#!/usr/bin/env python

"""
Usage: python3.4 count.py ELECTION.blt OUTPUT.txt

"""

import sys


# TODO: use Python's logging module.
def log(s=None):
    """Write to stderr."""
    if s is None:
        s = ""
    print(s, file=sys.stderr)


class Reader(object):

    line_no = 0
    line = None

    def iter_lines(self, f):
        """
        Return an iterator over the lines of an input file.

        Each iteration sets self.line and self.line_no but yields nothing.

        """
        for line_no, line in enumerate(iter(f), start=1):
            self.line = line
            self.line_no = line_no
            # This yields no values because we set the information
            # we need as instance attributes instead.  This is more
            # convenient for things like our Parser exception handler.
            yield line
        log("parsed: %d lines" % line_no)


def main(argv):
    ballots_path = "sample.blt"
    with open(ballots_path, "r") as f:
        reader = Reader()
        lines = reader.iter_lines(f)
        for line in lines:
            print("%d:%s" % (reader.line_no, line))


if __name__ == "__main__":
    main(sys.argv)
