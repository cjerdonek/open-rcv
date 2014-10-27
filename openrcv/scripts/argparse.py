
"""
Extensions to the argparse module.

This module contains generic functionality not specific to OpenRCV.

"""

import argparse
import logging


# The log level that should be used if the parser raises a UsageException.
USAGE_ERROR_LOG_LEVEL = 20  # corresponds to INFO.


# Unfortunately, we need to include this class before defining the
# OPTION_HELP global variable.
# TODO: address the comment above.
class Option(tuple):
    """
    Encapsulates a command option (e.g. "-h" and "--help", or "--run-tests").

    """
    def display(self, glue):
        return glue.join(self)


OPTION_HELP = Option(('-h', '--help'))


def parse_log_level(name_or_number):
    """
    Return the log level number associated to a string name or number.

    """
    try:
        return int(name_or_number)
    except ValueError:
        pass
    # It is a known quirk of getLevelName() that it can be used to convert
    # also from string name to integer.
    level = logging.getLevelName(name_or_number)
    if isinstance(level, str):
        raise argparse.ArgumentTypeError("invalid log level name: %r" % name_or_number)
    return level


class UsageException(Exception):

    """
    Exception class for command-line syntax errors.

    """

    def __init__(self, *args, parser=None):
        super().__init__(*args)
        self.parser = parser


class HelpRequested(UsageException):
    pass


# We create a custom help action to simplify unit testing and make all
# system exits occur through our global main() function.
#
# This class is modeled after Python 3.4's argparse._HelpAction.
class HelpAction(argparse.Action):

    def __init__(self, *args, nargs=0, **kwargs):
        super().__init__(*args, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        # Python 3.4's argparse implementation looks like this--
        #   parser.print_help()
        #   parser.exit()
        raise HelpRequested(parser=parser)


# We subclass ArgumentParser to prevent it from raising SystemExit when
# an argument-parsing error occurs.  We want all error handling to happen
# centrally through our catch-all.
class ArgParser(argparse.ArgumentParser):

    def safe_get_log_level(self, args, error_level=None):
        """
        Get the user-requested log level without raising an exception.

        Returns the log level as an integer.

        Arguments:
          error_level: the log level that should be used if a UsageException occurs.

        """
        if error_level is None:
            error_level = USAGE_ERROR_LOG_LEVEL
        try:
            ns = self.parse_args(args=args)  # Namespace object
        except UsageException:
            level = parse_log_level(error_level)
        else:
            level = ns.log_level
        return level

    # The base class implementation prints the usage string and exits
    # with status code 2.
    def error(self, message):
        """
        Handle an error occurring while parsing command arguments.

        """
        raise UsageException(message, parser=self)
