
"""
Internal models that do not require JSON serialization.

"""

from openrcv.utils import ReprMixin


def make_candidates(candidate_count):
    """
    Return an iterable of candidate numbers.

    """
    return range(1, candidate_count + 1)


# TODO: document the format of the ballots StreamInfo.
# TODO: rename to ContestInput.
class ContestInfo(ReprMixin):

    """
    Attributes:
      ballots: a readable StreamInfo object of ballots.
      candidates: an iterable of the names of all candidates, in numeric
        order of their ballot ID.
      name: contest name.
      seat_count: integer number of winners.

    """

    ballot_count = 0

    def __init__(self, seat_count=None):
        if seat_count is None:
            seat_count = 1

        self.ballots = None
        self.candidates = []
        self.name = None

        self.seat_count = seat_count

    def repr_desc(self):
        return "name=%r, candidates=%d" % (self.name, len(self.candidates))

    # TODO: give this method or more accurate name.
    def get_candidates(self):
        """Return an iterable of the candidate numbers."""
        return make_candidates(len(self.candidates))


class RoundResults(object):

    """
    Represents contest results.

    """

    def __init__(self, totals):
        """
        Arguments:
          totals: dict of candidate number to vote total.

        """
        self.totals = totals


class ContestResults(ReprMixin):

    """
    Represents contest results.

    """

    def __init__(self, rounds=None):
        self.rounds = rounds

    def repr_desc(self):
        return "rounds=%s" % (len(self.rounds), )
