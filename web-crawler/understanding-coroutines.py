
import inspect
from contextlib import suppress

def bar():
    pass

def foo():
    '''
    Doctests:

    >>> import dis
    >>> dis.dis(foo)
     21           0 LOAD_GLOBAL              0 (bar)
                  3 CALL_FUNCTION            0 (0 positional, 0 keyword pair)
                  6 POP_TOP
                  7 LOAD_CONST               1 (None)
                 10 RETURN_VALUE

    '''
    bar()

frame = None

def another_bar():
    global frame
    frame = inspect.currentframe()

def another_foo():
    '''
    Doctests:
    
    >>> frame = another_foo()
    >>> frame.f_code.co_name
    'another_bar'
    >>> caller_frame = frame.f_back
    >>> caller_frame.f_code.co_name
    'another_foo'
    
    '''
    another_bar()
    return frame

def gen_fn():
    '''
    Doctests
    
    >>> generator_bit = 1 << 5
    >>> bool(gen_fn.__code__.co_flags & generator_bit)
    True
    >>> gen = gen_fn()
    >>> type(gen)
    <class 'generator'>
    >>> gen.gi_code.co_name
    'gen_fn'
    >>> gen.gi_frame.f_lasti
    -1
    >>> gen.send(None)
    1
    >>> gen.gi_frame.f_lasti
    3
    >>> len(gen.gi_code.co_code)
    61
    >>> gen.send('hello')
    value sent to 1st yield: hello
    2
    >>> gen.gi_frame.f_locals
    {'result': 'hello'}
    >>> gen.send('goodbye')
    value sent to 2nd yield: goodbye
    3
    >>> gen.send('discard')
    Traceback (most recent call last):
      File "/usr/local/lib/python3.5/doctest.py", line 1321, in __run
        compileflags, 1), test.globs)
      File "<doctest __main__.gen_fn[11]>", line 1, in <module>
        gen.send('goodbye')
    StopIteration: done

    You can throw an exception into a generator from outside:
    >>> gen = gen_fn()
    >>> gen.send(None)
    1
    >>> gen.throw(Exception('error'))
    Traceback (most recent call last):
      File "/usr/local/lib/python3.5/doctest.py", line 1321, in __run
        compileflags, 1), test.globs)
      File "<doctest __main__.gen_fn[15]>", line 1, in <module>
        gen.throw(Exception('error'))
      File "understanding-coroutines.py", line 87, in gen_fn
        result = yield 1
    Exception: error

    '''
    result = yield 1
    print('value sent to 1st yield: {}'.format(result))
    result2 = yield 2
    print('value sent to 2nd yield: {}'.format(result2))
    yield 3 # ignore any sent value

    return 'done'

def broken_gen_fn(error='my error'):
    raise Exception(error)

def caller_fn(gen_fn):
    '''
    Doctests:

    While `caller` yields from `gen`, `caller` does not advance. Notice that its 
    instruction pointer remains at 15, the site of its yield from statement, 
    even while the inner generator `gen` advances from one yield statement to the next. 
    From our perspective outside `caller`, we cannot tell if the values it yields 
    are from `caller` or from the generator it delegates to. And from inside `gen`, 
    we cannot tell if values are sent in from `caller` or from outside it. 
    The `yield from` statement is a frictionless channel, through which values flow 
    in and out of `gen` until `gen` completes.

    >>> caller = caller_fn(gen_fn)
    >>> caller.send(None)
    1
    >>> caller.gi_frame.f_lasti
    15
    >>> caller.send('hello')
    value sent to 1st yield: hello
    2
    >>> caller.gi_frame.f_lasti # hasn't advanced
    15
    >>> caller.send('goodbye')
    value sent to 2nd yield: goodbye
    3
    >>> caller.send('exhausting inner generator')
    return value of yield-from: done
    4
    >>> caller.send('discard')
    Traceback (most recent call last):
      File "/usr/local/lib/python3.5/doctest.py", line 1321, in __run
        compileflags, 1), test.globs)
      File "<doctest __main__.caller_fn[7]>", line 1, in <module>
        caller.send('another step')
    StopIteration

    Earlier, when we criticized callback-based async programming, our most strident 
    complaint was about "stack ripping": when a callback throws an exception, the stack 
    trace is typically useless. It only shows that the event loop was running the callback, 
    not why. How do coroutines fare?
    >>> caller = caller_fn(broken_gen_fn)
    >>> caller.send(None)
    Traceback (most recent call last):
      File "/usr/local/lib/python3.5/doctest.py", line 1321, in __run
        compileflags, 1), test.globs)
      File "<doctest __main__.caller_fn[9]>", line 1, in <module>
        caller.send(None)
      File "understanding-coroutines.py", line 136, in caller_fn
        gen = gen_fn()
      File "understanding-coroutines.py", line 90, in broken_gen_fn
        raise Exception(error)
    Exception: my error

    This is much more useful! The stack trace shows `caller_fn` was delegating to 
    `broken_gen_fn` when it threw the error.
    '''
    gen = gen_fn()
    rv = yield from gen
    print('return value of yield-from: {}'.format(rv))
    yield 4 # ignore any sent value

def another_broken_gen_fn():
    yield 1
    raise Exception('uh oh')

def except_caller_fn(gen_fn):
    '''
    Doctests:

    Even more comforting, we can wrap the call to a sub-coroutine in an exception handler, 
    the same is with normal subroutines:
    >>> caller = except_caller_fn(another_broken_gen_fn)
    >>> caller.send(None)
    1
    >>> caller.send('hello')
    caught uh oh
    2
    '''
    try:
        yield from gen_fn()
    except Exception as exc:
        print('caught {}'.format(exc))
    
    yield 2






# run doctests ___________________________________________________________________{{{
if __name__ == "__main__":
    import doctest
    doctest.testmod()
#________________________________________________________________________________}}}
