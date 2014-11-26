
"""
Support for generating and managing election data.

This module provides functions to help work with the test cases
in the open-rcv-tests repo.

"""

import datetime
import logging
from random import random, sample

from openrcv import models
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


def create_random_contest(ballots_resource, candidate_count=None, ballot_count=None,
                          normalize=False):
    """Create a random contest.

    Returns a ContestInput object.
    """
    if ballot_count is None:
        ballot_count = 20
    candidates = make_candidates(candidate_count)

    choices = range(1, candidate_count + 1)
    chooser = BallotGenerator(choices=choices)

    # TODO: use subclassing here instead of an if-block.
    if normalize:
        with models.temp_ballots_resource() as source_resource:
            chooser.add_random_ballots(source_resource, ballot_count)
            models.normalize_ballots(source_resource, target=ballots_resource)
    else:
        chooser.add_random_ballots(ballots_resource, ballot_count)

    name = "Random Contest"

    now = datetime.datetime.now()
    # We call int() to remove leading zero-padding.
    dt_string = '{0:%B} {0:%d}, {0:%Y} {1:d}:{0:%M:%S%p}'.format(now, int(now.strftime("%I")))
    notes = [
        "Contest has {0:d} candidates and {1:d} ballots.  {2}".format(candidate_count,
            ballot_count, "Ballots are normalized.  " if normalize else ""),
        "Created on {0}.".format(dt_string),
    ]

    contest = ContestInput(name=name, notes=notes, candidates=candidates, ballots_resource=ballots_resource)

    return contest


# TODO: consider removing this.
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
