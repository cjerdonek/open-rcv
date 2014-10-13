
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

from openrcv.counting import InternalBallotsNormalizer
from openrcv.jsonlib import (from_jsobj, Attribute, JsonObjError, JsonableMixin)
from openrcv.models import make_candidates, ContestResults, RoundResults
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

    @staticmethod
    def to_ballot_stream(ballots):
        """
        Convert an iterable of ballots into a StreamInfo object.

        The StreamInfo represents the ballots in internal ballot file format.

        """
        lines = (b.to_internal_ballot(final="\n") for b in ballots)
        ballots_string = "".join(lines)
        return StringInfo(ballots_string)

    @classmethod
    def from_ballot_stream(cls, ballot_stream):
        """
        Return an iterable of JsonBallot objects.

        Arguments:
          ballot_stream: a StreamInfo object of internal ballots.

        """
        # TODO: would it help to create a general method to iterate through
        # internal ballots in a ballot stream?  Also, if we do this, we
        # could use a Parser, which would provide more error info.
        ballots = []
        with ballot_stream.open() as f:
            for line in f:
                weight, choices = parse_internal_ballot(line)
                ballot = cls(choices=choices, weight=weight)
                ballots.append(ballot)
        return ballots

    data_attrs = (Attribute('choices'),
                  Attribute('weight'))
    attrs = data_attrs

    def __init__(self, choices=None, weight=1):
        if choices is None:
            choices = ()
        self.choices = tuple(choices)
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

    def to_internal_ballot(self, final=''):
        """Return the ballot as an internal ballot string."""
        return make_internal_ballot_line(self.weight, self.choices, final=final)


# TODO: inherit from ContestInfo?
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

    def normalize(self):
        """
        Modifies the current contest in place.

        """
        ballot_stream = JsonBallot.to_ballot_stream(self.ballots)
        output_stream = StringInfo()
        parser = InternalBallotsNormalizer(output_stream)
        parser.parse(ballot_stream)
        new_ballots = JsonBallot.from_ballot_stream(output_stream)
        self.ballots = new_ballots


class JsonContestFile(JsonableMixin):

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

    def repr_desc(self):
        return "version=%s contests=%d" % (self.version, len(self.contests))


class JsonRoundResults(RoundResults, JsonableMixin):

    """
    Represents the results of a round for testing purposes.

    """

    data_attrs = (Attribute('totals'), )
    attrs = data_attrs

    def __init__(self, totals=None):
        self.totals = totals


# TODO: remove this.
class JsonContestResults(ContestResults, JsonableMixin):

    """
    Represents contest results for testing purposes.

    """

    meta_attrs = (Attribute('id'), )
    data_attrs = (Attribute('rounds', cls=JsonRoundResults), )
    attrs = data_attrs

    def __init__(self, rounds=None, id_=None):
        """
        Arguments:
          rounds: an iterable of JsonRoundResults objects.

        """
        self.id = id_
        self.rounds = rounds


class JsonTestCaseOutput(JsonableMixin):

    meta_attrs = ()
    data_attrs = (Attribute('rounds', cls=JsonRoundResults), )
    attrs = tuple(list(data_attrs) + list(meta_attrs))

    def __init__(self):
        self.rounds = []


class JsonTestCaseInput(JsonableMixin):

    meta_attrs = ()
    data_attrs = (Attribute('contest', cls=JsonContest), )
    attrs = tuple(list(data_attrs) + list(meta_attrs))

    def __init__(self):
        self.contest = None


class JsonTestCase(JsonableMixin):

    """
    An RCV test case (input and expected output).

    """

    meta_attrs = (Attribute('id'),
                  Attribute('contest_id'), )
    data_attrs = (Attribute('input', cls=JsonTestCaseInput),
                  Attribute('output', cls=JsonTestCaseOutput), )
    attrs = tuple(list(data_attrs) + list(meta_attrs))

    def __init__(self):
        self.id = None
        self.contest_id = None
        self.input = JsonTestCaseInput()
        self.output = JsonTestCaseOutput()


class JsonTestCaseFile(JsonableMixin):

    """
    A file of test cases (input and expected output).

    """

    meta_attrs = (Attribute('version'),
                  Attribute('rule_set'), )
    data_attrs = (Attribute('test_cases', cls=JsonTestCase), )
    attrs = tuple(list(data_attrs) + list(meta_attrs))

    def __init__(self):
        self.rule_set = None
        self.version = None
        self.test_cases = []
