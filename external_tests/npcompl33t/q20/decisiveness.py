# How decided is the bifolio order inside each quire, in npcompl33t's ensemble? Mean |2p - 1| over the pairs of bifolia of the quire,
# p = share of selected fits putting one after the other (1 = always the same order, 0 = coin flips). Needs the fits of ../golf_ensemble.
import os, sys, json, itertools, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); GOLF = os.path.join(HERE, '..', 'golf_ensemble')
src = open(os.path.join(GOLF, 'analyse_golf.py'), encoding='utf-8').read()
g = {'__file__': os.path.join(GOLF, 'analyse_golf.py')}; exec(src.split("pub = {r['id']")[0], g)
TEXTS = g['TEXTS']; D = {}
for t in TEXTS:
    F = json.loads((g['HERE'] / f'fits_{t}.json').read_text()); ids = F['meta']['pool50_point_l010']
    s, P, nb, groups = g['consensus'](F, 'pool50'); D[t] = (ids, P, groups)
ids = D['real'][0]
print('Decisiveness of the bifolio order inside each quire with >= 3 bifolia (pool cohort)')
print('quire (n)  real | ' + ' '.join(TEXTS[1:]) + '   Golf labels')
for q in sorted({i.split(':')[0] for i in ids}):
    ix = [k for k, i in enumerate(ids) if i.split(':')[0] == q]
    if len(ix) < 3: continue
    v = [np.mean([abs(2 * D[t][1][a, b] - 1) for a, b in itertools.combinations(ix, 2)]) for t in TEXTS]
    print('  %-2s (%d)   %.2f | %s   %s' % (q, len(ix), v[0], '      '.join('%.2f' % x for x in v[1:]), ' '.join(D['real'][2][k] for k in ix)))
