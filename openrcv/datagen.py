
"""
Support for generating and managing election data.

This module provides functions to help work with the test cases
in the open-rcv-tests repo.

"""

from random import randint, random, sample
import openrcv.jsmodels as models
from openrcv.jsmodels import JsonBallot, JsonContest, JsonContestFile
from openrcv import utils
from openrcv.utils import FileInfo


STOP_CHOICE = object()


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
        choice_index = randint(0, choice_count)
        try:
            choice = choices[choice_index]
        except IndexError:
            # Then choice_index equals choice_count.
            break
        seq.append(choice)
    return seq


# TODO: add a method to write `n` ballots to a StreamInfo object.
class BallotGenerator(object):

    """
    Generates random ballots (allowing duplicates).

    """

    def __init__(self, choices, max_length=None, undervote=0.1):
        """
        Arguments:
          choices: an iterable of choices from which to choose.
          max_length: the maximum length of a ballot.  Defaults to the
            number of choices.
          undervote: probability of selecting an undervote.

        """
        if max_length is None:
            max_length = len(choices)

        self.choices = set(choices)
        self.max_length = max_length
        self.undervote = undervote

    def choose(self, choices):
        """
        Choose a single element of choices at random.

        Arguments:
          choices: a sequence or set of objects.

        """
        # random.sample() returns a k-length list.
        return sample(choices, 1)[0]

    def after_choice(self, choices, choice):
        pass

    def make_ballot(self):
        ballot = []
        # random.random() returns a float in the range: [0.0, 1.0).
        # A strict inequality is used so that the edge case of 0 undervote
        # is handled correctly.
        if random() < self.undervote:
            return ballot

        choices = self.choices.copy()

        # Choose one choice before adding the "stop" choice.  This ensures
        # that the ballot is not an undervote.
        choice = self.choose(choices)
        ballot.append(choice)
        self.after_choice(choices, choice)

        choices.add(STOP_CHOICE)

        for i in range(self.max_length - 1):
            choice = self.choose(choices)
            if choice is STOP_CHOICE:
                break
            ballot.append(choice)
            self.after_choice(choices, choice)

        return ballot


class UniqueBallotGenerator(BallotGenerator):

    def after_choice(self, choices, choice):
        choices.remove(choice)


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


# TODO: this should return a non-JSON Contest object.
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

    test_file = JsonContestFile(contests, version="0.2.0-alpha")
    return test_file
