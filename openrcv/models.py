
"""
Contains object models for this project.

For the purposes of this project, "JSON object" (abbreviated in code
as "jsobj") means a Python object with a natural conversion to JSON.
These are objects composed of built-in type instances like Python
lists, dicts, strings, ints, etc.

Instances of most models in this module (those inheriting from JsonMixin)
can be converted to a JSON object by calling a to_jsobj() method on the
instance.  Similarly, calling to_json() on the object returns JSON.  We
call these objects "jsonable."

We use the convention that "None" attribute values do not get converted
to JSON, and JSON null values correspond to the JSNULL object.
This decision is based on the thinking that having "null" appear in the
JSON should be a deliberate decision (and in the Python world, None
is the usual default value).

"""

# TODO: move non-serializable models to a different location?
# TODO: move JSON-specific code to a jsonio module.

import json
import logging


log = logging.getLogger(__name__)

# TODO: refactor this to be a JSON object?  This would give us things
# like a nice repr() and the chance to reduce special-casing.
JSNULL = object()


def call_json(json_func, *args, **kwargs):
    return json_func(*args, indent=4, sort_keys=True, **kwargs)


def to_json(jsobj):
    """Convert a JSON object to a human-readable string."""
    return call_json(json.dumps, jsobj)


def write_json(jsobj, stream_info):
    """
    Arguments:
      stream_info: a StreamInfo object.

    """
    with stream_info.open("w") as f:
        return call_json(json.dump, jsobj, f)


# TODO: remove this.
def seq_to_jsobj(seq):
    return tuple((jsonable.to_jsobj() for jsonable in seq))


def to_jsobj(obj):
    if isinstance(obj, (list, tuple)):
        return tuple((to_jsobj(o) for o in obj))
    if obj.__class__.__module__ == "builtins":
        return obj
    return obj.to_jsobj()


def jsobj_to_seq(cls, jsobjs):
    log.info("%s: %r" % (cls.__name__, jsobjs))
    return [cls.from_jsobj(jsobj) for jsobj in jsobjs]


class JsonObjError(Exception):
    pass


class JsonMixin(object):

    meta_attrs = ()

    @classmethod
    def from_jsobj(cls, jsobj):
        """Convert a JSON object to an object of the class."""
        try:
            obj = cls()
        except TypeError:
            # We don't get the class name otherwise.
            raise Exception("error constructing class: %s" % cls.__name__)
        obj.load_jsobj(jsobj)
        return obj

    def __repr__(self):
        desc = self.repr_desc()
        return "<%s: %s%s%s>" % (self.__class__.__name__, desc,
                                 " " if desc else "", hex(id(self)))

    def __eq__(self, other):
        for attr in self.attrs:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    # From the Python documentation:
    #
    #   There are no implied relationships among the comparison operators.
    #   The truth of x==y does not imply that x!=y is false. Accordingly,
    #   when defining __eq__(), one should also define __ne__() so that the
    #   operators will behave as expected.
    #
    # (from https://docs.python.org/3/reference/datamodel.html#object.__ne__ )
    #
    #    HOWEVER, I did observe that Python 3.4 will call __eq__() if
    # __ne__() is not implemented.
    def __ne__(self, other):
        return not self.__eq__(other)

    def repr_desc(self):
        """Return additional info for __repr__()."""
        return ""

    def load_jsobj(self, jsobj):
        """
        Read data from the given JSON object and save it to attributes.

        This method skips over metadata.

        """
        raise NotImplementedError()

    def __fill_jsobj__(self, jsobj):
        """
        Write the state of the current object to the given JSON object.

        """
        raise NotImplementedError()

    def _load_attrs(self, attrs, jsobj):
        """
        Read data from the given JSON object and save it to attributes.

        Arguments:
          attrs: iterable of attribute names.
          jsobj: a JSON object that is a mapping object.

        """
        for attr in attrs:
            # TODO: test and handle null, etc.
            value = jsobj.get(attr)
            if value is None:
                value = JSNULL
            setattr(self, attr, value)

    def load_jsobj(self, jsobj):
        try:
            meta_dict = jsobj['_meta']
        except KeyError:
            # The metadata dict is optional.
            pass
        else:
            self._load_attrs(self.meta_attrs, meta_dict)
        self._load_attrs(self.data_attrs, jsobj)

    def get_meta_dict(self):
        """Return a dict containing the object metadata."""
        meta = {}
        for attr in self.meta_attrs:
            value = getattr(self, attr)
            meta[attr] = value
        return meta if meta else None

    def add_to_jsobj(self, jsobj, attr):
        """Add the given attribute value to the given JSON object."""
        value = getattr(self, attr)
        # TODO: handle JSNULL.
        if value is None:
            return
        jsobj[attr] = to_jsobj(value)

    def to_jsobj(self):
        jsobj = {}
        meta = self.get_meta_dict()
        if meta:
            jsobj['_meta'] = meta
        self.__fill_jsobj__(jsobj)
        return jsobj

    # This method should be thought of like __repr__() in that it is
    # useful for debugging.
    def to_json(self):
        """Convert the object to a human-readable JSON string."""
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


class JsonBallot(JsonMixin):

    """
    Represents a ballot for a JSON test case.

    This class should be used only for tests and small sets of ballots.
    For large numbers of ballots, ballot data should be kept on the
    file system, and ballots should not be converted to instances of
    user-defined classes.

    """

    attrs = ('choices', 'weight')

    # def _set_attrs(self, **kwargs):
    #     for attr, value in kwargs.items():
    #         setattr(self, attr, value)

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
        except ValueError:
            # Can happen for example with: "2 ".
            # ValueError: invalid literal for int() with base 10: ''
            raise JsonObjError("error parsing: %r" % jsobj)
        weight = numbers.pop(0)
        self.__init__(choices=numbers, weight=weight)

    def to_jsobj(self):
        """Convert the ballot to a string."""
        values = [self.weight] + self.choices
        return " ".join((str(v) for v in values))


class JsonContest(JsonMixin):

    """
    Represents a contest for a JSON test case.

    """

    data_attrs = ('ballots', 'candidate_count')
    meta_attrs = ('id', 'notes')
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
        """Return additional info for __repr__()."""
        return "id=%s candidate_count=%s" % (self.id, self.candidate_count)

    def load_jsobj_old(self, jsobj):
        # def _set_attrs(self, **kwargs):
        #     for attr, value in kwargs.items():
        #         setattr(self, attr, value)


        ballots = jsobj_to_seq(JsonBallot, jsobj["ballots"])
        candidate_count = jsobj["candidates"]
        self.__init__(ballots=ballots, candidate_count=candidate_count)

    def __fill_jsobj__(self, jsobj):
        self.add_to_jsobj(jsobj, "ballots")
        self.add_to_jsobj(jsobj, "candidate_count")


class TestInputFile(JsonMixin):

    """
    Represents an input file for open-rcv-tests.

    """

    meta_attrs = ('version', )

    def __init__(self, contests=None, version=None):

        """
        Arguments:
          contests: an iterable of JsonContest objects.

        """
        self.contests = contests
        self.version = version

    def load_jsobj(self, jsobj):
        jsobjs = jsobj['contests']
        # TODO: use a general jsobj_to_obj instead.
        self.contests = jsobj_to_seq(JsonContest, jsobjs)

    def __fill_jsobj__(self, jsobj):
        """Write the state of the current object to the given JSON object."""
        self.add_to_jsobj(jsobj, "contests")
