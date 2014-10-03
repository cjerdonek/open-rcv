
"""
Support for counting ballots.

"""

import logging
import os
import string

from openrcv.models import TestRoundResults
from openrcv.parsing import BLTParser, InternalBallotsParser
from openrcv import utils


log = logging.getLogger(__name__)


def count_ballots(openable_ballots, candidates):
    """
    Count one round, and return a TestRoundResults object.

    Arguments:
      openable_ballots: an openable to an internal ballot file.
      candidates: iterable of candidates eligible to receive votes.

    """
    parser = InternalBallotsParser(candidates)
    results = parser.parse(openable_ballots)
    return results


def get_majority(total):
    """Return the majority threshold for a single-winner election."""
    assert total > 0  # If not, the calling code has a bug!
    return total // 2 + 1


def get_winner(totals):
    """
    Return the candidate with a majority, or None.

    Arguments:
      totals: dict of candidate to vote total.

    """
    total = sum(totals.values())
    threshold = get_majority(total)
    for candidate, candidate_total in totals.items():
        if candidate_total >= threshold:
            return candidate
    return None


def _get_eliminated(totals):
    candidates = totals.keys()
    candidates = sorted(candidates, key=lambda c: totals[c])
    # TODO: find lowest.
    eliminated = candidates[0]



def _count_irv(sub_dir, blt_path):
    ballots_path = os.path.join(sub_dir, "ballots.txt")
    parser = BLTParser(ballots_path)
    info = parser.parse_path(blt_path)
    # TODO: make a helper function for the following?
    candidates = range(1, len(info.candidates) + 1)

    rounds = []
    while True:
        results = count_ballots(ballots_path, candidates)
        rounds.append(results)
        totals = results.candidates


    totals = count_ballots(ballots_path, candidates)
    return totals

# This is currently just a test function rather than part of the API.
def count_irv(blt_path, temp_dir=None):
    if temp_dir is None:
        temp_dir = "temp"
    utils.ensure_dir(temp_dir)
    with utils.temp_dir_inside(temp_dir) as sub_dir:
        totals = _count_irv(sub_dir, blt_path)

    print(totals.to_json())

    return totals
