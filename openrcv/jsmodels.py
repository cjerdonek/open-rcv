
"""
Contains models that support JSON serialization.

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

from openrcv.jsonlib import (from_jsobj, Attribute, JsonObjError, JsonableMixin)
from openrcv.models import make_candidates
from openrcv.parsing import make_internal_ballot_line, parse_internal_ballot
from openrcv.utils import StringInfo


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
        return "weight=%r choices=%r" % (self.weight, self.choices)

    def load_jsobj(self, jsobj):
        """
        Arguments:
          jsobj: a space-delimited string of integers of the form
            "WEIGHT CHOICE1 CHOICE2 CHOICE3 ...".

        """
        try:
            weight, choices = parse_internal_ballot(jsobj)
        except ValueError:
            # Can happen with "1 2 abc", for example.
            # ValueError: invalid literal for int() with base 10: 'abc'
            raise JsonObjError("error parsing: %r" % jsobj)
        self.__init__(choices=choices, weight=weight)

    def to_jsobj(self):
        """Return the ballot as a JSON object."""
        return self.to_internal_ballot()

    def to_internal_ballot(self):
        """Return the ballot as an internal ballot string."""
        return make_internal_ballot_line(self.weight, self.choices)


# Inherit from ContestInfo?
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
        Return a StreamInfo object representing the ballots in
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
