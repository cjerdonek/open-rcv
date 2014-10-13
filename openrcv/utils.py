
from contextlib import contextmanager
from datetime import datetime
import io
import json
import logging
import os
import shutil
import timeit
import sys


# We only need ascii for the internal ballot file.
ENCODING_INTERNAL_BALLOTS = "ascii"
ENCODING_JSON = "utf-8"
FILE_ENCODING = "utf-8"

log = logging.getLogger(__name__)


def log_create_dir(path):
    log.info("creating dir: %s" % path)


def logged_open(*args, **kwargs):
    log.info("opening file: (%r, %r): %s" % (args[1:], kwargs, args[0]))
    try:
        return open(*args, **kwargs)
    except TypeError:
        raise TypeError("arguments: open(*%r, **%r)" % (args, kwargs))


def make_dirs(path):
    """Creates intermediate directories.

    Raises an error if the leaf directory already exists.
    """
    log_create_dir(path)
    os.makedirs(path)


def ensure_dir(path):
    if not os.path.exists(path):
        log_create_dir(path)
        os.makedirs(path)


def make_temp_dirname(name=None):
    """Return a temp directory name."""
    if name is not None:
        chars = string.ascii_lowercase + "_"
        name = name.lower().replace(" ", "_")
        name = "".join((c for c in name if c in chars))

    now = datetime.now().strftime("%Y%m%d_%H%M%S")

    # For example, "temp_20141002_074531_my_election".
    suffix = "" if name is None else "_" + name
    return "temp_%s%s" % (now, suffix)


@contextmanager
def temp_dir(path):
    """
    Create a directory at the given path for temporary use.

    """
    log_create_dir(path)
    os.mkdir(path)
    yield
    log.info("removing dir: %s" % path)
    shutil.rmtree(path)


@contextmanager
def temp_dir_inside(parent_dir):
    """
    Create a directory inside the given directory for temporary use.

    Returns the path to the directory created.

    """
    dir_name = make_temp_dirname()
    dir_path = os.path.join(parent_dir, dir_name)
    with temp_dir(dir_path):
        yield dir_path


@contextmanager
def time_it(description):
    """
    A context manager for timing chunks of code and logging it.

    Arguments:
      description: task description for logging purposes

    """
    log.info("start: %s..." % description)
    start_time = timeit.default_timer()
    yield
    elapsed = timeit.default_timer() - start_time
    log.info("done: %s: %.4f seconds" % (description, elapsed))


class ReprMixin(object):

    def __repr__(self):
        desc = self.repr_desc()
        desc = "--" if desc is None else desc
        return "<%s object: [%s] %s>" % (self.__class__.__name__, desc, hex(id(self)))

    def repr_desc(self):
        return None


class StreamInfo(ReprMixin):

    def open(self, mode=None):
        """
        Open the stream, and return a file object.

        Specifically, this method returns an io.IOBase object.  IOBase
        objects are iterable.  Iterating over them yields the lines in
        the stream.

        """
        if mode is None:
            mode = "r"
        return self._open(mode)


# TODO: default to ASCII.
class FileInfo(StreamInfo):

    """A wrapped file path that opens to become a file object."""

    def __init__(self, path, *args, **kwargs):
        """
        The `mode` argument to open() should not be included here.

        """
        self.path = path
        self.args = args
        self.kwargs = kwargs

    def _open(self, mode):
        return logged_open(self.path, mode, *self.args, **self.kwargs)


class _EjectingStringIO(io.StringIO):

    """A StringIO wrapper that saves its contents when closing."""

    def __init__(self, initial_value, info):
        """
        Arguments:
          info: a StringInfo object.

        """
        super().__init__(initial_value)
        self.info = info

    def close(self):
        self.info.value = self.getvalue()
        # The memory buffer is discarded when the object is closed.
        super().close()


class StringInfo(StreamInfo):

    """
    A wrapped string that opens to become an in-memory text stream.

    This class allows functions that accept a FileInfo object to be called
    using strings.  In particular, writing to disk and creating temporary
    files isn't necessary.  This is especially convenient for testing.

    """

    def __init__(self, value=None):
        self.value = value

    def repr_desc(self):
        return "contents=%s" % (self.get_display_value(10), )

    def get_display_value(self, limit=None):
        """
        Return the first `limit` characters plus "...".

        """
        value = self.value
        if limit is None or not value or len(value) <= limit:
            return value
        return repr(value[:limit]) + "..."

    # TODO: test this method on short text strings.
    def _open(self, mode):
        value = self.value
        display = self.get_display_value(limit=24)
        # As a precaution, make sure the string is empty if not reading.
        if (value is not None and mode != "r"):
            raise ValueError("Cannot write to string that already has a value: %r" % display)
        log.info("opening in-memory text stream (mode=%r): contents=%r" % (mode, display))
        return _EjectingStringIO(self.value, self)
