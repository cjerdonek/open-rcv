#!/usr/bin/env python

"""
This module is for trying stuff out while developing.

"""

import sys

from openrcv import models
from openrcv.models import BallotList
from openrcv.parsing import BLTParser
from openrcv.utils import FILE_ENCODING


def make_json_tests():
    contests = []
    for count in range(3, 6):
        contest = models.random_contest(count)
        contests.append(contest)

    contests_obj = [c.__jsobj__() for c in contests]

    tests_jobj = {
        "_version": "0.1.0-alpha",
        "contests": contests_obj
    }
    json = models.to_json(tests_jobj)

    print(json)

def do_parse(ballots_path, encoding=None):
    if encoding is None:
        encoding = FILE_ENCODING
    parser = BLTParser()
    info = parser.parse_path(ballots_path)
    print(repr(info))
