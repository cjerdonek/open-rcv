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
Support for parsing and writing files in OpenRCV's internal format.

"""

from contextlib import contextmanager
import os

from openrcv.formats.common import Format, FormatWriter
from openrcv import models, streams
from openrcv.streams import StreamResourceBase
from openrcv.utils import join_values, parse_integer_line, FileWriter, NoImplementation


# ASCII makes reading and parsing the file faster.
ENCODING_BALLOT_FILE = 'ascii'


def to_internal_ballot(ballot):
    """Return the ballot as an internal ballot string."""
    # There is no terminal 0 like in the BLT format.
    weight, choices = ballot
    return join_values([weight] + list(choices))


def parse_internal_ballot(line):
    """
    Parse an internal ballot line (with or without a trailing newline).

    This function allows leading and trailing spaces.  ValueError is
    raised if one of the values does not parse to an integer.

    An internal ballot line is a space-delimited string of integers of the
    form--

    "WEIGHT CHOICE1 CHOICE2 CHOICE3 ...".

    """
    ints = parse_integer_line(line)
    weight = next(ints)
    choices = tuple(ints)
    return weight, choices


def internal_ballots_resource(resource):
        """
        Arguments:
          resource: a stream resource which is a backing store for the resource.
        """
        converter = _InternalBallotsConverter()
        return _InternalBallotsResource(resource, converter=converter)


class _InternalBallotsConverter(streams.Converter):

    def from_resource(self, item):
        return parse_internal_ballot(item)

    def to_resource(self, item):
        line = to_internal_ballot(item)
        return line + "\n"


class _InternalBallotsResource(streams.ConvertingResource, models.BallotsResourceMixin):
    pass


class InternalFormat(Format):

    @property
    def contest_writer_cls(self):
        return InternalContestWriter


# TODO: DRY up with BLTContestWriter.
class InternalContestWriter(FormatWriter):

    @property
    def get_output_infos(self):
        return (self.get_output_info, )

    def get_output_info(self, output_dir):
        return os.path.join(self.output_dir, "ballots.txt"), ENCODING_BALLOT_FILE

    def resource_write(self, resource, contest):
        writer = InternalBallotsWriter(resource)
        writer.write_ballots(contest)


# TODO: is this still necessary with InternalBallotsResource?
class InternalBallotsWriter(FileWriter):

    def _write_ballots(self, contest):
        with contest.ballots_resource.reading() as ballots:
            for ballot in ballots:
                self.writeln(to_internal_ballot(ballot))

    def write_ballots(self, contest):
        """
        Arguments:
          contest: a ContestInput object.
        """
        with self.open():
            self._write_ballots(contest)
