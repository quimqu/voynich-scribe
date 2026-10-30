# Agrega les llavors del xifrat de dues capes (xe/*.json): mitjana de les mesures, comparació amb el real (bateria de 88 de
# voynich-scribe), i quines mesures perd el xifrat respecte de l'skribe sol.   py -3 agrega.py -> xifrat_escriba.json + taula
import os, sys, json, glob
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, (os.environ.get('SCRIBE') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scribe')))
os.chdir((os.environ.get('SCRIBE') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scribe')))
import measures as M
from scribe import L_ALL, folio_num
os.chdir(HERE)
even = [l for l in L_ALL if folio_num(l['page']) % 2 == 0]; odd = [l for l in L_ALL if folio_num(l['page']) % 2 == 1]
REF = {'tots': M.evaluate(L_ALL, seed=1), 'senars': M.evaluate(even, seed=1)}
CEIL = sum(M.compare(REF['senars'], M.evaluate(odd, seed=1)).values())
NAMES = {'skribe': 'skribe (sense missatge)', '1': 'xifrat: 1 lletra per mot', '12': 'xifrat: 1-2 lletres per mot'}
out = {'sostre_senars': int(CEIL)}; lines = []
for split in ('tots', 'senars'):
    base = None
    for var in ('skribe', '1', '12'):
        fs = sorted(glob.glob(os.path.join(HERE, 'xe', f'{split}_{var}_*.json')))
        if not fs: continue
        J = [json.load(open(f, encoding='utf-8')) for f in fs]
        G = {k: float(np.mean([j['R'][k] for j in J])) for k in J[0]['R']}
        ok = M.compare(REF[split], G); sc = int(sum(ok.values()))
        inf = {k: float(np.mean([j['info'][k] for j in J if j['info'][k] is not None])) if any(j['info'][k] is not None for j in J) else None
               for k in J[0]['info']}
        lost = [k for k in ok if not ok[k] and base and base[k]]; gained = [k for k in ok if ok[k] and base and not base[k]]
        if var == 'skribe': base = ok
        out[f'{split} | {NAMES[var]}'] = dict(score=sc, n=len(ok), llavors=len(J), info=inf, perd=lost, guanya=gained,
                                             valors={k: (REF[split][k], G[k]) for k in lost})
        lines.append(f"{split:7} {NAMES[var]:30} {sc}/{len(ok)}  ({len(J)} llavors)  ordre {inf['ordre']:.3f}  intents {inf['intents']:.0f}  "
                     f"reserva {inf['reserva']:.0f}  bits/mot {inf['bits_per_mot']:.2f}  mots llatins {inf['mots_llatins']:.0f}  desxifrat {inf['desxifrat_ok']}")
        for k in lost: lines.append(f"          perd: {k}  real {REF[split][k]:.3f}  xifrat {G[k]:.3f}")
lines.append(f'sostre (senars reals contra parells reals): {CEIL}/88')
open(os.path.join(HERE, 'xifrat_escriba_taula.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n'); print('\n'.join(lines))
json.dump(out, open(os.path.join(HERE, 'xifrat_escriba.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
