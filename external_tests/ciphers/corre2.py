# Segona ronda: el xifrat «per model» (stego) amb i sense maqueta, en mostra sencera i a pàgines no vistes,
# i la mesura d'ordre dels mots (informació entre mots seguits, controls/control.py) per a tots els textos.
#   py -3 corre2.py     -> resultats2.json + resultats2_taula.txt ; textos xifrats a sortides/
import os, sys, json, time
import lab, ciphers, stego
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(lab.NOV, 'escriba', 'controls'))
import control
OUT = os.path.join(HERE, 'sortides'); os.makedirs(OUT, exist_ok=True)
V = lab.voynich_lines(); wv = lab.words(V); N = len(wv); lat = lab.words(lab.latin_lines())
tr, te = lab.split_pages(V)

texts = {}
texts['Voynich (ZL3b, escriba)'] = V
texts['Llatí (De docta)'] = lab.pour(V, lat[:N])
texts['PM-Cipher (notebook)'] = lab.pour(V, ciphers.pm_cipher(lat[:N], wv)[0])
texts['Tipus Naibbe (1-2 lletres/mot)'] = lab.pour(V, ciphers.naibbe_like(lat, wv, N)[0])
texts['Nomenclàtor (rang)'] = lab.pour(V, ciphers.nomenclator(lat[:N], wv)[0])
texts['Nomenclàtor + homòfons + contacte'] = lab.pour(V, ciphers.nomenclator_homophones(lat[:N], wv, contact=True)[0])
info = {}
for name, kw in [('Model: vocabulari de mà + còpia + contacte', dict(fn='plain')),
                 ('Model amb maqueta (sense còpia)', dict(fn='layout', lam=0.0, aa=0.0)),
                 ('Model amb maqueta + còpia + contacte', dict(fn='layout'))]:
    t = time.time(); fn = kw.pop('fn')
    out, inf = (stego.encode if fn == 'plain' else stego.encode_layout)(V, lat, **kw)
    texts[name] = out; info[name] = inf; print(f'{name}: {inf} ({time.time() - t:.0f}s)', flush=True)

res = {}
ref = lab.battery(V)
for name, L in texts.items():
    t = time.time(); b = lab.battery(L); n, tot, ok = lab.score(ref, b)
    res[name] = dict(battery=b, score=n, ordre=control.word_order(L), wordreset=lab.curve_wordreset(lab.words(L), 8),
                     info=info.get(name, {}))
    with open(os.path.join(OUT, name.replace(' ', '_').replace(':', '').replace('(', '').replace(')', '').replace('/', '-') + '.txt'), 'w', encoding='utf-8') as f:
        for l in L: f.write(f"<{l['locus']}> " + ' '.join(l['ws']) + '\n')
    print(f'{name:45} {n}/{tot}  ordre {res[name]["ordre"]:.3f}  ({time.time() - t:.0f}s)', flush=True)

# a pàgines no vistes (com el holdout de l'escriba): sostre = senars reals contra parells reals
ho = {}
ref_te = lab.battery(te)
ho['sostre: senars reals vs parells reals'] = lab.score(ref_te, lab.battery(tr))[0]
m_out, inf = stego.encode_layout(tr, lat, layout=te)
ho['Model amb maqueta + còpia + contacte (après dels senars)'] = lab.score(ref_te, lab.battery(m_out))[0]; info['holdout model'] = inf
ho['Nomenclàtor + homòfons + contacte (après dels senars)'] = lab.score(ref_te, lab.battery(lab.pour(te, ciphers.nomenclator_homophones(lat, lab.words(tr), contact=True)[0])))[0]
print('pàgines no vistes:', ho)

# capacitat: bits per mot del Voynich real sota cada model (pàgines no vistes)
cap = {'Model (mà + còpia + contacte)': stego.logloss(tr, te)}
print('capacitat:', cap)
json.dump(dict(res=res, holdout=ho, capacity=cap, info=info), open(os.path.join(HERE, 'resultats2.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, default=float)
