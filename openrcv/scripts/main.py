
import sys

from openrcv.main import do_parse

"""
Usage: python3.4 count.py ELECTION.blt OUTPUT.txt

"""

def _main(argv):
    if argv is None:
        argv = sys.argv
    # TODO: use argparse.
    print(repr(argv))
    ballots_path = argv[1]
    do_parse(ballots_path)


# We follow most of Guido van Rossum's 2003 advice regarding main()
# functions (though we choose _main() as the function that returns an exit
# status rather than main()):
# http://www.artima.com/weblogs/viewpost.jsp?thread=4829
def main(argv=None):
    status = _main(argv)
    sys.exit(status)
