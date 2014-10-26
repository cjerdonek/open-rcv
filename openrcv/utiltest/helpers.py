
"""
Helpers for unit testing.

"""

import os
import sys
import unittest

import openrcv

# The directory containing the openrcv package.
parent_dir = os.path.dirname(os.path.dirname(openrcv.__file__))

class CaseMixin(object):

    """
    General purpose mixin for unittest test cases.

    """

    def __str__(self):
        """
        Print the full dotted name of the test for easier cutting and pasting.

        This method's representation is more convenient than unittest's
        default representation because it simplifies cutting and pasting
        the test name to the command-line to run a specific test you are
        interested in.

        unittest's default display looks like this, for example:

          ERROR: test_main_status__exception (openrcv.test.scripts.test_run.MainTestCase)

        The new display looks like this--

          ERROR: MainTestCase.test_main_status__exception
           >> openrcv.test.scripts.test_run.MainTestCase.test_main_status__exception

        Specifically, the string on the second line can be cut-and-paste
        to the command-line as is.

        """
        cls = self.__class__
        mod_name = cls.__module__
        path = os.path.relpath(sys.modules[mod_name].__file__, parent_dir)
        return ("%s.%s\n"
                "  in %s\n"
                " >> %s.%s.%s" %
                (cls.__name__, self._testMethodName,
                 path,
                 mod_name, cls.__name__, self._testMethodName))


# This is for convenience to reduce typing.
class UnitCase(CaseMixin, unittest.TestCase):
    pass
