
from unittest import TestCase

from openrcv.scripts.main import main_status


class MainTestCase(TestCase):

    def test_main_status__bad_args(self):
        self.assertEqual(main_status(None), 1)
