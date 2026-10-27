# Can the sheets be put in a chain? (pre-registered in SHEET_CHAIN_PREREG.md, 27/10/2026)
# Sheets grouped by hand x section; three affinities between sheets (VOC: TF-IDF words, GLY: npcompl33t's Jensen-Shannon of
# glyph transitions, HAB: the five free habits); pairwise residuals after removing additive sheet effects; P1 coherence VOC-GLY,
# P2 real against the five skribe seeds, P3 neighbours in the current nesting.
#   PYTHONIOENCODING=utf-8 py -3 external_tests/sheet_chain/sheet_chain.py
# Input: scribe/manuscript_out/{real,scribe_seed*}.txt. Output: here, sheet_chain.{txt,json}
import os, re, glob, json, math
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import mannwhitneyu
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ns = {'__file__': os.path.join(ROOT, 'external_tests', 'npcompl33t', 'seriation.py')}
exec(open(ns['__file__'], encoding='utf-8').read().split('def analyse(')[0], ns)
MIN_PAGES, MIN_WORDS, MIN_SHEETS, NPERM = 2, 250, 4, 5000
OUT = []


def say(s=''):
    OUT.append(s); print(s, flush=True)


def sheets(path):
    P = ns['read'](path); S = defaultdict(lambda: dict(pages=[], words=[], lines=[], H=[], S=[]))
    for pg, d in P.items():
        if not d.get('F') or not d['lines']:
            continue
        s = S[d['F']]; s['pages'].append(pg); s['lines'] += d['lines']; s['words'] += [w for l in d['lines'] for w in l]
        s['H'].append(d.get('H')); s['S'].append(d.get('S'))
    out = {}
    for f, s in S.items():
        if len(s['pages']) >= MIN_PAGES and len(s['words']) >= MIN_WORDS:
            s['group'] = (Counter(s['H']).most_common(1)[0][0], Counter(s['S']).most_common(1)[0][0])
            m = re.fullmatch(r'([A-Z])(\d+)', f); s['quire'], s['pos'] = m.group(1), int(m.group(2))
            out[f] = s
    return out


def habits(ws):
    t = ' '.join(ws); t2 = t.replace('ckh', '').replace('cth', '').replace('cph', '').replace('cfh', '')
    k, tt = t2.count('k'), t2.count('t'); ch, sh = t.count('ch'), t.count('sh')
    qo = sum(w.startswith('qo') for w in ws); o = sum(w.startswith('o') for w in ws)
    dy = sum(w.endswith('dy') for w in ws); y = sum(w.endswith('y') for w in ws)
    return np.array([k / max(1, k + tt), sh / max(1, ch + sh), qo / max(1, qo + o), dy / max(1, y), np.mean(['e' in w for w in ws])])


def residual(A):
    n = len(A); m = ~np.eye(n, dtype=bool); mu = A[m].mean(); a = np.zeros(n)
    for _ in range(200):
        a = np.array([np.mean([A[i, j] - mu - a[j] for j in range(n) if j != i]) for i in range(n)])
    R = A - mu - a[:, None] - a[None, :]; R[~m] = 0
    return R


def affinities(S, fs):
    docs = {f: Counter(S[f]['words']) for f in fs}
    df = Counter(w for c in docs.values() for w in c); N = len(fs)
    voc = {f: {w: c * math.log(N / df[w]) for w, c in docs[f].items() if df[w] >= 2} for f in fs}
    def cos(a, b):
        num = sum(v * b.get(w, 0) for w, v in a.items()); na = math.sqrt(sum(v * v for v in a.values())); nb = math.sqrt(sum(v * v for v in b.values()))
        return num / (na * nb) if na and nb else 0.0
    T = {f: ns['transitions'](S[f]['lines'])[0] for f in fs}
    return voc, cos, T


def analyse(path):
    S = sheets(path); allf = sorted(S)
    voc, cos, T = affinities(S, allf)
    groups = defaultdict(list)
    for f in allf:
        groups[S[f]['group']].append(f)
    G = {}
    for g, fs in groups.items():
        if len(fs) < MIN_SHEETS:
            continue
        n = len(fs); V = np.zeros((n, n)); J = np.zeros((n, n)); Hb = np.zeros((n, n))
        H = np.array([habits(S[f]['words']) for f in fs]); sd = H.std(0); sd[sd == 0] = 1; Hz = (H - H.mean(0)) / sd
        for i in range(n):
            for j in range(i + 1, n):
                V[i, j] = V[j, i] = cos(voc[fs[i]], voc[fs[j]])
                J[i, j] = J[j, i] = -math.sqrt(ns['dissimilarity'](T[fs[i]], T[fs[j]]))
                Hb[i, j] = Hb[j, i] = -np.linalg.norm(Hz[i] - Hz[j])
        G[g] = dict(fs=fs, V=residual(V), J=residual(J), H=residual(Hb))
    return S, G


def upper(R):
    return R[np.triu_indices(len(R), 1)]


def pooled_r(G, a, b, perm=None):
    x, y = [], []
    for g, d in G.items():
        Ra, Rb = d[a], d[b]
        if perm is not None:
            p = perm[g]; Rb = Rb[np.ix_(p, p)]
        x += list(upper(Ra)); y += list(upper(Rb))
    return float(np.corrcoef(x, y)[0, 1])


def zs(R):
    u = upper(R); return R / (u.std() if u.std() > 0 else 1)


def p3(S, G):
    nb, ot = [], []
    for g, d in G.items():
        C = (zs(d['V']) + zs(d['J'])) / 2; fs = d['fs']
        for i in range(len(fs)):
            for j in range(i + 1, len(fs)):
                a, b = S[fs[i]], S[fs[j]]
                if a['quire'] != b['quire']:
                    continue
                (nb if abs(a['pos'] - b['pos']) == 1 else ot).append(C[i, j])
    p = mannwhitneyu(nb, ot, alternative='greater').pvalue if nb and ot else float('nan')
    return dict(n_nb=len(nb), n_other=len(ot), diff=float(np.mean(nb) - np.mean(ot)) if nb and ot else float('nan'), p=float(p))


def one_dim(G):
    num = den = 0.0
    for d in G.values():
        C = (zs(d['V']) + zs(d['J'])) / 2; ev = np.linalg.eigvalsh(C); pos = ev[ev > 0]
        if len(pos):
            num += pos.max(); den += pos.sum()
    return num / den if den else float('nan')


srcs = [('real', os.path.join(ROOT, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(ROOT, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
rng = np.random.default_rng(0)
RES = {}
for s, path in srcs:
    S, G = analyse(path)
    r_vg = pooled_r(G, 'V', 'J'); perms = []
    for _ in range(NPERM):
        perms.append(pooled_r(G, 'V', 'J', {g: rng.permutation(len(d['fs'])) for g, d in G.items()}))
    p1 = float((1 + sum(x >= r_vg for x in perms)) / (NPERM + 1))
    RES[s] = dict(groups={f'h{g[0]} {g[1]}': len(d['fs']) for g, d in G.items()}, r_VG=r_vg, p1=p1,
                  r_HV=pooled_r(G, 'H', 'V'), r_HG=pooled_r(G, 'H', 'J'), p3=p3(S, G), one_dim=one_dim(G),
                  herbal1=pooled_r({g: d for g, d in G.items() if g == ('1', 'herbal')}, 'V', 'J') if ('1', 'herbal') in G else None)
    say(f"{s}: groups {RES[s]['groups']}")
say('')
say(f"{'text':14} {'P1 r VOC-GLY':>12} {'p':>7} {'r HAB-VOC':>9} {'r HAB-GLY':>9} {'herbal h1':>9}   {'P3 nb-other':>11} {'p':>6} {'n nb/oth':>9}   {'1-D share':>9}")
for s, r in RES.items():
    q = r['p3']
    say(f"{s:14} {r['r_VG']:12.3f} {r['p1']:7.4f} {r['r_HV']:9.3f} {r['r_HG']:9.3f} {r['herbal1'] if r['herbal1'] is None else round(r['herbal1'], 3):>9}   "
        f"{q['diff']:+11.3f} {q['p']:6.3f} {q['n_nb']:>4}/{q['n_other']:<4}   {r['one_dim']:9.3f}")
sc = [r for s, r in RES.items() if s != 'real']; real = RES['real']
say('')
say(f"P1 coherence (real p < 0.05, Holm over 3): p = {real['p1']:.4f}")
say(f"P2 real r {real['r_VG']:.3f} above every skribe seed ({', '.join(f'{r['r_VG']:.3f}' for r in sc)}): {all(real['r_VG'] > r['r_VG'] for r in sc)}")
say(f"P3 neighbours in the nesting: real diff {real['p3']['diff']:+.3f}, p {real['p3']['p']:.3f}; skribe diffs {', '.join(f'{r['p3']['diff']:+.3f}' for r in sc)}; "
    f"real above all: {all(real['p3']['diff'] > r['p3']['diff'] for r in sc)}")
ps = sorted([('P1', real['p1']), ('P2', 1 / 32 if all(real['r_VG'] > r['r_VG'] for r in sc) else 1.0), ('P3', real['p3']['p'])], key=lambda x: x[1])
holm = {}; run = 0
for i, (k, p) in enumerate(ps):
    run = max(run, min(1, p * (3 - i))); holm[k] = run
say('Holm-adjusted: ' + ', '.join(f'{k} {v:.3f}' for k, v in sorted(holm.items())))
open(os.path.join(HERE, 'sheet_chain.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
json.dump(RES, open(os.path.join(HERE, 'sheet_chain.json'), 'w', encoding='utf-8'), indent=1)
