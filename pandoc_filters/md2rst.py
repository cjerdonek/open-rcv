#!/usr/bin/env python

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
