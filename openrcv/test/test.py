
import unittest

def run_tests():
    # TODO: discover all tests.
    unittest.main(module=__name__)


class MainTestCase(unittest.TestCase):

    def test(self):
        self.assertEqual(1, 1)
