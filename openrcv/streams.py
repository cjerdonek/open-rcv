
# TODO: explain what stream resources are and document the API.
#   Note that they do not need to inherit from StreamResourceBase.
"""

We support writing through a write() method and reading through iteration.

Notes
-----

In both the list and file cases, resource.open_write() returns a
stream object that supports a write() method.  How to make the
resulting stream support tracking?  Answer(?): The stream object's
write() method needs to support tracking.

Instantiating any stream object should reset the tracking info (i.e. the
current item and item number).


Helper functions to support using iterator resources.

In this project, we use the term "iterator resource" to mean a callable
that returns a with-statement context manager [1], which in turn yields
an iterator object for the target `as` expression.

Here is a typical example of using an iterator resource `resource`:

    with resource() as items:
        for item in items:
            # Do stuff.
            ...

Unsurprisingly, the above resembles the pattern of opening a file and
reading its lines.

Iterator resources are a central concept in this package.  For example,
for many of our APIs, we encapsulate ballots as an iterator resource
rather than as a plain iterable.  This lets us access large sets of
ballots as a file rather having to store them in memory.  By using an
iterator resource, we can open and close a ballot file in our
implementations when needed (e.g. using the convenient with statement),
as opposed to having to open a file handle earlier in the ballot
processing, and then passing open file objects around our APIs.

The current module provides helper functions for creating and using
iterator resources.


[1]: https://docs.python.org/3/library/contextlib.html
"""

from contextlib import contextmanager
from io import StringIO
import logging
import tempfile

from openrcv.utils import logged_open, ReprMixin


log = logging.getLogger(__name__)


# TODO: remove this after thinking about whether it would be useful.
def pipe_resource(resource, pipe_func):
    """
    Pipe a resource's iterator object through a function.

    Create an iterator resource that passes the iterator object from the
    given iterator resource through the given pipe function.

    Arguments:
      pip_func: a function that accepts an iterable and returns an
        iterator object.
      resource: an iterator resource.
    """
    return _PipedResource(resource, pipe_func)


# TODO: remove this after thinking about whether it would be useful.
class _PipedResource(object):

    """
    An iterator resource in which the target iterable is passed to a pipe
    function (i.e. as a post-process).
    """

    def __init__(self, resource, pipe_func):
        """
        Arguments:
          pip_func: a function that accepts an iterable and returns an
            iterator object.
          resource: an iterator resource.
        """
        self.pipe_func = pipe_func
        self.resource = resource

    @contextmanager
    def __call__(self):
        with self.resource() as items:
            yield self.pipe_func(items)


class StreamResourceMixin(object):

    def count(self):
        """Return the number of elements in the stream."""
        with self.reading() as stream:
            return sum(1 for item in stream)


class TrackedStreamBase(object):

    def __init__(self, stream):
        self.item_number = 0
        self.item = None
        self.stream = stream

    def increment(self, item):
        self.item = item
        self.item_number += 1


class ReadableTrackedStream(TrackedStreamBase):

    def __iter__(self):
        for item in self.stream:
            self.increment(item)
            yield item


class WriteableTrackedStream(TrackedStreamBase):

    def write(self, item):
        self.increment(item)
        self.stream.write(item)


class WriteableListStream(object):

    def __init__(self, seq):
        self.seq = seq

    def write(self, obj):
        self.seq.append(obj)


class NullStreamResource(StreamResourceMixin, ReprMixin):

    """A placeholder stream resource used as a default."""

    @contextmanager
    def reading(self):
        yield iter(())

    @contextmanager
    def writing(self):
        raise TypeError("The null stream resource does not allow writing.")


# TODO: rename to something that doesn't seem to imply that all
#   stream resources need to inherit from this class.
# TODO: consider simplifying the stream resource hierarchy, so that the
#   various backed stream resources possibly don't need a base class
#   and separate out the tracking part using a lighter-weight pattern.
class StreamResourceBase(ReprMixin):

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
        """Return an iterator object."""
        raise NotImplementedError()

    @contextmanager
    def open_write(self):
        raise NotImplementedError()

    @contextmanager
    def track_reading(self, stream):
        """
        Return a with-statement context manager for an iterable that provides
        item-level information when an exception occurs.

        The context manager yields an iterator object for the target `as`
        expression that we call a "tracked iterator."
        """
        tracked = ReadableTrackedStream(stream)
        try:
            yield tracked
        except Exception as exc:
            raise type(exc)("last read %s of %r: number=%d, %r" %
                            (self.label, self, tracked.item_number, tracked.item))

    @contextmanager
    def track_writing(self, stream):
        tracked = WriteableTrackedStream(stream)
        try:
            yield tracked
        except Exception as exc:
            raise type(exc)("last written %s of %r: number=%d, %r" %
                            (self.label, self, tracked.item_number, tracked.item))

    @contextmanager
    def reading(self):
        """
        Return a context manager that yields a readable stream.

        Here, "readable stream" means an iterator object over the elements
        of the backing store.
        """
        log.debug("opening for reading: %r" % self)
        with self.open_read() as f:
            with self.track_reading(f) as tracked:
                yield iter(tracked)

    @contextmanager
    def writing(self):
        """
        Return a context manager that yields a writeable stream.

        Return a writeable stream.

        Calling this method clears the contents of the backing store
        before returning a stream that writes to the store.
        """
        log.debug("opening for writing: %r" % self)
        with self.open_write() as f:
            with self.track_writing(f) as tracked:
                yield tracked


# TODO: add more to the repr and test.
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
        yield iter(self.seq)

    @contextmanager
    def open_write(self):
        # Delete the contents of the list (analogous to deleting a file).
        self.seq.clear()
        yield WriteableListStream(self.seq)


# TODO: add more to the repr and test.
class FilePathResource(StreamResourceBase):

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


class ReadWriteFileResource(StreamResourceBase):

    """A stream resource backed by a readable-writeable file.

    To support reading and writing to the same stream, this class never
    closes the underlying file.  Thus, closing the file is the responsibility
    of the caller.
    """

    def __init__(self, file_):
        self.file = file_

    @contextmanager
    def open_read(self):
        self.file.seek(0)
        yield self.file

    @contextmanager
    def open_write(self):
        self.file.seek(0)
        self.file.truncate()
        yield self.file


@contextmanager
def temp_stream_resource():
    resource = _TempFileResource()
    try:
        yield resource
    finally:
        if resource.file is not None:
            resource.file.close()


class _TempFileResource(StreamResourceBase):

    """A stream resource for temporary use.

    Unlike tempfile.SpooledTemporaryFile, this class delays opening a
    file handle until opening the resource for reading or writing.
    After that point, the underlying file remains open until manually
    closed by the caller.
    """

    def __init__(self, encoding=None):
        if encoding is None:
            encoding = 'ascii'
        self.encoding = encoding
        self.file = None

    def _open(self):
        try:
            seek = self.file.seek
        except AttributeError:
            self.file = tempfile.SpooledTemporaryFile(mode='w+t', encoding=self.encoding)
            seek = self.file.seek
        seek(0)

    @contextmanager
    def open_read(self):
        self._open()
        yield self.file

    @contextmanager
    def open_write(self):
        self._open()
        self.file.truncate()
        yield self.file


# TODO: add more to the repr and test.
# TODO: give a better name and test edge cases.
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


# TODO: add more to the repr and test.
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
    # TODO: include the initial content in the repr.

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
