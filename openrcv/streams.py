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

"""Exposes core stream-related functionality.

A "stream resource" is a core concept used throughout this project.
This module exposes many stream resource implementations.

A stream resource can be viewed as a generalization of a file path:
it can be opened for reading to yield a readable stream, or opened for
writing to yield a writeable stream.  It is more general than a file
because the stream can contain any objects and not just lines of text.
Also, the backing store for a stream resource can be something other
than a file.  For example, it can be backed by a container object like
a list or an in-memory text stream like an io.StringIO object.

Stream resources can also be written to transform data when reading and
writing from a stream.  For example, a stream resource can parse the lines
of a ballot file or serialize a ballot to text.  In this case, the caller
only interacts with the deserialized data.  The stream resource takes
care of the rest.


API
---

A stream resource must implement two methods, reading() and writing(), that
each return a with-statement context manager [1].  In both cases, entering
the context manager opens the stream, and exiting closes the stream.

For the reading() method, the context manager must yield an iterator object
for the target `as` expression, in the same way that calling the built-in
function `open(path)` yields an iterator object over the lines of a file.
Here is a typical example of reading from a stream resource named `resource`:

    with resource.reading() as stream:
        for item in stream:
            # Do stuff.
            ...

Similarly, for the writing() method, the context manager must yield
a writeable stream for the target `as` expression.  Here is a typical
example of writing to a stream resource:

    with resource.writing() as stream:
        for item in items:
            stream.write(item)
            ...

The semantics of the reading() and writing() methods closely resemble those
of the built-in function open() (with modes "r" and "w", respectively).


Advantages
----------

Encapsulating data as a stream resource has several advantages.
First and foremost, it simplifies our high-level code.  Stream resources
let us write high-level code that is independent of whether the stream is
backed by a file on disk or in memory as an in-memory text stream
or container.  For example, this lets us easily write unit tests that
use in-memory structures as opposed to writing to disk.

Moreover, in the case of files especially, stream resources let us write
code that is blind to what particular serialization format is being used.
For example, ballot-counting code can deal with ballots independent of
how they are being stored or serialized.  For example, the same code can
be used whether the ballots are being read from a BLT-formatted file
or a WinEDS-formatted file.

In addition, stream resources let us postpone the opening of files for
clearer file-handle management.  For example, instead of opening a stream
early and passing the open stream into an API, a stream resource can be
passed into the API, and the API's implementation can open the stream
(e.g. using `with resource.reading() as stream`).  This pattern also
lets us iterate over large sets of ballots without having to store
them in memory all at once.


TODO: decide whether we need to inherit from StreamResourceBase.

[1]: https://docs.python.org/3/library/contextlib.html
"""

import contextlib
from contextlib import contextmanager
from io import StringIO
import logging
import tempfile

from openrcv import utils
from openrcv.utils import logged_open, NoImplementation, ReprMixin


log = logging.getLogger(__name__)


def temp_stream_resource():
    """Return a context manager for a temporary stream resource.

    Entering the context manager yields a stream resource without
    actually opening a file handle.  Rather, the file is opened lazily,
    i.e. when the stream resource is first opened for reading or writing.
    Exiting the context manager closes the file handle if it is open.
    """
    resource = _TempFileResource()
    return contextlib.closing(resource)


def tracked(source, iterable):
    """Return a "tracking" generator over the items in the given stream.

    If gen.throw(exc) is called on the generator return value, then the
    generator adds information about the location of the stream to
    the exception stack trace.

    Arguments:
      source: the source of the stream (for display purposes).
      iterable: an iterable.  In particular, an iterator object is not
        required.
    """
    for i, item in enumerate(iterable, start=1):
        try:
            yield item
        except Exception as exc:
            raise type(exc)("last read item from %r (number=%d): %r" % (source, i, item))


@utils.coroutine
def _sink(write, target):
    """Return a generator that writes to the given target."""
    while True:
        item = yield
        write(target, item)


@utils.coroutine
def converting_pipe(convert, target):
    """
    Arguments:
      convert: a function that accepts one argument to transform
        items before sending them to the target coroutine.
    """
    while True:
        item = (yield)
        item = convert(item)
        target.send(item)


# TODO: incorporate this and test.
class StreamResourceMixin(object):

    def count(self):
        """Return the number of elements in the stream."""
        with self.reading() as stream:
            return sum(1 for item in stream)


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
# TODO: document the StreamResource API.
class StreamResourceBase(ReprMixin):

    """Abstract base class for stream resources.

    A stream resource is an object that encapsulates a stream that can
    be opened for reading or writing.  The backing store for the stream
    can be something like a file or an iterable like a list.

    Normally, the __init__() constructor accepts a reference to the stream
    backing store.

    TODO: clean up the below.

    An instance of this class is a context manager factory function
    for managing the resource of an iterable of ballots.

    An instance of this class could be used as follows, for example:

        with ballot_resource() as ballots:
            for ballot in ballots:
                # Handle ballot.
                ...

    This resembles the pattern of opening a file and reading its lines.
    One reason to encapsulate ballots as a context manager as opposed to
    an iterable is that ballots are often stored as a file.  Thus,
    implementations should really support the act of opening and closing
    the ballot file when the ballots are needed (i.e. managing the file
    resource).  This is preferable to opening a handle to a ballot
    file earlier than needed and then keeping the file open.
    """

    # TODO: remove this?
    @classmethod
    def make_temp(cls):
        raise NoImplementation(cls)

    def _delete(self):
        raise NoImplementation(cls)

    # TODO: remove this.
    def move(self, other):
        """Move the contents of a resource to another resource.

        This operation should be thought of like moving the contents of
        a file from one path to another.
        """
        raise NoImplementation(cls)

    @contextmanager
    def replacement(self):
        """Return a context manager that yields a temporary resource.

        The temporary resource replaces the contents of the current resource
        when exiting the context manager.
        """
        # try:
        #     yield temp_resource
        # try:
        #     normalize_ballots_to(ballots_resource, temp_ballots_resource)
        #     # TODO: can and should I modify the old backing resource?
        #     #   Either way, the behavior should be documented.
        #     ballots_resource.resource = temp_ballots_resource
        # except:
        #     temp_ballots_resource.delete()
        raise NoImplementation(self)

    @contextmanager
    def open_read(self):
        """Return an iterator object."""
        raise NoImplementation(self)

    # Default implementation.
    def write(self, f, item):
        f.write(item)

    @contextmanager
    def open_write(self):
        raise NoImplementation(self)

    # TODO: decide whether to expose this.
    # @classmethod  # must be applied "last" (i.e. top-most).
    # @contextmanager
    # def temp(cls):
    #     temp_resource = cls.make_temp()
    #     try:
    #         yield temp_resource
    #     except:
    #         temp_resource._delete()

    @contextmanager
    def reading(self):
        """Return a context manager that yields a readable stream.

        Here, "readable stream" means an iterator object over the elements
        of the backing store.
        """
        log.debug("opening for reading: %r" % self)
        with self.open_read() as f:
            try:
                gen = tracked(self, f)
                try:
                    yield gen
                except Exception as exc:
                    gen.throw(exc)
            finally:
                gen.close()

    @contextmanager
    def writing(self):
        """Return a context manager that yields a generator.

        Calling this method clears the contents of the backing store
        before returning a stream that writes to the store.
        """
        log.debug("opening for writing: %r" % self)
        with self.open_write() as stream:
            gen = _sink(self.write, stream)
            try:
                yield gen
            finally:
                gen.close()


# TODO: add more to the repr and test.
class ListResource(StreamResourceBase):

    """A stream resource backed by a list."""

    def __init__(self, seq=None):
        """
        Arguments:
          seq: an iterable.  Defaults to the empty list.
        """
        if seq is None:
            seq = []
        # TODO: rename seq to _seq to keep it internal.
        self.seq = seq

    @classmethod
    def make_temp(cls):
        return cls()

    @classmethod  # must be applied "last" (i.e. top-most).
    @contextmanager
    def temp(cls):
        temp_resource = cls.make_temp()
        try:
            yield temp_resource
        finally:
            temp_resource.seq.clear()

    @contextmanager
    def replacement(self):
        """See StreamResourceBase.replacement()."""
        with self.temp() as temp_resource:
            try:
                yield temp_resource
            finally:
                # Replace the current resource with contents of the temporary.
                self.seq[:] = temp_resource.seq

    @contextmanager
    def open_read(self):
        yield iter(self.seq)

    def write(self, target, item):
        target.append(item)

    @contextmanager
    def open_write(self):
        seq = self.seq
        # Delete the contents of the list (analogous to deleting a file).
        seq.clear()
        yield seq


# TODO: add more to the repr and test.
class FilePathResource(StreamResourceBase):

    """A stream resource backed by a file."""

    def __init__(self, path, encoding=None, **kwargs):
        if encoding is None:
            encoding = 'ascii'
        self.path = path
        self.encoding = encoding
        self.kwargs = kwargs

    @classmethod
    def make_temp(cls):
        return tempfile.SpooledTemporaryFile(encoding=self.encoding)

    @contextmanager
    def _open(self, mode):
        with logged_open(self.path, mode, encoding=self.encoding, **self.kwargs) as f:
            yield f

    def open_read(self):
        return self._open("r")

    def open_write(self):
        return self._open("w")


class _ReadWriteFileBase(StreamResourceBase):

    """A stream resource backed by a readable-writeable file.

    To support reading and writing to the same stream, this class never
    closes the underlying file.  Thus, closing the file is the responsibility
    of the caller.
    """

    def __init__(self, file_):
        self.file = file_

    @classmethod
    def make_temp(cls):
        return tempfile.NamedTemporaryFile(mode='w+t', encoding='utf-8')

    def _open(self):
        raise NoImplementation(self)

    @contextmanager
    def open_read(self):
        self._open()
        yield self.file

    @contextmanager
    def open_write(self):
        self._open()
        self.file.truncate()
        yield self.file

    def close(self):
        # TODO: handle exception happening if self.file is None.
        close = self.file.close
        close()


class ReadWriteFileResource(_ReadWriteFileBase):

    """A stream resource backed by a readable-writeable file.

    To support reading and writing to the same stream, this class never
    closes the underlying file.  Thus, closing the file is the responsibility
    of the caller.
    """

    def __init__(self, file_, encoding=None):
        self.encoding = encoding
        self.file = file_

    def _open(self):
        self.file.seek(0)


class _TempFileResource(_ReadWriteFileBase):

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
        f = self.file
        try:
            seek = f.seek
        except AttributeError:
            f = tempfile.SpooledTemporaryFile(mode='w+t', encoding=self.encoding)
            self.file = f
            seek = f.seek
        seek(0)


# TODO: add more to the repr and test.
# TODO: give a better name and test edge cases.
class StandardResource(StreamResourceBase):

    """A stream resource backed by a file."""

    def __init__(self, file_):
        self.file = file_

    # def repr_info(self):
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

    """A stream resource backed by an in-memory text stream.

    This class allows functions that accept a PathInfo object to be called
    using strings.  In particular, writing to disk and creating temporary
    files isn't necessary.  This is especially convenient for testing.
    """

    def __init__(self, contents=None):
        self.contents = contents

    # TODO: include the length in characters.
    # TODO: include the initial content in the repr.

    # def repr_info(self):
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

    @classmethod
    def make_temp(cls):
        return cls()

    @contextmanager
    def open_read(self):
        yield StringIO(self.contents)

    def write(self, f, item):
        f.write(item)

    @contextmanager
    def open_write(self):
        # TODO: confirm that the contents get deleted.
        with StringIO() as f:
            yield f
            self.contents = f.getvalue()


class WrappedResourceMixin(ReprMixin):

    def repr_info(self):
        return "resource=%r" % self.resource

    def replacement(self):
        """See StreamResourceBase.replacement()."""
        return self.resource.replacement()


# TODO: unit test this.
class WrapperResource(WrappedResourceMixin):

    """A stream resource that wraps another resource.

    This class is useful for defining classes whose constructor can
    accept any stream resource.
    """

    def __init__(self, resource):
        """
        Arguments:
          resource: a stream resource.
        """
        self.resource = resource

    def make_temp(self):
        temp_resource = self.resource.make_temp()
        return self.__class__(temp_resource)

    def reading(self):
        return self.resource.reading()

    def writing(self):
        return self.resource.writing()


class Converter(object):

    def from_resource(self, item):
        raise NoImplementation(self)

    def to_resource(self, item):
        raise NoImplementation(self)


class ConvertingResource(WrappedResourceMixin):

    def __init__(self, resource, converter):
        """
        Arguments:
          TODO: define the "stream resource protocol."
          resource: a stream resource.
          converter: a converter
        """
        self.converter = converter
        self.resource = resource

    @contextmanager
    def reading(self):
        convert = self.converter.from_resource
        with self.resource.reading() as gen:
            yield (convert(item) for item in gen)

    @contextmanager
    def writing(self):
        convert = self.converter.from_resource
        with self.resource.writing() as gen:
            new_gen = converting_pipe(convert, target=gen)
            try:
                yield new_gen
            finally:
                new_gen.close()
