
import json
from random import randint


def to_json(obj):
    return json.dumps(obj, indent=4)


class JsonMixin(object):

    def to_json(self):
        return to_json(self.__jsobj__())


class BallotList(JsonMixin):

    """

    This should be used only for tests and small sets of ballots.
    For large numbers of ballots, ballot data should be kept on the
    file system for memory reasons.

    """

    def __init__(self, ballots=None):
        if ballots is None:
            ballots = []
        self.ballots = ballots

    def __jsobj__(self):
        return [" ".join((str(c) for c in ballot)) for ballot in self.ballots]


# TODO: document what this class is for.  For test data input?
class MinimalContest(JsonMixin):

    def __init__(self, candidates, ballots):

        """
        Arguments:
          candidates: integer number of candidates

        """

        self.ballots = ballots
        self.candidates = candidates

    def __jsobj__(self):
        return {
            "ballots": self.ballots.__jsobj__(),
            "candidates": self.candidates,
        }


class ContestInfo(object):

    """
    Attributes:
      name: name of contest.
      seat_count: integer number of winners.

    """

    ballot_count = 0

    def __init__(self):
        pass

    # TODO: look up the proper return type.
    def __repr__(self):
        return self.name


# TODO: rename to RoundTestRoundResults.
class TestRoundResults(JsonMixin):

    """
    Represents vote totals for a round.

    """

    def __init__(self, candidates):
        """
        Arguments:
          candidates: dict of candidate number to vote total.
          no_candidate: number of ballots counting towards no candidate.

        """
        self.candidates = candidates

    def __jsobj__(self):
        return {
            "candidates": self.candidates,
        }


# TODO: do we need more than one results object: one for testing
# and one for real use?  Should these inherit or compose from each other?
class TestContestResults(JsonMixin):

    """
    Represents the totals for all rounds.

    """

    def __init__(self, rounds):
        """
        Arguments:
          rounds: an iterable of TestRoundResults objects.

        """
        self.rounds = rounds

    def __jsobj__(self):
        return {
            "rounds": [r.__jsobj__() for r in self.rounds],
        }
