import random
import math
import itertools
from decimal import Decimal
from typing import Optional, List, Tuple, Sequence

"""From random documentation:

Note that for even rather small len(x), the total number of permutations of x is larger than the period of most random number generators; this implies that most permutations of a long sequence can never be generated.

TODO WHAT DO ABOUT THIS?

MT has a period length of 2^19937 - 1, which means it can be used to uniformly select a random permutation of size n<=2080

"""    

# For the typechecker
Permutation = Sequence[int]
Blacklist = List[Tuple[int, int]]

def decompose(perm: Permutation) -> List[Optional[List[int]]]:
    """
    decompose traverses `perm` to decompose it into its cycles. Returns a list
    containing a list for each cycle where the elements of the list are in
    cycle order.
    
    For example, [4, 3, 0, 1, 2] has a 3-cycle 0->4->2->0 and a 2-cycle 1->3->1 

    decompose([4, 3, 0, 1, 2])
    > [[4, 2, 0], [3, 1]]
    """

    cycles: List[Optional[List[int]]] = []
    unvisited = list(perm) # copy input to mutable list

    # Begin at the first unvisited element of the input permutation,
    # following its index to the next element until we get back to the
    # first to complete the cycle and append it to `cycles`. Each time an
    # element in `perm` is visited, remove it from `unvisited`. Once
    # `unvisited` is empty, we've visited every element and have all the
    # cycles.
    while len(unvisited):
        first = unvisited.pop(0)
        cur = [first]
        nextval = perm[first]
        while nextval != first:
            cur.append(nextval)
            unvisited.pop(unvisited.index(nextval)) # remove from unvisited list
            nextval = perm[nextval]
        cycles.append(cur)

    return cycles


def check_min_cycles(perm: Permutation, m: int) -> bool:
    """
    Returns true if perm does not contain any cycles of length less than m (so
    when m=2, returns true only for derangements)
    """
    if m < 2: return True

    unvisited = list(perm) # copy input to mutable list

    # Visit all cycles until we find one less than length m (or we visit them all)
    while len(unvisited):
        first = unvisited.pop(0)
        nextval = perm[first]
        cur = 1
        while nextval != first:
            cur += 1
            unvisited.pop(unvisited.index(nextval))
            nextval = perm[nextval]
        if cur < m: return False
    return True

def check_blacklist(perm: Permutation, bl: Optional[Blacklist]) -> bool:
    """
    Returns true if perm does not contain any cycles where the pairs in bl follow each other.
    """
    if bl is None:
        return True

    for pair in bl:
        if perm[pair[0]] == pair[1] or perm[pair[1]] == pair[0]:
            return False

    return True

def check_deranged(perm: Permutation) -> bool:
    """
    Returns True if perm is deranged. Faster than check_min_cycles when m=2.
    """
    for i, el in enumerate(perm):
        if el == i: return False
    return True

def check_constraints(perm: Permutation, m: int, bl: Optional[Blacklist]) -> bool:
    if m < 2: m = 2
    if m == 2:
        # faster
        if not check_deranged(perm):
            return False
    else:
        # slower but can handle any m
        if not check_min_cycles(perm, m):
            return False
    return check_blacklist(perm, bl)

def generate_backtrack(n: int) -> Permutation:
    if n == 0: return []
    remaining = list(range(n))
    perm = []

    # backtrack until solution
    while len(perm) < n:
        perm.append(random.choice(remaining))
        if not check_deranged(perm):
            if len(remaining) == 1:
                # we're down to one element and it is the last element
                # just swap it with the previously chosen element to get a derangement
                perm[-1], perm[-2] = perm[-2], perm[-1]
                return perm
            # undo last choice
            perm.pop(-1)
        else:
            remaining.remove(perm[-1])
    return perm

def generate_all(n: int, m: int = 2, bl: Blacklist = None) -> Permutation:
    perms = list(itertools.permutations(range(n)))
    p = random.choice(perms)
    while not check_constraints(p, m, bl):
        p = random.choice(perms)
    return p

def Dn(n: int):
    """
    Calculate the subfactorial of n
    This is the same as the number of derangements that can be made from a set of size n
    """
    # Use Decimal to handle large n accurately (by large, I mean n>13 or so)
    s = 0
    for k in range(n+1):
        s += (-1)**k/Decimal(math.factorial(k))
    return Decimal.to_integral_exact(math.factorial(n) * s)


def random_derangement(n):
    A = list(range(n))
    marked = [False] * n
    i = u = n-1
    while u >= 1:
        if not marked[i]:
            while 1:
                j = random.randrange(0, i)
                if not marked[j]: break
            A[i], A[j] = A[j], A[i] # pythonic swap with no explicit temporary space
            p = random.random()
            if p < u * Dn(u-1) / Dn(u+1):
                marked[j] = True
                u = u - 1
            u = u -1
        i = i -1
    return A

def random_derangement_det(n):
    A = range(n)
    marked = [False] * n
    i = u = n-1
    while u >= 1:
        if not marked[i]:
            remaining = random.sample(range(i), i)
            for j in remaining:
                if not marked[j]: break
            A[i], A[j] = A[j], A[i] # pythonic swap with no explicit temporary space
            p = random.random()
            if p < u * Dn(u-1) / Dn(u+1):
                marked[j] = True
                u = u - 1
            u = u -1
        i = i -1
    return A
