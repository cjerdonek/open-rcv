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
import collections
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

JsonLocationMetavar = collections.namedtuple('JsonLocationMetavar', ('contests_path', 'tests_dir'))

# TODO: move this to a utility module?
REPO_ROOT = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

TESTS_SUBMODULE_DIR = "submodules/open-rcv-tests/"
DEFAULT_CONTESTS_JSON_PATH = "contests.json"
DEFAULT_TESTS_DIR = "tests"


OPTION_HELP = Option(('-h', '--help'))
OPTION_JSON_LOCATION = Option(('-j', '--json-location'),
                              JsonLocationMetavar("CONTESTS_PATH", "TESTS_DIR"))
OPTION_OUTPUT_DIR = Option(('-o', '--output-dir'), "OUTPUT_DIR")
OPTION_OUTPUT_FORMAT = Option(('-f', '--output-format'), "OUTPUT_FORMAT")

OUTPUT_FORMAT_BLT = 'blt'
OUTPUT_FORMAT_INTERNAL = 'internal'
OUTPUT_FORMAT_TEST = 'jscase'
# TODO: default to OpenRCV format.
OUTPUT_FORMAT_DEFAULT = OUTPUT_FORMAT_BLT


HELP_DEFAULT_JSON_LOCATION = """\
Using the default requires running this command from a source checkout with
the `open-rcv-tests` submodule checked out.
"""

HELP_DEFAULT_CONTESTS_PATH = """\
The JSON contests file defaults to the path "{path}" inside the submodule.
""".format(path=DEFAULT_CONTESTS_JSON_PATH)

HELP_DEFAULT_TESTS_DIR = """\
The tests directory defaults to the path "{path}" inside the submodule.
""".format(path=DEFAULT_TESTS_DIR)


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
        UpdateTestOutputsCommand,
    )
    builder.add_commands(group, classes)

    return parser


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


class CommandBase(object):

    def __init__(self, formats):
        """
        Arguments:
          formats: TODO.
        """
        self.formats = formats

    @property
    def help_details(self):
        return ""

    @property
    def desc(self):
        details = fill(self.help_details)
        return "{help}\n\n{details}".format(help=self.help, details=details)

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

    def _make_path_relative(self, path):
        """Convert the given path to one relative to the cwd.

        This method is useful for providing shorter messages to the user
        (since absolute paths can be long).

        Arguments:
          path: a path relative to the repo root.
        """
        return os.path.relpath(os.path.join(REPO_ROOT, path))

    def _make_rel_submodule_path(self, rel_path):
        """
        Arguments:
          rel_path: a path relative to the submodule directory.
        """
        path = os.path.join(TESTS_SUBMODULE_DIR, rel_path)
        return self._make_path_relative(path)

    def _default_contests_paths(self):
        """Return the default contests path."""
        return self._make_rel_submodule_path(DEFAULT_CONTESTS_JSON_PATH)

    def _default_tests_dir(self):
        """Return the default tests directory."""
        return self._make_rel_submodule_path(DEFAULT_TESTS_DIR)

    def _add_argument_json_location(self, parser, help, metavar=None, **kwargs):
        """Add an argument for the JSON path or paths."""
        if metavar is None:
            metavar = OPTION_JSON_LOCATION.metavar.contests_path
        parser.add_argument(*OPTION_JSON_LOCATION, dest='json_location',
                            metavar=metavar, help=help, **kwargs)

    def add_json_location_optional(self, parser):
        """Add a contests path argument where the path is optional."""
        help = """\
        use a JSON contests file.  If {contests_path_metavar} is not provided,
        the default location is used.  {0}{1}
        """.format(HELP_DEFAULT_JSON_LOCATION,
                   HELP_DEFAULT_CONTESTS_PATH,
                   contests_path_metavar=OPTION_JSON_LOCATION.metavar.contests_path)
        default_path = self._default_contests_paths()
        self._add_argument_json_location(parser, help, nargs='?', const=default_path)

    def add_required_contests_path(self, parser):
        """Add a contests path argument where the path is required."""
        help = """\
        specify a custom JSON contests file.  If the option is not provided,
        the default location is used.  {0}{1}
        """.format(HELP_DEFAULT_JSON_LOCATION,
                   HELP_DEFAULT_CONTESTS_PATH)
        default_contests_path = self._default_contests_paths()
        self._add_argument_json_location(parser, help, default=default_contests_path)

    def add_required_tests_dir(self, parser):
        """Add a contests path argument where the path is required."""
        help = """\
        specify a custom JSON tests directory.  If the option is not provided,
        the default location is used.  {0}{1}
        """.format(HELP_DEFAULT_JSON_LOCATION,
                   HELP_DEFAULT_TESTS_DIR)
        default_tests_dir = self._default_tests_dir()
        self._add_argument_json_location(parser, help,
                                         metavar=OPTION_JSON_LOCATION.metavar.tests_dir,
                                         default=default_tests_dir)

    def add_required_contests_path_and_tests_dir(self, parser):
        """Add an argument for the contests path and tests directory."""
        help = """\
        specify a custom JSON contests file and tests directory.  If the option
        is not provided, the default location is used.  {0}{1}{2}
        """.format(HELP_DEFAULT_JSON_LOCATION,
                   HELP_DEFAULT_CONTESTS_PATH,
                   HELP_DEFAULT_TESTS_DIR)
        default_paths = (self._default_contests_paths(), self._default_tests_dir())
        self._add_argument_json_location(parser, help, nargs=2,
                                         metavar=OPTION_JSON_LOCATION.metavar,
                                         default=default_paths)


class CountCommand(CommandBase):

    name = "count"
    help = "Tally one or more contests."

    help_details = """\
    Tally the contests specified by the contests file at INPUT_PATH.
    """

    def add_arguments(self, parser):
        parser.add_argument('input_path', metavar='INPUT_PATH',
            help=("path to a contests configuration file. Supported file "
                  "formats are JSON (*.json) and YAML (*.yaml or *.yml)."))

    @property
    def func(self):
        return commands.count


class RandContestCommand(CommandBase):

    name = "randcontest"
    help = "Create a random contest."

    @property
    def help_details(self):
        return """\
            This command creates a contest with random ballot data and writes
            the contest to stdout in the format specified by {output_format}.
            If {output_dir} is provided, then the data is instead written to
            files, and only the paths to the output files are written to stdout.

            If the {json_contests_option} option is passed, then the contest
            is also added to the end of the specified JSON contests file.
            """.format(json_contests_option=OPTION_JSON_LOCATION.long,
                       output_format=OPTION_OUTPUT_FORMAT.metavar,
                       output_dir=OPTION_OUTPUT_DIR.metavar)

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
        # TODO: make the empty string mean the current directory.
        parser.add_argument(*OPTION_OUTPUT_DIR.flags, metavar=OPTION_OUTPUT_DIR.metavar,
            help=("directory to write output files to.  If the empty string, "
                  "writes to stdout."))
        # The output formats.
        labels = sorted(formats)
        list_desc = ", ".join((str(formats[label]) for label in labels))
        parser.add_argument(*OPTION_OUTPUT_FORMAT.flags, metavar=OPTION_OUTPUT_FORMAT.metavar,
            type=self.writer_type, default=OUTPUT_FORMAT_DEFAULT,
            help=('the output format.  Choose from: {!s}. Defaults to: "{!s}".'
                  .format(list_desc, OUTPUT_FORMAT_DEFAULT)))
        self.add_json_location_optional(parser)
        parser.add_argument('-S, ''--suppress-ballot-normalization',
            action='store_false', dest='normalize_ballots',
            help=("whether to suppress normalizing the list of ballots, which includes "
                  "ordering the ballots lexicographically and then grouping identical "
                  "choices using the weight."))

    def func(self, ns, stdout):
        ballot_count = ns.ballot_count
        candidate_count = ns.candidate_count
        output_dir = ns.output_dir
        format_cls = ns.output_format
        contests_path = ns.json_location
        normalize = ns.normalize_ballots
        return commands.make_random_contest(ballot_count=ballot_count,
                            candidate_count=candidate_count,
                            format_cls=format_cls,
                            json_contests_path=contests_path,
                            normalize=normalize,
                            output_dir=output_dir,
                            stdout=stdout)


class CleanContestsCommand(CommandBase):

    name = "cleancontests"

    help = "Clean and normalize a JSON contests file."

    help_details = """\
    Normalizations include updating the integer indices, setting the
    permanent IDs, and normalizing the ballots if needed.
    """

    def add_arguments(self, parser):
        self.add_required_contests_path(parser)

    def func(self, ns, stdout):
        contests_path = ns.json_location
        return jcmanage.normalize_contests_file(contests_path)


class UpdateTestInputsCommand(CommandBase):

    name = "updateinputs"

    help = "Update the test inputs in a tests directory."

    def add_arguments(self, parser):
        self.add_required_contests_path_and_tests_dir(parser)

    def func(self, ns, stdout):
        contests_path, tests_dir = ns.json_location
        return jcmanage.update_test_inputs(contests_path, tests_dir)


class UpdateTestOutputsCommand(CommandBase):

    name = "updateoutputs"

    help = "Update the test outputs in a tests directory."

    def add_arguments(self, parser):
        self.add_required_tests_dir(parser)

    def func(self, ns, stdout):
        tests_dir = ns.json_location
        return jcmanage.update_test_outputs(tests_dir)
