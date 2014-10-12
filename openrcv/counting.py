
"""
Support for counting ballots.

"""

import logging
import os
import string

# TODO: do not import from jsmodels in this module.
from openrcv.jsmodels import JsonContestResults, JsonRoundResults
from openrcv.parsing import (make_internal_ballot_line, parse_integer_line,
                             parse_internal_ballot, BLTParser, Parser)
from openrcv import utils
from openrcv.utils import FileInfo, ENCODING_INTERNAL_BALLOTS


log = logging.getLogger(__name__)


def any_value(dict_):
    """Return any value in dict."""
    try:
        return next(iter(dict_.values()))
    except StopIteration:
        raise ValueError("dict has no values")


def normalized_ballots(lines):
    """
    Return an iterator object of normalized internal ballots.

    Returns an iterator object that yields a sequence of internal ballots
    equivalent to the original, but "compressed" (using the weight component)
    and ordered lexicographically by the list of choices on each ballot.
    The iterator returns each internal ballot as a (weight, choices) 2-tuple.

    Arguments:
      lines: an iterable of lines in an internal ballot file.

    """
    # A dict mapping tuples of choices to the cumulative weight.
    choices_dict = {}

    for line in lines:
        weight, choices = parse_internal_ballot(line)
        try:
            choices_dict[choices] += weight
        except KeyError:
            # Then we are adding the choices for the first time.
            choices_dict[choices] = weight

    sorted_choices = sorted(choices_dict.keys())

    def iterator():
        for choices in sorted_choices:
            weight = choices_dict[choices]
            yield weight, choices

    return iterator()


def count_internal_ballots(ballot_stream, candidates):
    """
    Count one round, and return a JsonRoundResults object.

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
    Tabulate a contest using IRV, and return a JsonContestResults object.

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

    results = JsonContestResults(rounds)
    return results


def _count_irv(sub_dir, blt_path):
    ballot_path = os.path.join(sub_dir, "ballots.txt")
    ballot_stream = FileInfo(ballot_path, encoding=utils.ENCODING_INTERNAL_BALLOTS)
    blt_stream = FileInfo(blt_path)

    parser = BLTParser(ballot_stream)
    contest = parser.parse(blt_stream)
    candidates = set(contest.get_candidates())

    results = count_irv_contest(ballot_stream, candidates)

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


# TODO: test this class.
class InternalBallotsNormalizer(Parser):

    """
    Compresses and normalizes internal ballots.

    This class takes a StreamInfo of internal ballots and returns a
    new StreamInfo that represents an equivalent set of internal ballots,
    but both "compressed" (by using the weight component) and ordered
    lexicographically for readability by the list of choices on the ballot.

    """

    name = "normalizing internal ballots"

    def __init__(self, output_stream):
        """
        Arguments:
          output_stream: a StreamInfo object for output.

        """
        self.output_stream = output_stream

    def get_parse_return_value(self):
        return self.output_stream

    def parse_lines(self, lines):
        normalized = normalized_ballots(lines)

        with self.output_stream.open("w") as f:
            for weight, choices in normalized:
                line = make_internal_ballot_line(weight, choices, "\n")
                f.write(line)


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
        totals = JsonRoundResults(self.candidate_totals)
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
