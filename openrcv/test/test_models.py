
from contextlib import contextmanager
from unittest import TestCase

from openrcv.models import (ContestInfo, JsonContest, JsonObjError, JsonBallot,
                            JSNULL)


@contextmanager
def change_attr(obj, name, value):
    """Context manager to temporarily change the value of an attribute.

    This is useful for testing __eq__() by modifying one attribute
    at a time.

    """
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


class JsonBallotTest(TestCase):

    def make_ballot(self):
        return JsonBallot(choices=[1, 2], weight=3)

    def test_init(self):
        ballot = self.make_ballot()
        self.assertEqual(ballot.choices, [1, 2])
        self.assertEqual(ballot.weight, 3)

    def test_init__defaults(self):
        ballot = JsonBallot()
        self.assertEqual(ballot.choices, [])
        self.assertEqual(ballot.weight, 1)

    def test_repr(self):
        ballot = self.make_ballot()
        self.assertEqual(repr(ballot),
                         "<JsonBallot: jsobj='3 1 2' %s>" % hex(id(ballot)))

    def test_eq(self):
        ballot1 = self.make_ballot()
        ballot2 = self.make_ballot()
        self.assertEqual(ballot1, ballot2)
        with change_attr(ballot2, "choices", [1]):
            self.assertNotEqual(ballot1, ballot2)
        with change_attr(ballot2, "weight", 100):
            self.assertNotEqual(ballot1, ballot2)
        self.assertEqual(ballot1, ballot2)  # sanity check

    def test_to_jsobj(self):
        ballot = JsonBallot(choices=[1, 2], weight=3)
        jsobj = ballot.to_jsobj()
        self.assertEqual(jsobj, "3 1 2")

    def test_to_jsobj__undervote(self):
        ballot = JsonBallot(weight=3)
        jsobj = ballot.to_jsobj()
        self.assertEqual(jsobj, "3")

    def test_to_jsobj__none_choices(self):
        """Test having None for choices."""
        ballot = JsonBallot(weight=3)
        ballot.choices = None
        with self.assertRaises(TypeError):
            jsobj = ballot.to_jsobj()

    def test_load_jsobj(self):
        ballot = JsonBallot()
        ballot.load_jsobj("2")
        self.assertEqual(ballot, JsonBallot(weight=2))

    def test_from_jsobj(self):
        ballot = JsonBallot.from_jsobj("2 3 4")
        self.assertEqual(ballot, JsonBallot(choices=[3, 4], weight=2))

    def test_from_jsobj__trailing_space(self):
        """This checks that the format is strict (i.e. doesn't call strip())."""
        with self.assertRaises(JsonObjError):
            ballot = JsonBallot.from_jsobj("2 ")


class JsonContestTest(TestCase):

    def make_ballots(self):
        ballots = [JsonBallot(choices=[1, 2]),
                   JsonBallot(choices=[2], weight=3)]
        return ballots

    def make_contest(self, ballots=None):
        """Return a test contest."""
        if ballots is None:
            ballots = self.make_ballots()
        contest = JsonContest(candidate_count=2, ballots=ballots, id_=3, notes="foo")
        return contest

    def test_init(self):
        ballots = [JsonBallot(choices=[1, 2]),
                   JsonBallot(choices=[2], weight=3)]
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

    def test_load_jsobj(self):
        contest = JsonContest()
        self.assertEqual(contest.candidate_count, None)
        # Check loading an empty dict.
        # In particular, attributes should not get set to JsNull.
        contest.load_jsobj({})
        self.assertEqual(contest.candidate_count, None)

        # Check loading metadata.
        # Check that the id needs to be in the meta dict.
        contest.load_jsobj({"id": 5})
        self.assertEqual(contest.id, None)
        contest.load_jsobj({"_meta": {"id": 5}})
        self.assertEqual(contest.id, 5)
        # Check Javascript null (which the json module converts to None).
        contest.load_jsobj({"_meta": {"id": None}})
        self.assertEqual(contest.id, JSNULL)

        contest.load_jsobj({"candidate_count": 5})
        self.assertEqual(contest.candidate_count, 5)

        # TODO
        ballots = self.make_ballots()
        contest.load_jsobj({"ballots": ""})
