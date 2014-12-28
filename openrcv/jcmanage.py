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

"""Support for managing test cases in the open-rcv-tests repo."""

from contextlib import contextmanager
import datetime
import logging
import os
import os.path
from random import choice

from openrcv import contestgen, counting, jcmodels, jsonlib, models, utils
from openrcv.formats import jscase
from openrcv.jcmodels import (JsonCaseContestInput, JsonCaseTestInstance,
                              JsonCaseTestOutput, JsonCaseTestsFile)
from openrcv.models import ContestInput


PERM_ID_CHARS = "0123456789abcdef"


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
# TODO: normalize the candidate names.
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
    """Count a test case, and return a JsonCaseTestOutput object.

    Arguments:
      test: a JsonCaseTestInstance object.
    """
    jc_contest = test.input
    contest = jc_contest.to_model()
    contest_results = counting.count_irv_contest(contest)
    jc_output = JsonCaseTestOutput.from_contest_results(contest_results)
    return jc_output


def update_test_outputs_file(file_path):
    js_tests_file = jsonlib.read_json_path(file_path)
    jc_tests_file = JsonCaseTestsFile.from_jsobj(js_tests_file)
    for test in jc_tests_file.test_cases:
        jc_output = count_test_case(test)
        test.output = jc_output
    jsonlib.write_json(jc_tests_file, path=file_path)


def update_test_outputs(tests_dir):
    for file_name in os.listdir(tests_dir):
        file_path = os.path.join(tests_dir, file_name)
        update_test_outputs_file(file_path)
