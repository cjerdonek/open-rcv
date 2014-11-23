
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


# TODO: add tests.
class TrackingStream(object):

    def __init__(self, stream):
        self.item_number = 0
        self.item = None
        self.stream = stream

    def reset(self):
        pass

    # TODO: add increment method.
    def __iter__(self):
        for item in self.stream:
            self.item = item
            self.item_number += 1
            yield item

    def write(self, item):
        self.item_number += 1
        self.item = item
        self.stream.write(item)


# TODO: remove this.
class ListStream(object):

    def __init__(self, seq):
        self.seq = seq

    def write(self, obj):
        self.seq.append(obj)

    def __iter__(self):
        return iter(self.seq)


class WriteableListStream(object):

    def __init__(self, seq):
        self.seq = seq

    def write(self, obj):
        self.seq.append(obj)


class StreamResourceBase(object):

    """
    Abstract base class for stream resources.

    A stream resource is an object that encapsulates a stream that can
    be opened for reading or writing.  The backing store for the stream
    can be something like a file or an iterable like a list.

    Normally, the __init__() constructor accepts a reference to the stream
    backing store.
    """

    @contextmanager
    def open_read(self):
        """
        Return a readable stream, which is an iterator object over the
        elements of the backing store.
        """
        raise NotImplementedError()

    @contextmanager
    def open_write(self):
        """
        Return a writeable stream.

        Calling this method clears the contents of the backing store
        before returning a stream that writes to the store.
        """
        raise NotImplementedError()


# TODO: add error handling that reports the current item and item number.
class ListStreamResource(object):

    """A stream resource backed by a list."""

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


# TODO: add error handling that reports the current item and item number.
class FileStreamResource(object):

    """A stream resource backed by a file."""

    def __init__(self, path, encoding=None, **kwargs):
        if encoding is None:
            encoding = 'ascii'
        self.path = path
        self.encoding = encoding
        self.kwargs = kwargs

    @contextmanager
    def _open(self, mode):
        # TODO: use logged_open()?
        with open(self.path, mode, encoding=self.encoding, **self.kwargs) as f:
            yield f

    def open_read(self):
        return self._open("r")

    def open_write(self):
        return self._open("w")
