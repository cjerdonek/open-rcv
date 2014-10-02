#!/usr/bin/env python

"""
This module is for trying stuff out while developing.

"""

import sys

from openrcv import counting
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


def main(blt_path, encoding=None):
    counting.count_irv(blt_path)
