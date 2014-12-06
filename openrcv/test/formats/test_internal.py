
from openrcv.formats.internal import (parse_internal_ballot, to_internal_ballot,
                                      InternalBallotsResource)
from openrcv.streams import StringResource
from openrcv.utiltest.helpers import UnitCase


class ModuleTest(UnitCase):

    def test_parse_internal_ballot(self):
        cases = [
            ("1 2", (1, (2, ))),
            ("1", (1, ())),
            # Leading and trailing space are okay
            (" 1 2", (1, (2, ))),
            ("1 2 \n", (1, (2, ))),
        ]
        for line, expected in cases:
            with self.subTest(line=line, expected=expected):
                self.assertEqual(parse_internal_ballot(line), expected)

    def test_parse_internal_ballot__non_integer(self):
        with self.assertRaises(ValueError):
            parse_internal_ballot("f 2 \n")


class InternalBallotsResourceTest(UnitCase):

    def test_reading(self):
        resource = StringResource("1 2\n2 3 1\n")
        ballots_resource = InternalBallotsResource(resource)
        with ballots_resource.reading() as stream:
            actual = list(stream)
        expected = [
            (1, (2, )),
            (2, (3, 1)),
        ]
        self.assertEqual(actual, expected)

    def test_reading__error(self):
        resource = StringResource("1 2\n2 b 1\n")
        ballots_resource = InternalBallotsResource(resource)

        with self.assertRaises(ValueError) as cm:
            with ballots_resource.reading() as stream:
                actual = list(stream)
        # Check the exception text.
        err = cm.exception
        self.assertStartsWith(str(err), "last read item from <StringResource:")
        self.assertEndsWith(str(err), "(number=2): '2 b 1\\n'")

    def test_writing(self):
        ballots = [
            (1, (2, )),
            (2, (3, 1)),
        ]
        resource = StringResource()
        ballots_resource = InternalBallotsResource(resource)
        with ballots_resource.writing() as stream:
            for ballot in ballots:
                stream.write(ballot)
        self.assertEqual(resource.contents, "1 2\n2 3 1\n")

class InternalModuleTest(UnitCase):

    def test_to_internal_ballot(self):
        cases = [
            ((1, (2, )), "1 2"),
            ((1, (2, 3)), "1 2 3"),
            ((1, ()), "1"),
        ]
        for ballot, expected in cases:
            with self.subTest(ballot=ballot, expected=expected):
                self.assertEqual(to_internal_ballot(ballot), expected)
