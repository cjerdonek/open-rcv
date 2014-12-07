#
# Copyright (c) 2014 Chris Jerdonek. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import logging
import os

from openrcv.formats.internal import to_internal_ballot
from openrcv.models import ContestInput
from openrcv import utils
from openrcv.utils import parse_integer_line, time_it, FILE_ENCODING

log = logging.getLogger(__name__)


# TODO: add the line number, etc. as attributes.
class ParsingError(Exception):
    pass


class Parser(object):

    # TODO: reinitialize these when parsing a new file.
    line_no = 0
    line = None

    # TODO: consider moving this into StreamInfo by creating a method
    # to return an iterator object over lines -- perhaps by implementing
    # the iterator protocol.
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
            output_info = utils.PathInfo(os.devnull)
        # We check the argument here to fail fast and help the user locate
        # the source of the issue more quickly.
        assert isinstance(output_info, utils.StreamInfo)
        self.output_info = output_info

    def get_parse_return_value(self):
        """Return a ContestInput object."""
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
            ballot = weight, tuple(ints[1:-1])
            ballot_count += 1
            new_line = to_internal_ballot(ballot)
            f.write(new_line + "\n")
        return ballot_count

    def parse_ballot_lines(self, lines):
        with self.output_info.open("w") as f:
            ballot_count = self._parse_ballot_lines(lines, f)
        return ballot_count

    def parse_lines(self, lines):
        info = ContestInput()
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
