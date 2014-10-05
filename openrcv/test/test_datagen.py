
from unittest import TestCase
from unittest.mock import patch

from openrcv.datagen import gen_random_list


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
        cases = (
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
