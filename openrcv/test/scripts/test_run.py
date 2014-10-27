
from argparse import ArgumentParser
import os

from openrcv.scripts.rcv import create_argparser
from openrcv.scripts.run import main_status
from openrcv.utiltest.helpers import UnitCase

class MainTestCase(UnitCase):

    # TODO: add a test for good args.
    def test_main_status__exception(self):
        parser = create_argparser()
        # TODO: check stdout.
        def do_func(args):
            raise Exception("foo")
        with open(os.devnull, "w") as f:
            self.assertEqual(main_status(parser, [], log_file=f), 2)
