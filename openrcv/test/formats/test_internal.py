
from openrcv.formats.internal import to_internal_ballot
from openrcv.utiltest.helpers import UnitCase


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
