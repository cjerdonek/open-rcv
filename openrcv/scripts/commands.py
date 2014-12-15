#
# Copyright (c) 2014 Chris Jerdonek. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

"""Contains the functions for each rcv command-line command."""

from contextlib import contextmanager
import logging
import os
from textwrap import dedent
import sys

import yaml

from openrcv import counting, jcmanage, jcmodels, jsonlib, models, streams
from openrcv.formats import internal, jscase
from openrcv.models import ContestInput
from openrcv.utils import logged_open, PathInfo, StringInfo


log = logging.getLogger(__name__)


# TODO: is this necessary as its own function?
@contextmanager
def temp_ballots_resource():
    with streams.temp_stream_resource() as backing_resource:
        ballots_resource = internal.internal_ballots_resource(backing_resource)
        yield ballots_resource


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
                        normalize=True, stdout=None):
    """Generate a random contest."""
    if stdout is None:
        stdout = sys.stdout

    format = format_cls()
    creator = jcmanage.ContestCreator()

    with temp_ballots_resource() as ballots_resource:
        contest = creator.create_random(ballots_resource, ballot_count=ballot_count,
            candidate_count=candidate_count)
        if normalize:
            contest.ballots_resource.normalize()
        else:
            contest.normalize_ballots = False

        output_paths = format.write_contest(contest, output_dir=output_dir, stdout=stdout)

        # TODO: refactor this out into jcmanage.
        if json_contests_path:
            jc_contest = jscase.JsonCaseContestInput.from_object(contest)
            jsobj_contest = jc_contest.to_jsobj()
            data = jsonlib.read_json_path(json_contests_path)
            data["contests"].append(jsobj_contest)
            jsonlib.write_json(data, path=json_contests_path)

    return "\n".join(output_paths) + "\n" if output_paths else None
