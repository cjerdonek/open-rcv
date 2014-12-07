#!/usr/bin/env python
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

"""
Python Pandoc filter [1] for converting a GitHub markdown file to a Python
reST long_description (suitable for display on PyPI).

Sample usage:

    $ pandoc --filter ./md2rst.py --write=rst --output=long_description.rst README.md

PyPI's reST rendering breaks on things like relative links (supported by
GitHub [1]), and anchor fragments.  This filter converts these links
to links that will continue to work once on PyPI.

See also this PyPI bug report [3].


[1]: https://github.com/jgm/pandocfilters
[2]: https://github.com/blog/1395-relative-links-in-markup-files
[3]: https://bitbucket.org/pypa/pypi/issue/161/rest-formatting-fails-and-there-is-no-way

"""

import logging
import os
import sys
from urllib.parse import urljoin, urlparse, urlunparse

from pandocfilters import toJSONFilter

from openrcv_setup.pandoc import init_action


GITHUB_URL = "https://github.com/cjerdonek/open-rcv/blob/master/"
PYPI_URL = "https://pypi.python.org/pypi/OpenRCV/"

log = logging.getLogger(__file__)


def convert_url(url):
    """Convert URL appearing in a markdown file to a new URL.

    Returns None if URL should remain same.
    """
    parsed_url = urlparse(url)
    log.debug(repr(parsed_url))
    url_path = parsed_url[2]
    if not url_path:
        # Then we assume it is a fragment.
        new_url = urlunparse(parsed_url)
        new_url = urljoin(PYPI_URL, new_url)
        return new_url
    if (not url_path.endswith(".md") and
        url_path != "LICENSE"):
        return None
    # Otherwise, we link back to the original GitHub pages.
    new_url = urlunparse(parsed_url)
    new_url = urljoin(GITHUB_URL, new_url)
    return new_url


if __name__ == "__main__":
    toJSONFilter(init_action(convert_url))
