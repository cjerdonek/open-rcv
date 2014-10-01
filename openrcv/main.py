#!/usr/bin/env python

"""
This module houses the "highest-level" programmatic API.

"""

import sys

from openrcv import models
from openrcv.models import BallotList
from openrcv.parsing import BLTParser
from openrcv.utils import FILE_ENCODING


def do_parse(ballots_path, encoding=None):
    if encoding is None:
        encoding = FILE_ENCODING

    ballots = models.random_ballot_list(range(6), 5)
    #print(repr(ballots.ballots))
    parser = BLTParser()
    info = parser.parse_path(ballots_path)
    print(repr(info))
