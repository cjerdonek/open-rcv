#!/usr/bin/env python

"""
Usage: python3.4 count.py ELECTION.blt OUTPUT.txt

"""

from contextlib import contextmanager
import sys
import timeit


FILE_ENCODING = "utf-8"


# TODO: use Python's logging module.
def log(s=None):
    """Write to stderr."""
    if s is None:
        s = ""
    print(s, file=sys.stderr)


@contextmanager
def time_it(task_desc):
    """
    A context manager for timing chunks of code and logging it.

    Arguments:
      task_desc: task description for logging purposes

    """
    start_time = timeit.default_timer()
    yield
    elapsed = timeit.default_timer() - start_time
    log("elapsed (%s): %.4f seconds" % (task_desc, elapsed))


class Parser(object):

    line_no = 0
    line = None

    def iter_lines(self, f):
        """
        Return an iterator over the lines of an input file.

        Each iteration sets self.line and self.line_no.

        """
        for line_no, line in enumerate(iter(f), start=1):
            self.line = line
            self.line_no = line_no
            yield line
        log("parsed: %d lines" % line_no)

    def get_parse_return_value(self):
        return None

    def parse_lines(self, lines):
        raise NotImplementedError()

    def parse_file(self, f):
        with time_it("parsing %r" % self.name):
            log("parsing...\n  %r" % self.name)
            try:
                with f:
                    lines = self.iter_lines(f)
                    self.parse_lines(lines)
            except:
                raise Exception("error while parsing line %d: %r" %
                                (self.line_no, self.line))
        return self.get_parse_return_value()

    def parse_path(self, path):
        log("opening...\n  %s" % path)
        return self.parse_file(open(path, "r", encoding=FILE_ENCODING))


class ContestInfo(object):

    """
    Attributes:
      name:
      seat_count: integer number of winners.

    """

class BLTParser(Parser):

    name = "BLT file"

    def get_parse_return_value(self):
        return self.info

    def parse_int_line(self, line):
        """Return a generator of integers."""
        return (int(s) for s in line.split())

    def parse_next_line_ints(self, lines):
        return self.parse_int_line(next(lines))

    def parse_ballot_lines(self, lines):
        for line in lines:
            ballot_numbers = self.parse_int_line(line)
            weight = next(ballot_numbers)
            print("weight: %r" % weight)
            if weight == 0:
                return
            print(tuple(ballot_numbers))

    def parse_lines(self, lines):
        info = ContestInfo()
        self.info = info

        # First line.
        candidate_count, seat_count = self.parse_next_line_ints(lines)
        info.seat_count = seat_count

        # Withdrawn candidates.
        withdraw_numbers = self.parse_next_line_ints(lines)
        withdrawn = []
        for number in withdraw_numbers:
            assert number < 0
            withdrawn.append(-1 * number)
        info.withdrawn = withdrawn

        self.parse_ballot_lines(lines)

        for line in lines:
            print("%d:%s" % (self.line_no, line))


def main(argv):
    ballots_path = "sample.blt"
    parser = BLTParser()
    info = parser.parse_path(ballots_path)
    print(info.withdrawn)


if __name__ == "__main__":
    main(sys.argv)
