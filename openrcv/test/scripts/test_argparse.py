
from argparse import ArgumentTypeError

from openrcv.scripts.argparse import parse_log_level
from openrcv.utiltest.helpers import skipIfTravis, UnitCase


# TODO: add a test for good args.
class ModuleTestCase(UnitCase):

    def test_parse_log_level(self):
        self.assertEqual(parse_log_level('INFO'), 20)
        self.assertEqual(parse_log_level('DEBUG'), 10)
        self.assertEqual(parse_log_level('35'), 35)
        self.assertEqual(parse_log_level(35), 35)
        with self.assertRaises(ArgumentTypeError):
            parse_log_level('FOO')
