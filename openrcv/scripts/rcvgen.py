
"""
The rcv command for counting ballots.

"""

import json
import logging
import sys

from openrcv.counting import count_irv_contest, InternalBallotsNormalizer
from openrcv.datagen import create_json_tests
import openrcv.jsmodels as models
from openrcv.jsmodels import JsonBallot
from openrcv.jsonlib import from_jsobj, read_json_path, to_json, write_json
from openrcv.jsmodels import JsonContestFile, JsonTestCaseFile
from openrcv.scripts.main import main
from openrcv import utils
from openrcv.utils import FileInfo, StringInfo


log = logging.getLogger(__name__)

TEST_INPUT_PATH = "sub/open-rcv-tests/contests.json"


def run_main():
    main(do_rcvgen)

def do_rcvgen(argv):
    normalize_contest_file(argv)


def normalize_contest_file(argv):
    """Normalize a contest file."""
    jsobj = read_json_path(TEST_INPUT_PATH)
    test_file = JsonContestFile.from_jsobj(jsobj)
    for id_, contest in enumerate(test_file.contests, start=1):
        contest.id = id_
        contest.normalize()
    write_json(test_file, path=TEST_INPUT_PATH)


def count_test_file(argv):
    jsobj = read_json_path(TEST_INPUT_PATH)
    log.info("printing JsonContestFile JSON object")
    print(repr(jsobj))
    test_file = JsonContestFile.from_jsobj(jsobj)
    for contest in test_file.contests:
        log.info("contest: %r\n>>>%s" % (contest, contest.to_json()))
        ballot_stream = contest.get_ballot_stream()
        candidates = contest.get_candidates()
        contest_results = count_irv_contest(ballot_stream, candidates)
        print(contest_results.to_json())

    return

    log.info("printing JsonContestFile Python object")
    for contest in test_file.contests:
        print(repr(contest))
    log.info("printing JsonContestFile JSON")
    print(test_file.to_json())


def make_input_test_file(argv):
    # target_path="sub/open-rcv-tests/contests.json"

    test_file = create_json_tests()
    stream_info = FileInfo("temp.json")
    models.write_json(test_file.to_jsobj(), stream_info)

    with stream_info.open() as f:
        json = f.read()
    print(json)
