
"""
The rcv command for counting ballots.

"""

import json
import logging
import os
import sys

from openrcv.counting import count_irv_contest, InternalBallotsNormalizer
from openrcv.datagen import create_json_tests
import openrcv.jsmodels as models
from openrcv.jsmodels import JsonBallot
from openrcv.jsonlib import from_jsobj, read_json_path, to_json, write_json
from openrcv.jsmodels import (JsonContestFile, JsonRoundResults, JsonTestCase,
                              JsonTestCaseOutput, JsonTestCaseFile)
from openrcv.scripts.run import main
from openrcv import utils
from openrcv.utils import FileInfo, StringInfo


log = logging.getLogger(__name__)

TEST_INPUT_PATH = "sub/open-rcv-tests/contests.json"
TEST_CASE_DIR = "sub/open-rcv-tests/tests"

def run_main():
    main(do_rcvgen)

def do_rcvgen(argv):
    count_contest_file(argv)


def normalize_contest_file(argv):
    """Normalize a contest file."""
    jsobj = read_json_path(TEST_INPUT_PATH)
    test_file = JsonContestFile.from_jsobj(jsobj)
    for id_, contest in enumerate(test_file.contests, start=1):
        contest.id = id_
        contest.normalize()
    write_json(test_file, path=TEST_INPUT_PATH)


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
    stream_info = FileInfo("temp.json")
    models.write_json(test_file.to_jsobj(), stream_info)

    with stream_info.open() as f:
        json = f.read()
    print(json)
