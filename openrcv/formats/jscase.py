
"""
Support for parsing and writing JSON test cases.

"""

from openrcv.formats.common import FormatWriter
from openrcv.jcmodels import JsonCaseBallot

class JsonCaseOutput(FormatWriter):

    def get_ballot_info(self):
        return os.path.join(self.output_dir, "ballots.txt"), ENCODING_BALLOT_FILE

    def write_contest(self, contest):
        """
        Arguments:
          contest: a ContestInput object.
        """
        # TODO: finish implementing this method.
        with contest.ballots_resource() as ballots:
            for ballot in ballots:
                break
        jc_ballot = JsonCaseBallot.from_object(ballot)
        print(repr(jc_ballot))
        return None

        stream_infos, output_paths = self.make_output_info(self.get_ballot_info)
        stream_info = stream_infos[0]
        file_writer = InternalBallotsWriter(stream_info)
        file_writer.write_ballots(contest)
        return output_paths
