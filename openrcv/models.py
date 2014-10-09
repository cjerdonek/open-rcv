
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
# TODO: move JSON-specific code to a jsonio module.

import json
import logging

from openrcv.utils import StringInfo


log = logging.getLogger(__name__)

LIST_TYPES = (list, tuple)

# TODO: refactor this to be a JSON object?  This would give us things
# like a nice repr() and the chance to reduce special-casing.
class JsNull(object):
    pass
JS_NULL = JsNull()


def make_candidates(candidate_count):
    """
    Return an iterable of candidate numbers.

    """
    return range(1, candidate_count + 1)


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


def from_jsobj(jsobj, cls=None):
    """
    Convert a JSON object to a Python object, and return it.

    Arguments:
      cls: a class that serves as a "type hint."

    """
    if isinstance(jsobj, LIST_TYPES):
        return tuple((from_jsobj(o, cls=cls) for o in jsobj))

    if cls is not None:
        try:
            obj = cls()
        except TypeError:
            # We don't get the class name otherwise.
            raise Exception("error constructing class: %s" % cls.__name__)
        obj.load_jsobj(jsobj)
        return obj

    # The json module converts Javascript null to and from None.
    if jsobj is None:
        return JS_NULL
    return jsobj


def to_jsobj(obj):
    """
    Convert a Python object to a JSON object, and return it.

    Arguments:
      cls: a class that serves as a "type hint."

    """
    if isinstance(obj, LIST_TYPES):
        return [to_jsobj(o) for o in obj]
    if obj.__class__.__module__ == "builtins":
        return obj
    return obj.to_jsobj()


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


class JsonObjError(Exception):
    pass


class Attribute(object):

    """
    Represents an attribute of a jsonable class that should be
    serialized and deserialized to JSON.

    """

    def __init__(self, name, cls=None):
        """

        Arguments:
          name: the attribute name.
          cls: the jsonable class that should be used for serializing and
            deserializing the attribute value.  None means that no
            class is applicable: the attribute value is an instance of a
            Python built-in type.

        """
        self.name = name
        self.cls = cls


class JsonableMixin(object):

    __no_attribute__ = object()  # used in __eq__()

    meta_attrs = ()

    # TODO: remove this method (the function from_jsobj() replaces it).
    @classmethod
    def from_jsobj(cls, jsobj):
        """Convert a JSON object to an object of the class."""
        log.debug("called %s.from_jsobj()" % cls.__name__)
        try:
            obj = cls()
        except TypeError:
            # We don't get the class name otherwise.
            raise Exception("error constructing class: %s" % cls.__name__)
        obj.load_jsobj(jsobj)
        return obj

    def __repr__(self):
        desc = self.repr_desc() or "--"
        return "<%s: [%s] %s>" % (self.__class__.__name__, desc, hex(id(self)))

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        for attr in self.attrs:
            name = attr.name
            if (getattr(self, name, self.__no_attribute__) !=
                getattr(other, name, other.__no_attribute__)):
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

    def _attrs_from_jsdict(self, attrs, jsdict):
        """
        Read in attribute values from a JSON object dict.

        Arguments:
          attrs: iterable of attribute names.
          jsdict: a JSON object that is a mapping object.

        """
        for attr in attrs:
            name, cls = attr.name, attr.cls
            try:
                jsobj = jsdict[name]
            except KeyError:
                obj = None
            else:
                obj = from_jsobj(jsobj, cls=cls)
            setattr(self, name, obj)

    def _attrs_to_jsdict(self, attrs, jsdict):
        """
        Write attribute values to a JSON object dict.

        """
        for attr in attrs:
            try:
                name, cls = attr.name, attr.cls
            except AttributeError:
                # Make troubleshooting easier by providing the attr.
                raise JsonObjError("error processing attribute: %r" % attr)
            # TODO: handle and test None/JS_NULL.
            try:
                value = getattr(self, name)
            except TypeError:
                # Make troubleshooting easier by providing the name.
                raise JsonObjError("error getting attribute: %r" % name)
            jsobj = to_jsobj(value)
            if jsobj is None:
                # Don't write None values into the JSON object.
                continue
            jsdict[name] = jsobj

    # TODO: remove this.
    def add_to_jsobj(self, jsobj, attr):
        """Add the given attribute value to the given JSON object."""
        value = getattr(self, attr)
        # TODO: handle JS_NULL.
        if value is None:
            return
        jsobj[attr] = to_jsobj(value)

    def load_jsobj(self, jsobj):
        """
        Read data from the given JSON object and save it to attributes.

        """
        keys = set()
        try:
            meta_dict = jsobj['_meta']
        except KeyError:
            # The metadata dict is optional.
            pass
        else:
            keys |= set(meta_dict.keys())
            self._attrs_from_jsdict(self.meta_attrs, meta_dict)
        keys |= set(jsobj.keys())
        keys -= set(('_meta', ))
        extra_keys = set((attr.name for attr in self.attrs)) - keys
        if extra_keys:
            log.warning("JSON object has unserializable keys: %r" % (", ".join(extra_keys)))
        self._attrs_from_jsdict(self.data_attrs, jsobj)

    def get_meta_dict(self):
        """Return a dict containing the object metadata."""
        meta = {}
        self._attrs_to_jsdict(self.meta_attrs, meta)
        return meta

    def to_jsobj(self):
        """
        Convert the current object to a JSON object.

        """
        jsobj = {}
        meta = self.get_meta_dict()
        if meta:
            jsobj['_meta'] = meta
        self._attrs_to_jsdict(self.data_attrs, jsobj)
        return jsobj

    # This method should be thought of like __repr__() in that it is a
    # convenience useful for debugging.  It deliberately does not provide
    # any formatting and customization options since json.dumps() can
    # easily be used directly if more control is needed.
    def to_json(self):
        """Convert the object to a human-readable JSON string."""
        return to_json(self.to_jsobj())


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
