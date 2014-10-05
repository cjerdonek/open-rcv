
import json


def to_json(obj):
    return json.dumps(obj, indent=4, sort_keys=True)



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
        return range(1, len(self.candidates) + 1)

    # TODO: look up the proper return type.
    def __repr__(self):
        return self.name


class RawRoundResults(JsonMixin):

    """
    Represents the results of a round for testing purposes.

    """

    def __init__(self, totals):
        """
        Arguments:
          totals: dict of candidate number to vote total.

        """
        self.totals = totals

    def __jsobj__(self):
        return {
            "totals": self.totals,
        }


class RawContestResults(JsonMixin):

    """
    Represents contest results for testing purposes.

    """

    def __init__(self, rounds):
        """
        Arguments:
          rounds: an iterable of RawRoundResults objects.

        """
        self.rounds = rounds

    def __jsobj__(self):
        return {
            "rounds": [r.__jsobj__() for r in self.rounds],
        }


# TODO: add a dict of who breaks ties in each round there is a tie.
class TestContestInput(JsonMixin):

    """
    Represents a contest for an open-rcv-tests input file.

    """

    def __init__(self, candidates, ballots):

        """
        Arguments:
          candidates: integer number of candidates

        """

        self.ballots = ballots
        self.candidates = candidates

    def __jsobj__(self):
        # TODO: include _meta: id, notes.
        return {
            "ballots": self.ballots.__jsobj__(),
            "candidates": self.candidates,
        }


# tests_jobj = {
#     "_meta": {
#         "version": "0.1.0-alpha",
#     },
#     "contests": contests_obj
# }
class TestInputFile(JsonMixin):

    """
    Represents an open-rcv-tests input file.

    """

    def __init__(self, contests, version=None):

        """
        Arguments:
          contests: an iterable of TestContestInput objects.

        """

        self.contests = contests
        self.version = version

    def __jsobj__(self):
        # TODO: include _meta: id, notes.
        return {
            "ballots": self.ballots.__jsobj__(),
            "candidates": self.candidates,
        }
