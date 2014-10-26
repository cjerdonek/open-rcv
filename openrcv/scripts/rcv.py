
"""
The rcv command for counting ballots.

"""

import argparse
import logging
import os
import sys

import yaml

from openrcv import counting
from openrcv.jsmodels import JsonTestCaseOutput
from openrcv.scripts.argparse import ArgParser, HelpAction
from openrcv.scripts.argparser import create_argparser
from openrcv.scripts.run import main
from openrcv.utils import logged_open


log = logging.getLogger(__name__)


def run_main():
    parser = create_argparser()
    main(parser, do_func=run_rcv)


# TODO: unit-test this.
def run_rcv(ns):
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
