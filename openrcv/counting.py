
"""
Support for counting ballots.

"""

import logging
import os
import string

# This module should not import the module containing the JSON objects.
# In particular, it should not use any of the JSON object classes.  There
# are two reasons for this: (1) it avoids circular dependencies, and
# (2) for simplicity, the counting algorithms should be decoupled from
# and not depend on serialization, etc.  Serialization is supplemental
# to any counting and not a prerequisite.

from openrcv.formats.internal import parse_internal_ballot, to_internal_ballot
from openrcv.models import normalized_ballots, ContestResults, RoundResults
from openrcv.parsing import BLTParser, Parser
from openrcv import utils
from openrcv.utils import parse_integer_line, PathInfo, ENCODING_INTERNAL_BALLOTS


log = logging.getLogger(__name__)


def any_value(dict_):
    """Return any value in dict."""
    try:
        return next(iter(dict_.values()))
    except StopIteration:
        raise ValueError("dict has no values")


def count_internal_ballots(ballot_stream, candidates):
    """
    Count one round, and return a RoundResults object.

    Arguments:
      ballot_stream: a StreamInfo object for an internal ballot file.
      candidates: iterable of candidates eligible to receive votes.

    """
    parser = InternalBallotsCounter(candidates)
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


def count_irv_contest(ballot_stream, candidates):
    """
    Tabulate a contest using IRV, and return a ContestResults object.

    Arguments:
      ballot_stream: a StreamInfo object for an internal ballot file.
      candidates: an iterable of candidates eligible to receive votes.

    """
    # TODO: handle case of 0 total (no winner, probably)?  And add a test case.
    # TODO: add tests for degenerate cases (0 candidates, 1 candidate, 0 votes, etc).
    candidates = set(candidates)
    rounds = []
    while True:
        round_results = count_internal_ballots(ballot_stream, candidates)
        rounds.append(round_results)
        totals = round_results.totals
        winner = get_winner(totals)
        if winner is not None:
            break
        eliminated = get_lowest(totals)
        if len(eliminated) > 1:
            # Then there is a tie for last place.
            round_number = len(rounds)
            raise NotImplementedError("tie for last place occurred in round %d: %r" %
                                      (round_number, eliminated))

        candidates -= eliminated

    results = ContestResults(rounds)
    return results


def _count_irv(sub_dir, blt_path):
    ballot_path = os.path.join(sub_dir, "ballots.txt")
    ballot_stream = PathInfo(ballot_path, encoding=utils.ENCODING_INTERNAL_BALLOTS)
    blt_stream = PathInfo(blt_path)

    parser = BLTParser(ballot_stream)
    contest = parser.parse(blt_stream)
    candidates = set(contest.get_candidates())

    results = count_irv_contest(ballot_stream, candidates)

    return results


# This is currently just a test function rather than part of the API.
def count_irv(blt_path, temp_dir=None):
    """Return a ContestResults object."""
    if temp_dir is None:
        temp_dir = "temp"
    utils.ensure_dir(temp_dir)
    with utils.temp_dir_inside(temp_dir) as sub_dir:
        results = _count_irv(sub_dir, blt_path)

    return results


# TODO: this class should take the "count" function as an argument.
class InternalBallotsCounter(Parser):

    # TODO: document how to include undervotes.
    """
    Parses an internal ballots file.

    The file format is as follows:

    Each line is a space-delimited string of integers.  The first integer
    is the weight of the ballot, which is 1 for a single voter.  The
    remaining numbers are the candidates in the order in which they
    were ranked.

    A sample file:

    2 2
    1 2 4 3 1
    2 1 3 4
    3 1

    """

    name = "internal ballots"

    def __init__(self, candidates):
        """
        Arguments:
          candidates: iterable of candidate numbers.

        """
        self.candidates = candidates

    def get_parse_return_value(self):
        totals = RoundResults(self.candidate_totals)
        return totals

    def count_ballot(self, weight, choices):
        raise NotImplementedError()

    def parse_lines(self, lines):
        candidates = self.candidates
        totals = {}
        for candidate in candidates:
            totals[candidate] = 0

        candidate_set = set(candidates)
        for line in lines:
            ints = parse_integer_line(line)
            weight = next(ints)
            # TODO: use parse_internal_ballot()
            # TODO: replace with call to self.count_ballot().
            for i in ints:
                if i in candidate_set:
                    totals[i] += weight
                    break

        self.candidate_totals = totals
