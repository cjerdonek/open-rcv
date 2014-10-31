
from contextlib import closing, contextmanager
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
    try:
        mode = args[1]
    except IndexError:
        mode = 'r'

    _log = log.debug if (mode == 'r') else log.info
    _log('opening file (options=%r, %r): %s' % (args[1:], kwargs, args[0]))

    try:
        return open(*args, **kwargs)
    except (OSError, TypeError):
        raise Exception("arguments: open(*%r, **%r)" % (args, kwargs))


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

    # TODO: look up the proper return type.
    def __repr__(self):
        desc = self.repr_desc() or "--"
        return "<%s: [%s] %s>" % (self.__class__.__name__, desc, hex(id(self)))

    def repr_desc(self):
        return None


class ObjectExtension(ReprMixin):

    """An object wrapper allowing instance methods to be overridden."""

    def __init__(self, obj):
        self.object = obj

    def __getattr__(self, name):
        return getattr(self.object, name)

    def repr_desc(self):
        return "object=%r" % self.object


class UncloseableFile(ObjectExtension):

    """Used for wrapping standard streams like sys.stderr."""

    def close(self):
        pass


class StreamInfo(ReprMixin):

    """
    An object that can be opened to become a stream.

    This is an abstract base class for handling things like file objects,
    file paths, and strings with a common API.  StreamInfo instances
    encapsulate the information needed to expose or open a stream.

    The StreamInfo API lets us write higher-level APIs and implementations
    that handle all of the following use cases equally: file paths,
    strings, and standard streams like sys.stdout and sys.stderr (that are
    open to begin with and shouldn't be closed).  In particular, APIs can
    accept a StreamInfo object `stream_info` and then internally call
    `with stream_info.open() as f:` at the appropriate place, etc.

    This pattern is convenient for things like unit testing with strings
    as opposed to the file system, and writing API's that support writing
    to both standard streams and files defined by paths.

    """

    def open_object(self, mode):
        """Return a file object that is also a context manager."""
        raise NotImplementedError("by object: %r" % self)

    def open(self, mode=None):
        """
        Open the stream, and return a file object.

        Specifically, this method returns an io.IOBase object.  IOBase
        objects are iterable.  Iterating over them yields the lines in
        the stream.

        """
        if mode is None:
            mode = "r"
        return self.open_object(mode)


class PermanentFileInfo(StreamInfo):

    def __init__(self, file_):
        self.file = file_

    def repr_desc(self):
        return "stream=%r" % self.file

    def open_object(self, mode):
        # We call closing() to return a context manager.
        return closing(UncloseableFile(self.file))


# TODO: default to ASCII.
class PathInfo(StreamInfo):

    """A wrapped file path that opens to become a file object."""

    def __init__(self, path, *args, **kwargs):
        """
        The `mode` argument to open() should not be included here.

        """
        self.path = path
        self.args = args
        self.kwargs = kwargs

    def open_object(self, mode):
        return logged_open(self.path, mode, *self.args, **self.kwargs)


# TODO: check whether it would simplify things to use an ObjectExtension instead.
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

    This class allows functions that accept a PathInfo object to be called
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
    def open_object(self, mode):
        value = self.value
        display = self.get_display_value(limit=24)
        # As a precaution, make sure the string is empty if not reading.
        if (value is not None and mode != "r"):
            raise ValueError("Cannot write to string that already has a value: %r" % display)
        log.info("opening in-memory text stream (mode=%r): contents=%r" % (mode, display))
        return _EjectingStringIO(self.value, self)
