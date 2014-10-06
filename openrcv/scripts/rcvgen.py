
"""
The rcv command for counting ballots.

"""

import logging
import sys

from openrcv.datagen import create_json_tests
from openrcv import models
from openrcv.scripts.main import main
from openrcv.utils import FileInfo

log = logging.getLogger(__name__)


def run_main():
    main(do_rcvgen)

def do_rcvgen(argv):
    # target_path="sub/open-rcv-tests/contests.json"

    test_file = create_json_tests()
    stream_info = FileInfo("temp.json")
    models.write_json(test_file.to_jsobj(), stream_info)

    with stream_info.open() as f:
        json = f.read()
    print(json)
