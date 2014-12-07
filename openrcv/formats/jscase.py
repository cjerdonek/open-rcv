#
# Copyright (c) 2014 Chris Jerdonek. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

"""
Support for parsing and writing JSON test cases.

"""

import os

from openrcv.formats.common import Format, FormatWriter
from openrcv.jsonlib import write_json
from openrcv.jcmodels import JsonCaseContestInput


ENCODING_JSON = 'utf-8'


class JsonCaseFormat(Format):

    @property
    def contest_writer_cls(self):
        return JsonCaseContestWriter


class JsonCaseContestWriter(FormatWriter):

    @property
    def get_output_infos(self):
        return (self.get_output_info, )

    def get_output_info(self, output_dir):
        return os.path.join(output_dir, "contest.json"), ENCODING_JSON

    def resource_write(self, resource, contest):
        jc_contest = JsonCaseContestInput.from_model(contest)
        write_json(jc_contest, resource=resource)
