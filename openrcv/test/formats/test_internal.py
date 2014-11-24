
from openrcv.formats.internal import to_internal_ballot, InternalBallotsResource
from openrcv.streams import StringResource
from openrcv.utiltest.helpers import UnitCase


class InternalBallotsResourceTest(UnitCase):

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
