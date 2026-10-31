# Una llengua amagada síl·laba a síl·laba (30/10/2026; preregistre a SILLABES_PREREG.md). El xifrat de dues capes de §7
# (xifrat_escriba.py: l'skribe sencer, cada mot acceptat només si cau a la classe de la unitat que toca) amb síl·labes com a
# unitats en lloc de lletres: 300 síl·labes pròpies (la final de mot marcada amb #), la resta lletra a lletra i # a part.
#   py -3 sillabes.py prova [la|it]                    -> roundtrip en unes pàgines
#   py -3 sillabes.py corre <tots|senars> <la|it> <llavor>  -> out/<tots|senars>_<la|it>_<llavor>.json (+ el text, _text.json)
#   py -3 sillabes.py agrega                           -> sillabes.txt, sillabes.json (C1-C4 del preregistre)
import os, sys, re, json, math, random, time, unicodedata
import numpy as np                      # el fa servir heldout() de classes.py
from collections import Counter, defaultdict   # defaultdict: el fa servir exchange() de classes.py (faltava: les passades «tots» petaven al final)
HERE = os.path.dirname(os.path.abspath(__file__)); XIF = os.path.dirname(HERE)
sys.path.insert(0, XIF)
import xifrat_escriba as X              # llegeix sys.argv[2] == 'senars' per aprendre només dels senars
SC = X.SC; M = SC.M
src = open(os.path.join(XIF, 'classes.py'), encoding='utf-8').read()
exec(src[src.index('def pairs('):src.index("if __name__")])          # pairs, mi, exchange, heldout de classes.py, tal qual
sys.path.insert(0, os.path.join(X.lab.NOV, 'escriba', 'controls')); import control
odd_ = lambda L: [l for l in L if SC.folio_num(l['page']) % 2]; even_ = lambda L: [l for l in L if not SC.folio_num(l['page']) % 2]
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
TOP = 300


def syl(w):
    """síl·labes per regla fixa: V-CV, VC-CV, VCC-CV; muta cum liquida (b c d g p t f + l r) juntes; qu consonant; ae au oe un nucli"""
    v = w.replace('qu', 'Q')
    nuc = [m.span() for m in re.finditer(r'ae|au|oe|[aeiouy]', v)]
    if len(nuc) < 2: return [w]
    cuts = []
    for (a1, b1), (a2, b2) in zip(nuc, nuc[1:]):
        cons = v[b1:a2]
        if len(cons) <= 1: cuts.append(b1)
        elif cons[-2] in 'bcdgptf' and cons[-1] in 'lr': cuts.append(a2 - 2)
        else: cuts.append(a2 - 1)
    out = []; s = 0
    for c in cuts: out.append(v[s:c]); s = c
    out.append(v[s:])
    return [x.replace('Q', 'qu') for x in out]


def plain_words(lang):
    if lang == 'la':
        return X.lab.words(X.lab.latin_lines())
    s = open(os.path.join(HERE, 'pinocchio_pg52484.txt'), encoding='utf-8').read()
    a = s.find('*** START'); b = s.find('*** END'); s = s[s.find('\n', a):b]
    s = unicodedata.normalize('NFD', s.lower()); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.findall(r'[a-z]+', s.replace('y', 'i'))      # la y és tan rara a l'italià que no rep cap forma a la taula


def units_for(lang):
    ws = plain_words(lang); S = []
    for w in ws:
        ss = syl(w); S.append(ss[:-1] + [ss[-1] + '#'])
    keep = {u for u, _ in Counter(u for ss in S for u in ss).most_common(TOP)}
    us = []
    for ss in S:
        for u in ss:
            if u in keep: us.append(u)
            else: us += list(u.rstrip('#')) + (['#'] if u.endswith('#') else [])
    return us, ws


def setup(lang):
    us, ws = units_for(lang)
    rw = [w for l in SC.L_ALL for w in l['ws']]; code = X.Code(Counter(us), rw)
    assert not code.missing, code.missing
    return code, us, ws


def grams_repeated(L, n):
    c = Counter(tuple(l['ws'][i:i + n]) for l in L for i in range(len(l['ws']) - n + 1))
    return sum(1 for v in c.values() if v >= 2)


def run(split, lang, seed, desat=False):
    code, us, ws = setup(lang)
    lay = [l for l in SC.L_ALL if SC.folio_num(l['page']) % 2 == 0] if split == 'senars' else SC.L_ALL
    hand = {l['page']: l['hand'] for l in SC.L_ALL}
    if desat:   # «acaba»: el text ja escrit (les línies surten una a una de la maqueta); intents, reserva i temps no es van desar
        T = json.load(open(os.path.join(OUT, f'{split}_{lang}_{seed}_text.json'), encoding='utf-8')); assert len(T) == len(lay)
        out = [dict(page=l['page'], sheet=l['sheet'], lang=l['lang'], ps=l['ps'], pe=l['pe'], gb=l['gb'], ws=t['ws']) for l, t in zip(lay, T)]
        g = type('G', (), dict(tries=float('nan'), fb=float('nan'), pos=sum(len(o['ws']) for o in out)))(); t = time.time()
    else:
        g = X.Cipher(code, us, max_tries=3000); t = time.time(); out = g.write(seed=seed, layout=None if split == 'tots' else lay)
    for o in out: o['hand'] = hand[o['page']]
    n = sum(len(o['ws']) for o in out)
    if not desat: json.dump([dict(page=o['page'], ws=o['ws']) for o in out], open(os.path.join(OUT, f'{split}_{lang}_{seed}_text.json'), 'w', encoding='utf-8'))
    R = M.evaluate(out, seed=seed)
    H = -sum(v / len(us) * math.log2(v / len(us)) for v in Counter(us).values())
    upw = len(us) / len(ws)                                          # unitats per mot del text pla
    info = dict(lang=lang, split=split, seed=seed, segons=time.time() - t, mots=n, intents=g.tries / n, reserva=g.fb, unitats=g.pos,
                classes=len(set(us)), bits_per_mot=H, mots_text_pla=g.pos / upw, desxifrat_ok=(X.decode(code, out) == us[:g.pos]),
                tipus=len(set(w for l in out for w in l['ws'])), ordre=control.word_order(out),
                repeticio_immediata=sum(a == b for l in out for a, b in zip(l['ws'], l['ws'][1:])) / n)
    if split == 'tots':
        info['classes_K'] = {K: heldout(exchange(odd_(out), K), even_(out)) for K in (2, 4, 8, 16, 32)}
        info['repetits'] = {n_: grams_repeated(out, n_) for n_ in (2, 3, 4, 5)}
    json.dump(dict(R={k: float(v) for k, v in R.items()}, info=info), open(os.path.join(OUT, f'{split}_{lang}_{seed}.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, default=float)
    print(split, lang, seed, {k: v for k, v in info.items()}, flush=True)


def agrega():
    import glob
    import numpy as np
    real = SC.L_ALL; even = even_(real)
    REF = {'tots': M.evaluate(real, seed=1), 'senars': M.evaluate(even, seed=1)}
    lines = []; res = {}
    real_rep = {n_: grams_repeated(real, n_) for n_ in (2, 3, 4, 5)}
    lines.append(f'Voynich real: ordre 0.088, K=2 0.012, K=32 0.054, repetits 2/3/4/5 mots {real_rep}')
    for lang in ('la', 'it'):
        r = {}
        for split in ('tots', 'senars'):
            fs = sorted(glob.glob(os.path.join(OUT, f'{split}_{lang}_[0-9].json')))
            if not fs: continue
            J = [json.load(open(f, encoding='utf-8')) for f in fs]
            G = {k: float(np.mean([j['R'][k] for j in J])) for k in J[0]['R']}
            ok = M.compare(REF[split], G); r[split] = dict(score=int(sum(ok.values())), falla=[k for k in ok if not ok[k]], llavors=len(J),
                                                          info=[j['info'] for j in J])
        if 'tots' not in r: continue
        I = r['tots']['info']; mean = lambda f: float(np.mean([f(i) for i in I]))
        K2 = mean(lambda i: i['classes_K']['2']); K32 = mean(lambda i: i['classes_K']['32']); order = mean(lambda i: i['ordre'])
        tri = mean(lambda i: i['repetits']['3']); five = mean(lambda i: i['repetits']['5'])
        C = {'C1 bateria': r['tots']['score'] >= 74 and r.get('senars', {}).get('score', 0) >= 70,
             'C2 forma de l\'ordre': K2 <= 0.025 and 0.03 <= K32 <= 0.08, 'C3 ordre total': 0.06 <= order <= 0.12, 'C4 frases': tri <= 190 and five <= 2}
        res[lang] = dict(r, criteris=C, K2=K2, K32=K32, ordre=order, trios=tri, cinc=five)
        lines.append(f"\n== {'llatí' if lang == 'la' else 'italià'} ({r['tots']['llavors']} llavors al text sencer, {r.get('senars', {}).get('llavors', 0)} a pàgines no vistes)")
        lines.append(f"  bateria: text sencer {r['tots']['score']}/88, pàgines no vistes {r.get('senars', {}).get('score', '-')}/88")
        lines.append(f"  falla (text sencer): {'; '.join(r['tots']['falla'])}")
        lines.append(f"  ordre {order:.3f}; classes " + ' '.join(f"K={K}:{mean(lambda i, K=K: i['classes_K'][str(K)] if str(K) in i['classes_K'] else i['classes_K'][K]):.3f}" for K in (2, 4, 8, 16, 32)))
        lines.append(f"  repetits (seqüències diferents >= 2 cops) 2/3/4/5 mots: " + ' / '.join(f"{mean(lambda i, n_=n_: i['repetits'][str(n_)] if str(n_) in i['repetits'] else i['repetits'][n_]):.0f}" for n_ in (2, 3, 4, 5)))
        lines.append(f"  capacitat {mean(lambda i: i['bits_per_mot']):.2f} bits/mot, {mean(lambda i: i['mots_text_pla']):.0f} mots del text pla; classes {I[0]['classes']}; "
                     f"intents/mot {mean(lambda i: i['intents'] or float('nan')):.0f}; reserva {mean(lambda i: i['reserva'] or float('nan')):.0f}; desxifrat {all(i['desxifrat_ok'] for i in I)}; "
                     f"tipus {mean(lambda i: i['tipus']):.0f} (real 7.915); repetició immediata {mean(lambda i: i['repeticio_immediata']):.4f} (real 0,0090)")
        lines.append('  criteris: ' + '; '.join(f"{k} {'SÍ' if v else 'NO'}" for k, v in C.items()))
    open(os.path.join(HERE, 'sillabes.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n'); print('\n'.join(lines))
    json.dump(res, open(os.path.join(HERE, 'sillabes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'prova':
        lang = sys.argv[2] if len(sys.argv) > 2 else 'la'
        code, us, ws = setup(lang)
        print(lang, len(ws), 'mots;', len(us), 'unitats;', len(set(us)), 'classes;', f'{len(us) / len(ws):.2f} unitats/mot', us[:20])
        lay = [l for l in SC.L_ALL if l['page'] in ('f1r', 'f75r', 'f103r')]
        c = X.Cipher(code, us, max_tries=3000); t = time.time(); out = c.write(seed=1, layout=lay)
        n = sum(len(l['ws']) for l in out)
        print(f'{n} mots, {c.tries / n:.0f} intents/mot, {c.fb} de reserva, {time.time() - t:.0f}s; desxifrat == original:', X.decode(code, out) == us[:c.pos])
        for l in out[:5]: print('  ', ' '.join(l['ws']))
    if mode == 'corre': run(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    if mode == 'acaba': run(sys.argv[2], sys.argv[3], int(sys.argv[4]), desat=True)   # mesura un _text.json ja escrit
    if mode == 'agrega': agrega()
