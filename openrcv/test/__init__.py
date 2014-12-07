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
