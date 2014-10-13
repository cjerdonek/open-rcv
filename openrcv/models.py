
"""
Internal models that do not require JSON serialization.

"""

def make_candidates(candidate_count):
    """
    Return an iterable of candidate numbers.

    """
    return range(1, candidate_count + 1)


class ContestInfo(object):

    """
    Attributes:
      candidates: a list of the names of all candidates, in numeric order.
      name: name of contest.
      seat_count: integer number of winners.

    """

    ballot_count = 0

    def __init__(self):
        pass

    def get_candidates(self):
        """Return an iterable of the candidate numbers."""
        return make_candidates(len(self.candidates))

    # TODO: look up the proper return type.
    def __repr__(self):
        return self.name


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


class ContestResults(object):

    """
    Represents contest results.

    """

    def __init__(self, rounds=None):
        self.rounds = rounds

    def repr_desc(self):
        return "rounds=%s" % (len(self.rounds), )
