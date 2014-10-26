Design
======

This document describes the overall design of OpenRCV.  This is to assist
contributors and those who want to build applications that import from
the `openrcv` package or interact with it in some other way.

Some of the pieces are as follows:

1. **Input file.**  An "input file" is a file that contains ballot data and
   related contest information.  An input file can be in any number of
   formats (e.g. [BLT][blt-desc] or a jurisdiction-specific format).
2. **Contests files.**  A "contests file" is a configuration file passed
   to OpenRCV that specifies what contests should be tallied and how.
   A contests file can be either JSON or YAML and has a format specific
   to OpenRCV.  A contests file contains references to one or more
   input files and also specifies the format of those files (and in
   particular what parser should be used).
3. **Parsers.**  A "parser" is a Python object responsible for converting
   one or more input files into a Contest object (without tallying it).
   Normally, a parser is responsible for parsing only one input file format.
4. **Contest object.**  A "contest object" is a data structure used
   internally by OpenRCV to represent a contest before it has been tallied.
   A contest object comprises contest metadata (e.g. contest name,
   candidates, etc) and ballot data.  For memory reasons, the ballot data
   in a contest object is stored as a file.  The file format is an internal
   format that resembles BLT, but without the contest metadata.
5. **Counters.**  A "counter" is a Python object responsible for tallying,
   or counting the ballots in, a contest.  A counter
6. **Results object.**
7. **Renderers.**
8. **Output files.**


[blt-desc]: https://code.google.com/p/droop/wiki/BltFileFormat
