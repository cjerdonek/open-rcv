
from argparse import ArgumentParser
import os

from openrcv.scripts.rcv import create_argparser, RcvArgumentParser
from openrcv.scripts.run import non_exiting_main
from openrcv.utils import StringInfo
from openrcv.utiltest.helpers import UnitCase


def test_command(ns, stdout=None):
    return "foo"


# We use a minimal ArgumentParser for our tests.
def make_argparser():
    parser = RcvArgumentParser()
    parser.set_defaults(run_command=test_command)
    parser.set_defaults(log_level=20)  # level name INFO
    return parser


# TODO: add more tests for this.
class NonExitingMainTests(UnitCase):

    """Tests non_exiting_main()."""

    def test_output(self):
        """Check that output is written to stdout."""
        parser = make_argparser()
        info = StringInfo()
        with info.open("w") as f:
            status = non_exiting_main(parser, [], stdout=f)
        self.assertEqual(info.value, "foo")

    def test_non_exiting_main__exception(self):
        parser = create_argparser()
        # TODO: check stdout.
        def do_func(args):
            raise Exception("foo")
        with open(os.devnull, "w") as f:
            self.assertEqual(non_exiting_main(parser, [], log_file=f), 2)
