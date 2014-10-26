
"""
Extensions to the argparse module.

"""

import argparse


class Option(tuple):
    """
    Encapsulates a command option (e.g. "-h" and "--help", or "--run-tests").

    """
    def display(self, glue):
        return glue.join(self)


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

    # The base class implementation prints the usage string and exits
    # with status code 2.
    def error(self, message):
        """
        Handle an error occurring while parsing command arguments.

        """
        raise UsageException(message, parser=self)
