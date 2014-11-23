
"""
Support for parsing and writing JSON test cases.

"""

import os

from openrcv.formats.common import Format, FormatWriter
from openrcv.jsonlib import write_json
from openrcv.jcmodels import JsonCaseContestInput


ENCODING_JSON = 'utf-8'

class JsonCaseFormat(Format):

    def write_contest(self, contest, output_dir=None, stdout=None):
        """
        Arguments:
          contest: a ContestInput object.
        """
        writer = JsonCaseContestWriter(output_dir=output_dir, stdout=stdout)
        return writer.write_output(contest)


class JsonCaseContestWriter(FormatWriter):

    @property
    def file_info_funcs(self):
        return (self.get_output_info, )

    def get_output_info(self, output_dir):
        return os.path.join(output_dir, "contest.json"), ENCODING_JSON

    def resource_write(self, resource, contest):
        jc_contest = JsonCaseContestInput.from_object(contest)
        write_json(jc_contest, resource=resource)
