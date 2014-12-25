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


class _SampleJsonable(JsonableMixin):

    data_attrs = (Attribute('bar'),
                  # We include one use of the keyword argument.
                  Attribute('foo', keyword='fizz'))


class _SampleParentJsonable(JsonableMixin):

    """A sample nested jsonable class.

    In other words, one of the attributes is itself a jsonable.
    """

    data_attrs = (Attribute('simple', _SampleJsonable), )

    def __init__(self, simple=None):
        self.simple = simple

    def repr_info(self):
        return "simple=%r" % self.simple


class ModuleTest(UnitCase):

    def test_from_jsobj(self):
        self.assertEqual(from_jsobj(None), JS_NULL)

    def test_from_jsobj__with_cls(self):
        expected_sample = _SampleJsonable(bar="bar_value")
        self.assertEqual(from_jsobj({'bar': 'bar_value'}, cls=_SampleJsonable), expected_sample)

    def test_from_jsobj__with_complex_attr(self):
        """
        Test a serialized JSON object with an attribute that is also a
        JSON object.

        """
        child = _SampleJsonable(bar="bar_value")
        expected_sample = _SampleParentJsonable(simple=child)
        self.assertEqual(from_jsobj({'simple': {'bar': 'bar_value'}}, cls=_SampleParentJsonable), expected_sample)


class JsonableMixinTest(UnitCase):

    def test_init(self):
        j = _SampleJsonable(bar=3, fizz=4)
        self.assertEqual(j.bar, 3)
        self.assertEqual(j.foo, 4)

    def test_init__default(self):
        j = _SampleJsonable(bar=3)
        self.assertEqual(j.foo, None)

    def test_init__bad_kwarg(self):
        with self.assertRaises(TypeError) as cm:
            _SampleJsonable(bad=3, badder=4, bar=5)
        err = cm.exception
        # This checks that both bad keywords are shown.
        expected = "invalid keyword argument(s): 'bad', 'badder' (valid are: bar, fizz)"
        self.assertEqual(str(err), expected)

    def test_repr_info(self):
        j = _SampleJsonable(fizz=3)
        self.assertEqual(j.repr_info(), "bar=None foo=3")

    def test_eq(self):
        sample1 = _SampleJsonable()
        sample2 = _SampleJsonable()
        self.assertEqual(sample1, sample2)

    def test_eq__wrong_type(self):
        sample = _SampleJsonable()
        self.assertNotEqual(sample, "abc")

    def test_eq__missing_attribute(self):
        """
        Check if the objects don't have one of the attributes set.

        """
        sample1 = _SampleJsonable()
        sample2 = _SampleJsonable()
        sample1.foo = "abc"
        self.assertNotEqual(sample1, sample2)
        sample1 = _SampleJsonable()
        sample2.foo = "abc"
        self.assertNotEqual(sample1, sample2)
        sample1.foo = "abc"
        self.assertEqual(sample1, sample2)

    def test_assert_equal(self):
        sample1 = _SampleJsonable()
        sample2 = _SampleJsonable()
        sample1.assert_equal(sample2)
        sample1.foo = "abc"
        with self.assertRaises(AssertionError) as cm:
            sample1.assert_equal(sample2)
        # Check the exception text.
        err = cm.exception
        self.assertEndsWith(str(err), "'foo' attribute not equal: 'abc' != None")
