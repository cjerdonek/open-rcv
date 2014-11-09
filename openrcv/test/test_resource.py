
from openrcv.resource import iter_resource, tracking
from openrcv.utiltest.helpers import skipIfTravis, UnitCase


class IterResource(UnitCase):

    """Tests for iter_resource()."""

    def test(self):
        seq = [1, 2, 3]
        # Confirm the behavior of a list, for comparison with below.
        self.assertEqual(tuple(seq), (1, 2, 3))
        self.assertEqual(tuple(seq), (1, 2, 3))

        resource = iter_resource(seq)
        with resource() as items:
            self.assertEqual(tuple(items), (1, 2, 3))
            # Check that `items` behaves like an iterator object and exhausts
            # (unlike a list as shown above).
            self.assertEqual(tuple(items), ())

        # Confirm that resource() creates a new object each time.
        with resource() as items2:
            pass
        self.assertIsNot(items, items2)


class TrackingTest(UnitCase):

    """Tests for tracking()."""

    def test(self):
        seq = [1, "a"]
        with self.assertRaises(ValueError) as cm:
            with tracking(seq) as items:
                for item in items:
                    int(item)
        # Check the exception text.
        err = cm.exception
        self.assertEqual(str(err), "during item number 2: 'a'")
