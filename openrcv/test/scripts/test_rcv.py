
from argparse import ArgumentParser
import os

from openrcv.scripts.argparse import ArgParser, HelpRequested, UsageException
from openrcv.scripts.rcv import create_argparser
from openrcv.utiltest.helpers import skipIfTravis, UnitCase


# Sample valid command syntax.
VALID_COMMAND = ['count', 'path.py']


class SafeGetLogLevelTestCase(UnitCase):

    """Test the ArgumentParser's safe_get_log_level() method."""

    def _get_valid_args(self, level):
        args = ['--log-level', level]
        # We need to include valid command syntax in order to avoid a
        # UsageException.
        args.extend(VALID_COMMAND)
        return args

    def call_safe_get_log_level(self, level):
        parser = create_argparser()
        args = self._get_valid_args(level)
        return parser.safe_get_log_level(args, error_level=42)

    def call_safe_get_log_level_default_error_level(self, level):
        parser = create_argparser()
        args = self._get_valid_args(level)
        return parser.safe_get_log_level(args)

    def test_safe_get_log_level__valid_string(self):
        actual = self.call_safe_get_log_level('DEBUG')
        self.assertEqual(actual, 10)

    def test_safe_get_log_level__int(self):
        actual = self.call_safe_get_log_level('17')
        self.assertEqual(actual, 17)

    def test_safe_get_log_level__invalid_value(self):
        """Check an invalid log level string."""
        actual = self.call_safe_get_log_level('FOO')
        self.assertEqual(actual, 42)

    def test_safe_get_log_level__default_error_level(self):
        """Check the default error level."""
        # We pass an invalid log-level value to trigger the error.
        actual = self.call_safe_get_log_level_default_error_level('FOO')
        self.assertEqual(actual, 20)  # 20 means INFO

    def test_safe_get_log_level__no_level(self):
        """Check not passing the --log-level option."""
        parser = create_argparser()
        actual = parser.safe_get_log_level(VALID_COMMAND, error_level=42)
        self.assertEqual(actual, 20)

    def test_safe_get_log_level__invalid_command(self):
        """Check that passing invalid command syntax returns the error level."""
        parser = create_argparser()
        with self.assertRaises(UsageException):
            parser.parse_args([])
        actual = parser.safe_get_log_level([], error_level=42)
        self.assertEqual(actual, 42)

    def test_safe_get_log_level__unsupported_parser(self):
        """Check using an ArgumentParser that doesn't support --log-level."""
        parser = ArgumentParser()
        with self.assertRaises(AttributeError):
            actual = parser.safe_get_log_level([], error_level=42)


class ArgumentParserTestCase(UnitCase):

    """Test the ArgumentParser object returned by create_argparser()."""

    def test_create_argparser(self):
        parser = create_argparser()
        with self.assertRaises(UsageException) as cm:
            parser.parse_args([])
        err = cm.exception
        self.assertEqual(err.args, ('the following arguments are required: COMMAND', ))
        parser = err.parser
        self.assertEqual(type(parser), ArgParser)
        self.assertEqual(parser.prog, "rcv")

    def test_create_argparser__help(self):
        parser = create_argparser()
        with self.assertRaises(HelpRequested):
            parser.parse_args(["--help"])

    # Convenience function so we don't need to pass an input path.
    def parse_args(self, pre_args):
        parser = create_argparser()
        args = pre_args + VALID_COMMAND
        return parser.parse_args(args)

    def parse_log_level(self, args):
        ns = self.parse_args(args)
        return ns.log_level

    def test_log_level(self):
        # Test the default.
        self.assertEqual(self.parse_log_level([]), 20)
        # Test a number.
        self.assertEqual(self.parse_log_level(['--log-level', '15']), 15)
        # Test a string.
        self.assertEqual(self.parse_log_level(['--log-level', 'DEBUG']), 10)
        # Test missing value.
        with self.assertRaises(UsageException):
            self.parse_log_level(['--log-level'])
        # Test invalid value.
        with self.assertRaises(UsageException):
            self.parse_log_level(['--log-level', 'foo'])
