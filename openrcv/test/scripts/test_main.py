
from unittest import TestCase

from openrcv.scripts.main import main_status


class MainTestCase(TestCase):

    # TODO: add a test for good args.
    def test_main_status__bad_args(self):
        # TODO: check stdout.
        self.assertEqual(main_status(None), 1)
