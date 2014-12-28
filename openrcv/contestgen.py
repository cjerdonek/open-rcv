#
# Copyright (c) 2014 Chris Jerdonek. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

"""Supports the generation of contest data."""


import datetime
from random import random, sample

from openrcv.models import ContestInput


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

STOP_CHOICE = object()


def make_standard_candidate_names(count, names=None):
    if names is None:
        names = CANDIDATE_NAMES
    names = names[:count]
    for n in range(len(names) + 1, count + 1):
        names.append("Person %d" % n)
    return names


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
        """Choose a single element of choices at random.

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
        with ballots_resource.writing() as gen:
            for i in range(count):
                choices = self.make_choices()
                ballot = 1, choices
                gen.send(ballot)


class UniqueBallotGenerator(BallotGenerator):

    def after_choice(self, choices, choice):
        choices.remove(choice)


class ContestCreator(object):

    def make_notes(self, candidate_count, ballot_count):
        now = datetime.datetime.now()
        # We call int() to remove leading zero-padding.
        dt_string = ('{0:%B} {0:%d}, {0:%Y} at {1:d}:{0:%M:%S%p}'
                     .format(now, int(now.strftime("%I"))))
        # TODO: allow for extra notes.
        notes = [
            "Random contest with {0:d} candidates and {1:d} ballots.  "
                                .format(candidate_count, ballot_count),
            "Created on {0}.".format(dt_string),
        ]
        return notes

    def create_random(self, ballots_resource, candidate_count=None, ballot_count=None):
        """Create a random contest.

        Returns a ContestInput object.
        """
        if ballot_count is None:
            ballot_count = 20

        candidates = make_standard_candidate_names(candidate_count)

        choices = range(1, candidate_count + 1)
        chooser = BallotGenerator(choices=choices)
        chooser.add_random_ballots(ballots_resource, ballot_count)

        name = "Random Contest"
        notes = self.make_notes(candidate_count, ballot_count)
        contest = ContestInput(name=name, notes=notes, candidates=candidates,
                               ballots_resource=ballots_resource)
        return contest
