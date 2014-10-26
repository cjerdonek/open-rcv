
import os
from unittest import TestCase

from openrcv.scripts.run import main_status


class MainTestCase(TestCase):

    # TODO: add a test for good args.
    def test_main_status__exception(self):
        # TODO: check stdout.
        def do_func(args):
            raise Exception("foo")
        with open(os.devnull, "w") as f:
            self.assertEqual(main_status(do_func, None, log_file=f), 1)
