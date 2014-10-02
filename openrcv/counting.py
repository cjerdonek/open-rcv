
"""
Support for counting ballots.

"""

import os
import string

from openrcv.models import RoundResult
from openrcv.parsing import BLTParser
from openrcv import utils


# This is currently just a test function rather than part of the API.
def count_irv(blt_path, temp_dir=None):
    if temp_dir is None:
        temp_dir = "temp"
    with utils.temp_dir_inside(temp_dir) as sub_dir:
        ballots_path = os.path.join(sub_dir, "ballots.txt")
        parser = BLTParser(ballots_path)
        info = parser.parse_path(blt_path)
    return info
