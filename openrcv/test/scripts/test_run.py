
from argparse import ArgumentParser
import os

from openrcv.scripts.rcv import create_argparser, RcvArgumentParser
from openrcv.scripts.run import non_exiting_main
from openrcv.utils import StringInfo
from openrcv.utiltest.helpers import UnitCase


def foo_command(ns, stdout=None):
    return "foo"


# We use a minimal ArgumentParser for our tests.
def make_argparser(command=None):
    parser = RcvArgumentParser()
    if command is not None:
        parser.set_defaults(run_command=command)
    parser.set_defaults(log_level=20)  # level name INFO
    return parser


# TODO: add more tests for this.
class NonExitingMainTests(UnitCase):

    """Tests non_exiting_main()."""

    def test_good_command(self):
        """Check that output is written to stdout."""
        parser = make_argparser(foo_command)
        info = StringInfo()
        with info.open("w") as f:
            status = non_exiting_main(parser, [], stdout=f)
        self.assertEqual(status, 0)
        self.assertEqual(info.value, "foo")

    def test_empty_args(self):
        """Check that empty args triggers help."""
        parser = make_argparser()
        info = StringInfo()
        with info.open("w") as f:
            status = non_exiting_main(parser, [], stdout=f)
        self.assertEqual(status, 0)
        # Confirm that help is displayed.
        self.assertStartsWith(info.value, "usage: ")

    def test_non_exiting_main__exception(self):
        def raise_exc(*args, **kwargs):
            raise ValueError("foo")
        parser = make_argparser(command=raise_exc)
        # TODO: check stdout.
        with self.assertRaises(ValueError):
            non_exiting_main(parser, ['foo'])
