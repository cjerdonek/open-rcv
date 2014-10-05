
"""
Support for generating and managing election data.

This module provides functions to help work with the test cases
in the open-rcv-tests repo.

"""

import random

from openrcv import models
from openrcv.models import TestBallot, TestContestInput, TestInputFile
from openrcv import utils
from openrcv.utils import FileInfo

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


def gen_random_ballot_list(choices, ballot_count, max_length=None):
    """
    Arguments:
      choices: a sequence of integers.

    """
    ballots = []
    for i in range(ballot_count):
        ballot_choices = gen_random_list(choices, max_length=max_length)
        ballot = TestBallot(ballot_choices)
        ballots.append(ballot)

    return ballots


def random_contest(candidates):
    ballots = gen_random_ballot_list(range(candidates), 5)
    contest = TestContestInput(candidates, ballots)
    return contest


def create_json_tests(target_path):
    contests = []
    for id_, count in enumerate(range(3, 6)):
        contest = random_contest(count)
        contest.id = id_
        contest.note = "foo"
        contests.append(contest)

    test_file = TestInputFile(contests, version="0.2.0-alpha")
    stream_info = FileInfo("temp.json")
    models.write_json(test_file.to_jsobj(), stream_info)

    #print(json)
