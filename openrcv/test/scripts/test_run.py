
from argparse import ArgumentParser
import os
from unittest import TestCase

from openrcv.scripts.argparser import create_argparser
from openrcv.scripts.run import main_status
from openrcv.utiltest.helpers import UnitTestCase

class MainTestCase(UnitTestCase):

    # TODO: add a test for good args.
    def test_main_status__exception(self):
        parser = create_argparser()
        # TODO: check stdout.
        def do_func(args):
            raise Exception("foo")
        with open(os.devnull, "w") as f:
            self.assertEqual(main_status(parser, do_func, ['prog', 'foo'], log_file=f), 1)
