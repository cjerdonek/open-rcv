
"""
Support for parsing and writing files in OpenRCV's internal format.

"""

import os

from openrcv.formats.common import FormatWriter
from openrcv.utils import FileWriter


# ASCII makes reading and parsing the file faster.
ENCODING_BALLOT_FILE = 'ascii'


def format_values(values):
    return " ".join((str(v) for v in values))


# TODO: remove the "final" argument.g
def format_ballot(weight, choices, final=''):
    """
    Return the internal format representation of a ballot.

    Arguments:
      choices: an iterable of choices.

    """
    # There is no terminal 0 like in the BLT format.
    text = format_values([weight] + list(choices))
    if final:
        text += final
    return text


class InternalOutput(FormatWriter):

    def get_ballot_info(self):
        return os.path.join(self.output_dir, "ballots.txt"), ENCODING_BALLOT_FILE

    def write_contest(self, contest):
        """
        Arguments:
          contest: a ContestInput object.
        """
        stream_infos, output_paths = self.make_output_info(self.get_ballot_info)
        stream_info = stream_infos[0]
        file_writer = InternalBallotsWriter(stream_info)
        file_writer.write_ballots(contest)
        return output_paths


class InternalBallotsWriter(FileWriter):

    def _write_ballots(self, contest):
        with contest.ballots_resource() as ballots:
            for ballot in ballots:
                self.writeln(format_ballot(*ballot))

    def write_ballots(self, contest):
        """
        Arguments:
          contest: a ContestInput object.
        """
        with self.open():
            self._write_ballots(contest)
