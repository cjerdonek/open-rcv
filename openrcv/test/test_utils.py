
from unittest import TestCase

from openrcv.utils import StringInfo


class StringInfoTest(TestCase):

    def test_init(self):
        stream = StringInfo("abc")
        self.assertEquals(stream.value, "abc")

    def test_reading(self):
        stream = StringInfo("abc")
        with stream.open() as f:
            out = f.read()
        self.assertEqual(out, "abc")
        # The value is also still available as an attribute.
        self.assertEqual(stream.value, "abc")

    def test_writing(self):
        stream = StringInfo()
        with stream.open("w") as f:
            f.write("abc")
        # The value can be obtained from the attribute.
        self.assertEqual(stream.value, "abc")

    def test_writing_to_non_empty(self):
        """Test writing to a non-empty string."""
        stream = StringInfo()
        stream.value = "foo"
        with self.assertRaises(AssertionError):
            stream.open("w")
