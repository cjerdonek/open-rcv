
from textwrap import dedent
import unittest
from unittest import TestCase

from openrcv.counting import count_ballots, get_lowest, get_majority, get_winner
from openrcv.models import TestRoundResults
from openrcv.utils import StringInfo


class TestCounting(TestCase):

    def test_count_ballots(self):
        internal_ballots = dedent("""\
        1 2
        3 1 4
        1 2
        """)
        openable = StringInfo(internal_ballots)
        result = count_ballots(openable, (1, 2, 4))
        self.assertEqual(type(result), TestRoundResults)
        self.assertEqual(result.totals, {1: 3, 2: 2, 4: 0})

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

    def test_get_lowest__no_totals(self):
        """Test passing an empty totals dict."""
        with self.assertRaises(ValueError):
            get_lowest({})

    def test_get_lowest(self):
        cases = [
            ({1: 6, 2: 5}, [2]),
            ({1: 5, 2: 6}, [1]),
            ({1: 1, 2: 6, 3: 4}, [1]),
            # Test ties.
            ({1: 5, 2: 5}, [1, 2]),
            ({1: 5, 2: 6, 3: 5}, [1, 3]),
        ]
        for totals, lowest in cases:
            with self.subTest(totals=totals, lowest=lowest):
                self.assertEqual(get_lowest(totals), lowest)
