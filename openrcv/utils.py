
from contextlib import contextmanager
import logging
import os
import timeit
import sys


FILE_ENCODING = "utf-8"

log = logging.getLogger(__name__)


def logged_open(*args, **kwargs):
    log.info("opening: %s" % args[0])
    return open(*args, **kwargs)


def make_dirs(path):
    """Creates intermediate directories.

    Raises an error if the leaf directory already exists.
    """
    log.info("creating dir: %s" % path)
    os.makedirs(path)


def ensure_dir(path):
    if not os.path.exists(path):
        log.info("creating dir: %s" % path)
        os.makedirs(path)


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
