
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

    """Tests of ListStreamResource."""

    def test_open_read(self):
        resource = ListStreamResource([3, 1])
        with resource.open_read() as stream:
            items = tuple(stream)
        self.assertEqual(items, (3, 1))
        # Check that you can read again.
        with resource.open_read() as stream:
            items = tuple(stream)
        self.assertEqual(items, (3, 1))

    def test_reading_exhausts(self):
        resource = ListStreamResource([3, 1])
        with resource.open_read() as stream:
            items1 = tuple(stream)
            # Check that iterating through the stream exhausts it, i.e.
            # that stream is an iterator object.
            items2 = tuple(stream)
        self.assertEqual(items1, (3, 1))
        self.assertEqual(items2, ())

    def test_open_write(self):
        resource = ListStreamResource()
        with resource.open_write() as stream:
            stream.write(3)
            stream.write(2)
        with resource.open_read() as stream:
            items = tuple(stream)
        self.assertEqual(items, (3, 2))

    def test_writing_deletes(self):
        """
        Check that open_write() deletes the current data.
        """
        resource = ListStreamResource([3, 1])
        with resource.open_read() as stream:
            items = tuple(stream)
        self.assertEqual(items, (3, 1))
        with resource.open_write() as stream:
            pass
        with resource.open_read() as stream:
            items = tuple(stream)
        self.assertEqual(items, ())


class ListStreamResourceTest(StreamResourceTestMixin, UnitCase):

    """Tests of ListStreamResource."""

    pass


class FileStreamResourceTest(UnitCase):

    """Tests of PathStreamResource."""

    def test_open_read(self):
        with TemporaryDirectory() as dirname:
            path = os.path.join(dirname, 'temp.txt')
            with open(path, 'w') as f:
                f.write('foo\nbar\n')

            resource = FileStreamResource(path)
            with resource.open_read() as stream:
                items = tuple(stream)
            self.assertEqual(items, ('foo\n', 'bar\n'))
            # Check that you can read again.
            with resource.open_read() as stream:
                items = tuple(stream)
            self.assertEqual(items, ('foo\n', 'bar\n'))
