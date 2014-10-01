
import logging
import os
from subprocess import check_output

from setuptools import Command


ENCODING = 'utf-8'
LONG_DESCRIPTION_PATH = "setup_long_description.rst"

log = logging.getLogger(os.path.basename(__name__))


def read(path, encoding=None):
    if encoding is None:
        encoding = ENCODING
    # This implementation was chosen to be compatible across Python 2/3.
    with open(path, 'r', encoding=ENCODING) as f:
        text = f.read()
    return text


def write(text, path, description=None):
    """Write a string to a file."""
    desc = ('%s ' % description) if description else ''
    log.info("writing %sto: %s" % (desc, path))
    with open(path, 'w', encoding=ENCODING) as f:
        f.write(text)


def run_pandoc(args):
    args = ['pandoc'] + args
    log.info("running pandoc in a subprocess: %r" % " ".join(args))
    try:
        stdout = check_output(args)
    except FileNotFoundError as err:
        msg = ("pandoc not found:\n"
               "  -->%s\n"
               "  Did you install pandoc? See the documentation for more info." % err)
        raise Exception(msg)
    return stdout


def update_long_description_file():
    rst = run_pandoc(["--write=rst", "README.md"])
    rst = rst.decode('utf-8')
    write(rst, "setup_long_description.rst", "long_description")


class CommandBase(Command):

    description = None

    # The following three must all be present to avoid errors.
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class LongDescriptionCommand(CommandBase):

    description = "Update the reST long_description file."

    def run(self):
        update_long_description_file()
