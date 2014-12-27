OpenRCV
=======

[![Build Status](https://travis-ci.org/cjerdonek/open-rcv.svg?branch=master)](https://travis-ci.org/cjerdonek/open-rcv)
[![Coverage Status](https://img.shields.io/coveralls/cjerdonek/open-rcv.svg)](https://coveralls.io/r/cjerdonek/open-rcv?branch=master)
[![Read the Docs Status](https://readthedocs.org/projects/openrcv/badge/?version=latest)](http://docs.openrcv.org)

OpenRCV is an open source software project for tallying ranked-choice
voting elections like instant runoff voting and the single transferable vote.

OpenRCV supports auditing, reporting, and converting files.  It can be used
as either a command-line tool or as a Python library.

OpenRCV is distributed for free on [PyPI][openrcv_pypi].  The project page
and source code are on [GitHub][openrcv_github].  Project documentation is
hosted on [Read the Docs][openrcv_docs].

It is licensed under a permissive open source license.  See the
[License](#License) section for license details.

To report a bug or request a feature, visit the [issue tracker][openrcv_issues].
You can also contact the author listed [below](#Author).

**Note (as of December 2014): This project is not yet usable, but we are
actively working on it.**


Features
--------

* Completely open and extensible.
* Tested against the publicly available test cases in the
  [open-rcv-tests][open-rcv-tests] repository.
* Exposes both a command-line API and a Python API.
* Both APIs support neutral input and output text formats to allow
  interoperability with other applications and programming languages.
  For example, round-by-round results can be output as JSON to be--
    * Passed to a custom "pretty" HTML renderer, or
    * Checked numerically (i.e. independent of presentation) against
      test data.
* Detailed logging while counting contests.


Requirements
------------

OpenRCV can be run using Python 3.4 (preferably 3.4.2 or later).

If you do not already have Python 3.4, you can download it
[here][python-download].


Installing
----------

    $ pip install openrcv

If you see an error like the following in the logs, you can safely ignore it:

    build/temp.macosx-10.9-x86_64-3.4/check_libyaml.c:2:10: fatal error: 'yaml.h' file not found
        #include <yaml.h>
                 ^
        1 error generated.

        libyaml is not found or a compiler error: forcing --without-libyaml


Running It
----------

To count the ballots for one or more contests, pass the path to an OpenRCV
contests file:

    $ rcv count data/sample.yaml

For detailed command-line help:

    $ rcv --help


Testing It
----------

    $ python -m unittest discover openrcv


Developing
----------

For information on contributing technically to the project or developing
applications that interact with OpenRCV, see the [Development][doc-develop]
page.


License
-------

This project is licensed under the permissive MIT license.
See the [LICENSE](LICENSE) file for the actual license wording.


History
-------

Chris Jerdonek began writing the code on September 27, 2014.


Author
------

Chris Jerdonek (<chris.jerdonek@gmail.com>)


[doc-develop]: docs/develop.md
[openrcv_docs]: http://openrcv.readthedocs.org/
[openrcv_github]: https://github.com/cjerdonek/open-rcv
[openrcv_issues]: https://github.com/cjerdonek/open-rcv/issues
[openrcv_pypi]: https://pypi.python.org/pypi/OpenRCV
[open-rcv-tests]: https://github.com/cjerdonek/open-rcv-tests
[python-download]: https://www.python.org/downloads/
