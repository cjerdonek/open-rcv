#!/usr/bin/env python

"""
This module houses the "highest-level" programmatic API.

"""

import sys

from openrcv.parsing import BLTParser
from openrcv.utils import FILE_ENCODING


def do_parse(ballots_path, encoding=None):
    if encoding is None:
        encoding = FILE_ENCODING
    parser = BLTParser()
    info = parser.parse_path(ballots_path)
    print(repr(info))
