
"""
The rcv command for counting ballots.

"""

import logging
import os

import yaml

from openrcv import counting
from openrcv.datagen import (random_contest, BallotGenerator,
                             UniqueBallotGenerator)
from openrcv.formats.blt import BLTWriter
from openrcv.jsmodels import JsonTestCaseOutput
from openrcv.models import ContestInfo
from openrcv.utils import logged_open


log = logging.getLogger(__name__)


# TODO: unit-test this.
def count(ns):
    input_path = ns.input_path
    with logged_open(input_path) as f:
        config = yaml.load(f)
    # TODO: use a common pattern for accessing config values.
    base_dir = os.path.dirname(input_path)
    config = config['openrcv']
    contests = config['contests']
    contest = contests[0]
    blt_path = os.path.join(base_dir, contest['file'])
    results = counting.count_irv(blt_path)
    json_results = JsonTestCaseOutput.from_contest_results(results)
    print(json_results.to_json())

def rand_contest(ns):
    contest = ContestInfo()
    contest.candidates = ['A', 'B', 'C']
    print(repr(contest))
    writer = BLTWriter()
    writer.write_contest(contest)
    return
    print(repr(ns))
    #contest = random_contest(ns.candidates)

    choices = list(range(ns.candidates))
    generator = NonUniqueBallotGenerator()
    print(repr(generator.generate(choices)))
    generator = UniqueBallotGenerator()
    print(repr(generator.generate(choices)))
    #print(contest)
