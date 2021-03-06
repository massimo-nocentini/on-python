
from muk.sexp import *
from muk.core import *
from muk.ext import *

def machine(*, rules):
    @adapt_iterables_to_conses(all_arguments)
    def M(α, β):
        return condi(*[[r(α, β, machine=M), succeed] for r in rules])
    return M

@adapt_iterables_to_conses(all_arguments)
def nullo(l):
    return unify([], l)

@adapt_iterables_to_conses(all_arguments)
def appendo(r, s, out):
    
    def A(r, out):
        return conde([nullo(r), unify(s, out)],
                     else_clause=[fresh(lambda a, d, res:
                                            conj(unify([a]+d, r),
                                                 unify([a]+res, out),
                                                 fresh(lambda: A(d, res)),))])
    return A(r, out)

@adapt_iterables_to_conses(all_arguments)
def reverseo(a, l):
    return conde([nullo(a), nullo(l)],
                 else_clause=[fresh(lambda car, cdr, res: 
                                        conji(unify([car]+cdr, a), 
                                              appendo(res, [car], l),
                                              fresh(lambda: reverseo(cdr, res)),))])

@adapt_iterables_to_conses(all_arguments)
def associateo(γ, γ2γ):
    return appendo(γ, [2]+γ, γ2γ)

@adapt_iterables_to_conses(all_arguments)
def symmetrico(α):
    return reverseo(α, α)

@adapt_iterables_to_conses(all_arguments)
def repeato(γ, γγ):
    return appendo(γ, γ, γγ)

def mcculloch_first_ruleo(α, β, *, machine):
    return fresh(lambda η: conj(unify([2]+η, α), unify(η, β)))

def mcculloch_second_ruleo(α, δ2δ, *, machine):
    return fresh(lambda η, δ: conj(unify([3]+η, α), associateo(δ, δ2δ), machine(η, δ)))

def mcculloch_third_ruleo(α, δ_reversed, *, machine):
    return fresh(lambda η, δ: conj(unify([4]+η, α), reverseo(δ, δ_reversed), machine(η, δ)))

def mcculloch_fourth_ruleo(α, δδ, *, machine):
    return fresh(lambda η, δ: conj(unify([5]+η, α), repeato(δ, δδ), machine(η, δ)))

def mcculloch_fifth_ruleo(α, β, *, machine):
    return appendo([2]+β, [2], α)
    #return conji(appendo([2]+β, [2], α), complement(nullo(β)))
    #return fresh(lambda η: conji(appendo([2]+η, [2], α), unify(η, β)))

def mcculloch_sixth_ruleo(α, _2δ, *, machine):
    return fresh(lambda η, δ: conji(unify([6]+η, α), unify([2]+δ, _2δ), machine(η, δ)))

mccullocho = machine(rules=[ mcculloch_second_ruleo, mcculloch_first_ruleo, ])

def mcculloch_lawo(γ, αγ, *, machine=mccullocho):
    return fresh(lambda α: conji(appendo([3, 2]+α, [3], γ), 
                                 appendo(α, γ, αγ), 
                                 complement(nullo(α)), 
                                 complement(nullo(γ)), 
                                 machine(γ, αγ)))

@adapt_iterables_to_conses(lambda α, l: {α})
def lengtho(α, l):

    def L(α, *, acc):
        return conde([nullo(α), unify(l, acc)],
                     else_clause=[fresh(lambda a, β: conj(unify([a]+β, α),  
                                                          fresh(lambda: L(β, acc=acc+1))))])

    return L(α, acc=0)

def leqo(a, b):
    return project(a, b, into=lambda a, b: unify(True, a <= b))


mcculloch_o = machine(rules=[ mcculloch_second_ruleo, mcculloch_third_ruleo, mcculloch_first_ruleo, ])
mcculloch__o = machine(rules=[ mcculloch_second_ruleo, mcculloch_fourth_ruleo, mcculloch_third_ruleo, mcculloch_first_ruleo, ])

@adapt_iterables_to_conses(all_arguments)
def opnumbero(α):
     return disj(nullo(α), fresh(lambda a, β: conj(appendo(β, [a], α), 
                                     condi([unify(a, 3), succeed],
                                           [unify(a, 4), succeed],
                                           [unify(a, 5), succeed]), 
                                     fresh(lambda: opnumbero(β)))))


def operationo(M, χ, M_of_χ, *, machine=mcculloch__o):
    return fresh(lambda M2χ: conji(appendo(M, [2]+χ, M2χ), machine(M2χ, M_of_χ)))

def craig_lawo(Mγ, M_of_Mγ, *, machine=mcculloch__o):
    return fresh(lambda γ: conji(mcculloch_lawo(γ, Mγ), machine(Mγ, M_of_Mγ)))

def craig_second_lawo(Mγ, M_of_Mγ, *, machine=mcculloch__o):
    return fresh(lambda γ, M, A: conji(mcculloch_lawo(γ, Mγ), appendo(A, M, Mγ), machine(Mγ, M_of_Mγ)))

mcculloch___o = machine(rules=[ mcculloch_fourth_ruleo, mcculloch_third_ruleo, mcculloch_sixth_ruleo,mcculloch_fifth_ruleo ])


