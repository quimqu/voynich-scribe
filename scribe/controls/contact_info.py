# Where the information between consecutive words lies (CONTROLS.md): mutual information between a property of the previous word
# and the next word of the same line (the 200 most frequent words; the rest, a single class), minus the same after shuffling the
# words within each line (5 shuffles). Property: the whole previous word (same classes), or only its last glyph.
# Real even folios and the skribe's even folios (manuscript_out, five seeds, trained on the whole text).
#   PYTHONIOENCODING=utf-8 py -3 controls/contact_info.py          (from scribe/)
import os, re, sys, random
import numpy as np
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from control import MI
UNITS = re.compile(r'cth|ckh|cph|cfh|ch|sh|.')


def lines(path, even=True):
    L = []; pg = None
    for ln in open(path, encoding='utf-8'):
        m = re.match(r'^<(f(\d+)[rv]\d*)>\s+<!', ln)
        if m:
            pg = int(m.group(2)); continue
        m = re.match(r'^<[^>]+>\s*(.*)$', ln.rstrip('\n'))
        if not m or ln.startswith('#') or pg is None or (even and pg % 2):
            continue
        ws = [w for w in m.group(1).replace('<%>', '').replace('<$>', '').replace('<->', '.').split('.') if w]
        if len(ws) > 1:
            L.append(ws)
    return L


def info(L, K=200, reps=5):
    top = set(w for w, _ in Counter(w for l in L for w in l).most_common(K))
    m = lambda w: w if w in top else '*'
    last = lambda w: UNITS.findall(w)[-1]
    def both(LL):
        pp = [(a, b) for l in LL for a, b in zip(l, l[1:])]
        return MI([(m(a), m(b)) for a, b in pp]), MI([(last(a), m(b)) for a, b in pp])
    r = both(L); rng = random.Random(0); base = []
    for _ in range(reps):
        S = []
        for l in L:
            l = l[:]; rng.shuffle(l); S.append(l)
        base.append(both(S))
    b = np.mean(base, axis=0)
    return r[0] - b[0], r[1] - b[1]


OUT = os.path.join(HERE, '..', 'manuscript_out')
out = [f"{'text (even folios)':22} {'whole word':>10} {'last glyph':>10}"]
r = info(lines(os.path.join(OUT, 'real.txt'))); out.append(f"{'real':22} {r[0]:10.3f} {r[1]:10.3f}")
R = [info(lines(os.path.join(OUT, f'scribe_seed{s}.txt'))) for s in range(1, 6)]
out += [f"{'skribe seed ' + str(s):22} {r[0]:10.3f} {r[1]:10.3f}" for s, r in enumerate(R, 1)]
out.append(f"{'skribe, mean':22} {np.mean([r[0] for r in R]):10.3f} {np.mean([r[1] for r in R]):10.3f}")
print('\n'.join(out)); open(os.path.join(HERE, 'contact_info_out.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
