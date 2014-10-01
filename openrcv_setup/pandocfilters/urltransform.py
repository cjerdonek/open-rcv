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

from pandocfilters import toJSONFilter, Link

# From the toJSONFilter() docstring in pandocfilters:
#
# """
# Converts an action into a filter that reads a JSON-formatted
# pandoc document from stdin, transforms it by walking the tree
# with the action, and returns a new JSON-formatted pandoc document
# to stdout.  The argument is a function action(key, value, format, meta),
# where key is the type of the pandoc object (e.g. 'Str', 'Para'),
# value is the contents of the object (e.g. a string for 'Str',
# a list of inline elements for 'Para'), format is the target
# output format (which will be taken for the first command line
# argument if present), and meta is the document's metadata.
# If the function returns None, the object to which it applies
# will remain unchanged.  If it returns an object, the object will
# be replaced.  If it returns a list, the list will be spliced in to
# the list to which the target object belongs.  (So, returning an
# empty list deletes the object.)
# """
#
def transform_url(key, value, format, meta):
    if key != 'Link':
        return None
    # Then value has the following form:
    # [[{'t': 'Str', 'c': 'Contributing'}], ['docs/contributing.md', '']]
    # Extract the URL.
    parsed_url = urlparse(value[1][0])
    if not parsed_url[2].endswith(".md"):
        return None
    # Otherwise, change the md extension to html.
    parsed_url = list(parsed_url)
    path = parsed_url[2]
    parsed_url[2] = path[:-2] + "html"
    value[1][0] = urlunparse(parsed_url)
    return Link(*value)


if __name__ == "__main__":
    toJSONFilter(transform_url)
