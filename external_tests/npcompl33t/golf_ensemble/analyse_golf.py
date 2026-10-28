# Consensus orders from the fits of run_golf.py, computed as his path-v2 default (path 1): converged fits with 1a before 1b, the best
# fit per resampling replicate, pairwise "after" frequencies over jointly retained rows, the two penalties weighted equally.
# Compared: his published path-v2 bifolio order, our real text, three skribe seeds (no order between sheets by construction).
import os, json, csv, sys, itertools
from pathlib import Path
import numpy as np
from scipy.stats import kendalltau, spearmanr
HERE = Path(__file__).resolve().parent
OLD = Path(os.environ.get('NPC_WORK', r'C:\Temp\npc_work')) / 'solve/botanical_enrichment/team_golf/golf_published_stability_20261016'
PUB = Path(os.environ.get('NPC_CLONE', r'C:\Temp\npc_clone\repo')) / 'path-v2/bifolia.csv'   # his published path-v2 order
TEXTS = [t for t in ('real', 'skribe_s1', 'skribe_s2', 'skribe_s3') if (HERE / f'fits_{t}.json').exists()]
TOL = 1e-7
OUT = []


def say(s=''): OUT.append(s); print(s, flush=True)


def consensus(F, cohort):
    fr = []
    for lam in ('010', '050'):
        key = f'{cohort}_point_l{lam}'; d = json.loads((OLD / f'ensemble_{key}.json').read_text())['design']
        masks = np.array(d['masks'], bool); runs = F['runs'][key]
        ok = [r for r in runs if r['converged'] and r['group_readout_all']['contrasts']['1a|1b']['sign'] == -1]
        best = [min([r for r in ok if r['replicate'] == q], key=lambda r: (r['objective'], r['start_index'])) for q in sorted({r['replicate'] for r in ok})]
        n = masks.shape[1]; after = np.zeros((n, n)); ties = np.zeros((n, n)); joint = np.zeros((n, n))
        for r in best:
            keep = masks[r['replicate']]; both = keep[:, None] & keep[None, :]; t = np.asarray(r['positions']); dl = t[:, None] - t[None, :]
            after += both & (dl > TOL); ties += both & (np.abs(dl) <= TOL); joint += both
        fr.append((after + .5 * ties) / joint)
        groups = [m['group'] for m in d['meta']]
    P = np.mean(fr, axis=0); score = (P.sum(1) - .5) / (len(P) - 1)
    return score, P, len(best), groups


def contrasts(F):
    out = {}
    for c in ('3a|3b', '4a|4c'):
        s = [r['group_readout_all']['contrasts'][c]['sign'] for key in F['runs'] if key.startswith('pool50_point') for r in F['runs'][key] if r['converged']]
        out[c] = np.mean(np.array(s) < 0)
    return out


pub = {r['id']: (float(r['path_1_score']), r['golf_2_1']) for r in csv.DictReader(open(PUB, encoding='utf-8'))}
R = {}
for t in TEXTS:
    F = json.loads((HERE / f'fits_{t}.json').read_text()); ids = F['meta']['pool50_point_l010']
    s, P, nb, groups = consensus(F, 'pool50'); R[t] = dict(ids=ids, score=dict(zip(ids, s)), P=P, nbest=nb, groups=groups, contr=contrasts(F))
ids = R[TEXTS[0]]['ids']
say("npcompl33t's chronology ensemble (path-v2 default consensus) on our real text and on the skribe. 50 resampling replicates,")
say('both penalties, Zattera units, the published Golf 2.1 labels, masks and anchor orders. Bifolio pools (50).')
say('')
say('Agreement of the 50 bifolio scores with his published order (Spearman):')
for t in TEXTS: say('  %-10s %+.2f' % (t, spearmanr([pub[i][0] for i in ids], [R[t]['score'][i] for i in ids]).statistic))
say('')
say('Share of fits with 3a before 3b and 4a before 4c (pool cohort, converged fits):')
for t in TEXTS: say('  %-10s 3a<3b %.2f   4a<4c %.2f' % (t, R[t]['contr']['3a|3b'], R[t]['contr']['4a|4c']))
for q, name in (('M', 'Q13'), ('T', 'Q20')):
    bl = [i for i in ids if i.startswith(q + ':')]; ix = [ids.index(i) for i in bl]
    say(''); say(f'-- {name}: order of the bifolia (earliest first), Golf label in brackets --')
    order = lambda sc: sorted(bl, key=lambda i: sc[i])
    lab = lambda o: ' '.join('%s[%s]' % (i.split(':')[1], pub[i][1]) for i in o)
    say('  %-10s %s' % ('published', lab(order({i: pub[i][0] for i in bl}))))
    for t in TEXTS:
        sc = R[t]['score']; o = order(sc); P = R[t]['P'][np.ix_(ix, ix)]
        sure = np.mean([abs(2 * P[a, b] - 1) for a, b in itertools.combinations(range(len(ix)), 2)])
        tau = kendalltau([pub[i][0] for i in bl], [sc[i] for i in bl]).statistic
        say('  %-10s %s   tau vs published %+.2f   decisiveness %.2f' % (t, lab(o), tau, sure))
    sk = [t for t in TEXTS if t.startswith('skribe')]
    for a, b in itertools.combinations(sk, 2):
        say('  %s vs %s: tau %+.2f' % (a, b, kendalltau([R[a]['score'][i] for i in bl], [R[b]['score'][i] for i in bl]).statistic))
say('')
say('Decisiveness: mean |2p - 1| over the pairs of bifolia in the quire, p = share of selected fits putting one after the other (1 = always the same order).')
(HERE / 'golf_results.txt').write_text('\n'.join(OUT) + '\n', encoding='utf-8')
