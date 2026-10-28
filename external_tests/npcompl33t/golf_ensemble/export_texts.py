# Writes, for the 207 paragraph pages, the lines of words of the real text (ZL3b, as the skribe learns it) and of the skribe.
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'scribe'))
import measures as M
from scribe import Escriba, L_ALL
def pages(lines, meta):
    P = {}
    for l, m in zip(lines, meta): P.setdefault(m['page'], []).append(l['ws'])
    return P
real = M.load_real(); out = {'real': pages(real, real)}
for s in (1, 2, 3): out['skribe_s%d' % s] = pages(Escriba().write(seed=s), L_ALL)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'texts.json'), 'w', encoding='utf-8'))
print({k: sum(len(w) for ls in v.values() for w in ls) for k, v in out.items()})
