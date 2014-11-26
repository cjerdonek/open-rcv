
"""
Supporting code for JSON serialization.

For the purposes of this project, "JSON object" (abbreviated in code as
`js_obj`) means a Python object composed of instances of built-in types
like lists, dicts, strings, ints, etc.  These objects can be converted
to JSON using the json module with no extra configuration.

TODO: clean up the documentation below.

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

import json
import logging

from openrcv import streams
from openrcv.utils import PathInfo, ReprMixin, ENCODING_JSON


log = logging.getLogger(__name__)

LIST_TYPES = (list, tuple)

# TODO: refactor this to be a JSON object?  This would give us things
# like a nice repr() and the chance to reduce special-casing.
class JsNull(object):
    pass
JS_NULL = JsNull()


def call_json(json_func, *args, **kwargs):
    return json_func(*args, indent=4, sort_keys=True, **kwargs)


def to_json(jsobj):
    """Convert a JSON object to a human-readable string."""
    return call_json(json.dumps, jsobj)


def read_json_path(path):
    """
    Read a JSON file and return its contents as a JSON object.

    """
    stream_info = JsonPathInfo(path)
    with stream_info.open() as f:
        jsobj = json.load(f)
    return jsobj


# TODO: remove the path argument?
# TODO: create a write_json_path() function?
def write_json(obj, resource=None, path=None):
    """
    Arguments:
      resource: a stream resource object.

    """
    try:
        jsobj = obj.to_jsobj()
    except AttributeError:
        jsobj = obj
    if path is not None:
        assert resource is None
        resource = streams.FilePathResource(path, encoding=ENCODING_JSON)
    with resource.open_write() as f:
        return call_json(json.dump, jsobj, f)


# TODO: choose a less ambiguous name.
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
            # TODO: preserve the exception type below.
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


class JsonPathInfo(PathInfo):

    def __init__(self, path):
        super().__init__(path, encoding=ENCODING_JSON)


# TODO: replace this with JsonSerialization and JsonDeserialization classes.
class JsonableError(Exception):
    pass


class JsonDeserializeError(Exception):
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


class JsonableMixin(ReprMixin):

    meta_attrs = ()

    @classmethod
    def attrs(cls):
        return list(cls.meta_attrs) + list(cls.data_attrs)

    def return_false(self, *args):
        return False

    def raise_not_equal(self, other, value_desc, self_value, other_value):
        raise AssertionError("{!r} != {!r}: {!s} not equal: {!r} != {!r}".
                             format(self, other, value_desc, self_value, other_value))

    # TODO: recursively call self._check_eq().
    def _check_eq(self, other, not_equal_func):
        if type(self) != type(other):
            return not_equal_func(other, "types", type(self), type(other))
        for attr in self.attrs():
            name = attr.name
            if (getattr(self, name) != getattr(other, name)):
                return not_equal_func(other, "{!r} attribute".format(name), getattr(self, name),
                                      getattr(other, name))
        return True

    def assert_equal(self, other):
        """
        Raise an informative AssertionError if self and other differ.

        This is useful for debugging and unit testing.
        """
        return self._check_eq(other, self.raise_not_equal)

    def __eq__(self, other):
        return self._check_eq(other, self.return_false)

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

    def repr_info(self):
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
                raise JsonableError("error processing attribute: %r" % attr)
            # TODO: handle and test None/JS_NULL.
            try:
                value = getattr(self, name)
            except TypeError:
                # Make troubleshooting easier by providing the name.
                raise JsonableError("error getting attribute: %r" % name)
            jsobj = to_jsobj(value)
            if jsobj is None:
                # Don't write None values into the JSON object.
                continue
            jsdict[name] = jsobj

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
        extra_keys = set((attr.name for attr in self.attrs())) - keys
        if extra_keys:
            log.warning("JSON object has unserializable keys: %r" % (", ".join(extra_keys)))
        self._attrs_from_jsdict(self.data_attrs, jsobj)

    def get_meta_dict(self):
        """Return a dict containing the object metadata."""
        meta = {}
        self._attrs_to_jsdict(self.meta_attrs, meta)
        return meta

    @classmethod
    def from_object(cls, model_obj):
        """
        Create an instance of the current class from a model object.
        """
        jsonable = cls()
        jsonable.load_object(model_obj)
        return jsonable

    @classmethod
    def from_jsobj(cls, jsobj):
        """
        Create an instance of the current class from a JSON object.
        """
        jsonable = cls()
        jsonable.load_jsobj(jsobj)
        return jsonable

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
