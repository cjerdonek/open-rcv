
"""
Internal models that do not require JSON serialization.

"""

from contextlib import contextmanager

from openrcv.utils import tracked, ReprMixin


def make_candidates(candidate_count):
    """
    Return an iterable of candidate numbers.

    """
    return range(1, candidate_count + 1)


class BallotsResourceBase(object):

    """
    An instance of this class is a context manager factory function
    for managing the resource of an iterable of ballots.

    An instance of this class could be used as follows, for example:

        with ballot_resource() as ballots:
            for ballot in ballots:
                # Handle ballot.
                ...

    This resembles the pattern of opening a file and reading its lines.
    One reason to encapsulate ballots as a context manager as opposed to
    an iterable is that ballots are often stored as a file.  Thus,
    implementations should really support the act of opening and closing
    the ballot file when the ballots are needed (i.e. managing the file
    resource).  This is preferable to opening a handle to a ballot
    file earlier than needed and then keeping the file open.
    """

    item_name = 'ballot'

    @contextmanager
    def __call__(self):
        with self.resource() as items:
            with tracked(items, self.item_name) as tracked_items:
                yield tracked_items


class BallotsResource(BallotsResourceBase):

    """A resource wrapper for a raw iterable of ballots."""

    def __init__(self, ballots):
        """
        Arguments:
          ballots: an iterable of ballots.
        """
        self.ballots = ballots

    @contextmanager
    def resource(self):
        yield self.ballots


class BallotStreamResource(BallotsResourceBase):

    def __init__(self, stream_info, parse=None):
        """
        Arguments:
          parse: a function that accepts a line and returns the object
            it parses to.
        """
        if parse is None:
            parse = lambda line: line
        self.parse = parse
        self.stream_info = stream_info

    @contextmanager
    def resource(self):
        with self.stream_info.open() as f:
            with tracked(f, 'line') as lines:
                parse = self.parse
                ballots = map(parse, lines)
                yield ballots


# TODO: rename to ContestInput.
class ContestInfo(ReprMixin):

    """
    Attributes:
      ballots_resource: a context manager factory function that exposes a
        ballot stream.  This should be a BallotsResourceBase object.
      candidates: an iterable of the names of all candidates, in numeric
        order of their ballot ID.
      name: contest name.
      seat_count: integer number of winners.
    """

    ballot_count = 0

    def __init__(self, seat_count=None, name=None):
        if seat_count is None:
            seat_count = 1
        if name is None:
            name = "Election Contest"

        self.ballots_resource = None
        self.candidates = []
        self.name = name

        self.seat_count = seat_count

    def repr_desc(self):
        return "name=%r, candidates=%d" % (self.name, len(self.candidates))

    # TODO: give this method or more accurate name.
    def get_candidates(self):
        """Return an iterable of the candidate numbers."""
        return make_candidates(len(self.candidates))


class RoundResults(object):

    """
    Represents contest results.

    """

    def __init__(self, totals):
        """
        Arguments:
          totals: dict of candidate number to vote total.

        """
        self.totals = totals


class ContestResults(ReprMixin):

    """
    Represents contest results.

    """

    def __init__(self, rounds=None):
        self.rounds = rounds

    def repr_desc(self):
        return "rounds=%s" % (len(self.rounds), )
