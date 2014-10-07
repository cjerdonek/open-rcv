
from contextlib import contextmanager
from unittest import TestCase

from openrcv.models import ContestInfo, JsonContest, JsonObjError, TestBallot


@contextmanager
def change_attr(obj, name, value):
    initial_value = getattr(obj, name)
    setattr(obj, name, value)
    yield
    setattr(obj, name, initial_value)


class JsonMixinTest(TestCase):

    def test_ne(self):
        pass


class ContestInfoTest(TestCase):

    def test_get_candidates(self):
        contest = ContestInfo()
        contest.candidates = ["Alice", "Bob", "Carl"]
        self.assertEqual(contest.get_candidates(), range(1, 4))


class TestBallotTest(TestCase):

    def make_ballot(self):
        return TestBallot(choices=[1, 2], weight=3)

    def test_init(self):
        ballot = self.make_ballot()
        self.assertEqual(ballot.choices, [1, 2])
        self.assertEqual(ballot.weight, 3)

    def test_init__defaults(self):
        ballot = TestBallot()
        self.assertEqual(ballot.choices, [])
        self.assertEqual(ballot.weight, 1)

    def test_repr(self):
        ballot = self.make_ballot()
        self.assertEqual(repr(ballot),
                         "<TestBallot: jsobj='3 1 2' %s>" % hex(id(ballot)))

    def test_eq(self):
        ballot1 = self.make_ballot()
        ballot2 = self.make_ballot()
        self.assertEqual(ballot1, ballot2)
        with change_attr(ballot2, "choices", [1]):
            self.assertNotEqual(ballot1, ballot2)
        with change_attr(ballot2, "weight", 100):
            self.assertNotEqual(ballot1, ballot2)

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

    def test_repr(self):
        contest = self.make_contest()
        self.assertEqual(repr(contest), "<JsonContest: id=3 candidate_count=2 %s>" %
                         hex(id(contest)))

    def test_eq(self):
        contest1 = self.make_contest()
        contest2 = self.make_contest()
        self.assertEqual(contest1, contest2)

        # Check that each attribute can trigger inequality.
        cases = [
            ("candidate_count", 3),
            ("ballots", []),
            ("id", 4),
            ("notes", "foo2"),
        ]
        for attr, value in cases:
            with self.subTest(attr=attr, value=value):
                with change_attr(contest2, attr, value):
                    self.assertNotEqual(contest1, contest2)
        self.assertEqual(contest1, contest2)  # sanity check
