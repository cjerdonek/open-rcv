
"""
Support for counting ballots.

"""

from openrcv.parsing import BLTParser


# This is currently just a test function rather than part of the API.
def count_irv(blt_path):
    parser = BLTParser()
    info = parser.parse_path(blt_path)
