# npcompl33t's chronology ensemble (eo777/voynich-clusters, chronology-stability, 16/10/2026) run on another text, the way his own
# RF1b study swaps the transcription: same 207 paragraph pages, same 50 bifolio pools, same Golf 2.1 labels, masks, penalties and the
# same eight anchor orders through the group centres; only the transition counts (and so the distances and the MDS) change.
# Zattera glyph units, word + joined-line transitions, weighted Jensen-Shannon, classical MDS: his code, imported unchanged.
#   python run_golf.py replay                      # replays his first saved fit from his frozen data (checks the environment)
#   python run_golf.py run <text> [reps] [workers] # text: real | skribe_s1 | skribe_s2 | skribe_s3 (from texts.json)
import os
for k in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']: os.environ[k] = '1'
import sys, json, copy, time, hashlib
from pathlib import Path
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
ROOT = Path(os.environ.get('NPC_WORK', r'C:\Temp\npc_work'))   # a COPY of his chronology-stability/replication (his scripts write beside themselves)
TEAM = ROOT / 'solve/botanical_enrichment/team_golf'; OLD = TEAM / 'golf_published_stability_20261016'
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(OLD / '_deps')); sys.path.insert(1, str(OLD)); sys.path.insert(2, str(ROOT))
import numpy as np
from threadpoolctl import threadpool_limits
import ensemble as engine
from voynich_toolkit.glyph_units import units
core = engine.core
DATA = core.COMMON.DATA
repro = core.module('repro_js', DATA / 'reproduce.py')
ALPHABET = [r['unit'] for r in repro.rows('alphabet.csv')]
IX = {g: i for i, g in enumerate(ALPHABET)}


def glyphs(w): return tuple('other' if u.rare else u.text for u in units(w, 'zattera'))


def counts(lines):
    a = {m: np.zeros((len(ALPHABET), len(ALPHABET))) for m in ('word', 'line')}
    for ws in lines:
        for w in ws:
            s = glyphs(w)
            for g, h in zip(('^',) + s, s + ('$',)): a['word'][IX[g], IX[h]] += 1
        s = glyphs(''.join(ws))
        if s:
            for g, h in zip(('^',) + s, s + ('$',)): a['line'][IX[g], IX[h]] += 1
    return a


def contexts_for(text):
    P = json.load(open(HERE / 'texts.json', encoding='utf-8'))[text]
    index = json.loads((OLD / 'ensemble_index.json').read_text())
    designs = {n.removeprefix('ensemble_').removesuffix('.json'): json.loads((OLD / n).read_text())['design'] for n in index['setting_files']}
    pm = designs['pool50_point_l010']['meta']; meta = designs['paragraph207_point_l010']['meta']
    blocks = np.array(designs['paragraph207_point_l010']['blocks'])
    C = [counts(P[m['id']]) for m in meta]
    geo = {}
    for prefix, rows in (('page', C), ('pool', [{k: sum(C[i][k] for i in np.flatnonzero(blocks == p['bifolium'])) for k in ('word', 'line')} for p in pm])):
        d = sum(repro.weighted_js(np.array([r[k] for r in rows]))[0] for k in ('word', 'line')) / 2
        geo[prefix] = core.COMMON.embed(d)[0]
    out = {}
    for key, d in designs.items():
        prefix = 'page' if d['cohort'] == 'paragraph207' else 'pool'; x = geo[prefix]; m_ = d['meta']
        w = np.array(d['original_weights']); labels = np.array([m['group'] for m in m_])
        centers = {g: w[labels == g] @ x[labels == g] / w[labels == g].sum() for g in core.ORDER}
        starts = []
        for old in d['starts']:
            s = {k: v for k, v in old.items() if k not in ('initial_sha256', 'prior_objective')}
            s['initial'] = np.array([centers[g] for g in s['anchor_order']]); starts.append(s)
        out[key] = dict(key=key, cohort=d['cohort'], sampler=d['sampler'], penalty=d['penalty'], meta=m_, x=x, weights=w,
                        blocks=np.array(d['blocks']), labels=labels, starts=starts, masks=np.array(d['masks'], dtype=bool),
                        mask_seed=d['mask_seed'], mask_unit=d['mask_unit'],
                        geometry_sha256=hashlib.sha256(x.tobytes()).hexdigest(), distance_sha256='')
    return out


def init_worker(text):
    threadpool_limits(limits=1); engine._STATE = contexts_for(text)


def fit(task): return engine.fit_one(task)


def replay():
    with threadpool_limits(limits=1):
        original = core.load_data(); d = json.loads((OLD / 'ensemble_paragraph207_point_l010.json').read_text())
        c = contexts_for('real')['paragraph207_point_l010']; x = core.COMMON.embed(original['ds']['combined'])[0]
        c['x'] = x; w = c['weights']; labels = c['labels']
        centers = {g: w[labels == g] @ x[labels == g] / w[labels == g].sum() for g in core.ORDER}
        for s in c['starts']: s['initial'] = np.array([centers[g] for g in s['anchor_order']])
        engine._STATE = {'replay': c}; _, got = engine.fit_one(('replay', 0, 0)); saved = d['runs'][0]
        print({k: float(abs(np.asarray(got[k]) - np.asarray(saved[k])).max()) for k in ['positions', 'objective', 'node_mse']}, 'seconds %.1f' % got['seconds'])


def run(text, reps, workers):
    ctx = contexts_for(text); out = HERE / f'fits_{text}.json'
    tasks = [(key, rep, s) for rep in range(reps) for key in ctx for s in range(8)]
    R = {key: [] for key in ctx}; began = time.time()
    with ProcessPoolExecutor(max_workers=workers, initializer=init_worker, initargs=(text,)) as pool:
        for n, f in enumerate(as_completed([pool.submit(fit, t) for t in tasks]), 1):
            key, r = f.result()
            R[key].append({k: r[k] for k in ('replicate', 'start_index', 'start_id', 'positions', 'objective', 'converged', 'group_readout_all')})
            if n % 200 == 0: print(f'{text}: {n}/{len(tasks)} fits, {time.time() - began:.0f} s', flush=True)
    meta = {key: [m['id'] for m in c['meta']] for key, c in ctx.items()}
    out.write_text(json.dumps(core.jsonable(dict(text=text, reps=reps, meta=meta, runs=R))), encoding='utf-8')
    print(f'{text}: done, {len(tasks)} fits in {time.time() - began:.0f} s', flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'replay': replay()
    else: run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 100, int(sys.argv[4]) if len(sys.argv) > 4 else 7)
