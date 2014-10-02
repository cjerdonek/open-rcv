
import json
from random import randint


def to_json(obj):
    return json.dumps(obj, indent=4)


def random_ballot_list(choices, count, max_length=None):
    """
    Arguments:
      choices: a sequence of integers.

    """
    if max_length is None:
        max_length = len(choices)

    ballots = []
    choice_count = len(choices)
    for i in range(count):
        ballot = []
        for j in range(max_length):
            choice_index = randint(0, choice_count)
            try:
                choice = choices[choice_index]
            except IndexError:
                # Then end the ballot early.
                break
            ballot.append(choice)
        ballots.append(ballot)

    return BallotList(ballots)


def random_contest(candidates):
    ballots = random_ballot_list(range(candidates), 5)
    contest = MinimalContest(candidates, ballots)
    return contest


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


class RoundResult(JsonMixin):
    """
    Represents the results for a round.

    """
    def __init__(self, candidate_count):
        self.candidate_count = candidate_count
