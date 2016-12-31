
# A Web Crawler With `asyncio` Coroutines

the article
http://aosabook.org/en/500L/a-web-crawler-with-asyncio-coroutines.html
by *A. Jesse Jiryu Davis and Guido van Rossum*, re-mastered. 

## Introduction

We report their words:

> Classical computer science emphasizes efficient algorithms that
> complete computations as quickly as possible. But many networked
> programs spend their time not computing, but holding open many
> connections that are slow, or have infrequent events. These programs
> present a very different challenge: to wait for a huge number of
> network events efficiently. A contemporary approach to this problem is
> asynchronous I/O, or *async*.

> This chapter presents a simple web crawler. The crawler is an
> archetypal async application because it waits for many responses, but
> does little computation. The more pages it can fetch at once, the
> sooner it completes. If it devotes a thread to each in-flight request,
> then as the number of concurrent requests rises it will run out of
> memory or other thread-related resource before it runs out of sockets.
> It avoids the need for threads by using asynchronous I/O.

> We present the example in three stages. First, we show an async event
> loop and sketch a crawler that uses the event loop with callbacks: it
> is very efficient, but extending it to more complex problems would
> lead to unmanageable spaghetti code. Second, therefore, we show that
> Python coroutines are both efficient and extensible. We implement
> simple coroutines in Python using generator functions. In the third
> stage, we use the full-featured coroutines from Python's standard
> `asyncio` library, and coordinate them using an async queue.

## Motivation

We get inspiration from them to adapt their prototype to our needs,
namely we would like to have a crawler for the [OEIS][oeis] in order to
fetch and save results for each sequence of numbers  in corresponding
json documents (ie. search http://oeis.org/A000045 will produce the
`A000045.json` file), to be crunched offline and mechanically later.

However, the fundamental reason underlying this work is to understand
the _asynchronous pattern of computation_ and the Pythonic way to write
it, in particular to provide some basis to understand definitions in the
`asyncio` module, `coroutine` objects and the relation among `yield`
expressions with `async/await` ones. 

## Implementation steps

At the beginning, progress and discussion of this project can be found in the PR
https://github.com/massimo-nocentini/on-python/pull/1 . We study the
original article and divide it in a sequence of steps, each one large
enough to represent a bunch of high cohesive concepts: the sequence
represent an accumulating of knowledge, hence each step is a
building block for the next one, in fact we believe it is interesting to
look at differences between consecutive ones to understand how the
gained skill changes the way we write code. We believe that splitting
the incremental work in dedicated files, one for each step, allows us to
manage the complexity of both studying the material and make it real in
code. 

Moreover, in the following sections we report the sequence of changes
that leads us to the final version of the code base; accordingly, step
numbering corresponds to the numbers recorded in commit messages and
we provide a succint description of features implemented in each one of
them.

- _Step 1_ ([source][step-one]): <br> sends a single GET request using a
  tight loop to know when the job is done; however, no handling of
  multiple sockets can be easily implemented.
- _Step 2_ ([source][step-two]): <br> a set of sockets is used to handle
  multiple connections; as event dispatcher, a
  `selectors.DefaultSelector` object is introduced.
- _Step 3_ ([source][step-three]): <br> first working prototype of
  fetching logic based on *callbacks*; introduced `fetcher` objects.
- _Step 4_ ([source][step-four]): <br> introduction of `future` objects
  and their drivers `task` objects.
- _Step 5_ ([source][step-five]): <br> refactoring `yield from`
  expressions only for pending on a future.
- _Step 5.5_ ([source][step-five.half]): <br> little enhancement using
  keywords `async` and `await` to introduce native `coroutine` objects,
  implementation code *is not* changed. 
- _Step 6_ ([source][step-six]): <br> implementation of `eventloop` and
  `queue` objects on top of _Step 5_, namely pending with `yield from`.
- _Step 6.5_ ([source][step-six.half]): <br> just use of native
  coroutines and latest *asynch comprehension* introduced in Python 3.6.
- _Intermezzo_ ([source][intermezzo]): <br> understanding generators
  objects and `yield from` expressions for understanding `coroutine`
  objects; `doctests` are used to record assertions.

## Reproducibility 

For each step in the sequence above there exists a rule in the
`Makefile` file to run it, this means that each step is *executable*
and, starting from _Step 3_, all of them fetch and store data as
explained in the §Introduction. Only _Step 6.5_ requires Python 3.6, for
the others Python 3.5 is fine. 

Each step has a purpose, whose result can be seen by running it: the
first two of them shows when connections with server happens, while the
latters populate the `fetched/` directory with json documents,
containing OEIS search results.


## Acknowledgements

Thank you, Guido and Jesse!

[oeis]:http://oeis.org

[step-one]:https://github.com/massimo-nocentini/on-python/blob/web-crawler/web-crawler/non-blocking-sockets-tight-loop.py
[step-two]:https://github.com/massimo-nocentini/on-python/blob/web-crawler/web-crawler/non-blocking-sockets-selectors.py
[step-three]:https://github.com/massimo-nocentini/on-python/blob/web-crawler/web-crawler/non-blocking-sockets-fetcher.py
[step-four]:https://github.com/massimo-nocentini/on-python/blob/web-crawler/web-crawler/fetcher-with-futures.py
[step-five]:https://github.com/massimo-nocentini/on-python/blob/web-crawler/web-crawler/fetcher-with-yield-from.py
[step-five.half]:https://github.com/massimo-nocentini/on-python/blob/web-crawler/web-crawler/fetcher-with-async-await.py
[step-six]:https://github.com/massimo-nocentini/on-python/blob/web-crawler/web-crawler/crawling.py
[step-six.half]:https://github.com/massimo-nocentini/on-python/blob/web-crawler/web-crawler/crawling-with-async-await.py
[intermezzo]:https://github.com/massimo-nocentini/on-python/blob/web-crawler/web-crawler/understanding-coroutines.py
