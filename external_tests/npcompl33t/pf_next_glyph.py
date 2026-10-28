# npcompl33t, voynich.ninja thread 6231 (27/10/2026): "kch and tch drop in popularity, while pch does not", as evidence that P/F
# change differently from K/T. Share of plain k/t and of plain p/f followed by ch, e, a, o, per language x section, in the real text
# and in the skribe (no chronology; only the rule that a plain p/f is never followed by e, R1.3).
#   PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/pf_next_glyph.py      (~30 s; writes pf_next_glyph.txt)
import os, re, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scribe'))
import measures as M
from scribe import Escriba, L_ALL
GROUPS = [('A', 'herbal'), ('A', 'pharmaceutical'), ('B', 'herbal'), ('B', 'biological'), ('B', 'stars')]
NEXT = ('ch', 'e', 'a', 'o')
OUT = []


def say(s=''):
    OUT.append(s); print(s, flush=True)


def stats(lines, meta):
    C = defaultdict(Counter)
    for l, m in zip(lines, meta):
        c = C[(m['lang'], m['section'])]
        for w in l['ws']:
            for mm in re.finditer(r'(?<!c)([ktpf])(?!h)', w):
                g = 'KT' if mm.group(1) in 'kt' else 'PF'; nx = w[mm.end():]; c[g] += 1
                for x in NEXT:
                    if nx.startswith(x): c[g + x] += 1
    return C


say('Plain k/t (KT) and plain p/f (PF): share followed by each glyph, per language x section. Last column: ch + e after k/t.')
say('%-18s %6s %6s | %s | %6s' % ('group', 'n KT', 'n PF', ' '.join('%6s %6s' % ('KT' + x, 'PF' + x) for x in NEXT), 'KTch+e'))
real = M.load_real()
for lab, (lines, meta) in [('real', (real, real))] + [('skribe s%d' % s, (Escriba().write(seed=s), L_ALL)) for s in (1, 2, 3)]:
    C = stats(lines, meta); say('-- %s --' % lab)
    for g in GROUPS:
        c = C[g]; f = lambda k, b: 100 * c[k] / max(c[b], 1)
        say('%-18s %6d %6d | %s | %5.1f%%' % ('%s %s' % g, c['KT'], c['PF'], ' '.join('%5.1f%% %5.1f%%' % (f('KT' + x, 'KT'), f('PF' + x, 'PF')) for x in NEXT),
                                            f('KTch', 'KT') + f('KTe', 'KT')))
open(os.path.join(HERE, 'pf_next_glyph.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
