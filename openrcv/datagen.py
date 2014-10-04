
"""
Support for generating and managing election data.

This module provides functions to help work with the test cases
in the open-rcv-tests repo.

"""

from random import randint

from openrcv import models
from openrcv.models import BallotList, MinimalContest

def main():
    create_json_tests(target_path="sub/open-rcv-tests/contests.json")

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


def create_json_tests(target_path):
    contests = []
    for count in range(3, 6):
        contest = random_contest(count)
        contests.append(contest)

    contests_obj = [c.__jsobj__() for c in contests]

    tests_jobj = {
        "_meta": {
            "version": "0.1.0-alpha",
        },
        "contests": contests_obj
    }
    json = models.to_json(tests_jobj)

    print(json)
