#
# Copyright (c) 2014 Chris Jerdonek. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

"""Extensions to the argparse module.

This module contains generic functionality not specific to OpenRCV.
"""

import argparse2 as argparse
import logging


class Option(object):

    """Encapsulates a command option.

    For example: "-h" and "--help", or "--run-tests".
    """

    def __init__(self, flags, metavar=None):
        self.flags = flags
        self.metavar = metavar

    def __getitem__(self, i):
        return self.flags[i]

    def display(self, glue):
        return glue.join(self.flags)


def parse_log_level(name_or_number):
    """Return the log level number associated to a string name or number."""
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

    """Exception class for command-line syntax errors."""

    def __init__(self, *args, parser=None):
        super().__init__(*args)
        self.parser = parser


class HelpRequested(UsageException):
    pass


# We create a custom help action to prevent the help command from raising
# SystemExit.  This allows all system exits to happen centrally through
# a main() catch-all.  This also simplifies unit testing.
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
# an argument-parsing error occurs.  This allows all error handling to happen
# centrally through a main() catch-all.
class ArgParser(argparse.ArgumentParser):

    # The base class implementation prints the usage string and exits
    # with status code 2.
    def error(self, message):
        """Handle an error occurring while parsing command arguments."""
        raise UsageException(message, parser=self)
