
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

    '''
    result = yield 1
    print('value sent to 1st yield: {}'.format(result))
    result2 = yield 2
    print('value sent to 2nd yield: {}'.format(result2))
    yield 3 # ignore any sent value

    return 'done'


# run doctests ___________________________________________________________________{{{
if __name__ == "__main__":
    import doctest
    doctest.testmod()
#________________________________________________________________________________}}}
