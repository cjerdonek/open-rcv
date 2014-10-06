
"""
Support for counting ballots.

"""

import logging
import os
import string

from openrcv.models import RawContestResults, RawRoundResults
from openrcv.parsing import BLTParser, InternalBallotsParser
from openrcv import utils
from openrcv.utils import FileInfo, ENCODING_INTERNAL_BALLOTS


log = logging.getLogger(__name__)


def any_value(dict_):
    """Return any value in dict."""
    try:
        return next(iter(dict_.values()))
    except StopIteration:
        raise ValueError("dict has no values")

def count_internal_ballots(ballot_stream, candidates):
    """
    Count one round, and return a RawRoundResults object.

    Arguments:
      ballot_stream: a StreamInfo object for an internal ballot file.
      candidates: iterable of candidates eligible to receive votes.

    """
    parser = InternalBallotsParser(candidates)
    round_results = parser.parse(ballot_stream)
    return round_results


def get_majority(total):
    """Return the majority threshold for a single-winner election.

    Note that this returns 1 for a 0 total.

    """
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


def get_lowest(totals):
    """
    Return which candidate to eliminate.

    Raises a NotImplementedError if there is a tie.

    """
    lowest_total = any_value(totals)
    lowest_candidates = set()
    for candidate, total in totals.items():
        if total < lowest_total:
            lowest_total = total
            lowest_candidates = set((candidate,))
        elif total == lowest_total:
            lowest_candidates.add(candidate)
    return lowest_candidates


def _count_irv(sub_dir, blt_path):
    iballots_path = os.path.join(sub_dir, "ballots.txt")
    iballots_stream = FileInfo(iballots_path, encoding=utils.ENCODING_INTERNAL_BALLOTS)
    blt_stream = FileInfo(blt_path)

    parser = BLTParser(iballots_stream)
    contest = parser.parse(blt_stream)
    candidates = set(contest.get_candidates())

    # TODO: handle case of 0 total?
    rounds = []
    while True:
        round_results = count_internal_ballots(iballots_stream, candidates)
        rounds.append(round_results)
        totals = round_results.totals
        winner = get_winner(totals)
        if winner is not None:
            break
        eliminated = get_lowest(totals)
        if len(eliminated) > 1:
            raise NotImplementedError()

        candidates -= eliminated

    results = RawContestResults(rounds)
    return results

# This is currently just a test function rather than part of the API.
def count_irv(blt_path, temp_dir=None):
    if temp_dir is None:
        temp_dir = "temp"
    utils.ensure_dir(temp_dir)
    with utils.temp_dir_inside(temp_dir) as sub_dir:
        results = _count_irv(sub_dir, blt_path)

    print(results.to_json())

    return results
