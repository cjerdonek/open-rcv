
"""
Helpers for unit testing.

"""

import unittest


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
        return ("%s.%s\n >> %s.%s.%s" %
                (self.__class__.__name__,
                 self._testMethodName,
                 self.__class__.__module__,
                 self.__class__.__name__,
                 self._testMethodName))


class UnitTestCase(CaseMixin, unittest.TestCase):
    pass
