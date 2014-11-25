
from copy import copy
from unittest.mock import patch, MagicMock

from openrcv import datagen
from openrcv.datagen import (gen_random_list, add_random_ballots,
                             BallotGenerator, UniqueBallotGenerator, STOP_CHOICE)
from openrcv.utiltest.helpers import UnitCase


class CopyingMock(MagicMock):

    def __call__(self, *args, **kwargs):
        # Shallow copy each arg.
        args = (copy(arg) for arg in args)
        kwargs = {k: copy(v) for k, v in kwargs}
        return super().__call__(*args, **kwargs)


class BallotGeneratorMixin(object):

    def patch_sample_one(self, values):
        # random.sample() returns a k-length list.
        values = ([v, ] for v in values)
        return patch('openrcv.datagen.sample', new_callable=CopyingMock,
                     side_effect=values)


class BallotGeneratorTest(UnitCase, BallotGeneratorMixin):

    def patch_random(self, return_value):
        return patch('openrcv.datagen.random', return_value=return_value)

    def test_init__defaults(self):
        maker = BallotGenerator((1, 2, 3))
        self.assertEqual(maker.choices, set([1, 2, 3]))
        self.assertEqual(maker.max_length, 3)
        self.assertEqual(maker.undervote, 0.1)

    def test_init__defaults(self):
        maker = BallotGenerator((1, 2, 3), max_length=4, undervote=0.5)
        self.assertEqual(maker.choices, set([1, 2, 3]))
        self.assertEqual(maker.max_length, 4)
        self.assertEqual(maker.undervote, 0.5)

    def test_choose(self):
        maker = BallotGenerator((1, 2, 3))
        self.assertEqual(maker.choose([1]), 1)

    def test_make_ballot__undervote(self):
        maker = BallotGenerator((1, 2, 3), undervote=0.5)
        with self.patch_random(0.49):
            self.assertEqual(maker.make_ballot(), [])
        with self.patch_random(0.5):
            ballot = maker.make_ballot()
            self.assertTrue(len(ballot) > 0)
        with self.patch_random(0.51):
            ballot = maker.make_ballot()
            self.assertTrue(len(ballot) > 0)

    def test_make_ballot__undervote__zero(self):
        """Check the zero edge case."""
        # Zero chance of an undervote.
        maker = BallotGenerator((1, 2, 3), undervote=0)
        with self.patch_random(0):
            ballot = maker.make_ballot()
            self.assertTrue(len(ballot) > 0)

    def test_make_ballot(self):
        maker = BallotGenerator((1, 2, 3), undervote=0)
        with self.patch_sample_one((1, 1, STOP_CHOICE)) as mock_sample:
            self.assertEqual(maker.make_ballot(), [1, 1])
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


class UniqueBallotGeneratorTest(UnitCase, BallotGeneratorMixin):

    def test_make_ballot(self):
        maker = UniqueBallotGenerator((1, 2, 3), undervote=0)
        with self.patch_sample_one((1, 2, STOP_CHOICE)) as mock_sample:
            self.assertEqual(maker.make_ballot(), [1, 2])
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


class ModuleTest(UnitCase):

    # TODO: check whether this can be simplified using patch's API.
    def make_randint(self, values):
        values = iter(values)
        def randint(*args):
            try:
                return next(values)
            except StopIteration:  # pragma: no cover
                raise Exception("to fix this, pass in more values for your test")
        return randint

    def patch_randint(self, randint_vals):
        randint = self.make_randint(randint_vals)
        return patch('openrcv.datagen.randint', randint)

    def test_gen_random_list(self):
        # args=(choices, max_length=None), randint_vals, expected
        cases = (
            # Normal case.
            (([1, 2], ), [0, 1], [1, 2]),
            # Check terminating the list early.
            (([1, 2], ), [2], []),
            # Check that duplications are allowed.
            (([1, 2], ), [0, 0], [1, 1]),
            # Check that max_length defaults to the number of choices.
            (([1, 2], ), [0, 0, 0, 0], [1, 1]),
            # Check that max_length is respected.
            (([1, 2], 3), [0, 0, 0, 0], [1, 1, 1]),
        )
        for args, randint_vals, expected in cases:
            with self.subTest(args=args, expected=expected, randint_vals=randint_vals):
                with self.patch_randint(randint_vals):
                    self.assertEqual(gen_random_list(*args), expected)

    def test_add_random_ballots(self):
        cases = (
            # args=(choices, ballot_count, max_length=None),
            #   randint_vals, expected_choices
            (([1, 2], 2), [0, 2, 1, 2], ((1, ), (2, ))),
        )
        for args, randint_vals, expected in cases:
            with self.subTest(args=args, expected=expected, randint_vals=randint_vals):
                with self.patch_randint(randint_vals):
                    ballots = add_random_ballots(*args)
                    actual = tuple((b.choices for b in ballots))
                    self.assertEqual(actual, expected)
