
"""
Supports the "rcv" command-line command (aka console_script).

"""

import argparse
from argparse import RawDescriptionHelpFormatter
import logging
from textwrap import dedent

from openrcv.scripts.argparse import (parse_log_level, ArgParser, HelpAction,
                                      HelpRequested, Option, UsageException)
from openrcv.formats.blt import BLTFormat
from openrcv.formats.internal import InternalFormat
from openrcv.formats.jscase import JsonCaseFormat
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

DESCRIPTION = """\
OpenRCV command-line tool.

"""

OPTION_HELP = Option(('-h', '--help'))
OPTION_OUTPUT_DIR = Option(('-o', '--output-dir'), "OUTPUT_DIR")
OPTION_OUTPUT_FORMAT = Option(('-f', '--output-format'), "OUTPUT_FORMAT")

OUTPUT_FORMAT_BLT = 'blt'
OUTPUT_FORMAT_INTERNAL = 'internal'
OUTPUT_FORMAT_TEST = 'jscase'
# TODO: default to OpenRCV format.
OUTPUT_FORMAT_DEFAULT = OUTPUT_FORMAT_BLT


def main():
    parser = create_argparser()
    _main(parser)


def make_output_formats():
    formats = (
        OutputFormat(OUTPUT_FORMAT_BLT, cls=BLTFormat,
                     desc="BLT format"),
        OutputFormat(OUTPUT_FORMAT_INTERNAL, cls=InternalFormat,
                     desc="internal OpenRCV format"),
        OutputFormat(OUTPUT_FORMAT_TEST, cls=JsonCaseFormat,
                     desc="JSON test case"),
    )
    mapping = {format.label: format for format in formats}
    return mapping


def add_help(parser):
    # The add_argument() call for help is modeled after how argparse
    # does it internally.
    parser.add_argument(*OPTION_HELP, action=HelpAction,
        help='show this help message and exit.')


def add_command_count(builder):
    subparsers = builder.subparsers
    parser = subparsers.add_parser('count', help='Tally one or more contests.',
        description='Tally the contests specified by the contests file at INPUT_PATH.',
        add_help=False)
    parser.add_argument('input_path', metavar='INPUT_PATH',
        help=("path to a contests configuration file. Supported file "
              "formats are JSON (*.json) and YAML (*.yaml or *.yml)."))
    return parser, commands.count


def add_command_randcontest(builder):
    subparsers = builder.subparsers
    formats = builder.formats
    help = 'Create a random sample contest.'
    desc = dedent("""\
    Create a random contest.

    This command creates a contest with random ballot data and writes the
    contest to stdout in the chosen format.  If {output_dir} is provided,
    then only the paths to the output files are written to stdout.
    """.format(output_dir=OPTION_OUTPUT_DIR.metavar))
    parser = subparsers.add_parser('randcontest', help=help, description=desc,
                                   add_help=False)
    default_candidates = 6
    parser.add_argument('-c', '--candidates', dest='candidate_count', metavar='N',
                        type=int, default=default_candidates,
                        help='number of candidates.  Defaults to {:d}.'.format(default_candidates))
    default_ballots = 20
    parser.add_argument('-b', '--ballots', dest='ballot_count', metavar='N', type=int,
                       help='number of ballots.  Defaults to {:d}.'.format(default_ballots))
    parser.add_argument('-N', '--normalize', action='store_true',
        help=("whether to normalize the list of ballots, which means "
              "ordering them lexicographically and grouping identical "
              "choices using weight."))
    parser.add_argument(*OPTION_OUTPUT_DIR.flags, metavar=OPTION_OUTPUT_DIR.metavar,
        help=("directory to write output files to.  If the empty string, "
              "writes to stdout.  Defaults to the empty string."))
    # The output formats.
    labels = sorted(formats)
    list_desc = ", ".join((str(formats[label]) for label in labels))
    parser.add_argument(*OPTION_OUTPUT_FORMAT.flags, metavar=OPTION_OUTPUT_FORMAT.metavar,
        type=builder.writer_type, default=OUTPUT_FORMAT_DEFAULT,
        help=('the output format.  Choose from: {!s}. Defaults to: "{!s}".'
              .format(list_desc, OUTPUT_FORMAT_DEFAULT)))
    parser.add_argument('-j', '--json-contests', metavar='JSON_PATH', dest='json_contests_path',
        help=("path to a contests.json file.  If provided, also adds the contest "
              "to the end of the given JSON file."))
    return parser, commands.make_random_contest


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
    add_help(parser)

    desc = dedent("""\
    Available commands are below.

    For help with a particular command, pass %s after the command name.
    For example, `%s count %s`.
    """ % (OPTION_HELP.display(' or '), prog, OPTION_HELP[0]))
    subparsers = parser.add_subparsers(title='commands', metavar='COMMAND',
                                       description=desc)
    subparsers.formatter_class = RawDescriptionHelpFormatter

    add_funcs = (
        add_command_count,
        add_command_randcontest,
    )

    builder = ArgParserBuilder(subparsers)
    for add_func in add_funcs:
        builder.add_command(add_func)

    return parser


# TODO: move this to openrcv.formats.common.
class OutputFormat(object):

    def __init__(self, label, desc=None, cls=None):
        self.cls = cls
        self.desc = desc
        self.label = label

    def __str__(self):
        return '"{!s}" ({!s})'.format(self.label, self.desc)


class ArgParserBuilder(object):

    """Support for constructing the script's argparse.ArgumentParser."""

    def __init__(self, subparsers):
        self.formats = make_output_formats()
        self.subparsers = subparsers

    def writer_type(self, label):
        formats = self.formats
        try:
            format = formats[label]
        except KeyError:
            labels = sorted(formats.keys())
            raise argparse.ArgumentTypeError("\ninvalid argument choice: %r "
                "(choose from: %s)" % (label, ", ".join(labels)))
        return format.cls

    def add_command(self, add_func):
        parser, command_func = add_func(self)
        # The RawDescriptionHelpFormatter preserves line breaks in the
        # description and epilog strings.
        parser.formatter_class = RawDescriptionHelpFormatter
        parser.set_defaults(run_command=command_func)
        # TODO: DRY up the fact that add_help=False needs to be added
        # when adding each command.
        add_help(parser)


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
