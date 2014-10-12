TODO
====

* Need code to convert a ballot stream into a list of JsonBallots.
* Review calls to make_internal_ballot_line() for final char.
* Improve the random ballot generation by removing undervotes and
  providing an option for not having duplicates.
* Make an `update_test_files()` function that reindices and updates expecteds.
* Make a JsonTestsFile class with input and output.
* Eliminate JS from counting.py and parsing.py and document this.
* Add tie-break and add convention to docs or code comment.
* Create a function to read a test input file, tabulate each contest,
  and write the results to a new file.
* Add the expected output to the JSON tests.
  - Figure out where to document the rules (e.g. tie-break) for given output.
* Create a "top-level" function to tabulate an election from a path to
  an internal ballot file and a ContestInfo object.
* Add remaining PyPI instructions to releasing.
* Stub out argparse.
* Add auto-generation comment to top of `setup_long_description.rst`.
* Only include newest changes in README.
* Add command to generate sample ballot file.
* Add nice online documentation.
* Add PEP8 checking.
* Change format of unit test errors from--
  `test_parse_internal_ballot__non_integer (openrcv.test.test_counting.ModuleTest`
  to--
  `openrcv.test.test_counting.ModuleTest.test_parse_internal_ballot__non_integer`
