# Fold position test (pre-registered in FOLD_POSITION_PREREG.md): are the words with a one-glyph variant on the facing page
# closer to the fold than the other words? On the open folded sheet the left page is a verso (fold at the end of its lines) and
# the right page a recto (fold at the start of its lines). Inner face a-v | b-r against outer face b-v | a-r (control).
#   PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/fold_position.py
# Input: scribe/manuscript_out/{real,scribe_seed*}.txt. Output: here, fold_position.{txt,json}
import os, re, glob, json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import wilcoxon
HERE = os.path.dirname(os.path.abspath(__file__)); NOV = os.path.abspath(os.path.join(HERE, '..', '..'))
QUIRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'M', 'T']
MAXPAGES = 40
rng = np.random.default_rng(0)
OUT = []


def say(s=''):
    OUT.append(s); print(s, flush=True)


def read(path):
    """page -> dict(meta, lines=[[words]])"""
    P = {}; cur = None
    for ln in open(path, encoding='utf-8'):
        if ln.startswith('#') or not ln.strip():
            continue
        m = re.match(r'^<(f\d+[rv]\d*)>\s+<!(.*)>', ln)
        if m:
            cur = m.group(1); P[cur] = dict(dict(re.findall(r'\$(\w)=(\S+)', m.group(2))), lines=[]); continue
        m = re.match(r'^<[^>]+>\s*(.*)$', ln.rstrip('\n'))
        if not m or cur is None:
            continue
        t = m.group(1).replace('<%>', '').replace('<$>', '').replace('<->', '.')
        ws = [w for w in t.split('.') if w]
        if ws:
            P[cur]['lines'].append(ws)
    return P


def fnum(f):
    return int(re.match(r'f(\d+)', f).group(1))


def bifolia(P):
    sheets = defaultdict(set)
    for pg, d in P.items():
        m = re.fullmatch(r'(f\d+)[rv]', pg)
        if m and d['Q'] in QUIRES:
            sheets[(d['Q'], d['F'])].add(m.group(1))
    out = []
    for (q, s), fs in sheets.items():
        if len(fs) == 2:
            a, b = sorted(fs, key=fnum)
            if all(f + x in P and P[f + x]['lines'] for f in (a, b) for x in 'rv'):
                out.append((q, a, b))
    return sorted(out, key=lambda t: fnum(t[1]))


def lev1(a, b):
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def tokens(page, verso, band):
    """(word, fold proximity, line fraction) for words of the band, lines of >= 2 words"""
    L = page['lines']; n = len(L); out = []
    for li, ws in enumerate(L):
        if len(ws) < 2:
            continue
        for i, w in enumerate(ws):
            if w in band:
                pos = i / (len(ws) - 1); out.append((w, pos if verso else 1 - pos, li / max(n - 1, 1)))
    return out


def face(P, band, left, right):
    """fold proximity of linked minus unlinked tokens; and vertical alignment of linked pairs"""
    TL, TR = tokens(P[left], True, band), tokens(P[right], False, band)
    tl, tr = {w for w, _, _ in TL}, {w for w, _, _ in TR}
    link_l = {w for w in tl if any(lev1(w, v) for v in tr)}; link_r = {w for w in tr if any(lev1(w, v) for v in tl)}
    toks = [(p, w in link_l) for w, p, _ in TL] + [(p, w in link_r) for w, p, _ in TR]
    lk = [p for p, f in toks if f]; un = [p for p, f in toks if not f]
    if not lk or not un:
        return None
    pairs = [abs(fa - fb) for wa, _, fa in TL for wb, _, fb in TR if lev1(wa, wb)]
    allp = [abs(fa - fb) for _, _, fa in TL for _, _, fb in TR]
    return dict(d=float(np.mean(lk) - np.mean(un)), n_linked=len(lk), n=len(toks), linked=float(np.mean(lk)), unlinked=float(np.mean(un)),
                vert=float(np.mean(pairs) / np.mean(allp)) if pairs else float('nan'))


def analyse(path):
    P = read(path); B = bifolia(P)
    pf = Counter(w for d in P.values() for w in {w for l in d['lines'] for w in l}); band = {w for w, c in pf.items() if c <= MAXPAGES}
    rows = []
    for q, a, b in B:
        fi, fo = face(P, band, a + 'v', b + 'r'), face(P, band, b + 'v', a + 'r')
        if fi and fo:
            rows.append(dict(q=q, bif=f'{a}|{b}', hand=P[a + 'r']['H'], lang=P[a + 'r']['L'], inner=fi, outer=fo))
    return rows


def wil(x, alt='two-sided'):
    x = np.asarray(x)
    return float(wilcoxon(x, alternative=alt).pvalue) if len(x) and np.any(x != 0) else 1.0


srcs = [('real', os.path.join(NOV, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(NOV, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
ALL = {s: analyse(p) for s, p in srcs}
say('Fold position test (pre-registered, FOLD_POSITION_PREREG.md). Fold proximity: 1 = at the fold (end of line on the verso, start of line on the recto).')
say(f'Linked token: word used on <= {MAXPAGES} pages with a one-glyph variant (not the same word) on the facing page. d = mean proximity of linked minus unlinked tokens.')
say('')
say('PRIMARY · hand 2, inner minus outer, paired, one-sided Wilcoxon (inner greater)')
for src, rows in ALL.items():
    r = [x for x in rows if x['hand'] == '2']; di = [x['inner']['d'] for x in r]; do = [x['outer']['d'] for x in r]; dd = np.array(di) - np.array(do)
    say(f"  {src:13} n {len(r)} | inner d {np.mean(di):+.3f} | outer d {np.mean(do):+.3f} | inner-outer {dd.mean():+.3f}, p (one-sided) {wil(dd, 'greater'):.3f}, "
        f"{100*np.mean(dd > 0):.0f}% > 0 | inner > 0: p (one-sided) {wil(di, 'greater'):.3f}")
say('')
say('SECONDARY · by group: inner d, outer d, inner-outer (two-sided p); mean linked tokens per face')
for grp in ('all', '1', '2', '3'):
    for src, rows in ALL.items():
        r = [x for x in rows if grp == 'all' or x['hand'] == grp]
        if not r:
            continue
        di = np.array([x['inner']['d'] for x in r]); do = np.array([x['outer']['d'] for x in r])
        if src == 'real' or src == 'scribe_seed1':
            say(f"  {grp:3} {src:13} n {len(r):2d} | inner {di.mean():+.3f} (p {wil(di):.2f}) | outer {do.mean():+.3f} (p {wil(do):.2f}) | "
                f"inner-outer {np.mean(di - do):+.3f} (p {wil(di - do):.2f}) | linked {np.mean([x['inner']['n_linked'] for x in r]):.1f} / {np.mean([x['outer']['n_linked'] for x in r]):.1f}")
    sc = [[x for x in ALL[s] if grp == 'all' or x['hand'] == grp] for s in ALL if s != 'real']
    say(f"  {grp:3} scribe, 5 seeds  | inner {np.mean([np.mean([x['inner']['d'] for x in r]) for r in sc]):+.3f} | outer {np.mean([np.mean([x['outer']['d'] for x in r]) for r in sc]):+.3f} | "
        f"inner-outer p {min(wil([x['inner']['d'] - x['outer']['d'] for x in r]) for r in sc):.2f}-{max(wil([x['inner']['d'] - x['outer']['d'] for x in r]) for r in sc):.2f}")
say('')
say('SECONDARY · vertical alignment of linked pairs: mean |difference in line fraction| of linked pairs / of all cross-page pairs (1 = no alignment, < 1 = same height)')
for src, rows in ALL.items():
    vi = [x['inner']['vert'] for x in rows if x['inner']['vert'] == x['inner']['vert']]; vo = [x['outer']['vert'] for x in rows if x['outer']['vert'] == x['outer']['vert']]
    v2 = [x['inner']['vert'] for x in rows if x['hand'] == '2' and x['inner']['vert'] == x['inner']['vert']]
    say(f'  {src:13} inner {np.mean(vi):.3f} | outer {np.mean(vo):.3f} | hand 2 inner {np.mean(v2):.3f}')
say('')
say('Per bifolium, real, hand 2: inner d / outer d (linked tokens inner / outer)')
for x in ALL['real']:
    if x['hand'] == '2':
        say(f"  {x['bif']:10} {x['q']} | {x['inner']['d']:+.3f} / {x['outer']['d']:+.3f} ({x['inner']['n_linked']} / {x['outer']['n_linked']})")

# ---------- positive control (power; not part of the pre-registration) ----------
# Inject copies into the real text, hand 2, inner faces only: in a fraction f of the lines of the right page (b-r), the first word
# is replaced by an existing word type at one glyph from the last word of a random line of the left page (a-v). Smallest f detected in >= 80% of runs.
def edit1(w, alphabet):
    i = int(rng.integers(len(w))); op = rng.integers(3); c = str(rng.choice(alphabet))
    return (w[:i] + c + w[i + 1:]) if op == 0 else ((w[:i] + c + w[i:]) if op == 1 or len(w) < 3 else (w[:i] + w[i + 1:]))


def inject(P, B, f):
    """the copy is an existing word type of the manuscript at one glyph from the model (as real copies are: chol -> kchol)"""
    Q = {pg: dict(d, lines=[list(l) for l in d['lines']]) for pg, d in P.items()}
    global NB
    if 'NB' not in globals() or NB[0] is not P:
        pf = Counter(w for d in P.values() for w in {w for l in d['lines'] for w in l}); types = sorted(w for w, c in pf.items() if c >= 2)   # sorted: reproducible across runs
        byl = defaultdict(list)
        for w in types:
            byl[len(w)].append(w)
        cache = {}
        def nb(w):
            if w not in cache:
                cache[w] = [v for L_ in (len(w) - 1, len(w), len(w) + 1) for v in byl.get(L_, []) if lev1(w, v)]
            return cache[w]
        NB = (P, nb)
    nb = NB[1]
    for q, a, b in B:
        if P[a + 'r']['H'] != '2':
            continue
        src = [l[-1] for l in Q[a + 'v']['lines'] if len(l) >= 2 and nb(l[-1])]
        for l in Q[b + 'r']['lines']:
            if len(l) >= 2 and src and rng.random() < f:
                l[0] = str(rng.choice(nb(str(rng.choice(src)))))
    return Q


def primary(P, B):
    pf = Counter(w for d in P.values() for w in {w for l in d['lines'] for w in l}); band = {w for w, c in pf.items() if c <= MAXPAGES}
    dd = []
    for q, a, b in B:
        if P[a + 'r']['H'] == '2':
            fi, fo = face(P, band, a + 'v', b + 'r'), face(P, band, b + 'v', a + 'r')
            if fi and fo:
                dd.append(fi['d'] - fo['d'])
    return wil(dd, 'greater'), float(np.mean(dd))


say('')
say('POSITIVE CONTROL (power, not pre-registered): copies injected into the real text, hand 2 inner faces; fraction of right-page lines whose first word is an existing one-glyph variant of a line-final word of the left page')
Preal = read(srcs[0][1]); Breal = bifolia(Preal); POW = {}
for f in (0.05, 0.1, 0.2, 0.3, 0.5):
    rs = [primary(inject(Preal, Breal, f), Breal) for _ in range(20)]
    POW[f] = dict(detected=float(np.mean([p < 0.05 for p, _ in rs])), mean_diff=float(np.mean([m for _, m in rs])))
    say(f'  f = {f:.2f}: detected (one-sided p < 0.05) in {100*POW[f]["detected"]:.0f}% of 20 runs, mean inner-outer {POW[f]["mean_diff"]:+.3f}')
open(os.path.join(HERE, 'fold_position.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
json.dump(ALL, open(os.path.join(HERE, 'fold_position.json'), 'w', encoding='utf-8'), indent=1)
