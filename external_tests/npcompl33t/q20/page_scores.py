# Consensus score of every page (paragraph207 cohort, path-v2 default) from the fits of ../golf_ensemble/run_golf.py,
# for the real text and the three skribe seeds. Writes page_scores.json (committed, so the other Q20 scripts run without the fits).
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); GOLF = os.path.join(HERE, '..', 'golf_ensemble')
src = open(os.path.join(GOLF, 'analyse_golf.py'), encoding='utf-8').read()
g = {'__file__': os.path.join(GOLF, 'analyse_golf.py')}; exec(src.split("pub = {r['id']")[0], g)   # its consensus(), not its report
out = {}
for t in g['TEXTS']:
    F = json.loads((g['HERE'] / f'fits_{t}.json').read_text()); ids = F['meta']['paragraph207_point_l010']
    s, P, nb, groups = g['consensus'](F, 'paragraph207'); out[t] = {i: float(v) for i, v in zip(ids, s)}
d = json.loads((g['OLD'] / 'ensemble_paragraph207_point_l010.json').read_text())['design']
out['_meta'] = {m['id']: (m['bifolium'], m['group']) for m in d['meta']}
json.dump(out, open(os.path.join(HERE, 'page_scores.json'), 'w'))
q = [i for i in out['_meta'] if out['_meta'][i][0].startswith('T:')]
print('Q20 page scores (0 = earliest end of his curve, 1 = latest)')
print('page   bifolium   golf  ' + '  '.join('%-9s' % t for t in g['TEXTS']))
for i in q: print('%-6s %-10s %-4s  ' % (i, *out['_meta'][i]) + '  '.join('%-9.3f' % out[t][i] for t in g['TEXTS']))
