
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


class BLTContestWriter(FormatWriter):

    @property
    def file_info_funcs(self):
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
        with contest.ballots_resource() as ballots:
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
