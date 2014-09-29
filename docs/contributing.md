Contributing to OpenRCV
=======================

This document provides assistance for contributors to OpenRCV.  In
particular, it shows you how to interact with OpenRCV from a source
checkout.

For instructions on installing or using the application, consult the
[`README`](../README.md) or [project page][open-rcv] instead.
For instructions on releasing the application to PyPI and understanding
the `setup.py`, consult the `releasing.md` file in the `docs` folder.

TODO: add instructions for previewing a Markdown file.


Setting Up
----------

First, clone the repository.

Next, we recommend creating a Python virtual environment to stay
isolated from your system Python.  You can do this using [pyvenv][venv],
which was included in Python as of Python 3.3.  Simply run the following
from the repository root:

    $ pyvenv venv
    $ source venv/bin/activate

Alternatively, you can use virtualenv (and virtualenvwrapper).  See
also the recommendations in the ["Python Packaging User Guide"][pug].

Finally, install the source code in "develop" mode:

    $ pip install -e .

This lets you `openrcv` from the command-line as if you had installed
it from PyPI.


Running Tests
-------------

TODO: add Tox instructions.


For Maintainers
---------------

For instructions on releasing new versions of OpenRCV and on how to use
`setup.py`, consult the file [`docs/releasing.md`](docs/releasing.md).


[open-rcv]: https://github.com/cjerdonek/open-rcv
[pug]: https://packaging.python.org/en/latest/tutorial.html
[venv]: https://docs.python.org/3/library/venv.html
