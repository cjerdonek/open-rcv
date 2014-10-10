
"""
The rcv command for counting ballots.

"""

import json
import logging
import sys

from openrcv.counting import count_irv_contest, InternalBallotsNormalizer
from openrcv.datagen import create_json_tests
import openrcv.jsmodels as models
from openrcv.jsonlib import from_jsobj, to_json
from openrcv.jsmodels import TestInputFile
from openrcv.scripts.main import main
from openrcv import utils
from openrcv.utils import read_json_path, FileInfo, StringInfo


log = logging.getLogger(__name__)

TEST_INPUT_PATH = "sub/open-rcv-tests/contests.json"


def run_main():
    main(do_rcvgen)

def do_rcvgen(argv):
    update_test_files(argv)

def update_test_files(argv):
    jsobj = read_json_path(TEST_INPUT_PATH)
    test_file = TestInputFile.from_jsobj(jsobj)
    contest = test_file.contests[0]
    ballot_stream = contest.get_ballot_stream()
    output_stream = StringInfo()
    parser = InternalBallotsNormalizer(output_stream)
    parser.parse(ballot_stream)
    print(repr(ballot_stream))

def count_test_file(argv):
    jsobj = read_json_path(TEST_INPUT_PATH)
    log.info("printing TestInputFile JSON object")
    print(repr(jsobj))
    test_file = TestInputFile.from_jsobj(jsobj)
    for contest in test_file.contests:
        log.info("contest: %r\n>>>%s" % (contest, contest.to_json()))
        ballot_stream = contest.get_ballot_stream()
        candidates = contest.get_candidates()
        contest_results = count_irv_contest(ballot_stream, candidates)
        print(contest_results.to_json())

    return

    log.info("printing TestInputFile Python object")
    for contest in test_file.contests:
        print(repr(contest))
    log.info("printing TestInputFile JSON")
    print(test_file.to_json())


def make_input_test_file(argv):
    # target_path="sub/open-rcv-tests/contests.json"

    test_file = create_json_tests()
    stream_info = FileInfo("temp.json")
    models.write_json(test_file.to_jsobj(), stream_info)

    with stream_info.open() as f:
        json = f.read()
    print(json)
