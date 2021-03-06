
import sys

from itertools import tee
from contextlib import contextmanager

def identity(a):
    return a

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def iterwrap(obj, classes=(tuple,)):
    return obj if isinstance(obj, classes) else [obj]

def foldr(λ, lst, initialize):

    def F(lst):
        if lst:
            car, *cdr = lst
            return λ(car, F(cdr))
        else:
            return initialize

    return F(lst)

def empty_iterable(α):
    α0, α = tee(α)
    try: next(α0)
    except StopIteration: return True
    else: return False

@contextmanager
def recursion_limit(n):
    previous = sys.getrecursionlimit()
    sys.setrecursionlimit(n)
    yield
    sys.setrecursionlimit(previous)

@contextmanager
def let(*args):
    yield (args[0] if len(args) == 1 else args)

