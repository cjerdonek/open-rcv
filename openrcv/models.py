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

"""Internal models that do not require JSON serialization.

Ballot Model
------------

For now, the "Ballot" object is not represented by a class.  It is
simply a `(weight, choices)` 2-tuple, where `weight` is a number and
choices is a tuple of integer choice ID's.
"""

from contextlib import contextmanager
import logging
import tempfile

# It is deliberate that this module does not depend on any modules
# in openrcv.formats.
from openrcv import streams, utils
from openrcv.utils import ReprMixin


log = logging.getLogger(__name__)


def make_candidates(candidate_count):
    """
    Return an iterable of candidate numbers.
    """
    return range(1, candidate_count + 1)


# TODO: allow ordering and compressing to be done separately.
def normalize_ballots_to(source, target):
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

    with target.writing() as gen:
        for choices in sorted_choices:
            weight = choices_dict[choices]
            ballot = weight, choices
            gen.send(ballot)


def normalize_ballots(ballots_resource):
    """Normalize the given ballots in place.

    Arguments:
      ballots_resource: a ballots resource.
    """
    with ballots_resource.replacement() as temp_resource:
        normalize_ballots_to(ballots_resource, temp_resource)


class BallotsResourceMixin(object):

    def count_ballots(self):
        with self.resource.reading() as gen:
            return sum(weight for weight, choices in gen)

    def normalize(self):
        normalize_ballots(self)


class BallotsResource(streams.WrapperResource, BallotsResourceMixin):
    pass


class ContestInput(ReprMixin):

    """
    Attributes:
      ballots_resource: a BallotsResource object.
      candidates: an iterable of the names of all candidates, in numeric
        order of their ballot ID.
      name: contest name.
      seat_count: integer number of winners.
    """

    # We include an underscore at the end of id_ since id() is a built-in.
    # TODO: test defaults -- especially properties of default ballots resource.
    def __init__(self, id_=None, name=None, candidates=None, seat_count=None,
                 ballots_resource=None, notes=None, normalize_ballots=None):
        if ballots_resource is None:
            ballots_resource = streams.NullStreamResource()
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
        self.normalize_ballots = normalize_ballots
        self.notes = notes
        self.seat_count = seat_count

    def repr_info(self):
        return "id=%r, name=%r" % (self.id, self.name)

    # TODO: give this method a more accurate name.
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

    def repr_info(self):
        return "rounds=%s" % (len(self.rounds), )
