# L'ordre dels mots (informació entre mots seguits de la mateixa línia, controls/control.py) al real, a l'skribe i al xifrat:
# soroll entre meitats i llavors, i quanta en queda sense les repeticions (parells de mots iguals o a un glif).
import os, sys, json, random, math
from collections import Counter
import numpy as np
sys.argv = ['x', 'ordre']
import xifrat_escriba as X, xifrat_extra as E, lab
SC = X.SC
sys.path.insert(0, os.path.join(lab.NOV, 'escriba', 'controls')); import control
import mesures

def order(L, drop=None, K=200, reps=5):
    top = set(w for w, _ in Counter(w for l in L for w in l['ws']).most_common(K)); m = lambda w: w if w in top else '*'
    keep = (lambda a, b: True) if drop is None else (lambda a, b: not drop(a, b))
    real = control.MI([(m(a), m(b)) for l in L for a, b in zip(l['ws'], l['ws'][1:]) if keep(a, b)])
    rng = random.Random(0); base = []
    for _ in range(reps):
        pp = []
        for l in L:
            ws = l['ws'][:]; rng.shuffle(ws); pp += [(m(a), m(b)) for a, b in zip(ws, ws[1:]) if keep(a, b)]
        base.append(control.MI(pp))
    return real - float(np.mean(base))

same = lambda a, b: a == b
near = lambda a, b: mesures.lev(mesures.gl(a), mesures.gl(b)) <= 1
def row(name, L):
    r = dict(tot=order(L), sense_iguals=order(L, same), sense_ed1=order(L, near)); print(f'{name:40}', {k: round(v, 3) for k, v in r.items()}, flush=True); return r

R = {}
real = SC.L_ALL; odd = [l for l in real if SC.folio_num(l['page']) % 2]; even = [l for l in real if not SC.folio_num(l['page']) % 2]
R['real'] = row('real', real); R['real senars'] = row('real senars', odd); R['real parells'] = row('real parells', even)
code, us, text = X.setup(0.0)
f = Counter(text); rnd = ''.join(random.Random(9).choices(list(f), weights=list(f.values()), k=len(text)))
code_r, us_r = E.setup_text(rnd)
for s in (1, 2, 3):
    R[f'skribe {s}'] = row(f'skribe {s}', SC.Escriba().write(seed=s))
    R[f'xifrat llatí {s}'] = row(f'xifrat llatí {s}', X.Cipher(code, us).write(seed=s))
    R[f'xifrat lletres a l\'atzar {s}'] = row(f'xifrat lletres a l\'atzar {s}', X.Cipher(code_r, us_r).write(seed=s))
json.dump(R, open(os.path.join(X.HERE, 'ordre.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
