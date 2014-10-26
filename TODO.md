TODO
====

* Rename main to common.
* Flesh out design doc more.
* Link to design doc from contributing doc.
* Incorporate at least one "dev" script into command-line API.
* Get logging level from argparse.
* Add extra command options from molt.
* Fix up remaining PyPI release instructions and commit.
* Stub out batch IRV in open-rcv-tests
  - Stub out option & style docs, and update README.
  - Stub out section to describe format of test files.
    ~ mention lexicographic ordering, and grouping/weighting.
* Improve the random ballot generation by removing undervotes and
  providing an option for not having duplicates.
  - Make sure we have a function to create a random contest (given
    number of candidates, ballots, etc).
* Make an `update_test_files()` function that reindices and updates expecteds.
* Add tie-break and add convention to docs or code comment.
* Create a "top-level" function to tabulate an election from a path to
  an internal ballot file and a ContestInfo object.
* Add auto-generation comment to top of `setup_long_description.rst`.
* Only include newest changes in README.
* Add command to generate sample ballot file.
* Add "sample election" command so people can play with using it.
* Add nice online documentation (convert to reST).
* Add PEP8 checking.
* Add option for specifying file format to bypass detection based on file extension.
* Change format of unit test errors from--
  `test_parse_internal_ballot__non_integer (openrcv.test.test_counting.ModuleTest`
  to--
  `openrcv.test.test_counting.ModuleTest.test_parse_internal_ballot__non_integer`
