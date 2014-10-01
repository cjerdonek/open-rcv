#!/usr/bin/env python

"""
Pandoc filter to transform URLs in hyperlinks from .md to .html.

This lets markdown files that hyperlink to each other to continue
hyperlinking to each other after being converted to HTML.

Sample usage:

pandoc --filter ./urltransform.py --write=html --output=README.html README.md

"""

import sys
from urllib.parse import urljoin, urlparse, urlunparse

from pandocfilters import toJSONFilter

from openrcv_setup.pandoc import init_action


URL_PREFIX = "https://github.com/cjerdonek/open-rcv/blob/master/"

def convert_url(url):
    parsed_url = urlparse(url)
    if not parsed_url[2].endswith(".md"):
        return None
    # Otherwise, change the md extension to html.
    new_url = urlunparse(parsed_url)
    new_url = urljoin(URL_PREFIX, new_url)
    return new_url


if __name__ == "__main__":
    toJSONFilter(init_action(convert_url))
