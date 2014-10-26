Design
======

This document describes the overall design of OpenRCV.  This is to assist
contributors and those who want to build applications that import from
the `openrcv` package or interact with it in some other way.

Some of the pieces are as follows:

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
5. **Counter.**  A "counter" is a Python object responsible for tallying,
   or counting the ballots in, a contest.  A counter
6. **Results object.**
7. **Renderer.**
8. **Output file.**

When running OpenRCV from the command-line, the data flow is as follows:

1. The user passes a JSON or YAML contests file to OpenRCV.
2. The following are all read from the contests file:
   * the paths to any input files,
   * what parser to use,
   * what counter to use, and
   * what renderer to use.
3. The parser converts the input files into a contest object.
4. The counter converts the contest object into a results object.
5. The renderer converts the results object into output files.

When using OpenRCV as a Python library, any of these steps can be
done separately through the API.


[blt-desc]: https://code.google.com/p/droop/wiki/BltFileFormat
