TODO
====

* Test glossary and start using reST with tests project.
* Look into how to use different Python versions in different virtualenvs.
  - document this.
* Make an `input_data` directory.
* Add the ability to skip tests.
* Add batch elimination as an IRV variation in the tests.
* Write up the assumptions about the JSON data in the submodule.
  For example--
  - tests files are meant to be stand-alone (no need to look at contests.json
    or outside the test case).
  - input in tests.json is auto-generated from...
  - meta contains any data not needed to generate the output
  - want a method of inheritance for data?
* Implement commands:
  - checktests
* Get unit tests checking JSON test cases (after normalizing and generating
  files)
* Store the model object for a jsonable class with the class.
* Move changelog to rst (following argparse2).
* Get version detection going from molt.
* Fix up remaining PyPI release instructions and commit.
* Consider a contests.json format that allows ballot data to be reused
  across count variations.


Technical debt
--------------

* Refactor JsonCaseContestInputTest2 away.
* Remove cruft from utils.py (specifically StreamInfo).


Uncategorized
-------------

* Improve the random ballot generation by removing undervotes and
  providing an option for not having duplicates.
* Define a BLT ballot stream resource that shares code with the internal one.
* Add "samplecontest" command so people can play with using it?
* Allow test logging messages to show (e.g. skips).
* Add extra command options from molt.
* Add definition of "contest metadata" to design doc.
* Stub out batch IRV in open-rcv-tests
  - Stub out option & style docs, and update README.
  - Stub out section to describe format of test files.
    ~ mention lexicographic ordering, and grouping/weighting.
* Incorporate submodule into tests.
* Make an `update_test_files()` function that reindices and updates expecteds.
* Add tie-break and add convention to docs or code comment.
* Create a "top-level" function to tabulate an election from a path to
  an internal ballot file and a ContestInput object.
* Add auto-generation comment to top of `setup_long_description.rst`.
* Only include newest changes in README.
* Add PEP8 checking.
* Add option for specifying file format to bypass detection based on file extension.
