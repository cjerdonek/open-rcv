#!/usr/bin/env python

"""
Pandoc filter to transform URLs in hyperlinks from .md to .html.

This lets markdown files that hyperlink to each other to continue
hyperlinking to each other after being converted to HTML.

Sample usage:

pandoc --filter ./urltransform.py --write=html --output=README.html README.md

"""

import logging
import os
import sys
from urllib.parse import urljoin, urlparse, urlunparse

from pandocfilters import toJSONFilter

from openrcv_setup.pandoc import init_action


GITHUB_URL = "https://github.com/cjerdonek/open-rcv/blob/master/"
PYPI_URL = "https://pypi.python.org/pypi/OpenRCV/"

log = logging.getLogger(os.path.basename(__name__))


def convert_url(url):
    parsed_url = urlparse(url)
    url_path = parsed_url[2]
    if not url_path:
        # Then we assume it is a fragment.
        new_url = urlunparse(parsed_url)
        new_url = urljoin(PYPI_URL, new_url)
        return new_url
    if (not url_path.endswith(".md") and
        url_path != "LICENSE"):
        return None
    # Otherwise, we link back to the GitHub pages.
    log.info(repr(parsed_url))
    # Otherwise, change the md extension to html.
    new_url = urlunparse(parsed_url)
    new_url = urljoin(GITHUB_URL, new_url)
    return new_url


if __name__ == "__main__":
    toJSONFilter(init_action(convert_url))
