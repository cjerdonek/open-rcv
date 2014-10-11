
import logging
import os

from openrcv.models import ContestInfo
from openrcv import utils
from openrcv.utils import time_it, FILE_ENCODING


log = logging.getLogger(__name__)


def parse_integer_line(line):
    """
    Parse a string of integers (with or without a trailing newline).

    Returns an iterator object of integers.

    This function allows leading and trailing spaces.  ValueError is
    raised if one of the values does not parse to an integer.

    """
    return (int(s) for s in line.split())


def make_internal_ballot_line(weight, choices):
    """
    Arguments:
      choices: an iterable of choices.

    """
    ballot = str(weight)
    if choices:
        ballot = "%s %s" % (ballot, " ".join((str(c) for c in choices)))
    # Do not include the terminal 0 that BLT files include.
    return ballot


def parse_internal_ballot(line):
    """
    Parse an internal ballot line (with or without a trailing newline).

    This function allows leading and trailing spaces.  ValueError is
    raised if one of the values does not parse to an integer.

    An internal ballot line is a space-delimited string of integers of the
    form--

    "WEIGHT CHOICE1 CHOICE2 CHOICE3 ...".

    """
    ints = parse_integer_line(line)
    weight = next(ints)
    choices = tuple(ints)
    return weight, choices


# TODO: add the line number, etc. as attributes.
class ParsingError(Exception):
    pass


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

    def parse_lines(self, lines):
        raise NotImplementedError()

    def parse_file(self, f):
        """
        Arguments:
          f: a file-like object.

        """
        with time_it("parser: %s" % (self.name, )):
            lines = self.iter_lines(f)
            try:
                self.parse_lines(lines)
            except:
                raise ParsingError("error while parsing line %d: %r" %
                                   (self.line_no, self.line))
        return self.get_parse_return_value()

    def parse(self, stream_info):
        """
        Arguments:
          stream_info: a StreamInfo object.

        """
        with stream_info.open() as f:
            return self.parse_file(f)


class BLTParser(Parser):

    name = "BLT (ballot)"

    def __init__(self, output_info=None):
        """
        Arguments:
          output_info: a StreamInfo object to which to write an internal
            ballot file.

        """
        if output_info is None:
            output_info = utils.FileInfo(os.devnull)
        # We check the argument here to fail fast and help the user locate
        # the source of the issue more quickly.
        assert isinstance(output_info, utils.StreamInfo)
        self.output_info = output_info

    def get_parse_return_value(self):
        """Return a ContestInfo object."""
        return self.info

    def parse_next_line_text(self, lines):
        return next(lines).strip()

    def parse_next_line_ints(self, lines):
        return parse_integer_line(next(lines))

    def _parse_ballot_lines(self, lines, f=None):
        ballot_count = 0
        for line in lines:
            ints = tuple(parse_integer_line(line))
            weight = ints[0]
            if weight == 0:
                break
            ballot_count += 1
            # Leave off the initial weight and terminal 0 for choices.
            new_line = make_internal_ballot_line(weight, ints[1:-1])
            f.write(new_line + "\n")
        return ballot_count

    def parse_ballot_lines(self, lines):
        with self.output_info.open("w") as f:
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

        for line in lines:
            if line.strip():
                raise ValueError("the BLT has non-empty lines at the end")
