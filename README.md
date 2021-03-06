# on-python

This repo should be thought as a sandbox where we are free to play with
interesting projects and ideas using the Python language. Our aim is purely
educational, we write the code just for fun and to deepen our knowledge, by
standing on the shoulders of giants ;)

# Projects

The following is the list of artifact we have worked on; as a developer guide
line, when the checkbox of a project is empty then the project is still open
and in progress.  Moreover, for each wip artifact should exist a development
branch with the same name of the folder hosting it; otherwise, when we have
nothing more to say about an artifact, we consider it "finished", so it is
possible to merge its development branch into the `master` branch and, finally,
mark its checkbox in the list below:

- [x] __A Web Crawler With `asyncio` Coroutines__ ([folder][project:web-crawler])
  by _A. Jesse Jiryu Davis_ and _Guido van Rossum_.
- [ ] __Python 3 Metaprogramming__ ([folder][project:metaprogramming])
  by _David Beazley_.
- [x] __μkanren__ ([folder][project:microkanren])
  by _Jason Hemann_ and _Daniel P. Friedman_.
- [x] __double dispatch__ ([folder][project:double-dispatch])
  by _myself_.
- [x] __Vigenere crypto analysis__ ([folder][project:vigenere])
  by _myself_.
- [ ] __Functional Differential Geometry__ ([folder][project:fdg])
  by _Gerald Jay Sussman and Jack Wisdom_.
  - [x] *introduction* about Lagrangian function ([view][nb:fdg-intro])
- [ ] __Greedy algorithms__ ([folder][project:greedys]) by _myself_.
  - [x] *interval partitioning* 
- [ ] __Calculus I__ ([folder][project:calculus-I]) by _myself_.
  - [x] *numbers* ([notebook](https://nbviewer.jupyter.org/github/massimo-nocentini/on-python/blob/master/calculus-I/numbers.ipynb))

# References

Some bookkeeping of stuff we hit on:

## Official

- [PEP 8 -- Style Guide for Python Code][pep8]

## Guides

- [The Hitchhiker's Guide to Python][Hitchhiker]
- [Transforming Code into Beautiful, Idiomatic Python][Hettinger:Transforming]

## Recipes

- [by Raymond Hettinger][Hettinger:recipes]

## Videos

- [Keynote David Beazley - Topics of Interest (Python Asyncio)][Beazley:asyncio]
- [Python 3 Metaprogramming][Beazley:metaprogramming]
- [Raymond Hettinger, Python's Class Development Toolkit][Hettinger:class:toolkit]


[pep8]:https://www.python.org/dev/peps/pep-0008/

[Hettinger:recipes]:https://code.activestate.com/recipes/users/178123/new/

[Hitchhiker]:http://docs.python-guide.org/en/latest/
[Hettinger:Transforming]:https://gist.github.com/JeffPaine/6213790

[Beazley:metaprogramming]:https://www.youtube.com/watch?v=sPiWg5jSoZI&t=104s
[Beazley:asyncio]:https://www.youtube.com/watch?v=ZzfHjytDceU
[Hettinger:class:toolkit]:https://www.youtube.com/watch?v=HTLu2DFOdTg

[project:web-crawler]:https://github.com/massimo-nocentini/on-python/tree/master/web-crawler
[project:metaprogramming]:https://github.com/massimo-nocentini/on-python/tree/beazley-metaprogramming/beazley-metaprogramming
[project:microkanren]:https://github.com/massimo-nocentini/on-python/tree/master/microkanren
[project:double-dispatch]:https://github.com/massimo-nocentini/on-python/tree/master/dispatching
[project:fdg]:https://github.com/massimo-nocentini/on-python/tree/master/fdg
[nb:fdg-intro]:http://nbviewer.jupyter.org/github/massimo-nocentini/on-python/blob/master/fdg/intro.ipynb
[project:greedys]:https://github.com/massimo-nocentini/on-python/tree/master/greedys
[project:calculus-I]:https://github.com/massimo-nocentini/on-python/tree/master/calculus-I
[project:vigenere]:https://github.com/massimo-nocentini/on-python/tree/master/vigenere
