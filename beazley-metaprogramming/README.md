
# Python 3 Metaprogramming

by _David Beazley (@dabeaz)_

A tutorial presented at PyCon'13, March 14, 2013. Santa Clara, California.

All the material is formely imported from http://www.dabeaz.com/py3meta/ which
we consider our upstream; moreover, this is the companion video of the lecture
http://pyvideo.org/pycon-us-2013/python-3-metaprogramming.html (or
https://www.youtube.com/watch?v=sPiWg5jSoZI&t=104s).

## Content guide

`debugly/`
    Simple metaprogramming concepts illustrated with
    examples focused on debugging.

`structly/`
    Structure definitions with signatures.

`typely/`
    Structure definitions with type checking/validation
    and descriptors.

`execly/`
    Structure definitions with optimized code generation
    using exec().

`importly/`
    Importing structure definition files and generating
    code via import hooks.

## Refs

The following list of refs we believe interesting readings:

- decorators:
  - http://blog.thedigitalcatonline.com/blog/2015/04/23/python-decorators-metaprogramming-with-style/#.WHSIU7YrJE7
- descriptors:
  - official:
    - https://docs.python.org/3/howto/descriptor.html
    - https://docs.python.org/3/library/functions.html#property
    - https://www.python.org/download/releases/2.2.3/descrintro/#cooperation
  - from web:
    - https://www.blog.pythonlibrary.org/2016/06/10/python-201-what-are-descriptors/
    - http://intermediatepythonista.com/classes-and-objects-ii-descriptors
    - http://www.ibm.com/developerworks/library/os-pythondescriptors/

# Our contribution

Our aim is to not enhance David's keynote; on the other hand, we augment and
make little changes to be more confortable and to match our style. We add
*comments*, mainly taken from David's presentation, and *doctests* in order to
have a reproducible artifact that binds code with expected results.

