
import argparse
import os

from openrcv.scripts.argparse import ArgParser, HelpRequested, UsageException
from openrcv.scripts.argparser import create_argparser, get_log_level, parse_log_level
from openrcv.utiltest.helpers import UnitCase


# TODO: add a test for good args.
class ModuleTestCase(UnitCase):

    def test_parse_log_level(self):
        self.assertEqual(parse_log_level('INFO'), 20)
        self.assertEqual(parse_log_level('DEBUG'), 10)
        self.assertEqual(parse_log_level('35'), 35)
        self.assertEqual(parse_log_level(35), 35)
        with self.assertRaises(ValueError):
            parse_log_level('FOO')

    def test_get_log_level(self):
        parser = create_argparser()
        self.assertEqual(get_log_level(parser, ['input_path', '--log-level', 'DEBUG']), 10)

        # Check what would otherwise be a UsageException.
        with self.assertRaises(UsageException):
            parser.parse_args([])
        self.assertEqual(get_log_level(parser, []), 20)

        # Check an unrecognized string.
        self.assertEqual(get_log_level(parser, ['input_path', '--log-level', 'FOO']), 20)

        # Check not passing the --log-level option.
        self.assertEqual(get_log_level(parser, ['input_path']), 20)

        # Test what happens if the parser doesn't have a --log-level option.
        parser = argparse.ArgumentParser()
        with self.assertRaises(AttributeError):
            self.assertEqual(get_log_level(parser, []), 40)

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
