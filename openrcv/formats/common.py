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

import sys

from openrcv.streams import FilePathResource, StandardResource
from openrcv.utils import NoImplementation


class Format(object):

    def write_contest(self, contest, output_dir=None, stdout=None):
        """
        Arguments:
          contest: a ContestInput object.
        """
        writer_cls = self.contest_writer_cls
        writer = writer_cls(output_dir=output_dir, stdout=stdout)
        return writer.write_output(contest)


class FormatWriter(object):

    def __init__(self, output_dir=None, stdout=None):
        if stdout is None:
            stdout = sys.stdout
        self.output_dir = output_dir
        self.stdout = stdout

    @property
    def get_output_infos(self):
        raise NoImplementation(self)

    def _make_output_info(self):
        """
        Return stream resources and output paths for the given functions.

        Arguments:
          info_funcs: a single function or an iterable of functions (one
            for each file that needs to be written).  Each function should
            return a 2-tuple of strings: (output_path, file_encoding).
        """
        output_dir = self.output_dir
        resources = []
        output_paths = []
        for get_output_info in self.get_output_infos:
            if not output_dir:
                resource = self.stdout_info()
            else:
                output_path, encoding = get_output_info(output_dir)
                resource = FilePathResource(output_path, encoding=encoding)
                # Only add an output path when not writing to stdout.
                output_paths.append(output_path)
            resources.append(resource)
        return resources, output_paths

    def stdout_info(self):
        """Return a StreamInfo object for stdout."""
        return StandardResource(self.stdout)

    # TODO: get all the FormatWriter classes using this method.
    def write_output(self, *args, **kwargs):
        """
        Arguments:
          info_func: TODO.
        """
        resources, output_paths = self._make_output_info()
        args = list(resources) + list(args)
        self.resource_write(*args)
        return output_paths
