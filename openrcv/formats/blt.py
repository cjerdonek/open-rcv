
"""
Support for parsing and writing BLT files.

"""

from contextlib import contextmanager

# TODO: move the code to parse BLT files here.

# TODO: move this to a more central location.
# TODO: compare implementation with wineds-converter.
class Writer(object):

    def __init__(self, stream_info):
        self.stream_info = stream_info

    @contextmanager
    def open(self):
        with self.stream_info.open("w") as f:
            self.file = f
            yield

    def writeln(self, line):
        self.file.write(line + "\n")


class BLTWriter(Writer):

    # TODO: make a helper method that creates a file stream_info for BLT
    # purposes (e.g. covering the encoding).

    def write_values(self, values):
        line = " ".join((str(v) for v in values))
        self.writeln(line)

    def _write_contest(self, contest):
        seat_count = contest.seat_count
        assert seat_count is not None
        self.write_values([len(contest.candidates), seat_count])

    def write_contest(self, contest):
        """
        Arguments:
          contest: a ContestInput object.

        """
        with self.open():
            self._write_contest(contest)
