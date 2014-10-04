
"""
Support for generating random ballots and test data.

"""

from openrcv.models import BallotList, MinimalContest

# TODO: rename this module to datagen.

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


def make_json_tests():
    contests = []
    for count in range(3, 6):
        contest = models.random_contest(count)
        contests.append(contest)

    contests_obj = [c.__jsobj__() for c in contests]

    tests_jobj = {
        "_version": "0.1.0-alpha",
        "contests": contests_obj
    }
    json = models.to_json(tests_jobj)

    print(json)
