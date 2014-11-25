
"""
The rcv command for counting ballots.

"""

import logging
import os
from textwrap import dedent
import sys

import yaml

from openrcv import counting
from openrcv.datagen import (create_random_contest, temp_ballots_resource, BallotGenerator,
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


def make_random_contest(ns, stdout=None):
    """Generate a random contest."""
    if stdout is None:
        stdout = sys.stdout
    output_dir = ns.output_dir
    format_cls = ns.output_format
    format = format_cls()

    with temp_ballots_resource() as ballots_resource:
        contest = create_random_contest(ballots_resource, candidate_count=ns.candidate_count)
        output_paths = format.write_contest(contest, output_dir=output_dir, stdout=stdout)

    return "\n".join(output_paths) + "\n" if output_paths else None
