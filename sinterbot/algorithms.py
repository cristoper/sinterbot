import random
import math
import itertools
from decimal import Decimal
from typing import Optional, List, Tuple

"""From random documentation:

Note that for even rather small len(x), the total number of permutations of x is larger than the period of most random number generators; this implies that most permutations of a long sequence can never be generated.

TODO WHAT DO ABOUT THIS?

MT has a period length of 2^19937 - 1, which means it can be used to uniformly select a random permutation of size n<=2080

"""    

# For the typechecker
Permutation = List[int]
Blacklist = List[Tuple[int, int]]

def Dn(n: int):
    """
    Calculate the subfactorial of n
    This is the same as the number of derangements that can be made from a set of size n
    """
    # Use Decimal to handle large n accurately (by large, I mean n>13 or so)
    s = 0
    for k in range(n+1):
        s += (-1)**k/Decimal(math.factorial(k))
    return Decimal.to_integral_exact(Decimal(math.factorial(n)) * s)

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

def all_derangements(n: int) -> Permutation:
    """
    Generator that yields all derangements of size n.
    """
    perms = itertools.permutations(range(n))
    for p in perms:
        if check_deranged(p): yield(p)
            
def generate_backtrack(n: int) -> Permutation:
    """
    Generate a random derangement by backtracking. THIS IS BIASED.
    """
    if n == 0: return []
    remaining = list(range(n))
    perm: List[int] = []

    # backtrack until solution
    while len(perm) < n:
        perm.append(random.choice(remaining))
        if not check_deranged(perm):
            if len(remaining) == 1:
                # we're down to the last two elements just swap them to get a
                # derangement
                perm[-1], perm[-2] = perm[-2], perm[-1]
                return perm
            # undo last choice
            perm.pop(-1)
        else:
            remaining.remove(perm[-1])
    return perm

def generate_all(n: int) -> Permutation:
    """
    Generates all possible permutations saving the derangements, and then
    returns a random derangement. SLOW AND MEMORY HOG.
    """
    potential = []
    perms = itertools.permutations(range(n))
    for p in perms:
        plist = list(p)
        if check_deranged(plist):
            potential.append(plist)
    return random.choice(potential)

def generate_rejection(n: int) -> Permutation:
    """
    Create a random derangement of [n] by first generating a random permutation
    and rejecting it if it is not a derangement.
    """
    perm = list(range(n))
    while not check_deranged(perm):
        # Fisher-Yates shuffle:
        for i in range(n):
            k = random.randrange(n-i)+i # i <= k < n
            perm[i], perm[k] = perm[k], perm[i]
    return perm

def rand_derangement(n: int) -> Permutation:
    """
    Directly generate a random derangement with uniform probability.
    """
    perm = list(range(n))
    remaining = list(perm)
    while (len(remaining)>1):
        rand_i = random.randrange(len(remaining)-1) # random index < last
        last = remaining[-1]
        rand = remaining[rand_i]

        # swap to join cycles
        perm[last], perm[rand] = perm[rand], perm[last]
        
        # remove last from remaining
        remaining.pop(-1)

        p = random.random() # uniform [0, 1)
        l = len(remaining)
        if l > 30:
            # fast approximation for large i
            prob = 1/l
        else:
            prob = l * Dn(l-1)/Dn(l+1)
        if p < prob:
            # Close the cycle
            remaining.pop(rand_i)
    return perm

def constrained(n: int, m: int = 2, bl: Blacklist = None) -> Permutation:
    """
    Return a random derangement given the constraints that minimum cycle must
    be >= m and neither pair in any of the pairs in bl may follow each other in
    a cycle (ie, for two santas in bl, niether can be assigned to each other).
    """
    # TODO: check to make sure this can return given bl!
    if m > n: return []
    perm = generate_rejection(n)
    while not check_constraints(perm, m, bl):
        perm = generate_rejection(n)
    return perm
