
import unittest
from unittest import TestCase

from openrcv.counting import get_majority, get_winner

class TestCounting(TestCase):

    def test_get_majority(self):
        self.assertEqual(get_majority(1), 1)
        self.assertEqual(get_majority(2), 2)
        self.assertEqual(get_majority(3), 2)
        self.assertEqual(get_majority(4), 3)
        self.assertEqual(get_majority(100), 51)
        self.assertRaises(AssertionError, get_majority, 0)
        self.assertRaises(AssertionError, get_majority, -1)

    def test_get_winner(self):
        self.assertIs(get_winner({1: 5, 2: 5}), None)
        cases = [
            ({1: 6, 2: 5}, 1),
            ({1: 5, 2: 6}, 2),
            ({1: 1, 2: 6, 3: 4}, 2),
        ]
        for totals, winner in cases:
            with self.subTest(totals=totals, winner=winner):
                self.assertEqual(get_winner(totals), winner)
    