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

from textwrap import dedent

from openrcv.formats.blt import BLTFileWriter
from openrcv.models import ContestInput
from openrcv.streams import ListResource, StringResource
from openrcv.utiltest.helpers import UnitCase


class BLTFileWriterTest(UnitCase):

    def test(self):
        contest = ContestInput()
        contest.name = "Foo"
        contest.candidates = ['A', 'B', 'C']
        contest.seat_count = 1
        ballots = [
            (2, (2, 1)),
            (1, (2, )),
        ]
        contest.ballots_resource = ListResource(ballots)
        resource = StringResource()
        writer = BLTFileWriter(resource)
        writer.write_contest(contest)
        expected = dedent("""\
        3 1
        2 2 1 0
        1 2 0
        0
        "A"
        "B"
        "C"
        "Foo\"
        """)
        self.assertEqual(resource.contents, expected)
