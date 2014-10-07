
from unittest import TestCase

from openrcv.models import ContestInfo, JsonContest, JsonObjError, TestBallot


class JsonMixinTest(TestCase):

    def test_ne(self):
        pass


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

    def test_eq(self):
        ballot = TestBallot(choices=[1, 2], weight=3)
        self.assertEqual(ballot, TestBallot(choices=[1, 2], weight=3))
        self.assertNotEqual(ballot, TestBallot(choices=[1], weight=3))
        self.assertNotEqual(ballot, TestBallot(choices=[1, 2], weight=2))

    def test_to_jsobj(self):
        ballot = TestBallot(choices=[1, 2], weight=3)
        jsobj = ballot.to_jsobj()
        self.assertEqual(jsobj, "3 1 2")

    def test_to_jsobj__undervote(self):
        ballot = TestBallot(weight=3)
        jsobj = ballot.to_jsobj()
        self.assertEqual(jsobj, "3")

    def test_to_jsobj__none_choices(self):
        """Test having None for choices."""
        ballot = TestBallot(weight=3)
        ballot.choices = None
        with self.assertRaises(TypeError):
            jsobj = ballot.to_jsobj()

    def test_load_jsdata(self):
        ballot = TestBallot()
        ballot.load_jsobj("2")
        self.assertEqual(ballot, TestBallot(weight=2))

    def test_from_jsobj(self):
        ballot = TestBallot.from_jsobj("2 3 4")
        self.assertEqual(ballot, TestBallot(choices=[3, 4], weight=2))

    def test_from_jsobj(self):
        with self.assertRaises(JsonObjError):
            ballot = TestBallot.from_jsobj("2 ")


class JsonContestTest(TestCase):

    def make_contest(self, ballots=None):
        """Return a test contest."""
        if ballots is None:
            ballots = [TestBallot(choices=[1, 2]),
                       TestBallot(choices=[2], weight=3)]
        contest = JsonContest(candidate_count=2, ballots=ballots, id_=3, notes="foo")
        return contest

    def test_init(self):
        ballots = [TestBallot(choices=[1, 2]),
                   TestBallot(choices=[2], weight=3)]
        contest = self.make_contest(ballots=ballots)
        cases = [
            ("candidate_count", 2),
            ("ballots", ballots),
            ("id", 3),
            ("notes", "foo"),
        ]
        for attr, expected in cases:
            with self.subTest(attr=attr, expected=expected):
                actual = getattr(contest, attr)
                self.assertEqual(actual, expected)

    def test_init__defaults(self):
        contest = JsonContest()
        cases = [
            ("candidate_count", None),
            ("ballots", None),
            ("id", None),
            ("notes", None),
        ]
        for attr, expected in cases:
            with self.subTest(attr=attr, expected=expected):
                actual = getattr(contest, attr)
                self.assertEqual(actual, expected)

    def test_eq(self):
        contest1 = self.make_contest()
        contest2 = self.make_contest()
        self.assertEqual(contest1, contest2)
