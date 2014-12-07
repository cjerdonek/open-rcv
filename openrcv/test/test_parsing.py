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

from io import StringIO
import os
from textwrap import dedent
import unittest

from openrcv.models import ContestInput
from openrcv.parsing import BLTParser, ParsingError
from openrcv.utils import PathInfo, StringInfo
from openrcv.utiltest.helpers import UnitCase


class BLTParserTest(UnitCase):

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

    def make_parser(self, blt_string, output_info=None):
        parser = BLTParser(output_info)
        blt_stream = StringInfo(blt_string)
        return parser, blt_stream

    def parse_blt(self, blt_string, output_info=None):
        """
        Arguments:
          blt_str: a BLT-formatted string.
          output_info: a StreamInfo object.

        """
        parser, blt_stream = self.make_parser(blt_string, output_info=output_info)
        info = parser.parse(blt_stream)
        return info

    def test_init(self):
        output_info = StringInfo()
        parser = BLTParser(output_info)
        self.assertIs(parser.output_info, output_info)

    def test_init__no_args(self):
        parser = BLTParser()
        output_info = parser.output_info
        self.assertIs(type(output_info), PathInfo)
        self.assertEqual(output_info.path, os.devnull)

    # TODO: test passing
    # TODO: test extra blank and non-empty lines at end.
    def test_parse(self):
        """Test passing an output StreamInfo object."""
        output_info = StringInfo()
        info = self.parse_blt(self.BLT_STRING, output_info=output_info)
        # TODO: test the other attributes.
        self.assertEqual(type(info), ContestInput)
        self.assertEqual(info.name, '"My Election"')
        self.assertEqual(info.ballot_count, 2)
        self.assertEqual(output_info.value, "2 2\n1 2 4 3 1\n")

    def test_parse__terminal_empty_lines(self):
        """Test a BLT string with empty lines at the end."""
        info = self.parse_blt(self.BLT_STRING + "\n\n")
        self.assertEqual(type(info), ContestInput)
        self.assertEqual(info.name, '"My Election"')

    def test_parse__terminal_non_empty_lines(self):
        """Test a BLT string with non-empty lines at the end."""
        suffixes = [
            "foo",
            "foo\n",
            "\nfoo",
            "\nfoo\n"
        ]
        for suffix in suffixes:
            with self.subTest(suffix=suffix):
                # TODO: check the line number.
                with self.assertRaises(ParsingError):
                    info = self.parse_blt(self.BLT_STRING + suffix)

    def test_parse__no_output_info(self):
        """Test passing no output StreamInfo object."""
        info = self.parse_blt(self.BLT_STRING)
        # TODO: test the other attributes.
        self.assertEqual(type(info), ContestInput)
        self.assertEqual(info.ballot_count, 2)
