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

from openrcv.utiltest.helpers import UnitCase


class UnitCaseTest(UnitCase):

    def test_change_attr(self):
        class Foo(object):
            def __init__(self):
                self.foo = 1
        obj = Foo()
        self.assertEqual(obj.foo, 1)
        with self.changeAttr(obj, 'foo', 2):
            self.assertEqual(obj.foo, 2)
        self.assertEqual(obj.foo, 1)
        # Check that the attribute is restored when an exception happens.
        try:
            with self.changeAttr(obj, 'foo', 2):
                raise ValueError()
        except ValueError:
            pass
        self.assertEqual(obj.foo, 1)

    def _assertEndsWith(self, err, ending):
        self.assertTrue(str(err).endswith(ending), msg='full error text:\n"""\n%s\n"""' % err)

    def test_assert_starts_with(self):
        self.assertStartsWith("abc", "a")
        with self.assertRaises(AssertionError) as cm:
            self.assertStartsWith("abc", "x")
        # Check the exception text.
        err = cm.exception
        ending = 'string does not start with: \'x\'\n-->"""abc"""'
        self._assertEndsWith(err, ending)

    def test_assert_ends_with(self):
        self.assertEndsWith("abc", "c")
        with self.assertRaises(AssertionError) as cm:
            self.assertEndsWith("abc", "x")
        # Check the exception text.
        err = cm.exception
        ending = 'string does not end with: \'x\'\n-->"""abc"""'
        self._assertEndsWith(err, ending)
