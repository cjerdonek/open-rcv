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

"""
Support for parsing and writing BLT files.

Here is an example BLT file (taken from: https://code.google.com/p/droop/wiki/BltFileFormat ):

    4 2
    -2
    3 1 3 4 0
    4 1 3 2 0
    2 4 1 3 0
    1 2 0
    2 2 4 3 1 0
    1 3 4 2 0
    0
    "Adam"
    "Basil"
    "Charlotte"
    "Donald"
    "Title"

"""

import os

from openrcv.formats.common import Format, FormatWriter
from openrcv.utils import FileWriter


BLT_ENCODING = 'utf-8'

# TODO: move the code to parse BLT files here.

class BLTFormat(Format):

    @property
    def contest_writer_cls(self):
        return BLTContestWriter


# TODO: DRY up with InternalContestWriter.
class BLTContestWriter(FormatWriter):

    @property
    def get_output_infos(self):
        return (self.get_output_info, )

    def get_output_info(self, output_dir):
        return os.path.join(self.output_dir, "output.blt"), BLT_ENCODING

    def resource_write(self, resource, contest):
        writer = BLTFileWriter(resource)
        writer.write_contest(contest)


class BLTFileWriter(FileWriter):

    def write_text(self, text):
        self.writeln('"%s"' % text)

    def write_values(self, values):
        line = " ".join((str(v) for v in values))
        self.writeln(line)

    def _write_contest(self, contest):
        seat_count = contest.seat_count
        assert seat_count is not None
        self.write_values([len(contest.candidates), seat_count])
        with contest.ballots_resource.reading() as ballots:
            for ballot in ballots:
                weight, choices = ballot
                self.write_values([weight] + list(choices) + [0])
        self.write_values([0])
        for candidate in contest.candidates:
            self.write_text(candidate)
        self.write_text(contest.name)

    def write_contest(self, contest):
        """
        Arguments:
          contest: a ContestInput object.
        """
        with self.open():
            self._write_contest(contest)
