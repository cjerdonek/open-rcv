
"""
Support for parsing and writing files in OpenRCV's internal format.

"""

from contextlib import contextmanager
import os

from openrcv.formats.common import Format, FormatWriter
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


class _WriteableBallotsBase(object):

    def __init__(self, resource, stream):
        self.resource = resource
        self.stream = stream

    def write(self, ballot):
        line = to_internal_ballot(ballot)
        self.stream.write(line + "\n")


class BallotsResourceBase(object):

    def read_convert(self, item):
        raise NoImplementation(self)

    def write_convert(self, item):
        raise NoImplementation(self)

    def __init__(self, resource):
        """
        Arguments:
          resource: backing store for the ballots.
        """
        self.resource = resource

    @contextmanager
    def reading(self):
        with self.resource.reading() as stream:
            yield map(self.read_convert, stream)

    @contextmanager
    def writing(self):
        with self.resource.writing() as stream:
            yield _WriteableBallotStream(stream)


class _WriteableBallotStream(object):

    def __init__(self, stream):
        self.stream = stream

    def write(self, ballot):
        line = to_internal_ballot(ballot)
        self.stream.write(line + "\n")


# TODO: get this inheriting from BallotsResourceBase.
class InternalBallotsResource(object):

    def __init__(self, resource):
        """
        Arguments:
          resource: backing store for the resource.
        """
        self.resource = resource

    # TODO: move this to a StreamResourceMixin.
    # TODO: add a count_ballots() method that takes weight into account.
    def count(self):
        with self.reading() as stream:
            return sum(1 for item in stream)

    @contextmanager
    def reading(self):
        with self.resource.reading() as stream:
            yield map(parse_internal_ballot, stream)

    @contextmanager
    def writing(self):
        with self.resource.writing() as stream:
            yield _WriteableBallotStream(stream)


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
