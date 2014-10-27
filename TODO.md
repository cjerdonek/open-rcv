TODO
====

* Add random_contest() function with flexible args.
* Add "samplecontest" command so people can play with using it.
  - Also add "random election" command.
  - The samples should have names:
    ~ Ann, Bob, Carol, Dave, Ellen, Fred, Gwen, Hank, Irene, Joe, Katy, Leo,
      Candidate 13, etc.
* Get rid of rcvgen.
* Allow test logging messages to show (e.g. skips).
* Add extra command options from molt.
* Fix up remaining PyPI release instructions and commit.
* Add definition of "contest metadata" to design doc.
* Stub out batch IRV in open-rcv-tests
  - Stub out option & style docs, and update README.
  - Stub out section to describe format of test files.
    ~ mention lexicographic ordering, and grouping/weighting.
* Improve the random ballot generation by removing undervotes and
  providing an option for not having duplicates.
  - Make sure we have a function to create a random contest (given
    number of candidates, ballots, etc).
* Incorporate submodule into tests.
* Make an `update_test_files()` function that reindices and updates expecteds.
* Add tie-break and add convention to docs or code comment.
* Create a "top-level" function to tabulate an election from a path to
  an internal ballot file and a ContestInfo object.
* Add auto-generation comment to top of `setup_long_description.rst`.
* Only include newest changes in README.
* Add nice online documentation (convert to reST).
* Add PEP8 checking.
* Add option for specifying file format to bypass detection based on file extension.
