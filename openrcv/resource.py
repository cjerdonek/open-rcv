
"""
Support for iterator resources.

An "iterator resource" is a callable that returns a with-statement context
manager [1], which in turn yields an iterable for the target `as` expression.
Here is an example of using an iterator resource `resource`:

    with resource() as items:
        for item in items:
            # Do stuff.
            ...

The above resembles the pattern of opening a file and reading its lines.

Iterator resources are a central concept in this package.  For example,
for many of our APIs, we pass ballots around as an iterator resource
rather than as a plain iterable.  This lets us access large sets of ballots
as a file rather having to store them in memory.  By using an iterator
resource, we can open and close a ballot file in our implementations
when needed (e.g. using the convenient with statement), as opposed to
having to open a file much earlier than needed, and passing open file
objects into our APIs.


[1]: https://docs.python.org/3/library/contextlib.html

"""

# TODO: add a helper class/function for "post-composing".
# TODO: convert StreamInfos to the iterator resource pattern?
