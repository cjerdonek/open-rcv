

"""
Support for parsing and writing JSON test cases.

"""

from openrcv.formats.common import FormatWriter


class JsonWriter(FormatWriter):

    def write_contest(self, contest):
        """
        Arguments:
          contest: a ContestInput object.

        """
        with self.open():
            self._write_contest(contest)
