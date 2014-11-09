
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

    def test_assert_starts_with(self):
        self.assertStartsWith("abc", "a")
        with self.assertRaises(AssertionError) as cm:
            self.assertStartsWith("abc", "x")
        # Check the exception text.
        err = cm.exception
        ending = 'The string """\\\nabc"""\ndoes not start with: \'x\''
        self.assertTrue(str(err).endswith(ending), msg="full error text: %r" % str(err))

    def test_assert_ends_with(self):
        self.assertEndsWith("abc", "c")
        with self.assertRaises(AssertionError) as cm:
            self.assertEndsWith("abc", "x")
        # Check the exception text.
        err = cm.exception
        ending = 'The string """\\\nabc"""\ndoes not end with: \'x\''
        self.assertTrue(str(err).endswith(ending), msg="full error text: %r" % str(err))
