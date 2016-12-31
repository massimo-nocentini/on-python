# Example of application of different kinds of decorators

from debugly import debug_simple, debug, debugargs, debugmethods, debugattr, debugmeta

def about_types():
    """
    __Every type, in Python, is defined by a class__, see also Smalltalk's object model.

    __The class is a callable that creates instances__
    >>> obj = Mondo()
    >>> isinstance(obj, Mondo)
    True

    __The class is the type of instances created__
    >>> obj = Mondo()
    >>> type(obj)
    <class 'example.Mondo'>

    __Classes are instances of types__
    >>> int
    <class 'int'>
    >>> type(int)
    <class 'type'>
    >>> type(list)
    <class 'type'>
    >>> Grok
    <class 'example.Grok'>
    >>> type(Grok)
    <class 'debugly.debugmeta'>

    __Types are their own class (builtin):
    class `type` creates new `type` objects and it is used when defining classes.
    >>> type
    <class 'type'>
    >>> type(type)
    <class 'type'>
    
    This `dict` serves as a local namespace for statements in the class body
    >>> clsdict = type.__prepare__('Bayes', (Base,))
    
    Then, the class body is executed in the returned dict `clsdict`.
    ```exec(body, globals(), clsdict)``` then populates `clsdict` with function defs.
    
    __Changing the `metaclass`__ 
    that keyword argument sets the class used for creating the type (class)
    we're defining: `class Spam(metaclass=type):...`; by default, it is set to `type`,
    but you can change it to something else.

    __Metaclasses propagates down hierarchies__
    think of it as genetic mutation, in general a *function decorator* rewrites
    a function, a *class decorator* rewrites a single class, a *metaclass*
    rewrites a class hierarchy.

    """
    pass

# Application of a simple decorator
@debug_simple
def add(x, y):
    '''
    >>> add(2, 3)
    add
    5
    '''
    return x + y

# Application of a decorator with args
@debugargs(prefix='*** ')
def sub(x, y):
    '''
    >>> sub(5, 3)
    *** sub
    2
    '''
    return x - y

# Application of decorator with optional args
@debug(prefix='+++ ')
def mul(x, y):
    '''
    >>> mul(5, 3)
    +++ mul
    15
    '''
    return x * y

# Application of a class decorator
@debugmethods
class Spam:
    def grok(self):
        '''
        >>> Spam().grok()
        Spam.grok
        '''
        pass
    def bar(self):
        '''
        >>> Spam().bar()
        Spam.bar
        '''
        pass
    def foo(self):
        '''
        >>> Spam().foo()
        Spam.foo
        '''
        pass

# Logging of attribute access
@debugattr
class Point:
    def __init__(self, x, y):
        '''
        >>> p = Point(x=3, y=4)
        >>> p.x
        Get: x
        3
        >>> p.y
        Get: y
        4
        '''
        self.x = x
        self.y = y

# Application of a metaclass: this pattern allows us to `debug` all the classes
# in the inheritance chain, having class `Base` as root, without attaching the
# decorator `@debugmethods` to all subclasses.
class Base(metaclass=debugmeta):

    def a(self):
        '''
        >>> Base().a()
        Base.a
        '''
        pass

    def b(self):
        '''
        >>> Base().b()
        Base.b
        '''
        pass

class Grok(Base):
    def c(self):
        '''
        >>> Grok().c()
        Grok.c
        '''
        pass
    
class Mondo(Grok):
    def d(self):
        '''
        >>> Mondo().d()
        Mondo.d
        >>> Mondo().a()
        Base.a
        '''
        pass

