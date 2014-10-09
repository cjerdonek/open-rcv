
"""
Contains object models for this project.

For the purposes of this project, "JSON object" (abbreviated in code
as "jsobj") means a Python object with a natural conversion to JSON.
These are objects composed of built-in type instances like Python
lists, dicts, strings, ints, etc.

Instances of most models in this module (those inheriting from JsonableMixin)
can be converted to a JSON object by calling a to_jsobj() method on the
instance.  Similarly, calling to_json() on the object returns JSON.  We
call these objects "jsonable."

We use the convention that "None" attribute values do not get converted
to JSON, and JSON null values correspond to the JS_NULL object.
This decision is based on the thinking that having "null" appear in the
JSON should be a deliberate decision (and in the Python world, None
is the usual default value).

"""

# TODO: move non-serializable models to a different location?

from openrcv.jsonlib import (from_jsobj, Attribute, JsonObjError, JsonableMixin)
from openrcv.utils import StringInfo


def make_candidates(candidate_count):
    """
    Return an iterable of candidate numbers.

    """
    return range(1, candidate_count + 1)


class ContestInfo(object):

    """
    Attributes:
      candidates: a list of the names of all candidates, in numeric order.
      name: name of contest.
      seat_count: integer number of winners.

    """

    ballot_count = 0

    def __init__(self):
        pass

    def get_candidates(self):
        """Return an iterable of the candidate numbers."""
        return make_candidates(len(self.candidates))

    # TODO: look up the proper return type.
    def __repr__(self):
        return self.name




class JsonBallot(JsonableMixin):

    """
    Represents a ballot for a JSON test case.

    This class should be used only for tests and small sets of ballots.
    For large numbers of ballots, ballot data should be kept on the
    file system, and ballots should not be converted to instances of
    user-defined classes.

    """

    data_attrs = (Attribute('choices'),
                  Attribute('weight'))
    attrs = data_attrs

    def __init__(self, choices=None, weight=1):
        if choices is None:
            choices = []
        self.choices = choices
        self.weight = weight

    def repr_desc(self):
        """Return additional info for __repr__()."""
        return "jsobj=%r" % self.to_jsobj()

    def load_jsobj(self, jsobj):
        """
        Arguments:
          jsobj: a space-delimited string of integers of the form
            "WEIGHT CHOICE1 CHOICE2 CHOICE3 ...".

        """
        try:
            numbers = [int(s) for s in jsobj.split(" ")]
        except (AttributeError, ValueError):
            # Can happen for example with: "2 ".
            # ValueError: invalid literal for int() with base 10: ''
            raise JsonObjError("error parsing: %r" % jsobj)
        weight = numbers.pop(0)
        self.__init__(choices=numbers, weight=weight)

    def to_jsobj(self):
        """Return the ballot as a JSON object."""
        values = [self.weight] + self.choices
        return " ".join((str(v) for v in values))

    def to_internal_ballot(self):
        """Return the ballot as an internal ballot string."""
        return self.to_jsobj()


class JsonContest(JsonableMixin):

    """
    Represents a contest for a JSON test case.

    """

    meta_attrs = (Attribute('id'),
                  Attribute('notes'))
    data_attrs = (Attribute('ballots', cls=JsonBallot),
                  Attribute('candidate_count'))
    attrs = tuple(list(data_attrs) + list(meta_attrs))

    def __init__(self, candidate_count=None, ballots=None, id_=None, notes=None):
        """
        Arguments:
          candidate_count: integer number of candidates

        """
        self.ballots = ballots
        self.candidate_count = candidate_count
        self.id = id_
        self.notes = notes

    def repr_desc(self):
        return "id=%s candidate_count=%s" % (self.id, self.candidate_count)

    def get_candidates(self):
        """Return an iterable of the candidate numbers."""
        return make_candidates(self.candidate_count)

    def get_ballot_stream(self):
        """
        Return an utils.StreamInfo object representing the ballots in
          internal ballot file format.

        """
        lines = (b.to_internal_ballot() for b in self.ballots)
        ballots_string = "\n".join(lines)
        return StringInfo(ballots_string)


# TODO: rename this to JsonInputFile.
class TestInputFile(JsonableMixin):

    """
    Represents an input file for open-rcv-tests.

    """

    meta_attrs = (Attribute('version'), )
    data_attrs = (Attribute('contests', cls=JsonContest), )
    attrs = tuple(list(data_attrs) + list(meta_attrs))

    def __init__(self, contests=None, version=None):
        """
        Arguments:
          contests: an iterable of JsonContest objects.

        """
        self.contests = contests
        self.version = version


class JsonRoundResults(JsonableMixin):

    """
    Represents the results of a round for testing purposes.

    """

    data_attrs = (Attribute('totals'), )
    attrs = data_attrs

    def __init__(self, totals):
        """
        Arguments:
          totals: dict of candidate number to vote total.

        """
        self.totals = totals


class JsonContestResults(JsonableMixin):

    """
    Represents contest results for testing purposes.

    """

    meta_attrs = (Attribute('id'), )
    data_attrs = (Attribute('rounds', cls=JsonContest), )
    attrs = data_attrs

    def __init__(self, rounds=None, id_=None):
        """
        Arguments:
          rounds: an iterable of JsonRoundResults objects.

        """
        self.id = id_
        self.rounds = rounds

    def repr_desc(self):
        return "rounds=%s" % (len(self.rounds), )
