# Layfield and Davis's published best orders for Q13 and Q20 (Digital Medievalist 19, 2026, "Bifolia reordering experiments") and
# npcompl33t's published path-v2 orders, ranked among all the permutations in our rebuild of their LSA (../../davis_layfield/lsa_singulion.py),
# on the real text and the five skribe seeds of scribe/manuscript_out.
import os, sys, glob, itertools, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); DL = os.path.join(HERE, '..', '..', 'davis_layfield', 'lsa_singulion.py')
sys.stdout.reconfigure(encoding='utf-8')
src = open(DL, encoding='utf-8').read(); sys.argv = [DL]
g = {'__file__': DL}; exec(src[:src.index('srcs = [')], g)   # its pages(), lsa(), pairs(), cos(); not its report
ORD = {'T': {'Layfield-Davis best': [105, 104, 106, 107, 108, 103], 'npcompl33t': [105, 104, 106, 107, 108, 103]},
       'M': {'Layfield-Davis best': [77, 78, 75, 76, 79], 'Layfield-Davis 2nd': [76, 77, 79, 75, 78], 'npcompl33t': [79, 76, 78, 75, 77]}}
OUT = os.path.join(g['NOV'], 'scribe', 'manuscript_out')
files = [('real', os.path.join(OUT, 'real.txt'))] + [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(OUT, 'scribe_seed*.txt')))]
print('Published orders ranked among all bifolio permutations, in our LSA rebuild (k=75, mean facing similarity, singulion reading).')
print('Q20 = T (720 orders), Q13 = M (120). Earliest bifolium first, named by its first folio.\n')
for name, path in files:
    P = g['pages'](path); vec, _ = g['lsa'](P, 75, 0); _, bifs = g['pairs'](P); cos = g['cos']
    for q in ('M', 'T'):
        bl = bifs[q]; by = {int(a[1:]): (a, b) for a, b in bl}

        def score(seq):
            order = []
            for a, b in seq: order += [a + 'r', a + 'v', b + 'r', b + 'v']
            return float(np.mean([cos(vec[x], vec[y]) for x, y in zip(order, order[1:]) if x.endswith('v') and y.endswith('r') and x in vec and y in vec]))
        allp = sorted(((score(s), s) for s in itertools.permutations(bl)), reverse=True); best = allp[0][0]
        ranks = ' | '.join('%s rank %d' % (lab, sum(1 for x, _ in allp if x > score([by[i] for i in o])) + 1) for lab, o in ORD[q].items())
        print('%-13s %s: best %-24s within 5%% of the best: %3d orders | %s' % (name, q, ' '.join(str(int(a[1:])) for a, b in allp[0][1]),
                                                                         sum(1 for s, _ in allp if s >= 0.95 * best), ranks))
