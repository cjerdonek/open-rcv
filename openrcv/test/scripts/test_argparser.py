
import os
from unittest import TestCase

from openrcv.scripts.argparse import ArgParser, HelpRequested, UsageException
from openrcv.scripts.argparser import create_argparser


# TODO: add a test for good args.
# TODO: test --help.
class ModuleTestCase(TestCase):

    def test_create_argparser(self):
        parser = create_argparser()
        with self.assertRaises(UsageException) as cm:
            parser.parse_args([])
        err = cm.exception
        self.assertEqual(err.args, ('the following arguments are required: INPUT_PATH', ))
        parser = err.parser
        self.assertEqual(type(parser), ArgParser)
        self.assertEqual(parser.prog, "rcv")

    def test_create_argparser__help(self):
        parser = create_argparser()
        with self.assertRaises(HelpRequested):
            parser.parse_args(["--help"])
