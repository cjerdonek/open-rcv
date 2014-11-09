
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
