
from textwrap import dedent

from openrcv.models import BallotsResource, BallotStreamResource, ContestInput
from openrcv.utils import StringInfo
from openrcv.utiltest.helpers import UnitCase


class BallotsResourceTest(UnitCase):

    def test(self):
        ballots = [1, 3, 2]
        ballot_resource = BallotsResource(ballots)
        with ballot_resource() as ballots:
            ballots = list(ballots)
        self.assertEqual(ballots, [1, 3, 2])


class BallotStreamResourceTest(UnitCase):

    def test(self):
        ballot_info = StringInfo("2 1 2\n3 1\n")
        ballot_resource = BallotStreamResource(ballot_info)
        with ballot_resource() as ballots:
            ballots = list(ballots)
        self.assertEqual(ballots, ['2 1 2\n', '3 1\n'])

    def test_parse_default(self):
        ballot_info = StringInfo("2 1 2\n3 1\n")
        parse = lambda line: line.strip()
        ballot_resource = BallotStreamResource(ballot_info, parse=parse)
        with ballot_resource() as ballots:
            ballots = list(ballots)
        self.assertEqual(ballots, ['2 1 2', '3 1'])


class ContestInputTest(UnitCase):

    def test_get_candidates(self):
        contest = ContestInput()
        contest.candidates = ["Alice", "Bob", "Carl"]
        self.assertEqual(contest.get_candidates(), range(1, 4))
