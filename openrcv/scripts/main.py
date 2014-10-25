
import argparse
from contextlib import contextmanager
import logging
import os
import sys
from traceback import format_exc

import colorlog

# TODO: give this module a better name (e.g. "common").

EXIT_STATUS_SUCCESS = 0
EXIT_STATUS_FAIL = 1
EXIT_STATUS_USAGE_ERROR = 2
LOGGING_LEVEL_DEFAULT = logging.DEBUG

PROG_NAME = os.path.basename(sys.argv[0])
log = logging.getLogger(PROG_NAME)


class UsageError(Exception):

    """
    Exception class for command-line syntax errors.

    """

    def __init__(self, *args, parser=None):
        super().__init__(*args)
        self.parser = parser


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
        raise UsageError(message, parser=self)


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
    # TODO: can we delete this code comment?  Is there any reason
    # to set this handler to a level different from the root logger?
    #handler.setLevel(level)

    filter_ = get_filter(level)
    handler.addFilter(filter_)

    formatter = make_formatter()
    handler.setFormatter(formatter)

    return handler


# TODO: rename stream to file.
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
    # If logging was already configured (e.g. at the outset of a test run),
    # then let's not change the root logging level.
    # TODO: simplify this logic (e.g. we should not need "if" logic).
    already_configured = root.hasHandlers()
    handler = make_log_handler(level, stream=stream)
    root.addHandler(handler)
    if not already_configured:
        root.setLevel(level)
        log.info("root logger level set to: %s" % logging.getLevelName(level))
    log.debug("a logging handler was added")
    yield
    root.removeHandler(handler)


# TODO: rename log_stream to log_file.
# TODO: test the UsageError code path.
def main_status(do_func, argv, log_stream=None):
    with config_log(stream=log_stream):
        log.debug("argv: %r" % argv)
        try:
            do_func(argv)
            status = EXIT_STATUS_SUCCESS
        except UsageError as err:
            # As of Python 3.4, argparse.ArgumentParser's error() implementation
            # looked like this--
            #   self.print_usage(_sys.stderr)
            #   args = {'prog': self.prog, 'message': message}
            #   self.exit(2, _('%(prog)s: error: %(message)s\n') % args)
            parser = err.parser
            # TODO: display user-friendly instruction for running --help.
            parser.print_usage(log_stream)
            args = err.args
            assert len(args) == 1
            log.error(args[0])
            status = EXIT_STATUS_USAGE_ERROR
        except Exception as err:
            # Log the full exception info for "unexpected" exceptions.
            log.error(format_exc())
            status = EXIT_STATUS_FAIL

    return status


# We follow most of Guido van Rossum's 2003 advice regarding main()
# functions (though we choose _main() as the function that returns an exit
# status rather than main()):
# http://www.artima.com/weblogs/viewpost.jsp?thread=4829
def main(do_func, argv=None):
    if argv is None:
        argv = sys.argv
    status = main_status(do_func, argv)
    sys.exit(status)
