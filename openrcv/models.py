
"""
Internal models that do not require JSON serialization.

Ballot Model
------------

For now, the "Ballot" object is not represented by a class.  It is
simply a `(weight, choices)` 2-tuple, where `weight` is a number and
choices is a tuple of integer choice ID's.

"""

from contextlib import contextmanager
import logging
import tempfile

from openrcv.formats import internal
from openrcv import streams
from openrcv.streams import NullStreamResource, ReadWriteFileResource
from openrcv.utils import ReprMixin


log = logging.getLogger(__name__)


def make_candidates(candidate_count):
    """
    Return an iterable of candidate numbers.
    """
    return range(1, candidate_count + 1)


@contextmanager
def temp_ballots_resource():
    with streams.temp_stream_resource() as backing_resource:
        ballots_resource = internal.InternalBallotsResource(backing_resource)
        yield ballots_resource


# TODO: remove this in favor of the ballots resource version.
def normalized_ballots(lines):
    """

    """
    parse_internal_ballot = internal.parse_internal_ballot
    # A dict mapping tuples of choices to the cumulative weight.
    choices_dict = {}

    for line in lines:
        weight, choices = parse_internal_ballot(line)
        try:
            choices_dict[choices] += weight
        except KeyError:
            # Then we are adding the choices for the first time.
            choices_dict[choices] = weight

    sorted_choices = sorted(choices_dict.keys())

    def iterator():
        for choices in sorted_choices:
            weight = choices_dict[choices]
            yield weight, choices

    return iterator()


# TODO: allow ordering and compressing to be done separately.
# TODO: think about proper use of yield here.
def normalize_ballots(source, target):
    """
    Normalize ballots by ordering and "compressing" them.

    This function orders the ballots lexicographically by the list of
    choices on each ballot, and also uses the weight component to "compress"
    ballots having identical choices.

    Arguments:
      source: source ballots resource.
      target: target ballots resource.

    TODO: incorporate some of the wording below into the above.

    This class takes a StreamInfo of internal ballots and returns a
    new StreamInfo that represents an equivalent set of internal ballots,
    but both "compressed" (by using the weight component) and ordered
    lexicographically for readability by the list of choices on the ballot.
    """
    # A dict mapping tuples of choices to the cumulative weight.
    choices_dict = {}

    with source.reading() as ballots:
        for weight, choices in ballots:
            try:
                choices_dict[choices] += weight
            except KeyError:
                # Then we are adding the choices for the first time.
                choices_dict[choices] = weight
        sorted_choices = sorted(choices_dict.keys())

    with target.writing() as ballots:
        for choices in sorted_choices:
            weight = choices_dict[choices]
            ballot = weight, choices
            ballots.write(ballot)


# TODO: remove this.
class BallotsResourceBase(object):


    item_name = 'ballot'

    @contextmanager
    def __call__(self):
        with self.resource() as items:
            yield items


# TODO: define a read-write interface for this class.
# TODO: use the same class as BallotsResource.
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
        with self.stream_info.open() as lines:
            parse = self.parse
            ballots = map(parse, lines)
            yield ballots


# TODO: add id and notes.
class ContestInput(ReprMixin):

    # TODO: fix the description of ballots.
    """
    Attributes:
      ballots: a context manager factory function that yields an
        iterable of ballots (e.g. a BallotsResourceBase object).
      candidates: an iterable of the names of all candidates, in numeric
        order of their ballot ID.
      name: contest name.
      seat_count: integer number of winners.
    """

    ballot_count = 0

    # TODO: test defaults -- especially properties of default ballots resource.
    def __init__(self, id_=None, name=None, candidates=None, seat_count=None,
                 ballots_resource=None, notes=None):
        if ballots_resource is None:
            ballots_resource = NullStreamResource()
        if candidates is None:
            candidates = []
        if id_ is None:
            id_ = 0
        if seat_count is None:
            seat_count = 1

        self.ballots_resource = ballots_resource
        self.candidates = candidates
        self.id = id_
        self.name = name
        self.notes = notes
        self.seat_count = seat_count

    def repr_info(self):
        return "id=%r, name=%r" % (self.id, self.name)

    # TODO: give this method a more accurate name.
    def get_candidates(self):
        """Return an iterable of the candidate numbers."""
        return make_candidates(len(self.candidates))

    # TODO: consider removing this, otherwise implement it.
    def normalize(self):
        """Modifies the current contest in place."""
        ballot_stream = JsonBallot.to_ballot_stream(self.ballots)
        output_stream = StringInfo()
        parser = InternalBallotsNormalizer(output_stream)
        parser.parse(ballot_stream)
        new_ballots = JsonBallot.from_ballot_stream(output_stream)
        self.ballots = new_ballots


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

    def repr_info(self):
        return "rounds=%s" % (len(self.rounds), )
