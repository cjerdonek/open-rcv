
from openrcv.resource import tracking
from openrcv.utiltest.helpers import skipIfTravis, UnitCase


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
