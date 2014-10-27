
"""
The rcv command for counting ballots.

"""

from openrcv.scripts.argparser import create_argparser
from openrcv.scripts.run import main as _main

# TODO: move the contents of the argparser module into this module.

def main():
    parser = create_argparser()
    _main(parser)
