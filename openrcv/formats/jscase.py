
"""
Support for parsing and writing JSON test cases.

"""

import os

from openrcv.formats.common import FormatWriter
from openrcv.jsonlib import write_json
from openrcv.jcmodels import JsonCaseContestInput

ENCODING_JSON = 'utf-8'

class JsonCaseOutput(FormatWriter):

    def get_file_info(self):
        return os.path.join(self.output_dir, "contest.json"), ENCODING_JSON

    def write_contest_stream(self, stream_info, contest):
        jc_contest = JsonCaseContestInput.from_object(contest)
        write_json(jc_contest, stream_info=stream_info, path=None)

    def contest_info(self):
        return self.get_file_info, self.write_contest_stream

    def write_contest(self, contest):
        """
        Arguments:
          contest: a ContestInput object.
        """
        return self.write_output(self.contest_info, contest)
