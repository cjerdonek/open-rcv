
from openrcv.models import ContestInfo
from openrcv.utiltest.helpers import UnitCase


class ContestInfoTest(UnitCase):

    def test_get_candidates(self):
        contest = ContestInfo()
        contest.candidates = ["Alice", "Bob", "Carl"]
        self.assertEqual(contest.get_candidates(), range(1, 4))
