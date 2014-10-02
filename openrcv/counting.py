
"""
Support for counting ballots.

"""

from datetime import datetime
import os
import string

from openrcv.models import RoundResult
from openrcv.parsing import BLTParser
from openrcv import utils

def make_temp_dirname(name=None):
    """Return a temp directory name."""
    if name is not None:
        chars = string.ascii_lowercase + "_"
        name = name.lower().replace(" ", "_")
        name = "".join((c for c in name if c in chars))

    now = datetime.now().strftime("%Y%m%d_%H%M%S")

    # For example, "temp_20141002_074531_my_election".
    suffix = "" if name is None else "_" + name
    return "temp_%s%s" % (now, suffix)

# This is currently just a test function rather than part of the API.
def count_irv(blt_path, temp_dir=None):
    if temp_dir is None:
        temp_dir = "temp"
    sub_dir = os.path.join(temp_dir, make_temp_dirname())
    # TODO: create a context manager to delete the directory (unless an
    # exception occurs).
    utils.make_dirs(sub_dir)
    ballots_path = os.path.join(sub_dir, "ballots.txt")

    parser = BLTParser(ballots_path)
    info = parser.parse_path(blt_path)
    print(make_temp_dirname(info.name))
