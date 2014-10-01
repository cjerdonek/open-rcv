
from random import randint

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


class BallotList(object):

    """

    This should be used only for tests and small sets of ballots.
    For large numbers of ballots, ballot data should be kept on the
    file system for memory reasons.

    """

    def __init__(self, ballots=None):
        if ballots is None:
            ballots = []
        self.ballots = ballots


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
