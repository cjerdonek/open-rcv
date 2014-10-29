
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

    def write_line(self, line):
        self.file.write(line + "\n")


class BLTWriter(object):

    # TODO: make a helper method that creates a file stream_info for BLT
    # purposes (e.g. covering the encoding).

    def write_contest(self, contest):
        """
        Arguments:
          contest: a ContestInput object.

        """
        self.writeln("a b c")
