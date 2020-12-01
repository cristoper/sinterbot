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
    cycles = decompose(perm)
    for c in cycles:
        if not c or len(c) < m:
            return False
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

def check_constraints(perm: Permutation, m: int, bl: Optional[Blacklist]) -> bool:
    if not check_min_cycles(perm, m):
        return False
    if not check_blacklist(perm, bl):
        return False
    return True

def generate_all(n: int, m: int, bl:Optional[Blacklist]) -> List[Permutation]:
    # list of valid assignments
    assignments: List[Permutation] = []

    perms = itertools.permutations(range(n))
    for p in perms:
        if check_constraints(p, m, bl):
            assignments.append(p)

    return assignments

def sub_factorial(n: int):
    # Use Decimal to handle large n
    return (Decimal(math.factorial(n))/Decimal(math.e)).to_integral_exact()

def random_derangement(n):
    A = range(n)
    marked = [False] * n
    i = u = n-1
    while u >= 1:
        if not marked[i]:
            while 1:
                j = random.randrange(0, i)
                if not marked[j]: break
            A[i], A[j] = A[j], A[i] # pythonic swap with no explicit temporary space
            p = random.uniform(0,1) # TODO correct range?
            if p < u * sub_factorial(u-1) / sub_factorial(u+1):
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
            p = random.uniform(0,1) # TODO correct range?
            if p < u * sub_factorial(u-1) / sub_factorial(u+1):
                marked[j] = True
                u = u - 1
            u = u -1
        i = i -1
    return A
