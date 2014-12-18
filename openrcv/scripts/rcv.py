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

"""Supports the "rcv" command-line command (aka console_script)."""

import argparse2 as argparse
from argparse2 import RawDescriptionHelpFormatter
import logging
import os
import textwrap

from openrcv.formats.blt import BLTFormat
from openrcv.formats.internal import InternalFormat
from openrcv import jcmanage
from openrcv.formats.jscase import JsonCaseFormat
from openrcv.scripts.argparse import (parse_log_level, ArgParser, HelpAction,
                                      HelpRequested, Option, UsageException)
from openrcv.scripts import commands
from openrcv.scripts.run import main as _main
from openrcv import utils


# For increased compatibility (specifically with Python 3.4 <= 3.4.1),
# we rely primarily on the log level number rather than the string name.
# This is because in Python 3.4 (but fixed in 3.4.2), you could not use
# logging.getLevelName() to obtain the level number from a level name.
# Travis CI was using 3.4.1 as of Oct. 26, 2014.  For more info, see--
#   http://bugs.python.org/issue22386"
LOG_LEVEL_DEFAULT = 20  # corresponds to INFO.
LOG_LEVEL_DEFAULT_NAME = logging.getLevelName(LOG_LEVEL_DEFAULT)
# The log level that should be used if the ArgumentParser raises a UsageException.
LOG_LEVEL_USAGE_ERROR = 20  # corresponds to INFO.

DESCRIPTION = """\
OpenRCV command-line tool.

"""

DEFAULT_CONTESTS_JSON_PATH = "submodules/open-rcv-tests/contests.json"

OPTION_HELP = Option(('-h', '--help'))
OPTION_OUTPUT_DIR = Option(('-o', '--output-dir'), "OUTPUT_DIR")
OPTION_OUTPUT_FORMAT = Option(('-f', '--output-format'), "OUTPUT_FORMAT")

OUTPUT_FORMAT_BLT = 'blt'
OUTPUT_FORMAT_INTERNAL = 'internal'
OUTPUT_FORMAT_TEST = 'jscase'
# TODO: default to OpenRCV format.
OUTPUT_FORMAT_DEFAULT = OUTPUT_FORMAT_BLT


# TODO: use this function throughout this module.
def fill(text):
    text = textwrap.dedent(text)
    paras = text.split("\n\n")
    fill_ = textwrap.fill
    text = "\n\n".join(fill_(p) for p in paras)
    return text


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


def main():
    parser = create_argparser()
    _main(parser)


class CommandBase(object):

    def __init__(self, formats):
        """
        Arguments:
          formats: TODO.
        """
        self.formats = formats

    @property
    def raw_desc(self):
        # Default to the short help message.
        return self.help

    @property
    def desc(self):
        return fill(self.raw_desc)

    def add_arguments(self, parser):
        raise utils.NoImplementation(self)

    def writer_type(self, label):
        formats = self.formats
        try:
            format = formats[label]
        except KeyError:
            labels = sorted(formats.keys())
            raise argparse.ArgumentTypeError("\ninvalid argument choice: %r "
                "(choose from: %s)" % (label, ", ".join(labels)))
        return format.cls

    # TODO: expose two variants of this method: one where contests.json
    #   is always necessary, and one where it is optional.
    def add_contests_path_argument(self, parser):
        file_dir = os.path.dirname(__file__)
        repo_root = os.path.join(file_dir, os.pardir, os.pardir)
        default_contests_path = os.path.join(repo_root, DEFAULT_CONTESTS_JSON_PATH)
        rel_default_path = os.path.relpath(default_contests_path)
        parser.add_argument('-j', '--json-contests', metavar='JSON_PATH',
            dest='json_contests_path', nargs='?', const=rel_default_path,
            help=("path to a contests.json file.  Defaults to the contests.json "
                  "file located at {0:s} relative to the source root.  "
                  "Using the default requires running this command from "
                  "a source checkout with the open-rcv-tests submodule "
                  "checked out.".format(DEFAULT_CONTESTS_JSON_PATH)))


class CountCommand(CommandBase):

    name = "count"
    help = "Tally one or more contests."
    raw_desc = """\
        Tally the contests specified by the contests file at INPUT_PATH.
        """

    @property
    def func(self):
        return commands.count

    def add_arguments(self, parser):
        parser.add_argument('input_path', metavar='INPUT_PATH',
            help=("path to a contests configuration file. Supported file "
                  "formats are JSON (*.json) and YAML (*.yaml or *.yml)."))


class RandContestCommand(CommandBase):

    name = "randcontest"
    help = "Make a random contest."

    @property
    def raw_desc(self):
        return ("""\
            Create a random contest.

            This command creates a contest with random ballot data and writes the
            contest to stdout in the format {output_format}. If {output_dir} is provided,
            then only the paths to the output files are written to stdout.
            """.format(output_format=OPTION_OUTPUT_FORMAT.metavar,
                       output_dir=OPTION_OUTPUT_DIR.metavar))

    def func(self, ns, stdout):
        ballot_count = ns.ballot_count
        candidate_count = ns.candidate_count
        output_dir = ns.output_dir
        format_cls = ns.output_format
        json_contests_path = ns.json_contests_path
        normalize = ns.normalize_ballots
        return commands.make_random_contest(ballot_count=ballot_count,
                            candidate_count=candidate_count,
                            format_cls=format_cls,
                            json_contests_path=json_contests_path,
                            normalize=normalize,
                            output_dir=output_dir,
                            stdout=stdout)

    def add_arguments(self, parser):
        default_candidates = 6
        default_ballots = 20
        formats = self.formats
        parser.add_argument('-c', '--candidates', dest='candidate_count', metavar='N',
                            type=int, default=default_candidates,
                            help=('number of candidates.  Defaults to {:d}.'
                                  .format(default_candidates)))
        parser.add_argument('-b', '--ballots', dest='ballot_count', metavar='N', type=int,
                           help=('number of ballots.  Defaults to {:d}.'
                                 .format(default_ballots)))
        parser.add_argument(*OPTION_OUTPUT_DIR.flags, metavar=OPTION_OUTPUT_DIR.metavar,
            help=("directory to write output files to.  If the empty string, "
                  "writes to stdout.  Defaults to the empty string."))
        # The output formats.
        labels = sorted(formats)
        list_desc = ", ".join((str(formats[label]) for label in labels))
        parser.add_argument(*OPTION_OUTPUT_FORMAT.flags, metavar=OPTION_OUTPUT_FORMAT.metavar,
            type=self.writer_type, default=OUTPUT_FORMAT_DEFAULT,
            help=('the output format.  Choose from: {!s}. Defaults to: "{!s}".'
                  .format(list_desc, OUTPUT_FORMAT_DEFAULT)))
        # TODO: DRY up with add_contests_path_argument().
        parser.add_argument('-j', '--json-contests', metavar='JSON_PATH',
            dest='json_contests_path',
            help=("path to a contests.json file.  If provided, also adds the contest "
                  "to the end of the given JSON file."))
        parser.add_argument('-S, ''--suppress-ballot-normalization',
            action='store_false', dest='normalize_ballots',
            help=("whether to suppress normalizing the list of ballots, which includes "
                  "ordering the ballots lexicographically and then grouping identical "
                  "choices using the weight."))


class CleanContestsCommand(CommandBase):

    name = "cleancontests"
    help = "Clean and normalize a contests.json file."

    raw_desc = """\
    Clean and normalize a contests.json file.

    Cleaning operations include updating the integer contest IDs and
    normalizing any ballot data that needs it.
    """

    def func(self, ns, stdout):
        json_path = ns.json_contests_path
        return jcmanage.clean_contests(json_path)

    def add_arguments(self, parser):
        self.add_contests_path_argument(parser)


class UpdateTestInputsCommand(CommandBase):

    name = "updatetestinputs"
    help = "Update test inputs from a contests.json file."

    def func(self, ns, stdout):
        json_path = ns.json_contests_path
        return commands.update_test_inputs(json_path)

    def add_arguments(self, parser):
        self.add_contests_path_argument(parser)


class GenExpectedCommand(CommandBase):

    name = "genexpected"
    help = "Generate JSON test expectations."

    def func(self):
        return commands.clean_contests

    def add_arguments(self, parser):
        self.add_contests_path_argument(parser)


class ArgBuilder(object):

    def __init__(self, formats):
        self.formats = formats

    def add_command(self, group, command_class):
        """Add the command to a sub-command group."""
        command = command_class(self.formats)
        parser = group.add_parser(command.name, help=command.help, description=command.desc,
                                  add_help=False)
        command.add_arguments(parser)
        # The RawDescriptionHelpFormatter preserves line breaks in the
        # description and epilog strings.
        parser.formatter_class = RawDescriptionHelpFormatter
        parser.set_defaults(run_command=command.func)
        add_help(parser)

    def add_commands(self, group, cmd_classes):
        for cls in cmd_classes:
            self.add_command(group, cls)

# TODO: unit-test print_help().
def create_argparser(prog="rcv"):
    """Return an ArgumentParser object."""
    parser = RcvArgumentParser(prog=prog, description=DESCRIPTION, add_help=False,
                               formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('--log-level', metavar='LEVEL',
        default=LOG_LEVEL_DEFAULT, type=parse_log_level,
        help=("logging level name or number (e.g. CRITICAL, ERROR, WARNING, "
              "INFO, DEBUG, 10, 20, etc). "
              "Defaults to %s." % LOG_LEVEL_DEFAULT_NAME))
    add_help(parser)

    desc = textwrap.dedent("""\
    Available commands are below.

    For help with a particular command, pass %s after the command name.
    For example, `%s count %s`.
    """ % (OPTION_HELP.display(' or '), prog, OPTION_HELP[0]))
    metavar = 'COMMAND'
    subparsers = parser.add_subparsers(title='commands', metavar=metavar,
                                       description=desc)
    subparsers.formatter_class = RawDescriptionHelpFormatter

    formats = make_output_formats()
    builder = ArgBuilder(formats)

    builder.add_command(subparsers, CountCommand)

    group = subparsers.add_parser_group("Test-case management")
    classes = (
        RandContestCommand,
        CleanContestsCommand,
        UpdateTestInputsCommand,
        GenExpectedCommand,
    )
    builder.add_commands(group, classes)

    return parser


# TODO: move this to openrcv.formats.common.
class OutputFormat(object):

    def __init__(self, label, desc=None, cls=None):
        self.cls = cls
        self.desc = desc
        self.label = label

    def __str__(self):
        return '"{!s}" ({!s})'.format(self.label, self.desc)


class RcvArgumentParser(ArgParser):

    option_help = OPTION_HELP

    def safe_get_log_level(self, args, error_level=None):
        """Get the user-requested log level without raising an exception.

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
