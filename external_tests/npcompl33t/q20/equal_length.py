# Is the Q20 axis page length? Every page cut to the length of the shortest one (a random stretch of consecutive words, 200 cuts).
import random
from scipy.stats import spearmanr
from common import *
nw = {p: sum(len(l['ws']) for l in lines[p]) for p in pages}; N = min(nw.values())
print('words per page: %d to %d; Spearman of page length with the page score %+.2f' % (N, max(nw.values()), spearmanr([score[p] for p in pages], [nw[p] for p in pages]).statistic))


def mattr(ws, w=100): return float(np.mean([len(set(ws[i:i + w])) / w for i in range(0, len(ws) - w + 1)]))


res = defaultdict(list); rng = random.Random(1)
for rep in range(200):
    v = defaultdict(dict)
    for p in pages:
        ws = [w for l in lines[p] for w in l['ws']]; i = rng.randrange(len(ws) - N + 1); cut = ws[i:i + N]; c = Counter(cut)
        v['Bio (Q13)-ness'][p] = pscore(cut, LO['Bio (Q13)-ness (vs other B)']); v['Herbal B-ness'][p] = pscore(cut, LO['Herbal B-ness (vs other B)'])
        v['Q20 axis (LOSO)'][p] = pscore(cut, LOSO[bif[p]]); v['MATTR'][p] = mattr(cut)
        v['top-20 %'][p] = 100 * sum(x for _, x in c.most_common(20)) / N; v['hapax %'][p] = 100 * sum(1 for x in c.values() if x == 1) / N
    for k, d in v.items(): res[k].append(spearmanr([score[p] for p in pages], [d[p] for p in pages]).statistic)
print('\nAll pages cut to %d consecutive words (200 random cuts). Spearman with the page score, median [5%% .. 95%%]:' % N)
for k, r in res.items(): print('  %-16s %+.2f  [%+.2f .. %+.2f]' % (k, np.median(r), np.percentile(r, 5), np.percentile(r, 95)))
