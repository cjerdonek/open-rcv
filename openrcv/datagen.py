
"""
Support for generating and managing election data.

This module provides functions to help work with the test cases
in the open-rcv-tests repo.

"""

import random

import openrcv.jsmodels as models
from openrcv.jsmodels import JsonBallot, JsonContest, TestInputFile
from openrcv import utils
from openrcv.utils import FileInfo


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


def gen_random_ballot_list(choices, ballot_count, max_length=None):
    """
    Arguments:
      choices: a sequence of integers.

    """
    ballots = []
    for i in range(ballot_count):
        ballot_choices = gen_random_list(choices, max_length=max_length)
        ballot = JsonBallot(ballot_choices)
        ballots.append(ballot)

    return ballots


def random_contest(candidate_count):
    choices = range(1, candidate_count + 1)
    ballots = gen_random_ballot_list(choices, 5)
    contest = JsonContest(candidate_count, ballots)
    return contest


def create_json_tests():
    contests = []
    for id_, candidate_count in enumerate(range(3, 6), start=1):
        contest = random_contest(candidate_count)
        contest.id = id_
        contest.notes = ("Random contest with {0:d} candidates".
                         format(candidate_count))
        contests.append(contest)

    test_file = TestInputFile(contests, version="0.2.0-alpha")
    return test_file
