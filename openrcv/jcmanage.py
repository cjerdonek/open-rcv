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

"""Support for generating and managing election data.

This module provides functions to help work with the test cases
in the open-rcv-tests repo.
"""

from contextlib import contextmanager
import datetime
import logging
import os
import os.path
from random import choice, random, sample

from openrcv import counting, jcmodels, jsonlib, models, utils
from openrcv.formats import jscase
from openrcv.jcmodels import JsonCaseContestInput, JsonCaseTestInstance, JsonCaseTestsFile
from openrcv.models import ContestInput


PERM_ID_CHARS = "0123456789abcdef"

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


def generate_id(ids):
    """
    Arguments:
      ids: a set of the current IDs.
    """
    while True:
        id_ = "".join(choice(PERM_ID_CHARS) for i in range(8))
        if id_ not in ids:
            break
    return id_


# TODO: test this.
def make_standard_candidate_names(count, names=None):
    if names is None:
        names = CANDIDATE_NAMES
    names = CANDIDATE_NAMES[:count]
    for n in range(len(names) + 1, count + 1):
        names.append("Candidate %d" % n)
    return names


def add_contest_to_contests_file(contest, contests_path):
    """
    Arguments:
      contests_path: a path to a JSON contests file.
    """
    jc_contest = jscase.JsonCaseContestInput.from_model(contest)
    jsobj_contest = jc_contest.to_jsobj()
    data = jsonlib.read_json_path(contests_path)
    data["contests"].append(jsobj_contest)
    jsonlib.write_json(data, path=contests_path)


def clean_contest(contest):
    """Normalize a contest in a JSON contests file."""
    if contest.should_normalize_ballots:
        contest.ballots_resource.normalize()
    if not contest.rule_sets:
        contest.rule_sets = []


def _get_jc_contests_file(contests_path):
    js_contests_file = jsonlib.read_json_path(contests_path)
    jc_contests_file = jcmodels.JsonCaseContestsFile.from_jsobj(js_contests_file)
    return jc_contests_file


def _get_jc_tests_file(tests_dir, rule_set):
    tests_path = os.path.join(tests_dir, "{0}.json".format(rule_set))
    try:
        js_tests_file = jsonlib.read_json_path(tests_path)
    except FileNotFoundError:
        jc_tests_file = JsonCaseTestsFile()
    else:
        jc_tests_file = JsonCaseTestsFile.from_jsobj(js_tests_file)
    return tests_path, jc_tests_file


# TODO: log normalization conversions (e.g. if they are unequal), and use
#   an equality check on the JSON object to know if there was a difference.
def normalize_contests_file(contests_path):
    contests_file = _get_jc_contests_file(contests_path)
    jc_contests = contests_file.contests
    ids = set()
    for id_ in (c.id.lower() for c in jc_contests if c.id):
        if id_ in ids:
            raise Exception("duplicate id_: {0} (lower-cased)".format(id_))
        ids.add(id_)
    for index, jc_contest in enumerate(jc_contests, start=1):
        jc_contest.index = index
        if not jc_contest.id:
            jc_contest.id = generate_id(ids)
        if jc_contest.normalize_ballots:
            contest = jc_contest.to_model()
            contest.ballots_resource.normalize()
            normalized = JsonCaseContestInput.from_model(contest)
            jc_contest.ballots = normalized.ballots
        if not jc_contest.rule_sets:
            jc_contest.rule_sets = []
    jsonlib.write_json(contests_file, path=contests_path)


def update_tests_file(contests_file, contest_inputs, tests_dir, rule_set):
    """
    Arguments:
      contests_file: a JsonCaseContestsFile object.
      rule_set: the name of a rule set.
      tests_dir: path to the tests directory.
    """
    tests_path, tests_file = _get_jc_tests_file(tests_dir, rule_set)

    # Create a mapping from ID to list of JsonCaseTestInstance objects.
    id_to_tests = {}
    # Add the existing tests, while preserving their current order.
    for test in tests_file.test_cases:
        jc_contest = test.input
        jc_contest_id = jc_contest.id
        seq = id_to_tests.setdefault(jc_contest_id, [])
        seq.append(test)
    # Make sure all IDs occur in the mapping.
    for jc_contest in contest_inputs:
        jc_contest_id = jc_contest.id
        try:
            id_to_tests[jc_contest_id]
        except KeyError:
            test = JsonCaseTestInstance()
            id_to_tests[jc_contest_id] = [test]

    # Update the file before saving.
    tests_file.version = contests_file.version
    tests_file.rule_set = rule_set
    tests = []
    index = 1
    # Add the contests in the order they appear in the contests file.
    for jc_contest in contests_file.contests:
        jc_contest_id = jc_contest.id
        for test in id_to_tests[jc_contest_id]:
            test.index = index
            test.input = jc_contest
            tests.append(test)
            index += 1
    tests_file.test_cases = tests
    jsonlib.write_json(tests_file, path=tests_path)


def update_test_inputs(contests_path, tests_dir):
    contests_file = _get_jc_contests_file(contests_path)
    jc_contests = contests_file.contests
    # Create a mapping from rule set to list of JsonCaseContestInput objects.
    rule_sets = {}
    for jc_contest in jc_contests:
        for rule_set in jc_contest.rule_sets:
            seq = rule_sets.setdefault(rule_set, [])
            seq.append(jc_contest)
    for rule_set in sorted(rule_sets.keys()):
        contest_inputs = rule_sets[rule_set]
        update_tests_file(contests_file, contest_inputs, tests_dir, rule_set)


def count_test_case(test):
    """Count a test case, and return a JsonCaseTestOutput object."""
    jc_contest = test.input
    # TODO
    candidates = contest.get_candidate_numbers()
    ballot_stream = JsonBallot.to_ballot_stream(contest.ballots)
    contest_results = count_irv_contest(ballot_stream, candidates)

    # Add results to output.
    output_rounds = test_case.output.rounds
    for round_results in contest_results.rounds:
        json_round = JsonRoundResults()
        json_round.totals = round_results.totals
        output_rounds.append(json_round)
    print(repr(jc_contest))


def update_test_outputs_file(file_path):
    js_tests_file = jsonlib.read_json_path(file_path)
    jc_tests_file = JsonCaseTestsFile.from_jsobj(js_tests_file)
    for test in jc_tests_file.test_cases:
        count_test_case(test)


def update_test_outputs(tests_dir):
    for file_name in os.listdir(tests_dir):
        file_path = os.path.join(tests_dir, file_name)
        update_test_outputs_file(file_path)


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
