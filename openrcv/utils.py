
from contextlib import contextmanager
import timeit
import sys


FILE_ENCODING = "utf-8"


# TODO: use Python's logging module.
# TODO: move this to an utils.py.
def log(s=None):
    """Write to stderr."""
    if s is None:
        s = ""
    print(s, file=sys.stderr)


@contextmanager
def time_it(task_desc):
    """
    A context manager for timing chunks of code and logging it.

    Arguments:
      task_desc: task description for logging purposes

    """
    start_time = timeit.default_timer()
    yield
    elapsed = timeit.default_timer() - start_time
    log("elapsed (%s): %.4f seconds" % (task_desc, elapsed))
