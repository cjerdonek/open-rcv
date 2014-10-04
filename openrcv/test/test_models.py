
from unittest import TestCase

from openrcv.models import ContestInfo


class ContestInfoTest(TestCase):

    def test_get_candidates(self):
        contest = ContestInfo()
        contest.candidates = ["Alice", "Bob", "Carl"]
        self.assertEqual(contest.get_candidates(), range(1, 4))
