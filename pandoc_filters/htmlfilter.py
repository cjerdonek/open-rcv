#!/usr/bin/env python

"""
Pandoc filter to transform URLs in hyperlinks from .md to .html.

This lets markdown files that hyperlink to each other to continue
hyperlinking to each other after being converted to HTML.

Sample usage:

pandoc --filter ./urltransform.py --write=html --output=README.html README.md

"""

import sys
from urllib.parse import urlparse, urlunparse

from pandocfilters import toJSONFilter

from openrcv_setup.pandoc import init_action


def convert_url(url):
    parsed_url = urlparse(url)
    if not parsed_url[2].endswith(".md"):
        return None
    # Otherwise, change the md extension to html.
    parsed_url = list(parsed_url)
    path = parsed_url[2]
    parsed_url[2] = path[:-2] + "html"
    return urlunparse(parsed_url)


if __name__ == "__main__":
    toJSONFilter(init_action(convert_url))
