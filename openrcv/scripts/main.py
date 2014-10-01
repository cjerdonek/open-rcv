
import sys
from traceback import format_exc

from openrcv.main import do_parse


EXIT_STATUS_SUCCESS = 0
EXIT_STATUS_FAIL = 1
EXIT_STATUS_USAGE_ERROR = 2


# TODO: switch to logging module
def log(msg):
    sys.stderr.write(msg)


def log_error(msg, add_trace=False):
    if add_trace:
        msg = traceback.format_exc()
    log(str(msg))


def main_status_inner(argv):
    if argv is None:
        argv = sys.argv
    # TODO: use argparse.
    print(repr(argv))
    ballots_path = argv[1]
    do_parse(ballots_path)


def main_status(argv):
    try:
        main_status_inner(argv)
        status = EXIT_STATUS_SUCCESS
    except Exception as err:
        # Log the full exception info for "unexpected" exceptions.
        log_error(format_exc())
        status = EXIT_STATUS_FAIL

    return status


# We follow most of Guido van Rossum's 2003 advice regarding main()
# functions (though we choose _main() as the function that returns an exit
# status rather than main()):
# http://www.artima.com/weblogs/viewpost.jsp?thread=4829
def main(argv=None):
    status = main_status(argv)
    sys.exit(status)
