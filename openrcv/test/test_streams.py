
from contextlib import contextmanager
import os
from tempfile import TemporaryDirectory

from openrcv.streams import (ListResource, FileResource, ReadableTrackedStream, StringResource)
from openrcv.utiltest.helpers import UnitCase


class ReadableTrackedStreamTest(UnitCase):

    def assert_state(self, tracking, item, number):
        self.assertEqual(tracking.item, item)
        self.assertEqual(tracking.item_number, number)

    def test_init(self):
        stream = [1, 2, 3]
        tracking = ReadableTrackedStream(stream)
        self.assert_state(tracking, None, 0)

    # TODO: enable this test.
    def _test_iter(self):
        stream = ListStream(['a', 'b', 'c'])
        tracking = ReadableTrackedStream(stream)
        items = iter(tracking)
        self.assert_state(tracking, None, 0)
        item = next(items)
        self.assert_state(tracking, 'a', 1)
        item = next(items)
        self.assert_state(tracking, 'b', 2)
        # Check what happens when you start over.
        items = iter(tracking)
        self.assert_state(tracking, None, 0)

class StreamResourceTestMixin(object):

    """Base mixin for StreamResource tests."""

    def test_reading(self):
        with self.resource() as resource:
            with resource.reading() as stream:
                items = tuple(stream)
            self.assertEqual(items, ("a\n", "b\n"))
            # Check that you can read again.
            with resource.reading() as stream:
                items = tuple(stream)
            self.assertEqual(items, ("a\n", "b\n"))

    def test_reading__exhausts(self):
        """
        Check that iterating through the stream exhausts it, i.e.
        that stream is an iterator object.
        """
        with self.resource() as resource:
            with resource.reading() as stream:
                items1 = tuple(stream)
                items2 = tuple(stream)
            self.assertEqual(items1, ("a\n", "b\n"))
            self.assertEqual(items2, ())

    def test_reading__error(self):
        """
        Check that an error while reading shows the line number.
        """
        with self.assertRaises(ValueError) as cm:
            with self.resource() as resource:
                with resource.reading() as stream:
                    item = next(stream)
                    self.assertEqual(item, "a\n")
                    raise ValueError()
        # Check the exception text.
        err = cm.exception
        self.assertStartsWith(str(err), "last read %s of <%s:" %
                              (self.expected_label, self.class_name))
        self.assertEndsWith(str(err), ": number=1, 'a\\n'")

    def test_writing(self):
        with self.resource() as resource:
            with resource.writing() as stream:
                stream.write('c\n')
                stream.write('d\n')
            with resource.reading() as stream:
                items = tuple(stream)
            self.assertEqual(items, ('c\n', 'd\n'))

    def test_writing__deletes(self):
        """
        Check that writing() deletes the current data.
        """
        with self.resource() as resource:
            with resource.reading() as stream:
                items = tuple(stream)
            self.assertEqual(items, ("a\n", "b\n"))
            with resource.writing() as stream:
                pass
            with resource.reading() as stream:
                items = tuple(stream)
            self.assertEqual(items, ())

    def test_writing__error(self):
        """
        Check that an error while writing shows the line number.
        """
        with self.assertRaises(ValueError) as cm:
            with self.resource() as resource:
                with resource.writing() as stream:
                    stream.write('c\n')
                    stream.write('d\n')
                    raise ValueError('foo')
        # Check the exception text.
        err = cm.exception
        self.assertStartsWith(str(err), "last written %s of <%s:" %
                              (self.expected_label, self.class_name))
        self.assertEndsWith(str(err), ": number=2, 'd\\n'")


class ListResourceTest(StreamResourceTestMixin, UnitCase):

    """ListResource tests."""

    class_name = "ListResource"
    expected_label = "item"

    @contextmanager
    def resource(self):
        yield ListResource(["a\n", "b\n"])


class FileResourceTest(StreamResourceTestMixin, UnitCase):

    """FileResource tests."""

    class_name = "FileResource"
    expected_label = "line"

    @contextmanager
    def resource(self):
        with TemporaryDirectory() as dirname:
            path = os.path.join(dirname, 'temp.txt')
            with open(path, 'w') as f:
                f.write('a\nb\n')
            yield FileResource(path)

# TODO: add StandardResource tests.

class StringResourceTest(StreamResourceTestMixin, UnitCase):

    """StringResource tests."""

    class_name = "StringResource"
    expected_label = "line"

    @contextmanager
    def resource(self):
        yield StringResource('a\nb\n')
