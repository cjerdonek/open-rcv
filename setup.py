# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import logging
import os

from openrcv_setup import utils


PACKAGE_NAME = "openrcv"

log = logging.getLogger(os.path.basename(__file__))


def configure_logging():
    """
    Configure setup.py logging with simple settings.

    """
    # Prefix the log messages to distinguish them from other text sent to
    # the error stream.
    format_string = ("%s: %%(name)s: [%%(levelname)s] %%(message)s" %
                     PACKAGE_NAME)
    logging.basicConfig(format=format_string, level=logging.INFO)
    log.debug("Debug logging enabled.")

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

    description='open-source software for tallying ranked-choice voting elections',
    keywords='ballot choice election ranked rcv single tally transferable stv vote voting',
    long_description=utils.read(utils.LONG_DESCRIPTION_PATH),

    author='Chris Jerdonek',
    author_email='chris.jerdonek@gmail.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=[]),

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    # install_requires=['peppercorn'],

    # To install dependencies for an extra from a source distribution,
    # you can do the following, for example:
    #
    #   $ pip install -e .[dev]
    #
    extras_require = {
        'dev':  [
            'check-manifest',
            'pandocfilters >=1.2,<1.3',
            'twine >=1.3,<1.4'
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

    # These commands can be run with--
    #
    #   $ python setup.py KEY
    #
    cmdclass={
        'build_html': utils.BuildHtmlCommand,
        'update_long_desc': utils.LongDescriptionCommand,
    },
    entry_points={
        'console_scripts': [
            'rcvcount=openrcv.main:main',
            'rcvtest=openrcv.test.test_parsing:run_tests',
        ],
    },
)
