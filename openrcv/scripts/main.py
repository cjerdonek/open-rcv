
import sys

from openrcv.main import do_parse


EXIT_STATUS_SUCCESS = 0
EXIT_STATUS_FAIL = 1
EXIT_STATUS_USAGE_ERROR = 2


def main_status_inner(argv):
    if argv is None:
        argv = sys.argv
    # TODO: use argparse.
    print(repr(argv))
    ballots_path = argv[1]
    do_parse(ballots_path)

def main_status(argv):
    try:
        main_status_inner(ballots_path)
        status = EXIT_STATUS_SUCCESS
    except Exception as err:
        status = EXIT_STATUS_FAIL

    return status


# We follow most of Guido van Rossum's 2003 advice regarding main()
# functions (though we choose _main() as the function that returns an exit
# status rather than main()):
# http://www.artima.com/weblogs/viewpost.jsp?thread=4829
def main(argv=None):
    status = main_status(argv)
    sys.exit(status)
