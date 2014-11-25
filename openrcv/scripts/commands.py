
"""
The rcv command for counting ballots.

"""

import logging
import os
from textwrap import dedent
import sys

import yaml

from openrcv import counting
from openrcv.datagen import (random_contest, temp_ballots_resource, BallotGenerator,
                             UniqueBallotGenerator)
from openrcv.formats.internal import parse_internal_ballot
from openrcv.jcmodels import JsonTestCaseOutput
from openrcv.models import BallotStreamResource, ContestInput
from openrcv.utils import logged_open, PathInfo, StringInfo


log = logging.getLogger(__name__)


# TODO: unit-test this.
def count(ns, stdout=None):
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


def rand_contest(ns, stdout=None):
    # contest = ContestInput(id_=0)
    # contest.candidates = ['A', 'B', 'C']
    # contest.seat_count = 1
    # ballot_stream_info = StringInfo(dedent("""\
    # 2 1 1
    # 3 5 1
    # """))
    # ballots_resource = BallotStreamResource(ballot_stream_info, parse=parse_internal_ballot)
    # contest.ballots_resource = ballots_resource
    #
    # choices = list(range(ns.candidates))
    # generator = NonUniqueBallotGenerator()
    # print(repr(generator.generate(choices)))
    # generator = UniqueBallotGenerator()
    # print(repr(generator.generate(choices)))
    #print(contest)

    if stdout is None:
        stdout = sys.stdout
    output_dir = ns.output_dir
    format_cls = ns.output_format

    with temp_ballots_resource() as ballots_resource:
        contest = random_contest(ballots_resource, candidate_count=ns.candidate_count)

        format = format_cls()
        output_paths = format.write_contest(contest, output_dir=output_dir, stdout=stdout)

    return "\n".join(output_paths) + "\n" if output_paths else None
