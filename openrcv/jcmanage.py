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
import os.path
from random import choice, random, sample

from openrcv.formats import jscase
from openrcv import jcmodels
from openrcv.jcmodels import JsonCaseContestInput, JsonCaseTestsFile
from openrcv import jsonlib, models
from openrcv.models import ContestInput
from openrcv import utils


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


def generate_perm_id(perm_ids):
    """
    Arguments:
      perm_ids: a set of the current perm_id's.
    """
    while True:
        perm_id = "".join(choice(PERM_ID_CHARS) for i in range(8))
        if perm_id not in perm_ids:
            break
    return perm_id


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
    test_case_path = os.path.join(tests_dir, "{0}.json".format(rule_set))
    try:
        js_tests_file = jsonlib.read_json_path(test_case_path)
    except FileNotFoundError:
        jc_tests_file = JsonCaseTestsFile()
    else:
        jc_tests_file = JsonCaseTestsFile.from_jsobj(js_tests_file)
    return jc_tests_file


# TODO: log normalization conversions (e.g. if they are unequal), and use
#   an equality check on the JSON object to know if there was a difference.
def normalize_contests_file(contests_path):
    contests_file = _get_jc_contests_file(contests_path)
    jc_contests = contests_file.contests
    perm_ids = set()
    for perm_id in (c.perm_id.lower() for c in jc_contests if c.perm_id):
        if perm_id in perm_ids:
            raise Exception("duplicate perm_id: {0} (lower-cased)".format(perm_id))
        perm_ids.add(perm_id)
    for index, jc_contest in enumerate(jc_contests, start=1):
        jc_contest.index = index
        if not jc_contest.perm_id:
            jc_contest.perm_id = generate_perm_id(perm_ids)
        if jc_contest.normalize_ballots:
            contest = jc_contest.to_model()
            contest.ballots_resource.normalize()
            normalized = JsonCaseContestInput.from_model(contest)
            jc_contest.ballots = normalized.ballots
        if not jc_contest.rule_sets:
            jc_contest.rule_sets = []
    jsonlib.write_json(contests_file, path=contests_path)


def update_tests_file(contests_file, tests_dir, rule_set):
    tests_file = _get_jc_tests_file(tests_dir, rule_set)
    tests_file.version = contests_file.version
    tests_file.rule_set = rule_set
    # Create a mapping from perm_id to existing JsonCaseTestInstance objects.
    existing_tests = {}
    # TODO
    for jc_contest in jc_contests:
        for rule_set in jc_contest.rule_sets:
            seq = rule_sets.setdefault(rule_set, [])
            seq.append(jc_contest)


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
        update_tests_file(contests_file, tests_dir, rule_set)


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


def count_contest_file(argv):
    rule_set = "san_francisco_irv"
    jsobj = read_json_path(TEST_INPUT_PATH)
    contest_file = JsonContestFile.from_jsobj(jsobj)

    results = JsonCaseTestsFile()
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
        candidates = contest.get_candidate_numbers()
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
