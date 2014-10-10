
from unittest import TestCase

from openrcv.utils import ReprMixin, StringInfo


class ReprMixinTest(TestCase):

    class ReprSample(ReprMixin):

        def repr_desc(self):
            return "foo"

    def test_repr(self):
        obj = ReprMixin()
        expected = "<ReprMixin object: [--] %s>" % hex(id(obj))
        self.assertEqual(repr(obj), expected)

    def test_repr__implemented(self):
        obj = ReprMixinTest.ReprSample()
        expected = "<ReprSample object: [foo] %s>" % hex(id(obj))
        self.assertEqual(repr(obj), expected)


class StringInfoTest(TestCase):

    def test_init(self):
        stream = StringInfo("abc")
        self.assertEqual(stream.value, "abc")

    def test_init__no_args(self):
        stream = StringInfo()
        self.assertEqual(stream.value, None)

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
        """Test writing to a StringInfo initialized to a string."""
        stream = StringInfo()
        stream.value = ""  # Even an empty string triggers the ValueError.
        with self.assertRaises(ValueError):
            stream.open("w")
