
"""
Support for counting ballots.

"""

import os
import string

from openrcv.models import Totals
from openrcv.parsing import BLTParser, InternalBallotsParser
from openrcv import utils


def _count_ballots(path, candidates):
    """
    A minimal function to count ballots in one pass.

    Returns a Totals object.

    Arguments:
      path: path to an internal ballot file.
      candidates: iterable of candidates eligible to receive votes.

    """
    parser = InternalBallotsParser(candidates)
    results = parser.parse_path(path)

    return results

# This is currently just a test function rather than part of the API.
def count_irv(blt_path, temp_dir=None):
    if temp_dir is None:
        temp_dir = "temp"
    utils.ensure_dir(temp_dir)
    with utils.temp_dir_inside(temp_dir) as sub_dir:
        ballots_path = os.path.join(sub_dir, "ballots.txt")
        parser = BLTParser(ballots_path)
        info = parser.parse_path(blt_path)
        # TODO: make a helper function for the following?
        candidates = range(1, len(info.candidates) + 1)
        totals = _count_ballots(ballots_path, candidates)

    print(totals.to_json())

    return info
