
from io import StringIO
from textwrap import dedent
import unittest
from unittest import TestCase

from openrcv.models import ContestInfo
from openrcv.parsing import BLTParser
from openrcv.utils import OpenableString


BLT_STRING = """\
4 2
-3
2 2 0
1 2 4 3 1 0
0
"Jen"
"Alice"
"Steve"
"Bill"
"My Election"
"""


class BLTParserTest(TestCase):

    def parse_string(self, s):
        parser = BLTParser()
        blt = OpenableString(s)
        info = parser.parse(blt)
        return info

    # TODO: test extra blank and non-empty lines at end.
    def test_parse_file(self):
        info = self.parse_string(BLT_STRING)
        # TODO: test the other attributes.
        self.assertEqual(type(info), ContestInfo)
        self.assertEqual(info.ballot_count, 2)
