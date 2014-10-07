Contributing to OpenRCV
=======================

This is a guide for contributors to OpenRCV.  In particular, it shows you
how to interact with the project from a source checkout.

For instructions on installing or using the application, consult the
[`README`](../README.md) or [project page][open-rcv] instead.

For instructions on releasing new versions of OpenRCV to PyPI, consult
the file [`docs/releasing.md`][openrcv-releasing].


Setting Up
----------

This section provides instructions on getting set up to contribute.


### Get the code

Clone the repository.

Then, download the [open-rcv-tests][open-rcv-tests] test cases:

    $ git submodule update --init

(Downloading the test cases is optional but recommended.)


### Create virtual environment

Next, we recommend creating a Python virtual environment to stay
isolated from your system Python.  You can do this using [pyvenv][venv],
which was included in Python as of Python 3.3.  Simply run the following
from the repository root:

    $ pyvenv venv
    $ source venv/bin/activate

Alternatively, you can use virtualenv (and virtualenvwrapper).  See
also the recommendations in the ["Python Packaging User Guide"][pug].

Also see [this gist][workon-gist] for a way to automatically enter
the project's virtualenv when entering its directory with `cd`.


### Install Requirements

Install the project in "develop" mode:

    $ pip install -e .[dev,test]

This lets you `openrcv` from the command-line as if you had installed
it from PyPI.

The `[dev,test]` portion of the command means to install the `extras_require`
dependencies specified in [`setup.py`](setup.py) and with key `dev`.
These are the development-only dependencies.


### Pandoc

Pandoc is a command-line tool for converting text files to and from
different formats (e.g. markdown, html, and rst).

It is needed more for [releasing][openrcv-releasing], but in certain
situations may be useful for other contributors (e.g. previewing
documentation locally).

To install pandoc, follow the instructions on [pandoc's home page][pandoc].


### TextMate

If you use TextMate, you can include the following at the beginning of
your `*.tmproj` file's `regexFolderFilter:

    <string>!dist|.*.egg-info|...


Running Tests
-------------

From the repo root, for tests and a code coverage report:

    $ ./test.sh

Or for just tests--

    $ python -m unittest

To run a single test, for example--

    $ python -m unittest openrcv.test.test_models.JsonContestTest.test_load_jsobj


Viewing Docs
------------

    $ python setup.py build_html


[workon-gist]: https://gist.github.com/cjerdonek/7583644
[open-rcv]: https://github.com/cjerdonek/open-rcv
[open-rcv-tests]: https://github.com/cjerdonek/open-rcv-tests
[openrcv-releasing]: releasing.md
[pandoc]: http://johnmacfarlane.net/pandoc/
[pug]: https://packaging.python.org/en/latest/tutorial.html
[venv]: https://docs.python.org/3/library/venv.html
