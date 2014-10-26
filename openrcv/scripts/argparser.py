
import argparse
import logging

from openrcv.scripts.argparse import ArgParser, HelpAction, Option, UsageException


# For better compatibility with Python 3.4.1, we rely more on the number
# than the string representation.  This is because in Python 3.4 (but
# fixedin 3.4.2), you could not use logging.getLevelName() to get the
# level number for a level name.  Travis CI was also uing 3.4.1 as of
# Oct. 26, 2014.
#  For more info, see:
#    http://bugs.python.org/issue22386"
LOG_LEVEL_DEFAULT = 20  # corresponds to INFO.
LOG_LEVEL_DEFAULT_NAME = logging.getLevelName(LOG_LEVEL_DEFAULT)

DESCRIPTION = """\
Tally the contests specified by the contests file at INPUT_PATH.

"""

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


def get_log_level(parser, args):
    """
    Returns the log level that should be used based on user args.

    This function does not raise if the user made an error.

    """
    try:
        ns = parser.parse_args(args=args)  # Namespace object
    except UsageException:
        level = parse_log_level(LOG_LEVEL_DEFAULT)
    else:
        level = ns.log_level
    return level


# TODO: unit-test print_help().
def create_argparser(prog="rcv"):
    """
    Return an ArgumentParser object.

    """
    parser = ArgParser(prog=prog, description=DESCRIPTION, add_help=False)
    parser.add_argument('input_path', metavar='INPUT_PATH',
        help=("path to a contests configuration file. Supported file "
              "formats are JSON (*.json) and YAML (*.yaml or *.yml)."))
    parser.add_argument('--log-level', metavar='LEVEL',
        default=LOG_LEVEL_DEFAULT, type=parse_log_level,
        help=("logging level name or number (e.g. CRITICAL, ERROR, WARNING, "
              "INFO, DEBUG, 10, 20, etc). "
              "Defaults to %s." % LOG_LEVEL_DEFAULT_NAME))
    # The add_argument() call for help is modeled after how argparse does it.
    parser.add_argument('-h', '--help', action=HelpAction,
        help='show this help message and exit.')
    return parser
