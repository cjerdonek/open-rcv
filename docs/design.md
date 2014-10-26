Design
======

This document describes the overall design of OpenRCV.  This is to assist
contributors and those who want to build applications that import from
the `openrcv` package or interact with it in some other way.


Components and Terminology
--------------------------

Some of the pieces involved are as follows:

1. **Input file.**  An "input file" is a file that contains ballot data and
   related contest information.  An input file can be in any number of
   formats (e.g. [BLT][blt-desc] or a jurisdiction-specific format).
2. **Contests file.**  A "contests file" is a configuration file that
   specifies what contests should be tallied and how.  A contests file
   is the input that is passed to OpenRCV on the command-line.
   The format of a contests file is specific to OpenRCV, and it can be
   either JSON or YAML.  A contests file contains references to one or more
   input files, as well as specifying the format of those files.  In
   particular, it is the contests file that says what parser should be
   used to parse any input files for a contest.
3. **Parser.**  A "parser" is a Python object responsible for converting
   one or more input files into a contest object.  A parser does not
   tally a contest.  It only converts the input into a standard
   representation that can be tallied.  Adding support for a new input
   file format normally only requires writing a parser for that format.
4. **Contest object.**  A "contest object" is a data structure used
   internally by OpenRCV to represent a contest before it has been tallied.
   A contest object comprises contest metadata (e.g. contest name,
   candidates, etc) and ballot data.  For memory reasons, the ballot data
   in a contest object is stored as a file.  The file format is an internal
   format that resembles BLT, but without the contest metadata.
5. **Counter.**  A "counter" is a Python object responsible for tallying
   a contest (aka counting the ballots).  A counter takes a contest
   object as input and outputs a results object.  Typically, adding
   support for a new vote-counting algorithm or variation requires only
   writing a new counter or modifying an existing one.
6. **Results object.**  A "results object" is a data structure used
   internally by OpenRCV to represent the results of tallying a contest
   (e.g. the round-by-round totals of an instant-runoff election).
   It represents the "data" after tallying an election, independent of
   how the results are displayed or presented.  Typically, to check that
   two implementations of a vote-counting algorithm agree, one would check
   that the results objects match.
7. **Renderer.**  A "renderer" is a Python object responsible for
   converting results objects into one or more output files.  Typically,
   adding support for a new output file format means writing a new renderer.
8. **Output file.**  An "output file" is a collection of one or more
   files containing a human-readable or machine-readable representation
   of a results object (typically along with some contest metadata).
   Examples of human-readable output file formats include things like
   HTML and PDF.  Machine-readable formats include things like JSON and EML.


Data Flow
---------

When running OpenRCV from the command-line, the data flow is as follows:

1. The user passes the path to a JSON or YAML contests file via the
   command-line (e.g. by running 'rcv INPUT_PATH`).
2. OpenRCV reads the following information from the contests file:
   * the paths to any input files,
   * what parser to use,
   * what counter to use, and
   * what renderer to use.
3. The parser converts the input files into a contest object.
4. The counter converts the contest object into a results object.
5. The renderer converts the results object into output files.
   Typically, command-line options for the command issued in step (1)
   specify the location to which the output files should be written.

Any of the steps above can also be done in isolation using OpenRCV's
Python API (i.e. by importing `openrcv` as a Python package and
calling appropriate functions directly, etc).


[blt-desc]: https://code.google.com/p/droop/wiki/BltFileFormat
