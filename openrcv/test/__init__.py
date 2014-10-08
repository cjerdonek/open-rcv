
import logging
import os
import sys

log = logging.getLogger(__name__)

DEFAULT_LEVEL = logging.CRITICAL

# TODO: the code in this module is a hack.
#   Eventually, we want to have a natural "entry point" into the test
#   runner where we can configure logging and share logging code
#   with the non-test scripts (for DRY purposes, common formatting, etc).
if "-m unittest" in sys.argv[0]:
    log_level = DEFAULT_LEVEL
    logging.basicConfig(level=log_level)
    # TODO: let the user change the log level from the command-line.
    #   (See the code comment above.)
    msg = ("stderr: *** logging configured for test: root logger set to: %s\n"
           "  See the module %s.%s to temporarily change this." %
           (logging.getLevelName(log_level), __name__, os.path.basename(__file__)))
    print(msg, file=sys.stderr)
