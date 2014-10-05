
"""
Support for generating and managing election data.

This module provides functions to help work with the test cases
in the open-rcv-tests repo.

"""

import random

from openrcv import models
from openrcv.models import BallotList, TestContestInput, TestInputFile

def main():
    create_json_tests(target_path="sub/open-rcv-tests/contests.json")


def gen_random_list(choices, max_length=None):
    """
    Generate a "random" list (allowing repetitions).

    Arguments:
      choices: a sequence of elements to choose from.

    """
    if max_length is None:
        max_length = len(choices)

    seq = []
    choice_count = len(choices)
    for i in range(max_length):
        # This choice satisifes: 0 <= choice <= choice_count
        choice_index = random.randint(0, choice_count)
        try:
            choice = choices[choice_index]
        except IndexError:
            # Then choice_index equals choice_count.
            break
        seq.append(choice)
    return seq


def random_ballot_list(choices, count, max_length=None):
    """
    Arguments:
      choices: a sequence of integers.

    """
    ballots = []
    for i in range(count):
        ballot = gen_random_list(choices, max_length=max_length)
        ballots.append(ballot)

    return BallotList(ballots)


def random_contest(candidates):
    ballots = random_ballot_list(range(candidates), 5)
    contest = TestContestInput(candidates, ballots)
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

    test_file = TestInputFile(contests, version="0.2.0-alpha")
    json = test_file.to_json()

    print(json)
