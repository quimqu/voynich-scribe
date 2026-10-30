# On viu el sobrant: cost de cada mot real (pàgines parelles) sota el model après de l'skribe menys sota el model après del real.
import os, sys, math, json
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); SCRIBE = (os.environ.get('SCRIBE') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scribe'))
sys.path.insert(0, SCRIBE); sys.path.insert(0, HERE); os.chdir(SCRIBE)
from scribe import Escriba, L_ALL, folio_num
os.chdir(HERE)
import lab, stego
from sobrant import norm, halves

def per_word(train, test, eps=0.03):
    m = stego.Model(train); cm = lab.WB(['^' + w + '$' for l in train for w in l['ws']], 5)
    def pc(w):
        s = '^' + w + '$'; return 2 ** sum(math.log2(cm.p(s[max(0, i - 4):i], s[i])) for i in range(1, len(s)))
    out = []; pw = defaultdict(list)
    for l in test:
        page_words = pw[l['page']]; prev = None; ws = []
        for i, w in enumerate(l['ws']):
            d = m.dist(l['hand'], page_words + ws, prev)
            out.append((w, stego.slot(l, i), l['section'], -math.log2((1 - eps) * d.get(w, 0.0) + eps * pc(w))))
            ws.append(w); prev = w
        page_words.extend(ws)
    return out

real = norm(L_ALL); rtr, rte = halves(real)
sk = norm(Escriba().write(seed=1)); str_, _ = halves(sk)
A = per_word(str_, rte); B = per_word(rtr, rte)
freq = Counter(w for l in rtr for w in l['ws'])
def band(w):
    f = freq[w]; return 'nou (no vist als senars)' if f == 0 else '1-2' if f <= 2 else '3-20' if f <= 20 else '21-200' if f <= 200 else '>200'
groups = {'freqüència del mot als senars reals': band, 'posició': lambda r: r[1], 'secció': lambda r: r[2]}
res = {}
tot = sum(a[3] - b[3] for a, b in zip(A, B)); n = len(A)
print(f'sobrant total: {tot / n:.2f} bits/mot ({n} mots)')
for gname, f in groups.items():
    acc = defaultdict(lambda: [0, 0.0])
    for a, b in zip(A, B):
        k = f(a[0]) if gname.startswith('freq') else f(a)
        acc[k][0] += 1; acc[k][1] += a[3] - b[3]
    print(gname); res[gname] = {}
    for k, (c, s) in sorted(acc.items(), key=lambda x: -x[1][1]):
        print(f'  {k:28} {100 * c / n:5.1f}% dels mots  sobrant/mot {s / c:6.2f}  part del total {100 * s / tot:6.1f}%')
        res[gname][k] = dict(frac=c / n, per_word=s / c, share=s / tot)
# mots reals que més sorprenen l'skribe
ex = Counter(); cnt = Counter()
for a, b in zip(A, B): ex[a[0]] += a[3] - b[3]; cnt[a[0]] += 1
print('mots amb més sobrant acumulat:', [(w, cnt[w], round(v, 1)) for w, v in ex.most_common(20)])
res['top'] = [(w, cnt[w], v) for w, v in ex.most_common(40)]
json.dump(res, open(os.path.join(HERE, 'sobrant_on.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
