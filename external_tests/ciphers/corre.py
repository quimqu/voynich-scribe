# Corre totes les famílies de xifrat sobre De docta ignorantia i les compara amb el Voynich (escriba: ZL3b net).
#   py -3 corre.py            -> resultats.json + resultats_taula.txt
import os, json, time
import lab, ciphers
HERE = os.path.dirname(os.path.abspath(__file__))
V = lab.voynich_lines(); wv = lab.words(V); N = len(wv)
La = lab.latin_lines(); wl = lab.words(La)
lat = wl[:N]

runs = {}
def add(name, ws, side, info, layout=True):
    L = lab.pour(V, ws) if layout else None
    t = time.time()
    r = dict(info={k: v for k, v in info.items() if k != 'joint'}, side_bits_per_word=side,
             wordreset=lab.curve_wordreset(ws[:N], 10))
    if L is not None:
        r['heldout'] = lab.curve_heldout(L, 8); r['bits_per_word'] = lab.bits_per_word(L)
        r['word_unigram_bits'] = lab.word_unigram_heldout(L); r['battery'] = lab.battery(L)
    if 'joint' in info: r['joint_wordreset'] = lab.curve_wordreset(info['joint'][:N], 10)
    runs[name] = r; print(f'{name:28} fet ({time.time() - t:.0f}s)', flush=True)

add('Voynich (ZL3b, escriba)', wv, 0, {})
add('Llatí (De docta)', lat, 0, {}, layout=True)
cw, side, info = ciphers.pm_cipher(lat, wv); add('PM-Cipher (notebook)', cw, side, info)
cw, side, info = ciphers.digit_homophonic(lat); add('Lletra+dígit (juny 2025)', cw, side, info)
cw, side, info = ciphers.naibbe_like(lat, wv, N); add('Tipus Naibbe (1-2 lletres/mot)', cw, side, info)
cw, side, info = ciphers.nomenclator(lat, wv); add('Nomenclàtor (rang)', cw, side, info)
cw, side, info = ciphers.nomenclator_homophones(lat, wv, contact=False); add('Nomenclàtor + homòfons', cw, side, info)
cw, side, info = ciphers.nomenclator_homophones(lat, wv, contact=True); add('Nomenclàtor + homòfons + contacte', cw, side, info)

json.dump(runs, open(os.path.join(HERE, 'resultats.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
ref = runs['Voynich (ZL3b, escriba)']['battery']
with open(os.path.join(HERE, 'resultats_taula.txt'), 'w', encoding='utf-8') as f:
    def P(s=''): print(s); f.write(s + '\n')
    P('corba word reset (notebook), n=1..8'); [P(f'  {k:34} ' + ' '.join(f'{x:5.2f}' for x in r['wordreset'][:8])) for k, r in runs.items()]
    P('corba amb espais, pàgines no vistes (WB), k=1..8'); [P(f'  {k:34} ' + ' '.join(f'{x:5.2f}' for x in r['heldout'])) for k, r in runs.items() if 'heldout' in r]
    P('informació'); [P(f'  {k:34} bits/mot (car.) {r.get("bits_per_word", float("nan")):6.2f}  mot-unigrama {r.get("word_unigram_bits", float("nan")):6.2f}  nota lateral {r["side_bits_per_word"]:5.2f}') for k, r in runs.items()]
    P('bateria de 76 mesures (|gen/real-1|<0,25)')
    for k, r in runs.items():
        if 'battery' in r: n, t, ok = lab.score(ref, r['battery']); P(f'  {k:34} {n}/{t}')
    for k, r in runs.items():
        if 'joint_wordreset' in r: P(f'{k}: flux conjunt glif+residu ' + ' '.join(f'{x:5.2f}' for x in r['joint_wordreset'][:8]))
    P('info'); [P(f'  {k:34} {r["info"]}') for k, r in runs.items()]
