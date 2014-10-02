OpenRCV
=======

|Build Status|

OpenRCV is an open source software project for tallying ranked-choice
voting elections like instant runoff voting and the single transferable
vote.

It is distributed for free on
`PyPI <https://pypi.python.org/pypi/OpenRCV>`__ and the source code is
hosted on `GitHub <https://github.com/cjerdonek/open-rcv>`__. It is
licensed under a permissive open source license. See the
`License <https://pypi.python.org/pypi/OpenRCV/#license>`__ section for
details on the license.

**Note: this software is not yet usable.**

Features
--------

-  Tested against the publicly available test cases in the
   `open-rcv-tests <https://github.com/cjerdonek/open-rcv-tests>`__
   repository.
-  Exposes both a command-line API and a Python API.
-  The command-line API returns results as JSON to allow
   interoperability with other tools (e.g. to use a different results
   renderer).

Requirements
------------

OpenRCV can be run using Python 3.4.

If you do not already have Python 3.4, you can download it
`here <https://www.python.org/downloads/>`__.

Installing
----------

::

    $ pip install openrcv

Running It
----------

::

    $ rcvcount ELECTION.blt

Testing It
----------

::

    $ python -m unittest discover openrcv

Contributing
------------

To contribute to the project, see the
`Contributing <https://github.com/cjerdonek/open-rcv/blob/master/docs/contributing.md>`__
page.

License
-------

This project is licensed under the permissive MIT license. See the
`LICENSE <https://github.com/cjerdonek/open-rcv/blob/master/LICENSE>`__
file for the actual license wording.

Author
------

Chris Jerdonek (chris.jerdonek@gmail.com)

.. |Build Status| image:: https://travis-ci.org/cjerdonek/open-rcv.svg?branch=master
   :target: https://travis-ci.org/cjerdonek/open-rcv
