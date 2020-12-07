import matplotlib.pyplot as plt # type:ignore
import sinterbot.algorithms as algo
import random
from collections import defaultdict
from scipy.stats import chisquare # type:ignore
from typing import Dict
import time

SEED=352215382956615399
ITERATIONS=10000
SIZEN=6
random.seed(SEED)

def test_func(func: str, num: int, ylim: int = None):
    data: Dict[str, int] = defaultdict(int)

    for i in range(ITERATIONS):
        p = getattr(algo, func)(SIZEN)
        data[repr(p)] += 1

    sorted_data = sorted(data.items())
    perms, counts = zip(*sorted_data)

    fig, ax = plt.subplots()
    fig.set_size_inches(6,3.5)
    #fig.subplots_adjust(top=0.7)
    if ylim:
        ax.set_ylim(top=100)
    ax.bar(perms, counts, width=1.0)
    ax.set_xticks([sorted_data[0][0], sorted_data[-1][0]])
    ax.axhline(ITERATIONS/num, color='grey')
    #ax.xaxis.set_major_locator(plt.AutoLocator())
    #ax.tick_params('x', labelrotation=90)
    fig.savefig(func+'.png')

    
    maxcount = max(counts)
    maxindex = counts.index(maxcount)
    print("#: {}".format(len(counts)))
    print("Max {} = {}".format(perms[maxindex], maxcount))
    mincount = min(counts)
    minindex = counts.index(mincount)
    print("Min {} = {}".format(perms[minindex], mincount))
    print(chisquare(list(data.values()), [float(ITERATIONS/num)]*int(num)))

if __name__ == "__main__":
    derange_funcs =['generate_backtrack', 'generate_all', 'generate_rejection', 'rand_derangement']
    perm_funcs = ['shuffle', 'shuffle_python']
    for f in derange_funcs:
        print("Running {}".format(f))
        start = time.monotonic()
        test_func(f, algo.Dn(SIZEN), ylim=100)
        finish = time.monotonic()
        print("Time: {} seconds".format(finish-start))
        print()
