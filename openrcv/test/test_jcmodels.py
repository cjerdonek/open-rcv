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

from openrcv.jsonlib import JsonableError, JsonDeserializeError, JS_NULL
from openrcv.jcmodels import (from_jsobj, JsonCaseBallot, JsonCaseContestInput,
                              JsonRoundResults, JsonTestCaseOutput)
from openrcv.models import ContestInput
from openrcv.streams import ListResource
from openrcv.utils import StreamInfo, StringInfo
from openrcv.utiltest.helpers import UnitCase


def make_jc_ballot(weight, choices):
    return JsonCaseBallot(weight=weight, choices=choices)


def make_jc_ballots(seq):
    ballots = []
    for weight, choices in seq:
        ballot = make_jc_ballot(weight, choices)
        ballots.append(ballot)
    return ballots


# TODO: move/convert tests from JsonBallotTest to JsonCaseBallotTest.
class JsonCaseBallotTest(UnitCase):

    def test_init(self):
        ballot = JsonCaseBallot(choices=(1, 2), weight=3)
        self.assertEqual(ballot.choices, (1, 2))
        self.assertEqual(ballot.weight, 3)

    def test_init__defaults(self):
        ballot = JsonCaseBallot()
        self.assertEqual(ballot.choices, ())
        self.assertEqual(ballot.weight, 1)

    def test_init__tuple(self):
        """Check that choices are converted to tuples."""
        ballot = JsonCaseBallot(choices=[])
        self.assertEqual(ballot.choices, ())
        ballot = JsonCaseBallot(choices=[1, 2])
        self.assertEqual(ballot.choices, (1, 2))

    def test_repr_info(self):
        cases = [
            (3, (1, 2), "weight=3 choices=(1, 2)"),
            (None, None, "weight=None choices=None"),
        ]
        for weight, choices, expected in cases:
            with self.subTest(weight=weight, choices=choices, expected=expected):
                ballot = JsonCaseBallot()
                ballot.choices = choices
                ballot.weight = weight
                self.assertEqual(ballot.repr_info(), expected)

    def test_repr(self):
        ballot = JsonCaseBallot(choices=(1, 2), weight=3)
        expected = "<JsonCaseBallot: [weight=3 choices=(1, 2)] %s>" % hex(id(ballot))
        self.assertEqual(repr(ballot), expected)

    def test_eq(self):
        ballot1 = JsonCaseBallot(choices=(1, 2), weight=3)
        ballot2 = JsonCaseBallot(choices=(1, 2), weight=3)
        self.assertEqual(ballot1, ballot2)
        with self.changeAttr(ballot2, "choices", (1, 3)):
            self.assertNotEqual(ballot1, ballot2)
        with self.changeAttr(ballot2, "weight", 100):
            self.assertNotEqual(ballot1, ballot2)
        self.assertEqual(ballot1, ballot2)  # sanity check

    def test_from_model(self):
        ballot = (2, (3, 1))
        jc_ballot = JsonCaseBallot.from_model(ballot)
        expected = JsonCaseBallot(choices=(3, 1), weight=2)
        jc_ballot.assert_equal(expected)

    def test_to_object(self):
        jc_ballot = JsonCaseBallot(choices=(1, 2), weight=3)
        ballot = jc_ballot.to_model()
        self.assertEqual(ballot, (3, (1, 2)))

    def test_from_jsobj(self):
        cases = [
            ('3 1 2', {'weight': 3, 'choices': (1, 2)}),
            # Test an undervote.
            ('3', {'weight': 3}),
        ]
        # kwargs is the kwargs for the "expected" JsonCaseBallot.
        for jsobj, kwargs in cases:
            with self.subTest(jsobj=jsobj, kwargs=kwargs):
                jc_ballot = JsonCaseBallot.from_jsobj(jsobj)
                expected = JsonCaseBallot(**kwargs)
                jc_ballot.assert_equal(expected)

    def test_from_jsobj__bad_format(self):
        """Check a string that does not parse."""
        with self.assertRaises(JsonDeserializeError):
            jc_ballot = JsonCaseBallot.from_jsobj("2 a 4")

    def test_to_jsobj(self):
        cases = [
            ({'weight': 3, 'choices': (1, 2)}, '3 1 2'),
            # Test an undervote.
            ({'weight': 3}, '3'),
        ]
        for kwargs, expected in cases:
            with self.subTest(kwargs=kwargs, expected=expected):
                jc_ballot = JsonCaseBallot(**kwargs)
                self.assertEqual(jc_ballot.to_jsobj(), expected)


# TODO: remove this case after moving the tests.
class JsonBallotTest(object):

    def test_to_ballot_stream(self):
        ballots = [JsonBallot(weight=3),
                   JsonBallot(choices=[1, 2])]
        stream = JsonBallot.to_ballot_stream(ballots)
        self.assertTrue(isinstance(stream, StreamInfo))
        self.assertEqual(stream.value, "3\n1 1 2\n")

    def test_from_ballot_stream(self):
        ballot_stream = StringInfo(dedent("""\
        2
        3 1 2
        """))
        ballots = JsonBallot.from_ballot_stream(ballot_stream)
        expected = [JsonBallot(weight=2),
                    JsonBallot(weight=3, choices=(1, 2))]
        self.assertEqual(ballots, expected)


class JsonCaseContestInputTest(UnitCase):

    cls = JsonCaseContestInput

    def make_ballots(self):
        seq = [
            (1, (1, 2)),
            (3, (2, )),
        ]
        return make_jc_ballots(seq)

    def make_contest(self, ballots=None):
        """Return a test contest."""
        if ballots is None:
            ballots = self.make_ballots()
        contest = JsonCaseContestInput(candidate_count=2, ballots=ballots, id_=3, notes="foo")
        return contest

    def test_init(self):
        ballots = [JsonCaseBallot(choices=[1, 2]),
                   JsonCaseBallot(choices=[2], weight=3)]
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
        contest = JsonCaseContestInput()
        cases = [
            ("candidate_count", None),
            ("ballots", None),
            ("id", 0),
            ("notes", None),
        ]
        # TODO: make a assertAttrsEqual method.
        for attr, expected in cases:
            with self.subTest(attr=attr, expected=expected):
                actual = getattr(contest, attr)
                self.assertEqual(actual, expected)

    def test_from_model(self):
        contest = ContestInput()
        contest.candidates = ['Ann', 'Bob']
        ballots = [(2, (3, 1))]
        contest.ballots_resource = ListResource(ballots)
        jc_contest = JsonCaseContestInput.from_model(contest)

        expected = JsonCaseContestInput(candidate_count=2)
        expected.ballots = [JsonCaseBallot(weight=2, choices=(3, 1))]
        jc_contest.assert_equal(expected)

    def test_to_model(self):
        cls = self.cls
        ballots = make_jc_ballots([(3, (2, 1))])
        jc_contest = cls(id_=2, name="My Name", notes="Notes...", candidate_count=3,
                         ballots=ballots, normalize_ballots=False)
        contest = jc_contest.to_model()
        expected_attrs = [
            ("id", 2),
            ("name", "My Name"),
            ("notes", "Notes..."),
        ]
        self.assertAttrs(contest, expected_attrs)


    def test_from_jsobj__ballots(self):
        """Check that ballots deserialize okay."""
        cls = self.cls
        jc_contest = cls.from_jsobj({"ballots": ["3 2 1"]})
        expected_ballots = make_jc_ballots([(3, (2, 1))])
        self.assertEqual(jc_contest.ballots, expected_ballots)

    def test_to_jsobj(self):
        jc_ballots = [
            JsonCaseBallot(choices=(1, 2), weight=3),
        ]
        jc_contest = JsonCaseContestInput(ballots=jc_ballots)
        expected = {'_meta': {'id': 0}, 'ballots': ['3 1 2']}
        self.assertEqual(jc_contest.to_jsobj(), expected)


# TODO: move the tests in here into JsonCaseContestInputTest, after
# checking for redundancy, etc.
class JsonCaseContestInputTest2(object):

    def make_ballots(self):
        ballots = [JsonBallot(choices=[1, 2]),
                   JsonBallot(choices=[2], weight=3)]
        return ballots

    def make_contest(self, ballots=None):
        """Return a test contest."""
        if ballots is None:
            ballots = self.make_ballots()
        contest = JsonCaseContestInput(candidate_count=2, ballots=ballots, id_=3, notes="foo")
        return contest

    def test_repr(self):
        contest = self.make_contest()
        self.assertEqual(repr(contest), "<JsonCaseContestInput: [id=3 candidate_count=2] %s>" %
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
                with self.changeAttr(contest2, attr, value):
                    self.assertNotEqual(contest1, contest2)
        self.assertEqual(contest1, contest2)  # sanity check

    def test_save_from_jsobj(self):
        contest = JsonCaseContestInput()
        self.assertEqual(contest.candidate_count, None)
        # Check loading an empty dict.
        # In particular, attributes should not get set to JS_NULL.
        contest.save_from_jsobj({})
        self.assertEqual(contest.candidate_count, None)

        # Check loading metadata.
        # Check that the id needs to be in the meta dict.
        contest.save_from_jsobj({"id": 5})
        self.assertEqual(contest.id, 0)
        contest.save_from_jsobj({"_meta": {"id": 5}})
        self.assertEqual(contest.id, 5)
        # Check explicit None (to which the json module converts Javascript null).
        contest.save_from_jsobj({"_meta": {"id": None}})
        self.assertEqual(contest.id, JS_NULL)

        contest.save_from_jsobj({"candidate_count": 5})
        self.assertEqual(contest.candidate_count, 5)


class JsonRoundResultsTest(UnitCase):

    def test_to_jsobj(self):
        results = JsonRoundResults(totals={1: 2})
        self.assertEqual(results.to_jsobj(), {'totals': {1: 2}})


class JsonTestCaseOutputTest(UnitCase):

    def test_to_jsobj(self):
        rounds = [
            JsonRoundResults(totals={1: 2}),
            JsonRoundResults(totals={3: 4})
        ]
        results = JsonTestCaseOutput(rounds=rounds)
        self.assertEqual(results.to_jsobj(),
                         {'rounds': [{'totals': {1: 2}}, {'totals': {3: 4}}]})
