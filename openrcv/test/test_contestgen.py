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

from contextlib import contextmanager
from copy import copy as copy_
import unittest
from unittest.mock import patch, MagicMock

from openrcv import models, streams
from openrcv.contestgen import (make_standard_candidate_names, BallotGenerator,
                                UniqueBallotGenerator, STOP_CHOICE)
from openrcv.utiltest.helpers import UnitCase


@contextmanager
def _temp_ballots_resource():
    resource = streams.ListResource()
    ballots_resource = models.BallotsResource(resource)
    yield ballots_resource


class ModuleTest(UnitCase):

    def test_make_standard_candidate_names(self):
        names = make_standard_candidate_names(2)
        self.assertEqual(names, ['Ann', 'Bob'])
        names = make_standard_candidate_names(4, names=['A', 'B'])
        self.assertEqual(names, ['A', 'B', 'Person 3', 'Person 4'])


class CopyingMock(MagicMock):

    def __call__(self, *args, **kwargs):
        # Shallow copy each arg.
        args = (copy_(arg) for arg in args)
        kwargs = {k: copy_(v) for k, v in kwargs}
        return super().__call__(*args, **kwargs)


class BallotGeneratorMixin(object):

    def patch_sample_one(self, values):
        # random.sample() returns a k-length list.
        values = ([v, ] for v in values)
        return patch('openrcv.contestgen.sample', new_callable=CopyingMock,
                     side_effect=values)


class BallotGeneratorTest(UnitCase, BallotGeneratorMixin):

    def patch_random(self, return_value):
        return patch('openrcv.contestgen.random', return_value=return_value)

    def test_init__defaults(self):
        chooser = BallotGenerator((1, 2, 3))
        self.assertEqual(chooser.choices, set([1, 2, 3]))
        self.assertEqual(chooser.max_length, 3)
        self.assertEqual(chooser.undervote, 0.1)

    def test_init__defaults(self):
        chooser = BallotGenerator((1, 2, 3), max_length=4, undervote=0.5)
        self.assertEqual(chooser.choices, set([1, 2, 3]))
        self.assertEqual(chooser.max_length, 4)
        self.assertEqual(chooser.undervote, 0.5)

    def test_choose(self):
        chooser = BallotGenerator((1, 2, 3))
        self.assertEqual(chooser.choose([1]), 1)

    def test_make_choices__undervote(self):
        chooser = BallotGenerator((1, 2, 3), undervote=0.5)
        with self.patch_random(0.49):
            self.assertEqual(chooser.make_choices(), [])
        with self.patch_random(0.5):
            ballot = chooser.make_choices()
            self.assertTrue(len(ballot) > 0)
        with self.patch_random(0.51):
            ballot = chooser.make_choices()
            self.assertTrue(len(ballot) > 0)

    def test_make_choices__undervote__zero(self):
        """Check the zero edge case."""
        # Zero chance of an undervote.
        chooser = BallotGenerator((1, 2, 3), undervote=0)
        with self.patch_random(0):
            ballot = chooser.make_choices()
            self.assertTrue(len(ballot) > 0)

    def test_make_choices(self):
        chooser = BallotGenerator((1, 2, 3), undervote=0)
        with self.patch_sample_one((1, 1, STOP_CHOICE)) as mock_sample:
            self.assertEqual(chooser.make_choices(), [1, 1])
            self.assertEqual(mock_sample.call_count, 3)
            # Also check that random.sample() is being called with the
            # right args each time.
            expecteds = [
                # The first call does not include STOP_CHOICE to ensure
                # that the ballot is not an undervote.
                ({1, 2, 3}, 1),
                ({1, 2, 3, STOP_CHOICE}, 1),
                ({1, 2, 3, STOP_CHOICE}, 1),
            ]
            for i, (actual, expected) in enumerate(zip(mock_sample.call_args_list, expecteds)):
                with self.subTest(index=i):
                    # The 0-th element is the positional args.
                    self.assertEqual(actual[0], expected)

    def test_add_random_ballots(self):
        chooser = BallotGenerator((1, 2, 3), undervote=0)
        with _temp_ballots_resource() as ballots_resource:
            chooser.add_random_ballots(ballots_resource, count=12)
            self.assertEqual(ballots_resource.count(), 12)


class UniqueBallotGeneratorTest(UnitCase, BallotGeneratorMixin):

    def test_make_choices(self):
        chooser = UniqueBallotGenerator((1, 2, 3), undervote=0)
        with self.patch_sample_one((1, 2, STOP_CHOICE)) as mock_sample:
            self.assertEqual(chooser.make_choices(), [1, 2])
            self.assertEqual(mock_sample.call_count, 3)
            # Also check that random.sample() is being called with the
            # right args each time (which is where UniqueBallotGenerator
            # differs from BallotGenerator).
            expecteds = [
                ({1, 2, 3}, 1),
                # Since this is the unique ballot generator, each call does
                # not contain any of the previously chosen choices.
                ({2, 3, STOP_CHOICE}, 1),
                ({3, STOP_CHOICE}, 1),
            ]
            for i, (actual, expected) in enumerate(zip(mock_sample.call_args_list, expecteds)):
                with self.subTest(index=i):
                    # The 0-th element is the positional args.
                    self.assertEqual(actual[0], expected)
