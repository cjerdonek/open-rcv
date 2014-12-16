# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import logging
import os

from openrcv_setup import utils


PACKAGE_NAME = "openrcv"

LONG_DESCRIPTION = """\
OpenRCV
=======

OpenRCV is an open source software project for tallying ranked-choice
voting elections like instant runoff voting and the single transferable vote.

OpenRCV can be used as a command-line tool or as a Python library.

It is distributed for free on PyPI_ and the source code
is hosted on GitHub_.  It is open source under the permissive MIT
license.  See the License section below for details.


Features
--------

* Completely open and extensible.
* Tested against the publicly available test cases in the
  `open-rcv-tests`_ repository.
* Exposes both a command-line API and a Python API.
* Both APIs support neutral input and output text formats to allow
  interoperability with other applications and programming languages.
  For example, round-by-round results can be output as JSON to be--

    * Passed to a custom "pretty" HTML renderer, or
    * Checked numerically (i.e. independent of presentation) against
      test data.

* Detailed logging while counting contests.


Author
------

Chris Jerdonek (chris.jerdonek@gmail.com)


License
-------

{license}

.. _GitHub: https://github.com/cjerdonek/open-rcv
.. _PyPI: https://pypi.python.org/pypi/OpenRCV
.. _open-rcv-tests: https://github.com/cjerdonek/open-rcv-tests

"""

log = logging.getLogger(os.path.basename(__file__))


def configure_logging():
    """Configure setup.py logging with simple settings."""
    # Prefix the log messages to distinguish them from other text sent to
    # the error stream.
    format_string = ("%s: %%(name)s: [%%(levelname)s] %%(message)s" %
                     PACKAGE_NAME)
    logging.basicConfig(format=format_string, level=logging.INFO)
    log.debug("Debug logging enabled.")


def make_long_description():
    license = utils.read(utils.LICENSE_PATH)
    return LONG_DESCRIPTION.format(license=license)

configure_logging()


setup(
    name='OpenRCV',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.0.1-alpha',
    license='MIT',
    # The project homepage.
    url='https://github.com/cjerdonek/open-rcv',

    description='Software for tallying ranked-choice voting elections like IRV and STV',
    keywords='ballot choice election IRV ranked RCV single tally transferable STV vote voting',
    long_description=make_long_description(),

    author='Chris Jerdonek',
    author_email='chris.jerdonek@gmail.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'Topic :: Other/Nonlisted Topic',
    ],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=[]),

    install_requires=[
        'argparse2==0.5.0-alpha1',
        'colorlog >=2.0,<2.4',
    ],

    # To install dependencies for an extra from a source distribution,
    # you can do the following, for example:
    #
    #   $ pip install -e .[dev,test]
    #
    extras_require = {
        'dev':  [
            'check-manifest',
            'pandocfilters >=1.2,<1.3',
            'PyYAML >=3,<4',
            'sphinx',
            'sphinx-autobuild',
            'twine >=1.3,<1.4',
        ],
        'test':  [
            'coverage',
        ],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
    #    'sample': ['package_data.dat'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # The cmdclass commands below can be run using the form--
    #
    #   $ python setup.py KEY
    #
    cmdclass={
        'build_html': utils.BuildHtmlCommand,
        'update_long_desc': utils.LongDescriptionCommand,
    },

    entry_points={
        # "distutils.commands": [
        #     "foo = mypackage.some_module:foo",
        # ],
        'console_scripts': [
            'rcv=openrcv.scripts.rcv:main'
        ]
    },
)
