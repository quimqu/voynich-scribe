# Q20 bifolia in the order of npcompl33t's axis: simple word and glyph features, their Spearman with the sheet score, and how much they
# vary between sheets in the real text against the skribe (mean over seeds 1-3 of the SD across its six Q20 sheets).
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import spearmanr
from common import *
from scribe import Escriba, L_ALL


def mattr(ws, w=100): return float(np.mean([len(set(ws[i:i + w])) / w for i in range(0, len(ws) - w + 1)])) if len(ws) >= w + 20 else np.nan


def feats(L):
    ws = [w for l in L for w in l['ws']]; n = len(ws); c = Counter(ws); gl = ''.join(ws)
    g = lambda f: 100 * sum(1 for w in ws if f(w)) / n
    return {'MATTR': mattr(ws), 'top-20 %': 100 * sum(v for _, v in c.most_common(20)) / n, 'hapax %': 100 * sum(1 for v in c.values() if v == 1) / n,
            'word len': np.mean([len(w) for w in ws]), 'words/line': n / len(L), 'qo- %': g(lambda w: w.startswith('qo')), 'with e %': g(lambda w: 'e' in w),
            'ee %': g(lambda w: 'ee' in w), '-dy %': g(lambda w: w.endswith('dy')), '-aiin %': g(lambda w: w.endswith('aiin')),
            '-ain %': g(lambda w: w.endswith('ain') and not w.endswith('aiin')), '-ol %': g(lambda w: w.endswith('ol')), '-al %': g(lambda w: w.endswith('al')),
            '-ar %': g(lambda w: w.endswith('ar')), '-y %': g(lambda w: w.endswith('y')), 'ch %': g(lambda w: 'ch' in w), 'sh %': g(lambda w: 'sh' in w),
            'k/(k+t)': gl.count('k') / max(1, gl.count('k') + gl.count('t')), 'o- %': g(lambda w: w.startswith('o')), 'l- %': g(lambda w: w.startswith('l')),
            'd- %': g(lambda w: w.startswith('d')), 'r- %': g(lambda w: w.startswith('r')), 's- %': g(lambda w: w.startswith('s')),
            'p/f %': g(lambda w: 'p' in w or 'f' in w)}


def by_sheet(L, mt):
    D = defaultdict(list)
    for l, m in zip(L, mt):
        b = meta.get(m['page'], ('',))[0]
        if b.startswith('T:'): D[b].append(l)
    return D


sc = {b: np.mean([score[p] for p in score if bif[p] == b]) for b in sheets}
FR = {b: feats(L) for b, L in by_sheet(real, real).items()}
FG = []
for s in (1, 2, 3):
    D = by_sheet(Escriba().write(seed=s), L_ALL); FG.append({b: feats(D[b]) for b in sheets})
print('Q20 bifolia ordered by npcompl33t\'s axis (mean page score of the real text):')
print('%-10s' % 'feature' + ''.join('%9s' % b[2:] for b in sheets) + '   rho(score)  SD real  SD skribe')
for k in FR[sheets[0]]:
    v = [FR[b][k] for b in sheets]
    print('%-10s' % k + ''.join('%9.2f' % x for x in v) + '   %+.2f      %7.2f  %7.2f' % (spearmanr([sc[b] for b in sheets], v).statistic, np.std(v),
                                                                                     np.mean([np.std([F[b][k] for b in sheets]) for F in FG])))
print('scores: ' + '  '.join('%s %.3f' % (b[2:], sc[b]) for b in sheets))
