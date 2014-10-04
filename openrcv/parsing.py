
import logging
import os

from openrcv.models import ContestInfo, TestRoundResults
from openrcv import utils
from openrcv.utils import FILE_ENCODING, time_it

log = logging.getLogger(__name__)


class Parser(object):

    # TODO: reinitialize these when parsing a new file.
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
        log.info("parsed: %d lines" % line_no)

    def get_parse_return_value(self):
        return None

    def parse_int_line(self, line):
        """Return a tuple of integers."""
        return tuple((int(s) for s in line.split()))

    def parse_lines(self, lines):
        raise NotImplementedError()

    def parse_file(self, f):
        """
        Arguments:
          f: a file-like object.

        """
        with time_it("parsing %s file" % self.name):
            lines = self.iter_lines(f)
            try:
                self.parse_lines(lines)
            except:
                raise Exception("error while parsing line %d: %r" %
                                (self.line_no, self.line))
        return self.get_parse_return_value()

    # TODO: remove this?
    def parse_path(self, path):
        with utils.logged_open(path, "r", encoding=FILE_ENCODING) as f:
            return self.parse_file(f)

    def parse(self, openable):
        """
        Arguments:
          openable: an object with an open() method like a FileOpener or
            StringOpener.

        """
        with openable.open() as f:
            return self.parse_file(f)

class InternalBallotsParser(Parser):

    # TODO: document how to include undervotes.
    """
    Parses an internal ballots file.

    The file format is as follows:

    Each line is a space-delimited string of integers.  The first integer
    is the weight of the ballot, which is 1 for a single voter.  The
    remaining numbers are the candidates in the order in which they
    were ranked.

    A sample file:

    2 2
    1 2 4 3 1
    2 1 3 4
    3 1

    """

    name = "internal ballots"

    def __init__(self, candidates):
        """
        Arguments:
          candidates: iterable of candidate numbers.

        """
        self.candidates = candidates

    def get_parse_return_value(self):
        totals = TestRoundResults(self.candidate_totals)
        return totals

    def parse_lines(self, lines):
        candidates = self.candidates
        totals = {}
        for candidate in candidates:
            totals[candidate] = 0

        candidate_set = set(candidates)
        for line in lines:
            ints = self.parse_int_line(line)
            weight = ints[0]
            for i in ints[1:]:
                if i in candidate_set:
                    totals[i] += weight
                    break

        self.candidate_totals = totals


class BLTParser(Parser):

    name = "BLT"

    # TODO: test the contents of the internal ballot file.
    # TODO: this should accept an openable.
    def __init__(self, output_path=None):
        """
        Arguments:
          output_path: path to which to write an internal ballot file.

        """
        if output_path is None:
            output_path = os.devnull
        self.output_path = output_path

    def get_parse_return_value(self):
        return self.info

    def parse_next_line_text(self, lines):
        return next(lines).strip()

    def parse_next_line_ints(self, lines):
        return self.parse_int_line(next(lines))

    def _parse_ballot_lines(self, lines, f=None):
        ballot_count = 0
        for line in lines:
            ints = self.parse_int_line(line)
            weight = ints[0]
            if weight == 0:
                break
            ballot_count += 1
            # Leave off the terminal 0.
            new_line = " ".join((str(n) for n in ints[:-1]))
            f.write(new_line + "\n")
        return ballot_count

    def parse_ballot_lines(self, lines):
        with utils.logged_open(self.output_path, "w", encoding="ascii") as f:
            ballot_count = self._parse_ballot_lines(lines, f)
        return ballot_count

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

        ballot_count = self.parse_ballot_lines(lines)
        info.ballot_count = ballot_count

        # Read candidate list.
        candidates = []
        for i in range(candidate_count):
            name = self.parse_next_line_text(lines)
            candidates.append(name)
        info.candidates = candidates

        name = self.parse_next_line_text(lines)
        info.name = name
        # TODO: assert remaining lines empty.
        # TODO: and add test that these asserts work.
