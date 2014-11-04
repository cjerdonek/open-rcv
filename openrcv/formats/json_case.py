
"""
Support for parsing and writing JSON test cases.

"""

from openrcv.formats.common import FormatWriter


class JsonTestCaseOutput(FormatWriter):

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
