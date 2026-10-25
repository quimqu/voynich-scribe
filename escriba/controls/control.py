# Control amb significat conegut (pregunta de voynich.ninja, 19/10/2026): si apliquem l'escriba a un text en una llengua real,
# passa també les mesures? El mateix escriba GENÈRIC (sense les regles pròpies del Voynich: q-, gallows, tancaments, p/f, hàbits)
# s'aplica igual al Voynich i al text de control: après dels folis senars, escriu els parells, i es compara amb els parells reals.
# Referència: els senars reals contra els parells reals (el sostre). Mesura afegida: informació que porta l'ordre dels mots.
#   PYTHONIOENCODING=utf-8 py -3 controls/control.py prepara <text.txt> <nom>     -> controls/<nom>.json (línies de ~45 caràcters)
#   PYTHONIOENCODING=utf-8 py -3 controls/control.py corre <nom|voynich>          -> controls/res_<nom>.json
#   PYTHONIOENCODING=utf-8 py -3 controls/control.py informe <nom> [<nom>...]     -> taula
# (des de escriba/)
import os, sys, re, json, math, random, numpy as np
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
GENERIC = dict(use_slots=False, use_word_rules=False, use_closure=False, use_end_table=False, use_first_line=False, use_style=False,
               use_ehabit=False, use_sec_dy=False, use_famrep=False, use_reprefix=False, use_lang=False)
VARIANTS = {'còpia 35%': dict(GENERIC), 'còpia 10%': dict(GENERIC, r_copy=0.10)}
SEEDS = (1, 2, 3)


def prepara(path, name, width=45, lines_par=10, lines_page=26):
    raw = open(path, encoding='utf-8', errors='ignore').read().lower()
    toks = [t for t in re.split(r'[^a-z]+', raw) if t]
    L = []
    cur = []
    n = 0
    for t in toks:
        if cur and n + 1 + len(t) > width:
            L.append(cur)
            cur = []
            n = 0
        n = len(t) if not cur else n + 1 + len(t)
        cur.append(t)
    if cur:
        L.append(cur)
    out = []
    for i, ws in enumerate(L):
        pg = i // lines_page
        li = i % lines_page
        out.append(dict(page=f'p{pg + 1}', quire='X', locus=f'p{pg + 1}.{li + 1}', sheet=f'S{pg // 4 + 1}', lang='X', hand='1',
                        section='control', ps=int(li % lines_par == 0), pe=int(li % lines_par == lines_par - 1 or li == lines_page - 1),
                        ws=ws, gb=[False] * len(ws)))
    json.dump(out, open(os.path.join(HERE, f'{name}.json'), 'w', encoding='utf-8'))
    print(f'{name}: {len(toks)} mots, {len(out)} línies, {out[-1]["page"]} pàgines')


# ---------- mesures afegides ----------
def chars(L):
    return ' '.join(' '.join(l['ws']) for l in L)


def H1(s):
    c = Counter(s)
    n = len(s)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def H2c(s):
    b = Counter(zip(s, s[1:]))
    u = Counter(s[:-1])
    n = len(s) - 1
    return -sum(v / n * math.log2(v / u[a]) for (a, _), v in b.items())


def zipf(L):
    f = np.array(sorted(Counter(w for l in L for w in l['ws']).values(), reverse=True), float)
    r = np.arange(1, len(f) + 1)
    k = r <= 1000
    return -np.polyfit(np.log(r[k]), np.log(f[k]), 1)[0]


def MI(pairs):
    n = len(pairs)
    xy = Counter(pairs)
    x = Counter(a for a, _ in pairs)
    y = Counter(b for _, b in pairs)
    return sum(v / n * math.log2((v / n) / ((x[a] / n) * (y[b] / n))) for (a, b), v in xy.items())


def word_order(L, K=200, reps=5):
    # informació entre mots seguits de la mateixa línia (els K mots més freqüents; la resta, una sola classe), menys la del
    # mateix text amb els mots barrejats DINS de cada línia (treu el biaix de mostra i la composició de la línia)
    top = set(w for w, _ in Counter(w for l in L for w in l['ws']).most_common(K))

    def m(w):
        return w if w in top else '*'
    real = MI([(m(a), m(b)) for l in L for a, b in zip(l['ws'], l['ws'][1:])])
    rng = random.Random(0)
    base = []
    for _ in range(reps):
        pp = []
        for l in L:
            ws = l['ws'][:]
            rng.shuffle(ws)
            pp += [(m(a), m(b)) for a, b in zip(ws, ws[1:])]
        base.append(MI(pp))
    return real - float(np.mean(base))


KEYS = [('AA / atzar', 'mot repetit just després / atzar'), ('quasi(ed=1) / base', 'veïns a un glif de distància / barreja'),
        ('repetició k=2 / base', 'mateix mot a distància 2 / barreja'),
        ('[A1] mots amb bessó (ED≤1) abans a la pàgina (%)', 'mots amb bessó abans a la pàgina (%)'),
        ('MI frontera k=1', 'acord de frontera (bits)'), ('tipus', 'tipus de mot'), ('hàpax (%)', 'hàpax (% dels tipus)'),
        ('[R2.6] longitud mitjana (glifs)', 'llargada mitjana (glifs)'), ('[R2.6] desv. típica longitud', 'desviació de la llargada'),
        ('Spearman longitud veïns', 'correlació de llargada entre veïns'),
        ('1r glif línia n-1=n / nul', 'mateix 1r glif que la línia de sobre / nul'),
        ('[ull] mots estranys (trigrama rar al real) (%)', 'mots estranys (%)'),
        ('h1', 'entropia de caràcter h1'), ('h2', 'entropia condicional h2'), ('zipf', 'pendent de Zipf'),
        ('ordre', 'ORDRE DELS MOTS: informació (bits)')]


def measures(L, seed=0):
    import mesures as M
    R = M.evaluate(L, seed=seed)
    s = chars(L)
    R.update(h1=H1(s), h2=H2c(s), zipf=zipf(L), ordre=word_order(L))
    return {k: float(R[k]) for k, _ in KEYS}


def corre(name):
    if name != 'voynich':
        os.environ['ESCRIBA_CORPUS'] = os.path.join(HERE, f'{name}.json')
    os.environ['ESCRIBA_TRAIN'] = 'senars'
    sys.path.insert(0, os.path.dirname(HERE))
    os.chdir(os.path.dirname(HERE))
    import mesures as M
    import escriba as E
    if name != 'voynich':
        M.set_reference(E.L_ALL)
    odd = [l for l in E.L_ALL if E.folio_num(l['page']) % 2 == 1]
    even = [l for l in E.L_ALL if E.folio_num(l['page']) % 2 == 0]
    res = dict(parells=measures(even), senars=measures(odd))
    for vn, kw in VARIANTS.items():
        rs = [measures(E.Escriba(**kw).write(seed=s, layout=even), seed=s) for s in SEEDS]
        res[vn] = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
        res[vn + ' (mostra)'] = [' '.join(l['ws']) for l in E.Escriba(**kw).write(seed=1, layout=even)[:6]]
    res['parells (mostra)'] = [' '.join(l['ws']) for l in even[:6]]
    json.dump(res, open(os.path.join(HERE, f'res_{name}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('fet', name)


def ok(r, g):
    return (abs(g - r) < 0.01) if abs(r) < 0.02 else (abs(g / r - 1) < 0.25)


def informe(names):
    R = {n: json.load(open(os.path.join(HERE, f'res_{n}.json'), encoding='utf-8')) for n in names}
    out = []
    cols = ['senars'] + list(VARIANTS)
    for n in names:
        r = R[n]
        out.append(f'\n### {n}: parells reals contra ... (✓ = dins del ±25%)')
        out.append(f"{'mesura':46}{'parells':>9}" + ''.join(f'{c:>16}' for c in cols))
        for k, nm in KEYS:
            out.append(f'{nm[:46]:46}{r["parells"][k]:9.3f}' + ''.join(f'{r[c][k]:13.3f} {"✓" if ok(r["parells"][k], r[c][k]) else "·"}' for c in cols))
        out.append(f"{'REPRODUÏDES':46}{'':9}" + ''.join(f'{sum(ok(r["parells"][k], r[c][k]) for k, _ in KEYS):>14d}/{len(KEYS)}' for c in cols))
        out.append('mostra real:')
        out += ['   ' + x for x in r['parells (mostra)'][:4]]
        out.append(f'mostra escriba ({list(VARIANTS)[0]}):')
        out += ['   ' + x for x in r[list(VARIANTS)[0] + ' (mostra)'][:4]]
    print('\n'.join(out))
    open(os.path.join(HERE, 'informe_' + '_'.join(names) + '.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'prepara':
        prepara(sys.argv[2], sys.argv[3])
    elif cmd == 'corre':
        corre(sys.argv[2])
    elif cmd == 'informe':
        informe(sys.argv[2:])
