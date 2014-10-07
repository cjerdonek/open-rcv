
from unittest import TestCase

from openrcv.models import ContestInfo, TestBallot


class ContestInfoTest(TestCase):

    def test_get_candidates(self):
        contest = ContestInfo()
        contest.candidates = ["Alice", "Bob", "Carl"]
        self.assertEqual(contest.get_candidates(), range(1, 4))


class TestBallotTest(TestCase):

    def test_init(self):
        ballot = TestBallot(choices=[1, 2], weight=3)
        self.assertEqual(ballot.choices, [1, 2])
        self.assertEqual(ballot.weight, 3)

    def test_init__defaults(self):
        ballot = TestBallot()
        self.assertEqual(ballot.choices, [])
        self.assertEqual(ballot.weight, 1)

    def test_to_jsobj(self):
        ballot = TestBallot(choices=[1, 2], weight=3)
        jsobj = ballot.to_jsobj()
        self.assertEqual(jsobj, "3 1 2")

    def test_to_jsobj__undervote(self):
        ballot = TestBallot(choices=[], weight=3)
        jsobj = ballot.to_jsobj()
        self.assertEqual(jsobj, "3")

    def test_to_jsobj__none_choices(self):
        ballot = TestBallot(weight=3)
        jsobj = ballot.to_jsobj()
        self.assertEqual(jsobj, "3")
