# What does npcompl33t's Q20 axis follow? Candidate variables per page, Spearman with the page score (real text): layout, hand and
# transcription marks (not vocabulary), physical position, vocabulary models trained OUTSIDE Q20, and where on the page the axis lives.
import re, pandas as pd
from scipy.stats import spearmanr
from common import *
Z = pd.read_csv(os.path.join(REPO, 'df_lines_ZL3b_strokes.csv'), dtype={'davis_hand': str})
Z = Z[(Z.is_label == 0) & (Z.locus_generic == 'P')]; ZT = Z[Z.page_tag.isin(score)]
rows = {}
for p in pages:
    L = lines[p]; z = ZT[ZT.page_tag == p]; ws = [w for l in L for w in l['ws']]; nw = len(ws); ng = sum(len(w) for w in ws)
    pars = z.paragraph_start.sum(); lo = LOSO[bif[p]]
    pos = defaultdict(list)
    for l in L:
        n = len(l['ws'])
        for i, w in enumerate(l['ws']):
            pos['first' if i == 0 else 'last' if i == n - 1 else 'medial'].append(w); pos['par line 1' if l['ps'] else 'par line 2+'].append(w)
    half = len(L) // 2; seen = []; local = far = 0
    for w in ws:
        if w in seen[-20:]: local += 1
        elif w in seen: far += 1
        seen.append(w)
    fnum = int(re.sub(r'\D', '', p))
    rows[p] = {
        'score': score[p],
        'lines': len(L), 'words': nw, 'paragraphs': pars, 'lines/paragraph': len(L) / max(pars, 1), 'words/line': nw / len(L), 'glyphs/word': ng / nw,
        'uncertain spaces /100w': 100 * z.n_comma_joins.sum() / nw, 'alt readings /100w': 100 * z.n_alt.sum() / nw,
        'weirdoes /1000g': 1000 * z.n_weirdo.sum() / ng, 'ligatures /100w': 100 * z.n_ligatures.sum() / nw, 'gaps /100w': 100 * z.n_gap.sum() / nw,
        'nesting (0=outer)': min(fnum - 103, 116 - fnum), 'verso': int(p.endswith('v')), 'second half of quire': int(fnum > 109),
        **{k: pscore(ws, v) for k, v in LO.items()},
        'axis: all words': pscore(ws, lo), 'axis: line-medial only': pscore(pos['medial'], lo), 'axis: line-first only': pscore(pos['first'], lo),
        'axis: line-last only': pscore(pos['last'], lo), 'axis: par line 1': pscore(pos['par line 1'], lo), 'axis: par lines 2+': pscore(pos['par line 2+'], lo),
        'axis: first half of page': pscore([w for l in L[:half] for w in l['ws']], lo), 'axis: second half of page': pscore([w for l in L[half:] for w in l['ws']], lo),
        'repeat within 20 words %': 100 * local / nw, 'repeat further back %': 100 * far / nw}
D = pd.DataFrame(rows).T.astype(float); sh = D.groupby(D.index.map(bif)).mean()
print('Q20, %d paragraph pages. Spearman with the page score, and with the sheet means (n = 6).' % len(D))
print('Vocabulary models are trained without any Q20 line; "axis" = Q20 words of the later half of the OTHER five sheets against the earlier half.\n')
for c in D.columns[1:]:
    r = spearmanr(D['score'], D[c], nan_policy='omit')
    print('  %-34s page rho %+.2f (p %.3f)   sheet rho %+.2f   range %.3g – %.3g' % (c, r.statistic, r.pvalue, spearmanr(sh['score'], sh[c]).statistic, D[c].min(), D[c].max()))
cols = ['score', 'lines', 'words', 'words/line', 'uncertain spaces /100w', 'Herbal B-ness (vs other B)', 'Bio (Q13)-ness (vs other B)',
        'axis: first half of page', 'axis: second half of page', 'repeat within 20 words %']
print('\nPer sheet (axis order):'); print(sh.loc[sheets, cols].round(3).to_string())
