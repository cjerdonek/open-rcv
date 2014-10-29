
from unittest.mock import patch

from openrcv import datagen
from openrcv.datagen import (gen_random_list, gen_random_ballot_list,
                             BallotGenerator, STOP_CHOICE)
from openrcv.utiltest.helpers import UnitCase


# TODO: also test UniqueBallotGenerator.
class BallotGeneratorTests(UnitCase):

    def patch_random(self, return_value):
        return patch('openrcv.datagen.random', return_value=return_value)

    def patch_sample_one(self, values):
        # random.sample() returns a k-length list.
        values = ([v, ] for v in values)
        return patch('openrcv.datagen.sample', side_effect=values)

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

    def test_make_ballot__simple(self):
        """
        Check make_ballot() relative to the return values of random.sample().

        """
        maker = BallotGenerator((1, 2, 3), undervote=0)
        with self.patch_sample_one((1, 1, STOP_CHOICE)):
            self.assertEqual(maker.make_ballot(), [1, 1])


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

    def test_gen_random_ballot_list(self):
        cases = (
            # args=(choices, ballot_count, max_length=None),
            #   randint_vals, expected_choices
            (([1, 2], 2), [0, 2, 1, 2], ((1, ), (2, ))),
        )
        for args, randint_vals, expected in cases:
            with self.subTest(args=args, expected=expected, randint_vals=randint_vals):
                with self.patch_randint(randint_vals):
                    ballots = gen_random_ballot_list(*args)
                    actual = tuple((b.choices for b in ballots))
                    self.assertEqual(actual, expected)
