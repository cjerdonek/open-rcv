
"""
Supports the "rcv" command-line command (aka console_script).

"""

import argparse
from argparse import RawDescriptionHelpFormatter
import logging
from textwrap import dedent

from openrcv.scripts.argparse import (parse_log_level, ArgParser, HelpAction,
                                      Option, UsageException)
from openrcv.scripts import commands
from openrcv.scripts.run import main as _main


# For better compatibility with Python 3.4.1, we rely more on the number
# than the string representation.  This is because in Python 3.4 (but
# fixedin 3.4.2), you could not use logging.getLevelName() to get the
# level number for a level name.  Travis CI was also uing 3.4.1 as of
# Oct. 26, 2014.
#  For more info, see:
#    http://bugs.python.org/issue22386"
LOG_LEVEL_DEFAULT = 20  # corresponds to INFO.
LOG_LEVEL_DEFAULT_NAME = logging.getLevelName(LOG_LEVEL_DEFAULT)
# The log level that should be used if the ArgumentParser raises a UsageException.
LOG_LEVEL_USAGE_ERROR = 20  # corresponds to INFO.

OPTION_HELP = Option(('-h', '--help'))

DESCRIPTION = """\
OpenRCV command-line tool.

"""


def main():
    parser = create_argparser()
    _main(parser)


def help_command():
    pass

def add_command(subparsers, add_func):
    parser, command_func = add_func(subparsers)
    # The RawDescriptionHelpFormatter preserves line breaks in the
    # description and epilog strings.
    parser.formatter_class = RawDescriptionHelpFormatter
    parser.set_defaults(run_command=command_func)


def add_command_count(subparsers):
    parser = subparsers.add_parser('count', help='Tally one or more contests.',
        description='Tally the contests specified by the contests file at INPUT_PATH.')
    parser.add_argument('input_path', metavar='INPUT_PATH',
        help=("path to a contests configuration file. Supported file "
              "formats are JSON (*.json) and YAML (*.yaml or *.yml)."))
    return parser, commands.count


def add_command_randcontest(subparsers):
    help = 'Create a random sample contest.'
    desc = dedent("""\
    Create a random sample contest.

    If writing to files, writes the file paths to stdout.
    """)
    parser = subparsers.add_parser('randcontest', help=help, description=desc)
    parser.add_argument('-b', '--ballots', metavar='N', type=int,
                       help='number of ballots.')
    parser.add_argument('-c', '--candidates', metavar='N', type=int, default=6,
                        help='number of candidates.')
    parser.add_argument('-o', '--output-dir', metavar='OUTPUT_DIR',
        help=("the directory to which to write any output files, or "
              "write to stdout if the empty string.  Defaults to the "
              "empty string."))
    # TODO: add output_path.
    # TODO: add output_format (default to BLT for now).
    return parser, commands.rand_contest


# TODO: unit-test print_help().
def create_argparser(prog="rcv"):
    """
    Return an ArgumentParser object.

    """
    parser = RcvArgumentParser(prog=prog, description=DESCRIPTION, add_help=False,
                               formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('--log-level', metavar='LEVEL',
        default=LOG_LEVEL_DEFAULT, type=parse_log_level,
        help=("logging level name or number (e.g. CRITICAL, ERROR, WARNING, "
              "INFO, DEBUG, 10, 20, etc). "
              "Defaults to %s." % LOG_LEVEL_DEFAULT_NAME))
    # The add_argument() call for help is modeled after how argparse does it.
    parser.add_argument(*OPTION_HELP, action=HelpAction,
        help='show this help message and exit.')

    desc = dedent("""\
    Available commands are below.

    For help with a particular command, pass %s after the command name.
    For example, `%s count %s`.
    """ % (OPTION_HELP.display(' or '), prog, OPTION_HELP[0]))
    subparsers = parser.add_subparsers(title='commands', metavar='COMMAND',
                                       description=desc)
    subparsers.formatter_class = RawDescriptionHelpFormatter

    # Default to running help.
    #parser.set_defaults(run_command=command_func)

    # TODO: default to help action?
    subparsers.required = True

    add_funcs = (
        add_command_count,
        add_command_randcontest,
    )

    for add_func in add_funcs:
        add_command(subparsers, add_func)

    return parser


class RcvArgumentParser(ArgParser):

    option_help = OPTION_HELP

    def safe_get_log_level(self, args, error_level=None):
        """
        Get the user-requested log level without raising an exception.

        Returns the log level as an integer.

        Arguments:
          error_level: the log level that should be used if a UsageException occurs.

        """
        if error_level is None:
            error_level = LOG_LEVEL_USAGE_ERROR
        try:
            ns = self.parse_args(args=args)  # Namespace object
        except UsageException:
            level = parse_log_level(error_level)
        else:
            level = ns.log_level
        return level
