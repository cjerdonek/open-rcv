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

"""
Tests of jsonlib.

"""

from openrcv.jsonlib import from_jsobj, Attribute, JsonableMixin, JS_NULL
from openrcv.utiltest.helpers import UnitCase


class JsonSample(JsonableMixin):

    data_attrs = (Attribute('bar'),
                  Attribute('foo'))

    def __init__(self, bar=None, foo=None):
        self.bar = bar
        self.foo = foo

    def repr_info(self):
        return "bar=%r foo=%r" % (self.bar, self.foo)


class ComplexJsonSample(JsonableMixin):

    data_attrs = (Attribute('simple', JsonSample), )

    def __init__(self, simple=None):
        self.simple = simple

    def repr_info(self):
        return "simple=%r" % self.simple


class ModuleTest(UnitCase):

    def test_from_jsobj(self):
        self.assertEqual(from_jsobj(None), JS_NULL)

    def test_from_jsobj__with_cls(self):
        expected_sample = JsonSample(foo="fooval")
        self.assertEqual(from_jsobj({'foo': 'fooval'}, cls=JsonSample), expected_sample)

    def test_from_jsobj__with_complex_attr(self):
        """
        Test a serialized JSON object with an attribute that is also a
        JSON object.

        """
        simple = JsonSample(foo="fooval")
        expected_sample = ComplexJsonSample(simple=simple)
        self.assertEqual(from_jsobj({'simple': {'foo': 'fooval'}}, cls=ComplexJsonSample), expected_sample)


class JsonableMixinTest(UnitCase):

    def test_eq(self):
        sample1 = JsonSample()
        sample2 = JsonSample()
        self.assertEqual(sample1, sample2)

    def test_eq__wrong_type(self):
        sample = JsonSample()
        self.assertNotEqual(sample, "abc")

    def test_eq__missing_attribute(self):
        """
        Check if the objects don't have one of the attributes set.

        """
        sample1 = JsonSample()
        sample2 = JsonSample()
        sample1.foo = "abc"
        self.assertNotEqual(sample1, sample2)
        sample1 = JsonSample()
        sample2.foo = "abc"
        self.assertNotEqual(sample1, sample2)
        sample1.foo = "abc"
        self.assertEqual(sample1, sample2)

    def test_assert_equal(self):
        sample1 = JsonSample()
        sample2 = JsonSample()
        sample1.assert_equal(sample2)
        sample1.foo = "abc"
        with self.assertRaises(AssertionError) as cm:
            sample1.assert_equal(sample2)
        # Check the exception text.
        err = cm.exception
        self.assertEndsWith(str(err), "'foo' attribute not equal: 'abc' != None")
