
"""
Support for parsing and writing files in OpenRCV's internal format.

"""

from openrcv.formats.common import FormatWriter


BLT_ENCODING = 'utf-8'

# TODO: move the code to parse BLT files here.

class InternalWriter(FormatWriter):

    @classmethod
    def make_path_info(cls, path):
        return PathInfo(path, encoding=BLT_ENCODING)

