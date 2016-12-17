
# A Web Crawler With `asyncio` Coroutines

the article http://aosabook.org/en/500L/a-web-crawler-with-asyncio-coroutines.html
by *A. Jesse Jiryu Davis and Guido van Rossum*, re-mastered. 

## Introduction

We report their words:

> Classical computer science emphasizes efficient algorithms that complete computations as 
> quickly as possible. But many networked programs spend their time not computing, but holding 
> open many connections that are slow, or have infrequent events. These programs present a very 
> different challenge: to wait for a huge number of network events efficiently. A contemporary 
> approach to this problem is asynchronous I/O, or *async*.

> This chapter presents a simple web crawler. The crawler is an archetypal async application 
> because it waits for many responses, but does little computation. The more pages it can fetch 
> at once, the sooner it completes. If it devotes a thread to each in-flight request, then as the 
> number of concurrent requests rises it will run out of memory or other thread-related resource 
> before it runs out of sockets. It avoids the need for threads by using asynchronous I/O.

> We present the example in three stages. First, we show an async event loop and sketch a crawler 
> that uses the event loop with callbacks: it is very efficient, but extending it to more complex 
> problems would lead to unmanageable spaghetti code. Second, therefore, we show that Python 
> coroutines are both efficient and extensible. We implement simple coroutines in Python using 
> generator functions. In the third stage, we use the full-featured coroutines from Python's 
> standard `asyncio` library, and coordinate them using an async queue.

Moreover, we get inspiration from their article to adapt it to our needs, namely we would like to
have a crawler for the [OEIS][oeis] in order to fetch and save results for each sequence of numbers
(http://oeis.org/A000045 <-> A000045.json, for an example) in a json document to be crunched offline 
and mechanically.

Progress and discussion about my work in the PR https://github.com/massimo-nocentini/on-python/pull/1

[oeis]:http://oeis.org
