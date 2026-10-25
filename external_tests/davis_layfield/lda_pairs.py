# The within-bifolium pairs with LDA (Latent Dirichlet Allocation), the topic model of the author's 2025 topic studies
# (voynich.ninja thread 4834). Exploratory: the LSA pattern was already seen. Documents of 40 words (word counts, not TF-IDF, as
# LDA expects); a page is folded in as its topic proportions; similarity = cosine and 1 - Hellinger distance. Several numbers of
# topics (5 and 9 as in the 2025 studies, 20, 50), three random starts each, and a variant without the 15 most frequent words
# (the 2025 list). Inner minus outer face, the six pairs, P1 (pairs written one after the other > outer) and P2 (inner > leaves).
#   PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/lda_pairs.py
# Input: scribe/manuscript_out/{real,scribe_seed*}.txt. Output: here, lda_pairs.{txt,json}
import os, glob, json, warnings
import numpy as np
from collections import Counter
from scipy.stats import wilcoxon
from sklearn.decomposition import LatentDirichletAllocation
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'__file__': os.path.join(HERE, 'sheet_order.py')}
exec(open(os.path.join(HERE, 'sheet_order.py'), encoding='utf-8').read().split('srcs = ')[0], ns)   # read, bifolia, PAIRS, NOV
read, bifolia, PAIRS, NOV = ns['read'], ns['bifolia'], ns['PAIRS'], ns['NOV']
CHUNK, MINREM = 40, 20
STOP2025 = ['aiin', 'ar', 'chedy', 'chey', 'chol', 'daiin', 'dar', 'dy', 'ol', 'or', 'qokeey', 's', 'shedy', 'shey', 'y']
CONFIGS = [(5, False), (9, False), (20, False), (50, False), (9, True)]
SEEDS = (0, 1, 2)
OUT = []


def say(s=''):
    OUT.append(s); print(s, flush=True)


def page_vectors(P, k, stop, seed):
    pages = {pg: [w for l in d['lines'] for w in l] for pg, d in P.items()}
    if stop:
        pages = {pg: [w for w in ws if w not in STOP2025] for pg, ws in pages.items()}
    docs = [ws[i:i + CHUNK] for ws in pages.values() for i in range(0, len(ws), CHUNK) if len(ws[i:i + CHUNK]) >= MINREM]
    df = Counter()
    for c in docs:
        df.update(set(c))
    terms = sorted(t for t in df if df[t] >= 2); ix = {t: i for i, t in enumerate(terms)}
    def counts(ws):
        v = np.zeros(len(terms))
        for w, n in Counter(ws).items():
            if w in ix:
                v[ix[w]] = n
        return v
    X = np.array([counts(c) for c in docs])
    lda = LatentDirichletAllocation(n_components=k, learning_method='batch', max_iter=60, random_state=seed).fit(X)
    names = list(pages); T = lda.transform(np.array([counts(pages[p]) for p in names]))
    return dict(zip(names, T))


def sims(a, b):
    c = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
    h = float(np.sqrt(0.5 * np.sum((np.sqrt(a) - np.sqrt(b)) ** 2)))
    return c, 1 - h


def analyse(P, B, k, stop, seed):
    V = page_vectors(P, k, stop, seed); rows = []
    for q, a, b in B:
        pg = {'ar': a + 'r', 'av': a + 'v', 'br': b + 'r', 'bv': b + 'v'}
        rows.append(dict(hand=P[a + 'r']['H'], pairs={nm: sims(V[pg[x]], V[pg[y]]) for nm, (x, y) in PAIRS.items()}))
    return rows


def contrasts(rows, j):
    p = lambda r, k: r['pairs'][k][j]
    inner_outer = [p(r, 'inner a-v|b-r') - p(r, 'outer b-v|a-r') for r in rows]
    P1 = [np.mean([p(r, 'leaf A a-r|a-v'), p(r, 'inner a-v|b-r'), p(r, 'leaf B b-r|b-v')]) - p(r, 'outer b-v|a-r') for r in rows]
    P2 = [p(r, 'inner a-v|b-r') - 0.5 * (p(r, 'leaf A a-r|a-v') + p(r, 'leaf B b-r|b-v')) for r in rows]
    return dict(inner_outer=inner_outer, P1=P1, P2=P2)


def one(x):
    x = np.asarray(x); return float(wilcoxon(x, alternative='greater').pvalue) if np.any(x != 0) else 1.0


srcs = [('real', os.path.join(NOV, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(NOV, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
DATA = {s: (lambda P: (P, bifolia(P)))(read(p)) for s, p in srcs}
say('Within-bifolium pairs with LDA (exploratory). 37 bifolia; 40-word documents, word counts; page = topic proportions.')
say('Each cell: mean over three random starts of LDA; one-sided Wilcoxon p (median of the three starts). Similarity: cosine | 1 - Hellinger.')
RES = {}
for k, stop in CONFIGS:
    lab = f'k={k}' + (' without the 15 frequent words (2025 list)' if stop else '')
    runs = {s: [analyse(P, B, k, stop, sd) for sd in SEEDS] for s, (P, B) in DATA.items()}
    RES[lab] = runs
    say(''); say(f'== LDA {lab}')
    say('six pairs (real, cosine | Hellinger; scribe mean of 5 seeds, cosine):')
    for nm in PAIRS:
        rc = np.mean([np.mean([r['pairs'][nm][0] for r in rr]) for rr in runs['real']]); rh = np.mean([np.mean([r['pairs'][nm][1] for r in rr]) for rr in runs['real']])
        sc = np.mean([np.mean([r['pairs'][nm][0] for r in rr]) for s in runs if s != 'real' for rr in runs[s]])
        say(f'  {nm:16} {rc:.3f} | {rh:.3f}   scribe {sc:.3f}')
    for j, sim in ((0, 'cosine'), (1, 'Hellinger')):
        for grp in ('all', '2', '1'):
            cells = []
            for name in ('inner_outer', 'P1', 'P2'):
                vals = [contrasts([r for r in rr if grp == 'all' or r['hand'] == grp], j)[name] for rr in runs['real']]
                scv = [contrasts([r for r in rr if grp == 'all' or r['hand'] == grp], j)[name] for s in runs if s != 'real' for rr in runs[s]]
                cells.append(f"{name} {np.mean([np.mean(v) for v in vals]):+.3f} (p {np.median([one(v) for v in vals]):.3f}) / scribe {np.mean([np.mean(v) for v in scv]):+.3f} (p {min(one(v) for v in scv):.2f}-{max(one(v) for v in scv):.2f})")
            say(f'  {sim:9} {"all" if grp == "all" else "hand " + grp:6} ' + ' | '.join(cells))
open(os.path.join(HERE, 'lda_pairs.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
json.dump({lab: {s: [[r['pairs'] for r in rr] for rr in v] for s, v in runs.items()} for lab, runs in RES.items()},
          open(os.path.join(HERE, 'lda_pairs.json'), 'w', encoding='utf-8'), indent=1)
