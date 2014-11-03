
from textwrap import dedent

from openrcv.formats.blt import BLTFileWriter
from openrcv.models import BallotsResource, ContestInput
from openrcv.utils import StringInfo
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
        contest.ballots_resource = BallotsResource(ballots)
        stream_info = StringInfo()
        writer = BLTFileWriter(stream_info)
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
        self.assertEqual(stream_info.value, expected)
