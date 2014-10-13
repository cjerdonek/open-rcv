
from unittest import TestCase
from unittest.mock import patch

from openrcv.datagen import gen_random_list, gen_random_ballot_list


class ModuleTest(TestCase):

    def make_randint(self, values):
        values = iter(values)
        def randint(*args):
            try:
                return next(values)
            except StopIteration:  # pragma: no cover
                raise Exception("to fix this, pass in more values for your test")
        return randint

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
                randint = self.make_randint(randint_vals)
                with patch('random.randint', randint):
                    self.assertEqual(gen_random_list(*args), expected)

    def test_gen_random_ballot_list(self):
        cases = (
            # args=(choices, ballot_count, max_length=None),
            #   randint_vals, expected_choices
            (([1, 2], 2), [0, 2, 1, 2], ((1, ), (2, ))),
        )
        for args, randint_vals, expected in cases:
            with self.subTest(args=args, expected=expected, randint_vals=randint_vals):
                randint = self.make_randint(randint_vals)
                with patch('random.randint', randint):
                    ballots = gen_random_ballot_list(*args)
                    actual = tuple((b.choices for b in ballots))
                    self.assertEqual(actual, expected)
