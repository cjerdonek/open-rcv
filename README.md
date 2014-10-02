OpenRCV
=======

[![Build Status](https://travis-ci.org/cjerdonek/open-rcv.svg?branch=master)](https://travis-ci.org/cjerdonek/open-rcv)

OpenRCV is an open source software project for tallying ranked-choice
voting elections like instant runoff voting and the single transferable vote.

It is distributed for free on [PyPI][openrcv-pypi] and the source code
is hosted on [GitHub][openrcv-github].  It is licensed under a permissive
open source license.  See the [License](#license) section for details
on the license.

**Note: this software is not yet usable.**


Features
--------

* Tested against the publicly available test cases in the
  [open-rcv-tests][open-rcv-tests] repository.
* Exposes both a command-line API and a Python API.
* The command-line API returns results as JSON to allow interoperability
  with other tools (e.g. to use a different results renderer).


Requirements
------------

OpenRCV can be run using Python 3.4.

If you do not already have Python 3.4, you can download it
[here][python-download].


Installing
----------

    $ pip install openrcv


Running It
----------

    $ rcvcount CONTEST.blt


Testing It
----------

    $ python -m unittest discover openrcv


Contributing
------------

To contribute to the project, see the [Contributing][openrcv-contribute]
page.


License
-------

This project is licensed under the permissive MIT license.
See the [LICENSE](LICENSE) file for the actual license wording.


Author
------

Chris Jerdonek (<chris.jerdonek@gmail.com>)


[openrcv-contribute]: docs/contributing.md
[openrcv-github]: https://github.com/cjerdonek/open-rcv
[openrcv-pypi]: https://pypi.python.org/pypi/OpenRCV
[open-rcv-tests]: https://github.com/cjerdonek/open-rcv-tests
[python-download]: https://www.python.org/downloads/
