
"""
Contains models used throughout this project.

For the purposes of this project, "JSON object" (abbreviated "jsobj")
means a Python object with a natural conversion to JSON.
These are objects composed of built-in type instances -- things like
Python lists, dicts, strings, ints, etc.

Instances of most models in this module (those inheriting from JsonMixin)
can be converted to JSON by calling a to_json() method on the instance.
We call these objects "jsonable."

"""

import json


NO_VALUE = object()


def seq_to_jsobj(seq):
    return tuple((jsonable.to_jsobj() for jsonable in seq))


def call_json(json_func, *args, **kwargs):
    return json_func(*args, indent=4, sort_keys=True, **kwargs)


def to_json(jsobj):
    return call_json(json.dumps, jsobj)


def write_json(jsobj, stream_info):
    """
    Arguments:
      stream_info: a StreamInfo object.

    """
    with stream_info.open("w") as f:
        return call_json(json.dump, jsobj, f)


class JsonMixin(object):

    meta_attrs = ()

    @classmethod
    def from_jsobj(cls, jsobj):
        """Convert a JSON object to an object of the class."""
        obj = cls()
        meta_dict = jsobj['_meta']
        for attr in cls.meta_attrs:
            value = meta_dict.get(attr, NO_VALUE)
            setattr(obj, attr, value)
        obj.__add_jsdata__(jsobj)
        return obj

    def get_meta_dict(self):
        """Return a dict containing the object metadata."""
        meta = {}
        for attr in self.meta_attrs:
            value = getattr(self, attr)
            meta[attr] = value
        return meta if meta else None

    def to_jsobj(self):
        meta = self.get_meta_dict()
        jsobj = self.__jsdata__()
        if meta:
            jsobj['_meta'] = meta
        return jsobj

    # TODO: remove this from the mixin.
    def to_json(self):
        return to_json(self.to_jsobj())


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
        return range(1, len(self.candidates) + 1)

    # TODO: look up the proper return type.
    def __repr__(self):
        return self.name


class RawRoundResults(JsonMixin):

    """
    Represents the results of a round for testing purposes.

    """

    def __init__(self, totals):
        """
        Arguments:
          totals: dict of candidate number to vote total.

        """
        self.totals = totals

    def __jsdata__(self):
        return {
            "totals": self.totals,
        }


class RawContestResults(JsonMixin):

    """
    Represents contest results for testing purposes.

    """

    def __init__(self, rounds):
        """
        Arguments:
          rounds: an iterable of RawRoundResults objects.

        """
        self.rounds = rounds

    def __jsdata__(self):
        return {
            "rounds": [r.__jsdata__() for r in self.rounds],
        }


class TestBallot(JsonMixin):

    """
    Represents a ballot.

    This should be used only for tests and small sets of ballots.
    For large numbers of ballots, ballot data should be kept on the
    file system for memory reasons.

    """

    def __init__(self, choices, weight=1):
        self.choices = choices
        self.weight = weight

    def __jsdata__(self):
        values = [self.weight] + self.choices
        return " ".join((str(v) for v in values))


# TODO: add a dict of who breaks ties in each round there is a tie.
class TestContestInput(JsonMixin):

    """
    Represents a contest for an open-rcv-tests input file.

    """

    meta_attrs = ('id', 'notes')

    # TODO: rename candidates to candidate_count.
    def __init__(self, candidates, ballots, id_=None, notes=None):
        """
        Arguments:
          candidates: integer number of candidates

        """
        self.ballots = ballots
        self.candidates = candidates
        self.id = id_
        self.notes = notes

    def __jsdata__(self):
        return {
            "ballots": seq_to_jsobj(self.ballots),
            "candidates": self.candidates,
        }


class TestInputFile(JsonMixin):

    """
    Represents an input file for open-rcv-tests.

    """

    meta_attrs = ('version', )

    def __init__(self, contests=None, version=None):

        """
        Arguments:
          contests: an iterable of TestContestInput objects.

        """

        self.contests = contests
        self.version = version

    def __add_jsdata__(cls, jsobj):
        # TODO
        pass

    def __jsdata__(self):
        return {
            "contests": seq_to_jsobj(self.contests),
        }
