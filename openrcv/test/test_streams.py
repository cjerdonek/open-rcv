#
# Copyright (c) 2014 Chris Jerdonek. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

from contextlib import contextmanager
import os
import tempfile
from tempfile import TemporaryDirectory

from openrcv import streams
from openrcv.streams import (tracked, FilePathResource,
                             ReadWriteFileResource, StringResource)
from openrcv.utiltest.helpers import UnitCase


class _Exception(Exception):
    pass


class TrackedTest(UnitCase):

    """Tests of tracked()."""

    def test(self):
        stream = ['a', 'b', 'c']
        gen = tracked("foo", stream)
        items = list(gen)
        self.assertEqual(items, ['a', 'b', 'c'])
        # Check that the return value exhausts (i.e. is an iterator object).
        items = list(gen)
        self.assertEqual(items, [])

    def test__exception(self):
        stream = ['a', 'b', 'c']
        gen = tracked("foo", stream)
        first = next(gen)
        self.assertEqual(first, "a")
        second = next(gen)
        with self.assertRaises(ValueError) as cm:
            gen.throw(ValueError("foo"))
        # Check the exception text.
        err = cm.exception
        self.assertEqual(str(err), "last read item from 'foo' (number=2): 'b'")
        # TODO: check that "foo" is also in the exception.

class StreamResourceTestMixin(object):

    """Base mixin for StreamResource tests."""

    @property
    def class_name(self):
        return self.cls.__name__

    def test_reading(self):
        with self.resource() as resource:
            with resource.reading() as stream:
                items = tuple(stream)
            self.assertEqual(items, ("a\n", "b\n"))
            # Check that you can read again.
            with resource.reading() as stream2:
                items = tuple(stream2)
            self.assertEqual(items, ("a\n", "b\n"))
            # Sanity-check that reading() doesn't return the same object each time.
            self.assertIsNot(stream, stream2)

    def test_reading__closes(self):
        """Check that the context manager closes the generator."""
        with self.resource() as resource:
            with resource.reading() as gen:
                item = next(gen)
            self.assertEqual(item, "a\n")
            self.assertGeneratorClosed(gen)

    def test_reading__iterator(self):
        """Check that reading() returns an iterator [1].

        [1]: https://docs.python.org/3/glossary.html#term-iterator
        """
        with self.resource() as resource:
            with resource.reading() as stream:
                # Check that __iter__() returns itself.
                self.assertIs(iter(stream), stream)
                # Check that the iterable exhausts after iteration.
                items = tuple(stream)
                with self.assertRaises(StopIteration):
                    next(stream)
            self.assertEqual(items, ("a\n", "b\n"))

    def test_reading__error(self):
        """Check that an error while reading shows the line number."""
        with self.assertRaises(_Exception) as cm:
            with self.resource() as resource:
                with resource.reading() as stream:
                    item = next(stream)
                    self.assertEqual(item, "a\n")
                    raise _Exception()
        # Check the exception text.
        err = cm.exception
        self.assertStartsWith(str(err), "last read item from <%s:" % self.class_name)
        self.assertEndsWith(str(err), "(number=1): 'a\\n'")

    def test_writing(self):
        with self.resource() as resource:
            with resource.writing() as target:
                target.send('c\n')
                target.send('d\n')
            with resource.reading() as stream:
                items = tuple(stream)
            self.assertEqual(items, ('c\n', 'd\n'))

    def test_writing__closes(self):
        """Check that the context manager closes the generator."""
        with self.resource() as resource:
            with resource.writing() as gen:
                gen.send('c\n')
            self.assertGeneratorClosed(gen)

    def test_writing__deletes(self):
        """Check that writing() deletes the current data."""
        with self.resource() as resource:
            with resource.reading() as stream:
                items = tuple(stream)
            self.assertEqual(items, ("a\n", "b\n"))
            with resource.writing() as stream:
                pass
            with resource.reading() as stream:
                items = tuple(stream)
            self.assertEqual(items, ())


class ListResourceTest(StreamResourceTestMixin, UnitCase):

    """ListResource tests."""

    cls = streams.ListResource

    @contextmanager
    def resource(self):
        yield self.cls(["a\n", "b\n"])

    def test_temp(self):
        with self.cls.temp() as temp_resource:
            with temp_resource.writing() as gen:
                gen.send("f\n")
            self.assertResourceContents(temp_resource, ["f\n"])
        # Check that the temp resource was deleted.
        self.assertResourceContents(temp_resource, [])

    def test_replacement(self):
        with self.resource() as resource:
            with resource.replacement() as temp_resource:
                with temp_resource.writing() as gen:
                    gen.send("f\n")
                self.assertResourceContents(resource, ["a\n", "b\n"])
                self.assertResourceContents(temp_resource, ["f\n"])
            # Check after replacement.
            self.assertResourceContents(resource, ["f\n"])
            self.assertResourceContents(temp_resource, [])

class FilePathResourceTest(StreamResourceTestMixin, UnitCase):

    """FilePathResource tests."""

    cls = streams.FilePathResource

    @contextmanager
    def resource(self):
        with TemporaryDirectory() as dirname:
            path = os.path.join(dirname, 'temp.txt')
            with open(path, 'w') as f:
                f.write('a\nb\n')
            yield FilePathResource(path)


class ReadWriteFileResourceTest(StreamResourceTestMixin, UnitCase):

    """ReadWriteFileResource tests."""

    cls = streams.ReadWriteFileResource

    @contextmanager
    def resource(self):
        with tempfile.TemporaryFile(mode='w+t', encoding='ascii') as f:
            f.write('a\nb\n')
            yield ReadWriteFileResource(f)


class SpooledReadWriteFileResourceTest(StreamResourceTestMixin, UnitCase):

    """ReadWriteFileResource tests (using tempfile.SpooledTemporaryFile)."""

    cls = streams.ReadWriteFileResource

    @contextmanager
    def resource(self):
        with tempfile.SpooledTemporaryFile(mode='w+t', encoding='ascii') as f:
            f.write('a\nb\n')
            yield ReadWriteFileResource(f)


# TODO: add StandardResource tests.

class StringResourceTest(StreamResourceTestMixin, UnitCase):

    """StringResource tests."""

    cls = streams.StringResource

    @contextmanager
    def resource(self):
        yield StringResource('a\nb\n')


class _Converter(object):

    def from_resource(self, item):
        return 2 * item

    def to_resource(self, item):
        return 3 * item


class ConvertingResourceTest(UnitCase):

    """Tests of the ConvertingResource class."""

    def test_reading(self):
        backing = streams.ListResource([1, 2, 3])
        converter = _Converter()
        resource = streams.ConvertingResource(backing, converter=converter)
        with resource.reading() as gen:
            items = list(gen)
        self.assertEqual(items, [2, 4, 6])
        self.assertGeneratorClosed(gen)

    def test_writing(self):
        backing = streams.ListResource()
        converter = _Converter()
        resource = streams.ConvertingResource(backing, converter=converter)
        with resource.writing() as gen:
            for i in range(4):
                gen.send(i)
        self.assertGeneratorClosed(gen)
        self.assertResourceContents(backing, [0, 2, 4, 6])
