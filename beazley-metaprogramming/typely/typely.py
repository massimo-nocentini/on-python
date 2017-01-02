# typely.py
#
# Example of defining descriptors to customize attribute access.

from inspect import Parameter, Signature
import re
from collections import OrderedDict

# It is possible to compose the following descriptors as *mixins*; the correct
# behavior is ensure by `super()` invocation and mandatory keyword arguments.
class Descriptor:
    def __init__(self, name=None):
        self.name = name

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        raise AttributeError("Can't delete")

class Typed(Descriptor):
    ty = object
    def __set__(self, instance, value):
        if not isinstance(value, self.ty):
            raise TypeError('Expected %s' % self.ty)
        super().__set__(instance, value)

# Specialized types
class Integer(Typed):
    ty = int

class Float(Typed):
    ty = float

class String(Typed):
    ty = str

# Value checking
class Positive(Descriptor):
    def __set__(self, instance, value):
        if value < 0:
            raise ValueError('Expected >= 0')
        super().__set__(instance, value)

# More specialized types
class PosInteger(Integer, Positive):
    pass

class PosFloat(Float, Positive):
    pass

# Length checking
class Sized(Descriptor):
    def __init__(self, *args, maxlen, **kwargs):
        self.maxlen = maxlen
        super().__init__(*args, **kwargs)
        

    def __set__(self, instance, value):
        if len(value) > self.maxlen:
            raise ValueError('Too big')
        super().__set__(instance, value)

class SizedString(String, Sized):
    pass

# Pattern matching
class Regex(Descriptor):
    '''
    Doctest

    >>> Regex.__mro__
    (<class 'typely.Regex'>, <class 'typely.Descriptor'>, <class 'object'>)
    '''

    def __init__(self, *args, pat, **kwargs):
        self.pat = re.compile(pat)
        super().__init__(*args, **kwargs)
    
    def __set__(self, instance, value):
        if not self.pat.match(value):
            raise ValueError('Invalid string')
        super().__set__(instance, value)

class SizedRegexString(SizedString, Regex):
    '''
    Doctest

    >>> SizedRegexString.__mro__
    (<class 'typely.SizedRegexString'>, <class 'typely.SizedString'>, <class 'typely.String'>, <class 'typely.Typed'>, <class 'typely.Sized'>, <class 'typely.Regex'>, <class 'typely.Descriptor'>, <class 'object'>)
    '''
    pass

# Structure definition code

def make_signature(names):
    return Signature(
        Parameter(name, Parameter.POSITIONAL_OR_KEYWORD)
        for name in names)

class StructMeta(type):

    @classmethod
    def __prepare__(cls, name, bases):
        '''Creates and returns a dictionary to use for execution of the class body'''
        return OrderedDict() # will preserve attrs order, as objs appears in body

    def __new__(cls, clsname, bases, clsdict):

        # collect descriptors and set their names
        fields = [key for key, val in clsdict.items() if isinstance(val, Descriptor)]
        for name in fields:
            clsdict[name].name = name

        clsobj = super().__new__(cls, clsname, bases, dict(clsdict)) # it seems to work even without `dict` 
        setattr(clsobj, '__signature__', make_signature(fields))
        return clsobj

class Structure(metaclass=StructMeta):
    def __init__(self, *args, **kwargs):
        bound = self.__signature__.bind(*args, **kwargs)
        for name, val in bound.arguments.items():
            setattr(self, name, val)

class Stock(Structure):
    '''
    Doctests

    >>> s = Stock('GOOG', 100, 490.1) # everything ok
    >>> s.name = 123 # expect type error
    Traceback (most recent call last):
      File "/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/doctest.py", line 1330, in __run
        compileflags, 1), test.globs)
      File "<doctest typely.Stock[1]>", line 1, in <module>
        s.name = 123
      File "/Users/mn/Developer/working-copies/pythons/on-python/beazley-metaprogramming/typely/typely.py", line 23, in __set__
        raise TypeError('Expected %s' % self.ty)
    TypeError: Expected <class 'str'>
    >>> s = Stock('G_OG', 100, 490.1) # expect string error
    Traceback (most recent call last):
      File "/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/doctest.py", line 1330, in __run
        compileflags, 1), test.globs)
      File "<doctest typely.Stock[1]>", line 1, in <module>
        s = Stock('G_OG', 100, 490.1) # everything ok
      File "/Users/mn/Developer/working-copies/pythons/on-python/beazley-metaprogramming/typely/typely.py", line 109, in __init__
        setattr(self, name, val)
      File "/Users/mn/Developer/working-copies/pythons/on-python/beazley-metaprogramming/typely/typely.py", line 24, in __set__
        super().__set__(instance, value)
      File "/Users/mn/Developer/working-copies/pythons/on-python/beazley-metaprogramming/typely/typely.py", line 60, in __set__
        super().__set__(instance, value)
      File "/Users/mn/Developer/working-copies/pythons/on-python/beazley-metaprogramming/typely/typely.py", line 73, in __set__
        raise ValueError('Invalid string')
    ValueError: Invalid string
    >>> s = Stock('GOOG', -2, 490.1) # expect int error
    Traceback (most recent call last):
      File "/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/doctest.py", line 1330, in __run
        compileflags, 1), test.globs)
      File "<doctest typely.Stock[2]>", line 1, in <module>
        s = Stock('GOOG', -2, 490.1) # expect string error
      File "/Users/mn/Developer/working-copies/pythons/on-python/beazley-metaprogramming/typely/typely.py", line 109, in __init__
        setattr(self, name, val)
      File "/Users/mn/Developer/working-copies/pythons/on-python/beazley-metaprogramming/typely/typely.py", line 24, in __set__
        super().__set__(instance, value)
      File "/Users/mn/Developer/working-copies/pythons/on-python/beazley-metaprogramming/typely/typely.py", line 40, in __set__
        raise ValueError('Expected >= 0')
    ValueError: Expected >= 0
    '''

    # the following ordering of attributes is preserved by `OrderedDict` in
    # `__prepare__` method in class `StructMeta`.
    name = SizedRegexString(maxlen=8, pat='[A-Z]+$')
    shares = PosInteger()
    price = PosFloat()




