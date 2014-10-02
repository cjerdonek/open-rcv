
"""
Support for counting ballots.

"""

from datetime import datetime
import string

from openrcv.models import RoundResult
from openrcv.parsing import BLTParser


def make_temp_dirname(name):
    """Return a temp directory name."""
    chars = string.ascii_lowercase + "_"
    name = name.lower().replace(" ", "_")
    name = "".join((c for c in name if c in chars))

    now = datetime.now().strftime("%Y%m%d_%H%M%S")

    # For example, "temp_20141002_074531_my_election".
    return "temp_%s_%s" % (now, name)

# This is currently just a test function rather than part of the API.
def count_irv(blt_path, temp_dir=None):
    if temp_dir is None:
        temp_dir = "temp"

    parser = BLTParser()
    info = parser.parse_path(blt_path)
    print(make_temp_dirname(info.name))
