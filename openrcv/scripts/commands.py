
"""Contains the functions for each rcv command-line command."""

import logging
import os
from textwrap import dedent
import sys

import yaml

from openrcv import counting
from openrcv import jcmanage
from openrcv.formats import jscase
from openrcv.formats.internal import parse_internal_ballot
from openrcv import jcmodels, jsonlib, models
from openrcv.models import BallotStreamResource, ContestInput
from openrcv.utils import logged_open, PathInfo, StringInfo


log = logging.getLogger(__name__)

# TODO: finish removing references to ns in this module.
#  This will decouple the argparse definitions from these functions.
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
    json_results = jcmodels.JsonTestCaseOutput.from_contest_results(results)
    print(json_results.to_json())


def make_random_contest(ballot_count, candidate_count, format_cls,
                        json_contests_path, output_dir,
                        normalize=False, stdout=None):
    """Generate a random contest."""
    if stdout is None:
        stdout = sys.stdout
    format = format_cls()

    creator_cls = (jcmanage.NormalizedContestCreator if normalize else
                   jcmanage.ContestCreator)
    creator = creator_cls()
    with models.temp_ballots_resource() as ballots_resource:
        contest = creator.create_random(ballots_resource, ballot_count=ballot_count,
            candidate_count=candidate_count)
        output_paths = format.write_contest(contest, output_dir=output_dir, stdout=stdout)

        # TODO: refactor this out into jcmanage.
        if json_contests_path:
            jc_contest = jscase.JsonCaseContestInput.from_object(contest)
            jsobj_contest = jc_contest.to_jsobj()
            data = jsonlib.read_json_path(json_contests_path)
            data["contests"].append(jsobj_contest)
            jsonlib.write_json(data, path=json_contests_path)

    return "\n".join(output_paths) + "\n" if output_paths else None


# TODO: refactor code out into jcmanage.
# TODO: log normalization conversions (e.g. if they are unequal).
def clean_contests(json_path):
    jsobj = jsonlib.read_json_path(json_path)
    test_file = jcmodels.JsonCaseContestsFile.from_jsobj(jsobj)
    jc_contests = []
    for id_, jc_contest in enumerate(test_file.contests, start=1):
        contest = jc_contest.to_model()
        contest.id = id_
        contest.normalize()
    #jsonlib.write_json(test_file, path=json_path)
