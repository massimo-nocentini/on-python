
from functools import singledispatch
from operator import attrgetter

import unittest

def dispatch(table, dispatch_method=attrgetter('__call__'), attr_joiner='__o__'):

    def dispatching(ty, recv, spec_table):

        def R(this, that):
            r = recv(this)
            m = dispatch_method(r)
            D = singledispatch(m)

            T = spec_table if isinstance(spec_table, dict) else (
                { t: '{}{}{}'.format(ty.__name__, attr_joiner, t.__name__) 
                    for t in spec_table })

            for t, λ_attr in T.items():
                λ = attrgetter(λ_attr)
                D.register(t, λ(r))

            return D(that)

        return R

    def D(f):
        F = singledispatch(f)
        for ty, (recv, inner_table) in table.items():
            dispatched = dispatching(ty, recv, inner_table)
            F.register(ty, dispatched)
        return F
    
    return D

#_______________________________________________________________________________

class UnificationError(ValueError):
    pass

class unifier:

    def __init__(self, this):
        self.this = this

    def __call__(self, this):
        self._doesnt_unify()

    def _doesnt_unify(self):
        raise UnificationError

class list_unifier(unifier):

    def unify_with_list(self, another_list : list):
        return (self.this, another_list)

    def unify_with_int(self, an_int : int):
        return (self.this, an_int)

    list__o__list = unify_with_list
    list__o__int = unify_with_int

class int_unifier(unifier):

    def int__o__int(self, another_int : int):
        return self.this == another_int

    def int__o__list(self, a_list : list):
        return self.this == len(a_list)

    def _doesnt_unify(self):
        return False

@dispatch({list: (list_unifier, { list: 'unify_with_list', 
                                  int:  'unify_with_int', })})
def unify_dict_dispatch(arg, other):
    try:
        return unify_dict_dispatch(other, arg)
    except UnificationError:
        raise


@dispatch({list: (list_unifier, {list, int})})
def unify_set_dispatch(arg, other):
    try:
        return unify_set_dispatch(other, arg)
    except UnificationError:
        raise


@dispatch({ list: (list_unifier, {list, int}), 
            int: (int_unifier, {int, list}) })
def another_unify(arg, other):
    try:
        return another_unify(other, arg)
    except UnificationError:
        raise



# ______________________________________________________________________________
# Tests
# ______________________________________________________________________________

class SimpleTests(unittest.TestCase):

    def helper(self, U):
        self.assertEqual(U([1,2,3], [4,5,6]), ([1,2,3], [4,5,6]))
        self.assertEqual(U([1,2,3], 456), ([1,2,3], 456))
        self.assertEqual(U(456, [1,2,3]), ([1,2,3], 456))
        try:
            U([1,2,3], object())
        except ValueError:
            pass

    def test_dispatching(self):
        self.helper(unify_dict_dispatch)
        self.helper(unify_set_dispatch)

    def test_unification(self):
        self.assertTrue(another_unify(3, 3))
        self.assertFalse(another_unify(3, [3]))
        self.assertTrue(another_unify(3, [1]*3))

    def test_learning_about_callable(self):

        def identity(i):
            return i

        self.assertEqual(identity.__call__(3), 3)


