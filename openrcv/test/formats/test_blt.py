
from textwrap import dedent

from openrcv.formats.blt import BLTWriter
from openrcv.models import BallotsResource, ContestInfo
from openrcv.utils import StringInfo
from openrcv.utiltest.helpers import UnitCase


class BLTWriterTest(UnitCase):

    def test(self):
        contest = ContestInfo()
        contest.name = "Foo"
        contest.candidates = ['A', 'B', 'C']
        contest.seat_count = 1
        ballots = [
            (2, (2, 1)),
            (1, (2, )),
        ]
        contest.ballots_resource = BallotsResource(ballots)
        output = StringInfo()
        writer = BLTWriter(output)
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
        self.assertEqual(output.value, expected)
