
from contextlib import contextmanager
from datetime import datetime
import logging
import os
import shutil
import timeit
import sys


ENCODING_INTERNAL_BALLOTS = "ascii"
FILE_ENCODING = "utf-8"

log = logging.getLogger(__name__)


def log_create_dir(path):
    log.info("creating dir: %s" % path)


def logged_open(*args, **kwargs):
    log.info("opening (%r, %r): %s" % (args[1:], kwargs, args[0]))
    return open(*args, **kwargs)


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
    log.info("start: %s" % description)
    start_time = timeit.default_timer()
    yield
    elapsed = timeit.default_timer() - start_time
    log.info("done: %s: %.4f seconds" % (description, elapsed))
