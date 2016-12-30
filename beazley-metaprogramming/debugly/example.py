# Example of application of different kinds of decorators

from debugly import debug_simple, debug, debugargs, debugmethods, debugattr, debugmeta

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

# Application of a metaclass
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

