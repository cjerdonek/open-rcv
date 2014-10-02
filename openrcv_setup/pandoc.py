
"""
Supporting code for the project's pandoc filters.

"""

import logging
import os

from pandocfilters import Link


log = logging.getLogger(__name__)

def configure_logging():
    """
    Configure setup.py logging with simple settings.

    """
    # Prefix the log messages to distinguish them from other text sent to
    # the error stream.
    format_string = ("%s: %%(name)s: [%%(levelname)s] %%(message)s" %
                     __name__)
    logging.basicConfig(format=format_string, level=logging.INFO)
    log.debug("Debug logging enabled.")

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
def init_action(convert_url):
    """
    Arguments:
      convert_url: a function that accepts an URL path and returns
        a new one.

    """
    configure_logging()

    def transform_url(key, value, format, meta):
        if key != 'Link':
            return None
        # Then value has the following form:
        # [[{'t': 'Str', 'c': 'Contributing'}], ['docs/contributing.md', '']]
        # Extract the URL.
        url = value[1][0]
        new_url = convert_url(url)
        if new_url is None:
            return None
        log.info("converting URL:\n"
                 "   %s\n"
                 "-->%s" % (url, new_url))
        value[1][0] = new_url
        return Link(*value)
    return transform_url
