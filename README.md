OpenRCV
=======

This repository contains open source software for tallying ranked-choice
voting elections like instant runoff voting and the single transferable vote.

The software is licensed under a permissive open source license.
See the [License](#license) section for details.

**Note: this software is not yet usable.**


Setting up
----------

The script was written for Python 3.4.

You can download Python [from here][python-download].

Then just clone this repo and follow the usage instructions below.
Currently, there are no third-party dependencies.


Usage
-----

To run the script, run the following from the repo root--

    $ python3.4 count.py ELECTION.blt OUTPUT.txt

For additional usage notes, see the docstring of the main
[`count.py`](count.py#L7) file.


License
-------

This project is licensed under the permissive BSD 3-clause license.
See the [`LICENSE`](LICENSE) file for the actual license wording.


Author
------

Chris Jerdonek (<chris.jerdonek@gmail.com>)


[python-download]: https://www.python.org/downloads/
