
from openrcv.resource import tracked
from openrcv.utiltest.helpers import skipIfTravis, UnitCase


class TrackedTest(UnitCase):

    """Tests for tracked()."""

    def test(self):
        seq = [1, "a"]
        with self.assertRaises(ValueError) as cm:
            with tracked(seq) as items:
                for item in items:
                    int(item)
        # Check the exception text.
        err = cm.exception
        self.assertEqual(str(err), "during item number 2: 'a'")
