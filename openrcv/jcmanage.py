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

"""
Support for generating and managing election data.

This module provides functions to help work with the test cases
in the open-rcv-tests repo.

"""

from contextlib import contextmanager
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


class _ContestCreatorBase(object):

    @contextmanager
    def adding_ballots(self, target_resource):
        raise utils.NoImplementation(self)

    def create_random(self, ballots_resource, candidate_count=None, ballot_count=None):
        """Create a random contest.

        Returns a ContestInput object.
        """
        if ballot_count is None:
            ballot_count = 20
        candidates = make_candidates(candidate_count)

        choices = range(1, candidate_count + 1)
        chooser = BallotGenerator(choices=choices)

        with self.adding_ballots(ballots_resource) as initial_resource:
            chooser.add_random_ballots(initial_resource, ballot_count)

        name = "Random Contest"

        now = datetime.datetime.now()
        # We call int() to remove leading zero-padding.
        dt_string = ('{0:%B} {0:%d}, {0:%Y} {1:d}:{0:%M:%S%p}'
                     .format(now, int(now.strftime("%I"))))
        notes = [
            "Contest has {0:d} candidates and {1:d} ballots.  {2}"
            .format(candidate_count, ballot_count, self.notes),
            "Created on {0}.".format(dt_string),
        ]

        contest = ContestInput(name=name, notes=notes, candidates=candidates,
                               ballots_resource=ballots_resource)

        return contest


class ContestCreator(_ContestCreatorBase):

    """Creates random contest without normalizing ballots."""

    notes = ""

    @contextmanager
    def adding_ballots(self, target_resource):
        yield target_resource


class NormalizedContestCreator(_ContestCreatorBase):

    """Creates random contest with normalized ballots."""

    notes = "Ballots are normalized.  "

    @contextmanager
    def adding_ballots(self, target_resource):
        with models.temp_ballots_resource() as source_resource:
            yield source_resource
            models.normalize_ballots(source_resource, target=target_resource)


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


def count_contest_file(argv):
    rule_set = "san_francisco_irv"
    jsobj = read_json_path(TEST_INPUT_PATH)
    contest_file = JsonContestFile.from_jsobj(jsobj)

    results = JsonTestCaseFile()
    results.version = contest_file.version
    results.rule_set = rule_set
    test_cases = []
    results.test_cases = test_cases

    for id_, contest in enumerate(contest_file.contests, start=1):
        test_case = JsonTestCase()
        test_case.id = id_
        test_case.contest_id = contest.id
        test_case.input.contest = contest

        # Tabulate results.
        candidates = contest.get_candidates()
        ballot_stream = JsonBallot.to_ballot_stream(contest.ballots)
        contest_results = count_irv_contest(ballot_stream, candidates)

        # Add results to output.
        output_rounds = test_case.output.rounds
        for round_results in contest_results.rounds:
            json_round = JsonRoundResults()
            json_round.totals = round_results.totals
            output_rounds.append(json_round)

        test_cases.append(test_case)

    print(results.to_json())
    path = os.path.join(TEST_CASE_DIR, "%s.json" % rule_set)
    write_json(results, path=path)


def make_input_test_file(argv):
    # target_path="sub/open-rcv-tests/contests.json"

    test_file = create_json_tests()
    stream_info = PathInfo("temp.json")
    models.write_json(test_file.to_jsobj(), stream_info)

    with stream_info.open() as f:
        json = f.read()
    print(json)
