
import os
from unittest import TestCase

from openrcv.scripts.main import ArgParser, HelpRequested, UsageException
from openrcv.scripts.rcv import run_rcv


# TODO: add a test for good args.
# TODO: test --help.
class ModuleTestCase(TestCase):

    def test_run_rcv(self):
        with self.assertRaises(UsageException) as cm:
            run_rcv(["prog.py"])
        err = cm.exception
        self.assertEqual(err.args, ('the following arguments are required: INPUT_PATH', ))
        parser = err.parser
        self.assertEqual(type(parser), ArgParser)
        self.assertEqual(parser.prog, "rcv")

    def test_run_rcv__help(self):
        with self.assertRaises(HelpRequested):
            run_rcv(["prog.py", "--help"])
