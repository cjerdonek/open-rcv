
from io import StringIO
from textwrap import dedent
import unittest
from unittest import TestCase

from openrcv.models import ContestInfo
from openrcv.parsing import BLTParser
from openrcv.utils import StringInfo


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

    def parse_blt(self, blt, output_stream=None):
        """
        Arguments:
          blt: a BLT-formatted string.
          output_stream: a StreamInfo object.

        """
        parser = BLTParser(output_stream)
        blt_stream = StringInfo(blt)
        info = parser.parse(blt_stream)
        return info

    # TODO: test passing
    # TODO: test extra blank and non-empty lines at end.
    def test_parse_file(self):
        info = self.parse_blt(BLT_STRING)
        # TODO: test the other attributes.
        self.assertEqual(type(info), ContestInfo)
        self.assertEqual(info.ballot_count, 2)
