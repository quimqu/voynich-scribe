# Pass 2 of the glyph-pair scan (pre-registered in CONTEXT_PAIRS_PREREG.md, 27/10/2026): glyph pairs whose rate changes with the
# place of the word (word place in the line, line type, hand, section, language) differently in the real text and in the skribe.
# Per cell (a, context, value c, b): [P(b|a,c) - P(b|a,not c)]_real - [same]_skribe, z on the binomial errors; flagged if |z| >= 4.5
# on the whole text and the same sign with |z| >= 2 on odd and on even folios.
#   PYTHONIOENCODING=utf-8 py -3 scribe/pairs/context_pairs.py <real.txt> <skribe_seed*.txt glob> <label>
import os, re, sys, glob, math
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
U = re.compile(r'cth|ckh|cph|cfh|ch|sh|.')
MIN_N, Z_ALL, Z_HALF = 80, 4.5, 2.0
VARS = ['wplace', 'ltype', 'hand', 'section', 'lang']


def read(path):
    """list of (context dict, word) for every word of paragraph text"""
    out = []; meta = {}; odd = None
    for ln in open(path, encoding='utf-8'):
        m = re.match(r'^<f(\d+)[rv]\d*>\s+<!(.*)>', ln)
        if m:
            odd = int(m.group(1)) % 2 == 1; meta = dict(re.findall(r'\$(\w)=(\S+)', m.group(2))); continue
        if ln.startswith('#') or not ln.strip():
            continue
        m = re.match(r'^<[^>]+>\s*(.*)$', ln.rstrip('\n'))
        if not m:
            continue
        t = m.group(1); ps, pe = '<%>' in t, '<$>' in t
        t = t.replace('<%>', '').replace('<$>', '')
        toks = []   # (word, gap before)
        for k, chunk in enumerate(t.split('<->')):
            ws = [w for w in chunk.split('.') if w]
            toks += [(w, k > 0 and i == 0) for i, w in enumerate(ws)]
        n = len(toks); lt = 'par_first' if ps else ('par_last' if pe else 'interior')
        for i, (w, gb) in enumerate(toks):
            nxt_gap = i + 1 < n and toks[i + 1][1]
            wp = 'first' if i == 0 else ('last' if i == n - 1 else ('after_gap' if gb else ('before_gap' if nxt_gap else 'inner')))
            out.append((dict(wplace=wp, ltype=lt, hand=meta.get('H'), section=meta.get('S'), lang=meta.get('L'), odd=odd), w))
    return out


def counts(items, parity=None):
    """C[var][(a, value)][b] and T[var][(a, value)] totals"""
    C = {v: defaultdict(Counter) for v in VARS}
    for ctx, w in items:
        if parity is not None and ctx['odd'] != (parity == 'odd'):
            continue
        g = ['^'] + U.findall(w) + ['$']
        for a, b in zip(g, g[1:]):
            for v in VARS:
                C[v][(a, ctx[v])][b] += 1
    return C


def cells(CR, CS):
    """yield (var, a, c, b, did, z, n_real_c)"""
    for v in VARS:
        byA_R, byA_S = defaultdict(dict), defaultdict(dict)
        for (a, c), cnt in CR[v].items(): byA_R[a][c] = cnt
        for (a, c), cnt in CS[v].items(): byA_S[a][c] = cnt
        for a, vals in byA_R.items():
            totR = sum(vals.values(), Counter()); totS = sum(byA_S[a].values(), Counter())
            for c, cr in vals.items():
                nrc = sum(cr.values())
                if nrc < MIN_N or c not in byA_S[a]:
                    continue
                cs = byA_S[a][c]; nsc = sum(cs.values()); nrn = sum(totR.values()) - nrc; nsn = sum(totS.values()) - nsc
                if nrn < MIN_N or nsc < MIN_N or nsn < MIN_N:
                    continue
                for b in set(cr) | set(cs) | set(totR):
                    prc = cr[b] / nrc; prn = (totR[b] - cr[b]) / nrn; psc = cs[b] / nsc; psn = (totS[b] - cs[b]) / nsn
                    did = (prc - prn) - (psc - psn)
                    pr = totR[b] / (nrc + nrn); ps = totS[b] / (nsc + nsn)
                    se = math.sqrt(max(pr * (1 - pr), 1e-6) * (1 / nrc + 1 / nrn) + max(ps * (1 - ps), 1e-6) * (1 / nsc + 1 / nsn))
                    yield v, a, c, b, did, did / se, nrc, (prc, prn, psc, psn)


def scan(real_path, skribe_paths, label):
    R = read(real_path); S = [x for p in skribe_paths for x in read(p)]
    full = {(v, a, c, b): (d, z, n, P) for v, a, c, b, d, z, n, P in cells(counts(R), counts(S))}
    halves = {}
    for par in ('odd', 'even'):
        halves[par] = {(v, a, c, b): z for v, a, c, b, d, z, n, P in cells(counts(R, par), counts(S, par))}
    flagged = []
    for k, (d, z, n, P) in full.items():
        if abs(z) < Z_ALL:
            continue
        zo, ze = halves['odd'].get(k, 0), halves['even'].get(k, 0)
        if zo * z > 0 and ze * z > 0 and abs(zo) >= Z_HALF and abs(ze) >= Z_HALF:
            flagged.append((k, d, z, zo, ze, n, P))
    flagged.sort(key=lambda x: -abs(x[2]))
    L = [f'### {label}: {len(full)} cells tested, {len(flagged)} flagged (|z| >= {Z_ALL}, replicated on odd and even folios)',
         f"{'context':26} {'pair':9} {'real c / rest':>15} {'skribe c / rest':>16} {'DiD':>7} {'z':>6} {'z odd':>6} {'z even':>6} {'n':>5}"]
    for (v, a, c, b), d, z, zo, ze, n, (prc, prn, psc, psn) in flagged:
        L.append(f"{v + '=' + str(c):26} {a + ' ' + b:9} {prc:6.3f} /{prn:6.3f}  {psc:6.3f} /{psn:6.3f}  {d:+7.3f} {z:+6.1f} {zo:+6.1f} {ze:+6.1f} {n:5d}")
    return L


if __name__ == '__main__':
    real, pat, label = sys.argv[1], sys.argv[2], sys.argv[3]
    L = scan(real, sorted(glob.glob(pat)), label)
    print('\n'.join(L))
    open(os.path.join(HERE, f'context_pairs_{label}.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
