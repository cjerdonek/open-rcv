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

from openrcv.formats.internal import internal_ballots_resource, parse_internal_ballot, to_internal_ballot
from openrcv.streams import StringResource
from openrcv.utiltest.helpers import UnitCase


class ModuleTest(UnitCase):

    def test_parse_internal_ballot(self):
        cases = [
            ("1 2", (1, (2, ))),
            ("1", (1, ())),
            # Leading and trailing space are okay
            (" 1 2", (1, (2, ))),
            ("1 2 \n", (1, (2, ))),
        ]
        for line, expected in cases:
            with self.subTest(line=line, expected=expected):
                self.assertEqual(parse_internal_ballot(line), expected)

    def test_parse_internal_ballot__non_integer(self):
        with self.assertRaises(ValueError):
            parse_internal_ballot("f 2 \n")


class InternalBallotsResourceTest(UnitCase):

    def test_reading(self):
        resource = StringResource("1 2\n2 3 1\n")
        ballots_resource = internal_ballots_resource(resource)
        with ballots_resource.reading() as stream:
            actual = list(stream)
        expected = [
            (1, (2, )),
            (2, (3, 1)),
        ]
        self.assertEqual(actual, expected)

    def test_reading__error(self):
        resource = StringResource("1 2\n2 b 1\n")
        ballots_resource = internal_ballots_resource(resource)

        with self.assertRaises(ValueError) as cm:
            with ballots_resource.reading() as stream:
                actual = list(stream)
        # Check the exception text.
        err = cm.exception
        self.assertStartsWith(str(err), "last read item from <StringResource:")
        self.assertEndsWith(str(err), "(number=2): '2 b 1\\n'")

    def test_writing(self):
        ballots = [
            (1, (2, )),
            (2, (3, 1)),
        ]
        resource = StringResource()
        ballots_resource = internal_ballots_resource(resource)
        with ballots_resource.writing() as gen:
            for ballot in ballots:
                gen.send(ballot)
        self.assertEqual(resource.contents, "1 2\n2 3 1\n")

class InternalModuleTest(UnitCase):

    def test_to_internal_ballot(self):
        cases = [
            ((1, (2, )), "1 2"),
            ((1, (2, 3)), "1 2 3"),
            ((1, ()), "1"),
        ]
        for ballot, expected in cases:
            with self.subTest(ballot=ballot, expected=expected):
                self.assertEqual(to_internal_ballot(ballot), expected)
