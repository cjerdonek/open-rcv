Design
======

This document describes the overall design of OpenRCV.  This is to assist
contributors and those who want to build applications that import from
the `openrcv` package or interact with it in some other way.

Some of the pieces are as follows:

1. **Ballot data files.**  These are the input files that contain ballot
   data.  These can be in any number of formats (e.g. [BLT][blt-desc]).
2. **Contests files.**  This is an OpenRCV
3. **Parsers.**  A parser is a Python object responsible for converting
   ballot data files into Contest objects.
4. **Contest object.**  A Contest object is
5. **Counters.**
6. **Renderers.**
7. **Output files.**

2) parser -> structured internal ballot format (with metadata)
   - explain that this is a simple text file with Python metadata.
3) tallier -> structured results
4) results renderers


[blt-desc]: https://code.google.com/p/droop/wiki/BltFileFormat
