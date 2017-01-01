# structly.py
#
# Example of "simplified" structures with signatures

from inspect import Parameter, Signature
from operator import attrgetter


def make_signature(names):
    return Signature(Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) 
                     for name in names)

def make_StructMeta_class(signature_attrname, fields_attrname):

    fields_attrgetter = attrgetter(fields_attrname)

    class StructMeta(type):

        def __new__(cls, clsname, bases, clsdict):
            clsobj = super().__new__(cls, clsname, bases, clsdict)
            sig = make_signature(fields_attrgetter(clsobj))
            setattr(clsobj, signature_attrname, sig)
            return clsobj

    return StructMeta

class Structure(metaclass=make_StructMeta_class(
    signature_attrname='__signature__', 
    fields_attrname='_fields')):

    # here we can use these names because we've declared them at metaclass
    # creation time(see just a few lines above). 
    _fields = [] 

    def __init__(self, *args, **kwargs):
        '''
        Without the metaclass `StructMeta` we're forced to include in each
        subclass a line similar to `_signature = make_signature(['<name>',
        ...])` as a static variable.
        '''
        bound = self.__signature__.bind(*args, **kwargs)
        for name, val in bound.arguments.items():
            setattr(self, name, val)

# Definitions

class Stock(Structure):
    '''
    >>> s = Stock('Peter', 30, 401.5)
    >>> s.name, s.shares, s.price
    ('Peter', 30, 401.5)
    '''

    _fields = ['name', 'shares', 'price']
    
class Point(Structure):
    '''
    >>> p = Point(x=34, y=65)
    >>> p.x, p.y
    (34, 65)
    '''

    _fields = ['x', 'y']

class Host(Structure):
    _fields = ['address', 'port']



