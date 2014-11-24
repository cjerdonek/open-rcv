
'''
This module is **experimental**.

We support writing through a write() method and reading through iteration.

Notes
-----

In both the list and file cases, resource.open_write() returns a
stream object that supports a write() method.  How to make the
resulting stream support tracking?  Answer(?): The stream object's
write() method needs to support tracking.

Instantiating any stream object should reset the tracking info (i.e. the
current item and item number).

'''

from contextlib import contextmanager
from io import StringIO

from openrcv.utils import logged_open


# TODO: add tests?
class TrackingStream(object):

    def __init__(self, stream):
        self.item_number = 0
        self.item = None
        self.stream = stream

    def __iter__(self):
        for item in self.stream:
            self.increment(item)
            yield item

    def increment(self, item):
        self.item = item
        self.item_number += 1

    def write(self, item):
        self.increment(item)
        self.stream.write(item)


class WriteableListStream(object):

    def __init__(self, seq):
        self.seq = seq

    def write(self, obj):
        self.seq.append(obj)


# TODO: should this inherit from ReprMixin?
class StreamResourceBase(object):

    """
    Abstract base class for stream resources.

    A stream resource is an object that encapsulates a stream that can
    be opened for reading or writing.  The backing store for the stream
    can be something like a file or an iterable like a list.

    Normally, the __init__() constructor accepts a reference to the stream
    backing store.
    """

    label = "line"

    @contextmanager
    def open_read(self):
        raise NotImplementedError()

    @contextmanager
    def open_write(self):
        raise NotImplementedError()

    @contextmanager
    def tracking(self, stream):
        tracked = TrackingStream(stream)
        try:
            yield tracked
        except Exception as exc:
            # TODO: find a way of including additional information in the
            # stack trace that doesn't involve raising a new exception
            # (and unnecessarily lengthening the stack trace).
            raise type(exc)("during %s number %d of %r: %r" %
                            (self.label, tracked.item_number, self, tracked.item))

    @contextmanager
    def reading(self):
        """
        Return a context manager that yields a readable stream.

        Here, "readable stream" means an iterator object over the elements
        of the backing store.
        """
        with self.open_read() as f:
            with self.tracking(f) as tracked:
                yield iter(tracked)

    @contextmanager
    def writing(self):
        """
        Return a context manager that yields a writeable stream.

        Return a writeable stream.

        Calling this method clears the contents of the backing store
        before returning a stream that writes to the store.
        """
        with self.open_write() as f:
            with self.tracking(f) as tracked:
                yield tracked


class ListResource(StreamResourceBase):

    """A stream resource backed by a list."""

    label = "item"

    def __init__(self, seq=None):
        """
        Arguments:
          seq: an iterable.  Defaults to the empty list.
        """
        if seq is None:
            seq = []
        self.seq = seq

    @contextmanager
    def open_read(self):
        """Return an iterator object."""
        yield iter(self.seq)

    @contextmanager
    def open_write(self):
        # Delete the contents of the list (analogous to deleting a file).
        self.seq.clear()
        yield WriteableListStream(self.seq)


class FileResource(StreamResourceBase):

    """A stream resource backed by a file."""

    def __init__(self, path, encoding=None, **kwargs):
        if encoding is None:
            encoding = 'ascii'
        self.path = path
        self.encoding = encoding
        self.kwargs = kwargs

    @contextmanager
    def _open(self, mode):
        with logged_open(self.path, mode, encoding=self.encoding, **self.kwargs) as f:
            yield f

    def open_read(self):
        return self._open("r")

    def open_write(self):
        return self._open("w")


class StandardResource(StreamResourceBase):

    """A stream resource backed by a file."""

    def __init__(self, file_):
        self.file = file_

    # def repr_desc(self):
    #     return "stream=%r" % self.file

    @contextmanager
    def _open(self):
        yield self.file

    def open_read(self):
        return self._open()

    def open_write(self):
        return self._open()


class StringResource(StreamResourceBase):

    """
    A stream resource backed by an in-memory text stream.

    This class allows functions that accept a PathInfo object to be called
    using strings.  In particular, writing to disk and creating temporary
    files isn't necessary.  This is especially convenient for testing.
    """

    def __init__(self, contents=None):
        self.contents = contents

    # TODO: include the length in characters.
    # def repr_desc(self):
    #     return "contents=%s" % (self.get_display_value(10), )
    #
    # def get_display_value(self, limit=None):
    #     """
    #     Return the first `limit` characters plus "...".
    #     """
    #     value = self.value
    #     if limit is None or not value or len(value) <= limit:
    #         return value
    #     return repr(value[:limit]) + "..."

    @contextmanager
    def open_read(self):
        yield StringIO(self.contents)

    @contextmanager
    def open_write(self):
        with StringIO() as f:
            yield f
            self.contents = f.getvalue()
