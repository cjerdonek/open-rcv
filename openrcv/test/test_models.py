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

from openrcv import models
from openrcv.models import normalize_ballots, normalize_ballots_to, BallotsResource, ContestInput
from openrcv import streams
from openrcv.streams import ListResource
from openrcv.utils import StringInfo
from openrcv.utiltest.helpers import UnitCase


class NormalizeBallotsToTest(UnitCase):

    """Tests of normalize_ballots_to()."""

    def test(self):
        """
        Simultaneously checks--
        (1) "compressing" (by weight),
        (2) lexicographically ordering by choice (and not by weight), and
        (3) ballots with no choices (aka undervotes).
        """
        ballots = [
            (1, (2, )),
            (1, ()),
            (1, (3, )),
            (2, ()),
            (4, (1, )),
            (1, (2, )),
        ]
        source = ListResource(ballots)
        target = ListResource()
        normalize_ballots_to(source, target)
        with target.reading() as gen:
            normalized = list(gen)
        self.assertEqual(normalized, [(3, ()), (4, (1,)), (2, (2,)), (1, (3,))])


class NormalizeBallotTest(UnitCase):

    """Tests of normalize_ballots()."""

    def test(self):
        ballots = [
            (1, (2, )),
            (1, ()),
            (1, (3, )),
            (2, ()),
            (4, (1, )),
            (1, (2, )),
        ]
        resource = ListResource(ballots)
        ballots_resource = BallotsResource(resource)
        normalize_ballots(ballots_resource)
        with ballots_resource.reading() as gen:
            normalized = list(gen)
        expected = [(3, ()), (4, (1,)), (2, (2,)), (1, (3,))]
        self.assertEqual(normalized, expected)
        # Check that the original resource was normalized.
        with resource.reading() as gen:
            original_ballots = list(gen)
        # TODO
        #self.assertEqual(original_ballots, expected)
        # TODO: check that the original backing list was also normalized.


class BallotsResourceTest(UnitCase):

    def make_ballots_resource(self):
        # We deliberately choose a list of ballots complicated enough to
        # have better tests for (1) count_ballots() (by including weights
        # greater than 1), and (2) normalize() (by listing the ballots out
        # out of order and including multiple ballots with the same choice).
        ballots = [
            (1, (3, )),
            (1, ()),
            (1, (2, )),
            (2, ()),
        ]
        resource = ListResource(ballots)
        ballots_resource = BallotsResource(resource)
        return ballots_resource

    def test_repr(self):
        resource = self.make_ballots_resource()
        self.assertStartsWith(repr(resource), "<BallotsResource: [resource=<ListResource: [")

    def test_count_ballots(self):
        resource = self.make_ballots_resource()
        count = resource.count_ballots()
        self.assertEqual(count, 5)

    def test_normalize(self):
        resource = self.make_ballots_resource()
        resource.normalize()
        with resource.reading() as ballots:
            ballots = list(ballots)
        self.assertEqual(ballots, [(3, ()), (1, (2,)), (1, (3,))])

    def test_reading(self):
        resource = self.make_ballots_resource()
        with resource.reading() as ballots:
            ballots = list(ballots)
        self.assertEqual(ballots, [(1, (3,)), (1, ()), (1, (2,)), (2, ())])

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
