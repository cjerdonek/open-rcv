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

from openrcv.formats.internal import parse_internal_ballot, to_internal_ballot
from openrcv.jsonlib import (from_jsobj, Attribute, JsonableError, JsonableMixin,
                             JsonDeserializeError)
from openrcv import models
from openrcv.models import make_candidates, RoundResults
from openrcv import streams
from openrcv.utils import StringInfo


class JsonCaseBallot(JsonableMixin):

    """The serialization format is a space-delimited string of integers of
    the form: "WEIGHT CHOICE1 CHOICE2 CHOICE3 ...".
    """

    data_attrs = (Attribute('choices'),
                  Attribute('weight'))

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

    """Contest input for a JSON test case."""

    meta_attrs = (Attribute('id'),
                  Attribute('name'),
                  Attribute('normalize_ballots'),
                  Attribute('notes'))
    data_attrs = (Attribute('ballots', cls=JsonCaseBallot),
                  Attribute('candidate_count'))

    def __init__(self, id_=None, candidate_count=None, ballots=None,
                 name=None, normalize_ballots=None, notes=None):
        """
        Arguments:
          ballots: an iterable of JsonCaseBallot objects.
          candidate_count: integer number of candidates.
          normalize_ballots: None means True.  Defaults to None.
        """
        if id_ is None:
            id_ = 0
        self.ballots = ballots
        self.candidate_count = candidate_count
        self.id = id_
        self.name = name
        self.normalize_ballots = normalize_ballots
        self.notes = notes

    def repr_info(self):
        return "id=%s candidate_count=%s" % (self.id, self.candidate_count)

    def save_from_model(self, contest):
        """
        Arguments:
          contest: a ContestInput object.
        """
        candidate_count = None if contest.candidates is None else len(contest.candidates)
        with contest.ballots_resource.reading() as ballots:
            ballots = [JsonCaseBallot.from_model(b) for b in ballots]
        self.__init__(id_=contest.id, candidate_count=candidate_count, ballots=ballots,
                      name=contest.name, notes=contest.notes,
                      normalize_ballots=contest.normalize_ballots)

    # TODO: implement and unit test this.
    # TODO: think about how the creation of a new ballots resource should
    # be handled, since it involves managing another resource.
    def to_model(self):
        """Return a ContestInput object."""
        candidates = make_candidates(self.candidate_count)
        ballots = [b.to_model() for b in self.ballots]
        # We use a list resource as the backing store for now because the
        # number of ballots is small.
        resource = streams.ListResource(ballots)
        ballots_resource = models.BallotsResource(resource)
        contest = models.ContestInput(id_=self.id,name=self.name, notes=self.notes,
                                      candidates=candidates,
                                      ballots_resource=ballots_resource,
                                      normalize_ballots=self.normalize_ballots)
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

    """Represents a contests.json file for open-rcv-tests."""

    meta_attrs = (Attribute('version'), )
    data_attrs = (Attribute('contests', cls=JsonCaseContestInput), )

    def __init__(self, contests=None, version=None):
        """
        Arguments:
          contests: an iterable of JsonContest objects.
        """
        self.contests = contests
        self.version = version

    def repr_info(self):
        return "version=%s contests=%d" % (self.version, len(self.contests))


class JsonRoundResults(RoundResults, JsonableMixin):

    """Represents the results of a round for testing purposes."""

    data_attrs = (Attribute('totals'), )

    def __init__(self, totals=None):
        self.totals = totals


class JsonTestCaseOutput(JsonableMixin):

    meta_attrs = ()
    data_attrs = (Attribute('rounds', cls=JsonRoundResults), )

    @classmethod
    def from_contest_results(cls, results):
        """
        Arguments:
          results: a ContestResults object.
        """
        json_rounds = []
        for round_results in results.rounds:
            json_round = JsonRoundResults()
            json_round.totals = round_results.totals
            json_rounds.append(json_round)
        return JsonTestCaseOutput(rounds=json_rounds)

    def __init__(self, rounds=None):
        if rounds is None:
            rounds = []
        self.rounds = rounds


class JsonTestCase(JsonableMixin):

    """An RCV test case (input and expected output)."""

    meta_attrs = (Attribute('id'),
                  Attribute('contest_id'), )
    data_attrs = (Attribute('input', cls=JsonCaseContestInput),
                  Attribute('output', cls=JsonTestCaseOutput), )

    def __init__(self):
        self.id = None
        self.contest_id = None
        self.input = JsonTestCaseInput()
        self.output = JsonTestCaseOutput()


class JsonTestCaseFile(JsonableMixin):

    """A file of test cases (input and expected output)."""

    meta_attrs = (Attribute('version'),
                  Attribute('rule_set'), )
    data_attrs = (Attribute('test_cases', cls=JsonTestCase), )

    def __init__(self):
        self.rule_set = None
        self.version = None
        self.test_cases = []
