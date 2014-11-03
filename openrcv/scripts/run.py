
import argparse
from contextlib import contextmanager
import logging
import os
import sys
from textwrap import dedent
from traceback import format_exc

import colorlog

from openrcv.scripts.argparse import (parse_log_level, HelpRequested,
                                      UsageException)


EXIT_STATUS_SUCCESS = 0
EXIT_STATUS_FAIL = 1
EXIT_STATUS_USAGE_ERROR = 2

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

def make_log_handler(level, file_=None):
    if file_ is None:
        file_ = sys.stderr

    # If file_ is None, StreamHandler uses sys.stderr.
    handler = logging.StreamHandler(file_)
    # TODO: can we delete this code comment?  Is there any reason
    # to set this handler to a level different from the root logger?
    #handler.setLevel(level)

    filter_ = get_filter(level)
    handler.addFilter(filter_)

    formatter = make_formatter()
    handler.setFormatter(formatter)

    return handler


@contextmanager
def log_config(level, file_=None):
    """
    A context manager to configure logging and then undo the configuration.

    Undoing the configuration is useful for testing, since otherwise
    many log handlers might accumulate during the course of testing,
    due to successive calls to this method.

    Arguments:

      level: lowest logging level to log.
      file_: the file object to use for logging (e.g. sys.stderr).

    """
    if level is None:
        level = LOG_LEVEL_DEFAULT
    root = logging.getLogger()
    # If logging was already configured (e.g. at the outset of a test run),
    # then let's not change the root logging level.
    # TODO: simplify this logic (e.g. we should not need "if" logic).
    already_configured = root.hasHandlers()
    handler = make_log_handler(level, file_=file_)
    root.addHandler(handler)
    if not already_configured:
        root.setLevel(level)
        log.debug("root logger level set to: %r" % logging.getLevelName(level))
    log.debug("a logging handler was added")
    yield
    root.removeHandler(handler)


def make_usage_error(msg, help_options):
    text = dedent("""\
    Command-line usage error: {!s}

    Pass {!s} for help documentation and available options.""").format(msg, help_options)
    return text


def print_usage_error(parser, msg, file_=None):
    if file_ is None:
        file_ = sys.stderr
    if len(sys.argv) == 1:
        parser.print_help()
    parser.print_usage(file_)
    text = make_usage_error(msg, parser.option_help.display(' or '))
    log.error(text)


# TODO: test the UsageException code path.
def non_exiting_main(parser, argv, stdout=None, log_file=None):
    """
    Run the program, and return the exit status without exiting.

    Arguments:
      parser: an argparse.ArgumentParser object.

    """
    args = argv[1:]
    log_level = parser.safe_get_log_level(args)
    if stdout is None:
        stdout = sys.stdout
    with log_config(level=log_level, file_=log_file):
        log.debug("argv: %r" % argv)
        try:
            ns = parser.parse_args(args=args)  # Namespace object
            log.debug("ns: %r" % ns)
            # Make no args default to running help.
            try:
                # There seems to be a bug in argparse where the parent
                # parser's default run_command is used for args like
                # "rcv randcontest" (when nothing is after randcontest),
                # when parser.set_defaults(run_command=...) is used to set
                # the default on the parent parser.  Thus we use try-except
                # here instead.  I believe this is the issue:
                # http://bugs.python.org/issue9351
                command = ns.run_command
            except AttributeError:
                raise HelpRequested(parser=parser)
            output = command(ns, stdout=stdout)
            if output is not None:
                stdout.write(output)
            status = EXIT_STATUS_SUCCESS
        except HelpRequested as exc:
            parser = exc.parser
            parser.print_help(file=stdout)
            status = EXIT_STATUS_SUCCESS
        except UsageException as exc:
            # As of Python 3.4, argparse.ArgumentParser's error() implementation
            # looked like this--
            #   self.print_usage(_sys.stderr)
            #   args = {'prog': self.prog, 'message': message}
            #   self.exit(2, _('%(prog)s: error: %(message)s\n') % args)
            err_args, parser = exc.args, exc.parser
            assert len(err_args) == 1
            print_usage_error(parser, err_args[0], file_=log_file)
            status = EXIT_STATUS_USAGE_ERROR
        # TODO: decide whether to handle the error case manually, or let
        # Python do it by default.  One problem with the former
        # is that exceptions don't show up during test failures.
        # except Exception as err:
            #
            # # Log the full exception info for "unexpected" exceptions.
            # log.error(format_exc())
            # status = EXIT_STATUS_FAIL

    return status


# We follow most of Guido van Rossum's 2003 advice regarding main()
# functions (though we choose _main() as the function that returns an exit
# status rather than main()):
# http://www.artima.com/weblogs/viewpost.jsp?thread=4829
def main(parser, argv=None):
    if argv is None:
        argv = sys.argv
    status = non_exiting_main(parser, argv)
    sys.exit(status)
