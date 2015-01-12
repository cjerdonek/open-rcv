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

"""Contains classes that support serialization to JSON test cases.

Terminology
-----------

The model class names in this module have the form `JsonCase*` (as
opposed to `JsonTestCase*`).  This is partly to avoid confusion with
`unittest.TestCase` classes.  We also frequently follow the convention
of using variables of the form `jc_*` (e.g. `jc_ballot`) to represent
instances of JsonCase classes -- especially when needed to distinguish
from other types of ballot objects (e.g. `Ballot` objects and ballot
JSON objects).

Warning
-------

The classes in this module should be used only for small sets of ballots
(e.g. those that arise in JSON test cases).  For large numbers of ballots,
ballot data should be backed by a concrete file and ballots read and
processed one at a time -- as opposed to having to load them into memory
all at once.
"""

from openrcv import contestgen, models, streams
from openrcv.formats.internal import parse_internal_ballot, to_internal_ballot
from openrcv.jsonlib import (from_jsobj, Attribute, JsonableError, JsonableMixin,
                             JsonDeserializeError)
from openrcv.utils import StringInfo


class JsonCaseConstants(JsonableMixin):

    meta_attrs = (Attribute('name'),
                  Attribute('notes'), )
    data_attrs = (Attribute('candidate_names'), )


class JsonCaseBallot(JsonableMixin):

    """The serialization format is a space-delimited string of integers of
    the form: "WEIGHT CHOICE1 CHOICE2 CHOICE3 ...".
    """

    data_attrs = (Attribute('choices'),
                  Attribute('weight'))

    # We need to override model_to_kwargs() since the model object is a
    # tuple rather than a class with attributes.
    @classmethod
    def model_to_kwargs(cls, model_obj):
        """Make jsonable kwargs from the given model object."""
        weight, choices = model_obj
        return {'weight': weight, 'choices': choices}

    def __init__(self, choices=None, weight=1):
        if choices is None:
            choices = ()
        self.choices = tuple(choices)
        self.weight = weight

    def repr_info(self):
        return "weight=%r choices=%r" % (self.weight, self.choices)

    def save_from_model(self, ballot):
        """
        Arguments:
          ballot: a Ballot object.
        """
        try:
            weight, choices = ballot
        except:
            raise Exception("ballot: %r" % ballot)
        self.__init__(choices=choices, weight=weight)

    def to_model(self):
        """
        Arguments:
          ballot: a Ballot object.
        """
        return self.weight, self.choices

    def save_from_jsobj(self, jsobj):
        """Read a JSON object, and set attributes to match."""
        try:
            weight, choices = parse_internal_ballot(jsobj)
        except ValueError:
            # Can happen with "1 2 abc", for example.
            # ValueError: invalid literal for int() with base 10: 'abc'
            raise JsonDeserializeError("error parsing: %r" % jsobj)
        self.__init__(choices=choices, weight=weight)

    def to_jsobj(self):
        """Return a JSON object."""
        ballot = self.to_model()
        return to_internal_ballot(ballot)


class JsonCaseContestInput(JsonableMixin):

    """Contest input for a JSON test case.

    Attributes (metadata):
      normalize_ballots: None means True.  Defaults to None.

    Attributes:
      ballots: an iterable of JsonCaseBallot objects.
      candidate_count: integer number of candidates.
    """

    meta_attrs = (Attribute('id', model=False),
                  Attribute('index', model=False),
                  Attribute('name'),
                  Attribute('normalize_ballots', model=False),
                  Attribute('rule_sets', model=False),
                  Attribute('notes'), )
    data_attrs = (Attribute('ballots', cls=JsonCaseBallot, model=False),
                  Attribute('candidate_count', model=False),
                  # TODO: make model=True.
                  Attribute('tie_elimination_order', model=False), )

    def repr_info(self):
        return "index=%s id=%s" % (self.index, self.id)

    def make_candidate_names(self):
        return contestgen.make_standard_candidate_names(self.candidate_count)

    # TODO: DRY this up by making last two lines part of base class.
    def save_from_model(self, contest):
        """
        Arguments:
          contest: a ContestInput object.
        """
        candidate_count = None if contest.candidates is None else len(contest.candidates)
        with contest.ballots_resource.reading() as ballots:
            ballots = [JsonCaseBallot.from_model(b) for b in ballots]
        kwargs = self.model_to_kwargs(contest)
        self.__init__(candidate_count=candidate_count, ballots=ballots, **kwargs)

    # TODO: think about how the creation of a new ballots resource should
    # be handled, since it involves managing another resource.
    # TODO: DRY this up by making last two lines part of base class.
    def to_model(self):
        """Return a ContestInput object."""
        candidates = self.make_candidate_names()
        ballots = [b.to_model() for b in self.ballots]
        # We use a list resource as the backing store for now because the
        # number of ballots is small.
        resource = streams.ListResource(ballots)
        ballots_resource = models.BallotsResource(resource)
        kwargs = self.model_to_kwargs(self)
        contest = models.ContestInput(candidates=candidates,
                                      ballots_resource=ballots_resource, **kwargs)
        return contest

    # def save_from_jsobj(self, jsobj):
    #     """Read a JSON object, and set attributes to match."""
    #     try:
    #         weight, choices = parse_internal_ballot(jsobj)
    #     except ValueError:
    #         # Can happen with "1 2 abc", for example.
    #         # ValueError: invalid literal for int() with base 10: 'abc'
    #         raise JsonDeserializeError("error parsing: %r" % jsobj)
    #     self.__init__(choices=choices, weight=weight)


class JsonCaseContestsFile(JsonableMixin):

    """Represents a JSON contests file for open-rcv-tests."""

    meta_attrs = (Attribute('version'), )
    data_attrs = (Attribute('contests', cls=JsonCaseContestInput), )


class JsonCaseRoundResult(JsonableMixin):

    """Represents the results of a round for testing purposes.

    Attributes:
      candidates_info: a CandidatesInfo object.
    """

    data_attrs = (Attribute('candidates_info'),
                  Attribute('elected'),
                  Attribute('eliminated'),
                  Attribute('tie_break'),
                  Attribute('tied_last_place'),
                  Attribute('totals'), )

    # TODO: move this functionality to the base class (and DRY up with related methods).
    def save_attrs_to_jsobj(self, jsobj, names, convert=lambda x: x):
        for name in names:
            value = getattr(self, name)
            if value is None:
                continue
            jsobj[name] = convert(value)

    def numbers_to_names(self, numbers):
        from_number = self.candidates_info.from_number
        return [from_number(n) for n in numbers]

    def totals_to_named_totals(self, totals):
        from_number = self.candidates_info.from_number
        return {from_number(number): total for number, total in totals.items()}

    def to_jsobj(self):
        jsobj = {}
        self.save_attrs_to_jsobj(jsobj, ('tie_break', ))
        self.save_attrs_to_jsobj(jsobj, ('elected', 'eliminated', 'tied_last_place'), self.numbers_to_names)
        self.save_attrs_to_jsobj(jsobj, ('totals', ), self.totals_to_named_totals)
        return jsobj


class JsonCaseTestOutput(JsonableMixin):

    meta_attrs = ()
    data_attrs = (Attribute('rounds', cls=JsonCaseRoundResult), )


class JsonCaseTestInstance(JsonableMixin):

    """An RCV test case (input and expected output)."""

    meta_attrs = (Attribute('index'),
                  Attribute('rules'), )
    data_attrs = (Attribute('input', cls=JsonCaseContestInput),
                  Attribute('output', cls=JsonCaseTestOutput), )


class JsonCaseTestsFile(JsonableMixin):

    """A file of test cases (input and expected output)."""

    meta_attrs = (Attribute('version'),
                  Attribute('rule_set'), )
    data_attrs = (Attribute('test_cases', cls=JsonCaseTestInstance), )
