
from contextlib import contextmanager
import logging
import os
import sys
from traceback import format_exc

import colorlog

from openrcv import counting


EXIT_STATUS_SUCCESS = 0
EXIT_STATUS_FAIL = 1
EXIT_STATUS_USAGE_ERROR = 2
LOGGING_LEVEL_DEFAULT = logging.DEBUG

PROG_NAME = os.path.basename(sys.argv[0])
log = logging.getLogger(PROG_NAME)


class DisplayNameFilter(object):

    """A logging filter that sets display_name."""

    def filter(self, record):
        record.display_name = record.name
        return True


class TruncatedDisplayNameFilter(object):

    """A logging filter that sets a truncated display_name."""

    def filter(self, record):
        parts = record.name.split(".")
        if len(parts) <= 3:
            display_name = record.name
        else:
            # For example, "a.b.c.d" becomes "a.b...d".
            display_name = '.'.join(parts[:2] + ['.', parts[-1]])
        record.display_name = display_name
        return True


def get_filter(level):
    if level <= logging.DEBUG:
        cls = DisplayNameFilter
    else:
        cls = TruncatedDisplayNameFilter
    return cls()


def make_formatter():
    # Prefix log messages unobtrusively with "log" to distinguish log
    # messages more obviously from other text sent to the error stream.
    format_string = ("%(bg_black)s%(log_color)slog: %(display_name)s: "
                     "[%(levelname)s]%(reset)s %(message)s")
    colors = colorlog.default_log_colors
    colors['DEBUG'] = 'white'
    formatter = colorlog.ColoredFormatter(format_string, log_colors=colors)
    return formatter

def make_log_handler(level, stream=None):
    if stream is None:
        stream = sys.stderr

    # If stream is None, StreamHandler uses sys.stderr.
    handler = logging.StreamHandler(stream)

    filter_ = get_filter(level)
    handler.addFilter(filter_)

    formatter = make_formatter()
    handler.setFormatter(formatter)

    return handler


@contextmanager
def config_log(level=None, stream=None):
    """
    A context manager to configure logging and then undo the configuration.

    Undoing the configuration is useful for testing, since otherwise
    many log handlers might accumulate during the course of testing,
    due to successive calls to this method.

    Arguments:

      level: lowest logging level to log.
      stream: the stream to use for logging (e.g. sys.stderr).

    """
    if level is None:
        level = LOGGING_LEVEL_DEFAULT
    root = logging.getLogger()
    root.setLevel(level)
    handler = make_log_handler(level, stream=stream)
    root.addHandler(handler)
    log.info("logging configured to: %s" % logging.getLevelName(level))
    yield
    root.removeHandler(handler)


def run_count(blt_path):
    counting.count_irv(blt_path)


def main_status_inner(argv):
    if argv is None:
        argv = sys.argv
    # TODO: use argparse.
    log.debug("argv: %r" % argv)
    blt_path = argv[1]
    run_count(blt_path)


def main_status(argv, log_stream=None):
    with config_log(stream=log_stream):
        try:
            main_status_inner(argv)
            status = EXIT_STATUS_SUCCESS
        except Exception as err:
            # Log the full exception info for "unexpected" exceptions.
            log.error(format_exc())
            status = EXIT_STATUS_FAIL

    return status


# We follow most of Guido van Rossum's 2003 advice regarding main()
# functions (though we choose _main() as the function that returns an exit
# status rather than main()):
# http://www.artima.com/weblogs/viewpost.jsp?thread=4829
def main(argv=None):
    status = main_status(argv)
    sys.exit(status)
