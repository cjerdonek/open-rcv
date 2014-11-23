
from contextlib import contextmanager
import os
from tempfile import TemporaryDirectory

from openrcv.streams import (ListStream, ListStreamResource, FileStreamResource,
                             TrackingStream)
from openrcv.utiltest.helpers import UnitCase


class TrackingStreamTest(UnitCase):

    def assert_state(self, tracking, item, number):
        self.assertEqual(tracking.item, item)
        self.assertEqual(tracking.item_number, number)

    def test_init(self):
        stream = ListStream([1, 2, 3])
        tracking = TrackingStream(stream)
        self.assert_state(tracking, None, 0)

    # TODO: enable this test.
    def _test_iter(self):
        stream = ListStream(['a', 'b', 'c'])
        tracking = TrackingStream(stream)
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

    def test_open_read(self):
        with self.resource() as resource:
            with resource.open_read() as stream:
                items = tuple(stream)
            self.assertEqual(items, ("a\n", "b\n"))
            # Check that you can read again.
            with resource.open_read() as stream:
                items = tuple(stream)
            self.assertEqual(items, ("a\n", "b\n"))

    def test_open_read__exhausts(self):
        """
        Check that iterating through the stream exhausts it, i.e.
        that stream is an iterator object.
        """
        with self.resource() as resource:
            with resource.open_read() as stream:
                items1 = tuple(stream)
                items2 = tuple(stream)
            self.assertEqual(items1, ("a\n", "b\n"))
            self.assertEqual(items2, ())

    # TODO: enable this test.
    def _test_open_read__error(self):
        """
        Check that an error while reading shows the line number.
        """
        with self.resource() as resource:
            with resource.open_read() as stream:
                item = next(stream)
                self.assertEqual(item, "a\n")
                raise Exception()

    def test_open_write(self):
        with self.resource() as resource:
            with resource.open_write() as stream:
                stream.write('c\n')
                stream.write('d\n')
            with resource.open_read() as stream:
                items = tuple(stream)
            self.assertEqual(items, ('c\n', 'd\n'))

    def test_writing_deletes(self):
        """
        Check that open_write() deletes the current data.
        """
        with self.resource() as resource:
            with resource.open_read() as stream:
                items = tuple(stream)
            self.assertEqual(items, ("a\n", "b\n"))
            with resource.open_write() as stream:
                pass
            with resource.open_read() as stream:
                items = tuple(stream)
            self.assertEqual(items, ())


class ListStreamResourceTest(StreamResourceTestMixin, UnitCase):

    """ListStreamResource tests."""

    @contextmanager
    def resource(self):
        yield ListStreamResource(["a\n", "b\n"])


class FileStreamResourceTest(StreamResourceTestMixin, UnitCase):

    """FileStreamResource tests."""

    @contextmanager
    def resource(self):
        with TemporaryDirectory() as dirname:
            path = os.path.join(dirname, 'temp.txt')
            with open(path, 'w') as f:
                f.write('a\nb\n')
            yield FileStreamResource(path)
