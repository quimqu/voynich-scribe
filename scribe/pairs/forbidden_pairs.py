# Pass 1 of the glyph-pair scan (27/10/2026): which glyph pairs inside a word are (almost) never written, against what the
# frequencies of the two glyphs would give? This is how "a plain p/f is never followed by e" shows (R1.3). Glyph units as in the
# rest of the programme (cth ckh cph cfh ch sh as one glyph); word start ^ and end $ are glyphs too. Paragraph text, ZL3b.
# Expected count of a -> b: (pairs leaving a) x (pairs entering b) / (all pairs). Listed: expected >= MIN_E and observed /
# expected <= MAX_OE, on the whole text and, as replication, on the odd and the even folios separately. Each pair is marked
# with the rule that already covers it, if any.
#   PYTHONIOENCODING=utf-8 py -3 scribe/pairs/forbidden_pairs.py [path]   (default: scribe/manuscript_out/real.txt)
import os, re, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'scribe', 'manuscript_out', 'real.txt')
U = re.compile(r'cth|ckh|cph|cfh|ch|sh|.')
MIN_E, MAX_OE = 30, 0.20
GALL, BENCHG = set('ktpf'), {'cth', 'ckh', 'cph', 'cfh'}


def words(path, parity=None):
    W = []; odd = None
    for ln in open(path, encoding='utf-8'):
        m = re.match(r'^<f(\d+)[rv]\d*>\s+<!', ln)
        if m:
            odd = int(m.group(1)) % 2 == 1; continue
        if ln.startswith('#') or not ln.strip():
            continue
        m = re.match(r'^<[^>]+>\s*(.*)$', ln.rstrip('\n'))
        if not m or (parity is not None and odd != (parity == 'odd')):
            continue
        W += [w for w in m.group(1).replace('<%>', '').replace('<$>', '').replace('<->', '.').split('.') if w]
    return W


def table(W):
    P = Counter()
    for w in W:
        g = ['^'] + U.findall(w) + ['$']
        P.update(zip(g, g[1:]))
    out, inn = Counter(), Counter()
    for (a, b), n in P.items():
        out[a] += n; inn[b] += n
    return P, out, inn, sum(P.values())


def oe(T, a, b):
    P, out, inn, N = T; e = out[a] * inn[b] / N
    return P[(a, b)], e


def known(a, b):
    """the rule that already says this pair is (almost) never written, or ''"""
    if a == '^' and b == '$': return 'empty word'
    if a == 'q' and b != 'o': return 'R1.4 q only before o'
    if b == 'q' and a != '^': return 'R1.4 q only initial'
    if a == '^' and b in ('e', 'i', 'n', 'm'): return 'R1.5 e i n m never begin'
    if b == '$' and a in ('e', 'a', 'i', 'ch', 'q', 'sh'): return 'R1.5 e a i ch q never end'
    if {a, b} <= {'e', 'i'} and a != b: return 'R13.7 e and i never together'
    if (a in GALL | BENCHG) and (b in GALL | BENCHG): return 'R2.2 one gallows per word'
    if a in ('p', 'f') and b == 'e': return 'R1.3 (27/10) no e after plain p/f'
    return ''


W = words(PATH); T = table(W); To, Te = table(words(PATH, 'odd')), table(words(PATH, 'even'))
P, out, inn, N = T
rows = []
for a in out:
    for b in inn:
        o, e = oe(T, a, b)
        if e >= MIN_E and o / e <= MAX_OE:
            oo, eo = oe(To, a, b); ov, ev = oe(Te, a, b)
            rows.append((o / e, a, b, o, e, oo / eo if eo else float('nan'), ov / ev if ev else float('nan'), known(a, b)))
rows.sort()
L = [f'Glyph pairs inside words written at most {MAX_OE:.0%} of the expected count (expected >= {MIN_E}); {len(W)} words, {N} pairs.',
     '^ = word start, $ = word end. obs/exp also on odd and even folios (replication).', '',
     f"{'pair':10} {'obs':>6} {'exp':>8} {'obs/exp':>8} {'odd':>6} {'even':>6}   rule that covers it"]
for r, a, b, o, e, ro, rv, k in rows:
    L.append(f"{a + ' ' + b:10} {o:6d} {e:8.1f} {r:8.3f} {ro:6.3f} {rv:6.3f}   {k or '-- NEW? --'}")
new = [x for x in rows if not x[7]]
L += ['', f'{len(rows)} pairs listed, {len(rows) - len(new)} covered by a rule, {len(new)} not covered.']
open(os.path.join(HERE, 'forbidden_pairs.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
