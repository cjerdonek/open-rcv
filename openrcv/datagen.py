
"""
Support for generating and managing election data.

This module provides functions to help work with the test cases
in the open-rcv-tests repo.

"""

from contextlib import contextmanager
import logging
from random import randint, random, sample

from openrcv.models import ContestInput
from openrcv import utils


STOP_CHOICE = object()

CANDIDATE_NAMES = """\
Ann
Bob
Carol
Dave
Ellen
Fred
Gwen
Hank
Irene
Joe
Katy
Leo
""".split()


log = logging.getLogger(__name__)


# TODO: add a method to write `n` ballots to a StreamInfo object.
# TODO: the API should accept a ballot store object of some kind (e.g.
#   can be an iterable or file).
# choices = list(range(ns.candidates))
# generator = NonUniqueBallotGenerator()
# print(repr(generator.generate(choices)))
# generator = UniqueBallotGenerator()
# print(repr(generator.generate(choices)))
class BallotGenerator(object):

    """Generates random ballots (allowing duplicates)."""

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

    def make_choices(self):
        chosen = []
        # random.random() returns a float in the range: [0.0, 1.0).
        # A strict inequality is used so that the edge case of 0 undervote
        # is handled correctly.
        if random() < self.undervote:
            return chosen

        choices = self.choices.copy()

        # Choose one choice before adding the "stop" choice.  This ensures
        # that the ballot is not an undervote.
        choice = self.choose(choices)
        chosen.append(choice)
        self.after_choice(choices, choice)

        choices.add(STOP_CHOICE)

        for i in range(self.max_length - 1):
            choice = self.choose(choices)
            if choice is STOP_CHOICE:
                break
            chosen.append(choice)
            self.after_choice(choices, choice)

        return chosen

    def add_random_ballots(self, ballots_resource, count):
        """
        Arguments:
          choices: a sequence of integers.

        """
        with ballots_resource.writing() as stream:
            for i in range(count):
                choices = self.make_choices()
                ballot = 1, choices
                stream.write(ballot)


class UniqueBallotGenerator(BallotGenerator):

    def after_choice(self, choices, choice):
        choices.remove(choice)


# TODO: test this.
def make_candidates(count):
    names = CANDIDATE_NAMES[:count]
    for n in range(len(names) + 1, count + 1):
        names.append("Candidate %d" % n)
    return names


def create_random_contest(ballots_resource, candidate_count=None):
    ballot_count = 20
    candidates = make_candidates(candidate_count)

    choices = range(1, candidate_count + 1)
    chooser = BallotGenerator(choices=choices)
    chooser.add_random_ballots(ballots_resource, ballot_count)

    contest = ContestInput(candidates=candidates, ballots_resource=ballots_resource)

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
