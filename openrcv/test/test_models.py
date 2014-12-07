
from textwrap import dedent

from openrcv import models
from openrcv.models import normalized_ballots, BallotsResource, ContestInput
from openrcv import streams
from openrcv.streams import ListResource
from openrcv.utils import StringInfo
from openrcv.utiltest.helpers import UnitCase


class ModuleTest(UnitCase):

    def test_normalized_ballots(self):
        # This test case simultaneously checks all of (1) "compressing" (by
        # weight), (2) lexicographically ordering by choice (and not
        # by weight), and (3) ballots with no choices (aka undervotes).
        lines = dedent("""\
            1 2
            1
            1 3
            2
            4 1
            1 2
            """).splitlines(keepends=True)
        normalized = normalized_ballots(lines)
        # Check that it returns a generator iterator and not a concrete
        # list/tuple/etc.
        self.assertEqual(type(normalized), type((x for x in ())))
        self.assertEqual(list(normalized), [(3, ()), (4, (1,)), (2, (2,)), (1, (3,))])


class BallotsResourceTest(UnitCase):

    def make_ballots_resource(self):
        ballots = [(2, (1, 3)), (1, (4, 2))]
        resource = ListResource(ballots)
        ballots_resource = BallotsResource(resource)
        return ballots_resource

    def test_repr(self):
        resource = self.make_ballots_resource()
        self.assertStartsWith(repr(resource),
                    "<BallotsResource: [resource=<ListResource: [")

    def test_count_ballots(self):
        resource = self.make_ballots_resource()
        count = resource.count_ballots()
        self.assertEqual(count, 3)

    def test_reading(self):
        resource = self.make_ballots_resource()
        with resource.reading() as ballots:
            ballots = list(ballots)
        self.assertEqual(ballots, [(2, (1, 3)), (1, (4, 2))])

    def test_writing(self):
        resource = self.make_ballots_resource()
        with resource.writing() as target:
            target.send((1, (2, 3)))
        with resource.reading() as ballots:
            ballots = list(ballots)
        self.assertEqual(ballots, [(1, (2, 3))])


class ContestInputTest(UnitCase):

    def test_init__defaults(self):
        contest = ContestInput()
        self.assertEqual(contest.candidates, [])
        self.assertEqual(contest.id, 0)
        self.assertEqual(contest.name, None)
        self.assertEqual(contest.notes, None)
        self.assertEqual(contest.seat_count, 1)

        # Check default ballots resource.
        resource = contest.ballots_resource
        self.assertEqual(type(resource), streams.NullStreamResource)
        self.assertEqual(resource.count(), 0)
        with self.assertRaises(TypeError):
            resource.writing()

    def test_get_candidates(self):
        contest = ContestInput()
        contest.candidates = ["Alice", "Bob", "Carl"]
        self.assertEqual(contest.get_candidates(), range(1, 4))
