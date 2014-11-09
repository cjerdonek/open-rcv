
"""
Support for parsing and writing JSON test cases.

"""

from openrcv.formats.common import FormatWriter
from openrcv.jsonlib import write_json
from openrcv.jcmodels import JsonCaseContestInput

ENCODING_JSON = 'utf-8'

class JsonCaseOutput(FormatWriter):

    def get_file_info(self):
        return os.path.join(self.output_dir, "contest.json"), ENCODING_JSON

    # TODO: DRY up so that we do not need to manually return output_paths.
    def write_contest(self, contest):
        """
        Arguments:
          contest: a ContestInput object.
        """
        stream_infos, output_paths = self.make_output_info(self.get_file_info)
        stream_info = stream_infos[0]

        jc_contest = JsonCaseContestInput.from_object(contest)

        write_json(jc_contest, stream_info=stream_info, path=None)
        return output_paths
