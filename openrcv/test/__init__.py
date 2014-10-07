
import logging
import os
import sys

log = logging.getLogger(__name__)

DEFAULT_LEVEL = logging.WARN

# TODO: the code in this module is a hack.
#   Eventually, we want to have a natural "entry point" into the test
#   runner where we can configure logging and share logging code
#   with the non-test scripts (for DRY purposes, common formatting, etc).
if "-m unittest" in sys.argv[0]:
    log_level = DEFAULT_LEVEL
    logging.basicConfig(level=log_level)
    log.warn("*** test logging configured to level: %s\n"
             "  See the file %s.%s to change this." %
             (logging.getLevelName(log_level), __name__, os.path.basename(__file__)))
