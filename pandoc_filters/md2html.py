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
Pandoc filter to transform URLs in hyperlinks from .md to .html.

Sample usage:

    $ pandoc --filter ./md2html.py --write=html --output=README.html README.md

This lets markdown files with relative links that hyperlink to each other
(as supported by GitHub [1]) continue hyperlinking to each other after
being converted to HTML.


[1]: https://github.com/blog/1395-relative-links-in-markup-files

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
