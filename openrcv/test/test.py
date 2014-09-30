
from io import StringIO
from textwrap import dedent
import unittest
from unittest import TestCase

from openrcv.main import BLTParser, ContestInfo


def run_tests():
    # TODO: discover all tests.
    unittest.main(module=__name__)


class MainTestCase(TestCase):

    def test(self):
        self.assertEqual(1, 1)


class BLTParserTest(TestCase):

    def test_parse_file(self):
        # TODO: simplify this string.
        blt = dedent("""\
        4 2
        -3
        2 2 0
        1 2 4 3 1 0
        2 1 3 4 0
        3 1 0
        2 3 4 0
        4 4 1 3 0
        0
        "Jen"
        "Alice"
        "Steve"
        "Bill"
        "My Election"
        """)
        parser = BLTParser()

        with StringIO(blt) as f:
            info = parser.parse_file(f)
        # TODO: test the other attributes.
        self.assertEqual(type(info), ContestInfo)
