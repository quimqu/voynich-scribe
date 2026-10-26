# Control with known meaning (voynich.ninja question, 19/10/2026): if we apply the scribe to a text in a real language,
# does it pass the measures too? The same GENERIC scribe (without the Voynich-specific rules: q-, gallows, closures, p/f, habits)
# is applied the same way to the Voynich and to the control text: learned from the odd folios, it writes the even ones, and is compared with the real even ones.
# Reference: the real odd folios against the real even ones (the ceiling). Added measure: information carried by word order.
#   PYTHONIOENCODING=utf-8 py -3 controls/control.py prepare <text.txt> <name>     -> controls/<name>.json (lines of ~45 characters)
#   PYTHONIOENCODING=utf-8 py -3 controls/control.py run <name|voynich>            -> controls/res_<name>.json
#   PYTHONIOENCODING=utf-8 py -3 controls/control.py report <name> [<name>...]     -> table
# (from scribe/)
import os, sys, re, json, math, random, numpy as np
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
GENERIC = dict(use_slots=False, use_word_rules=False, use_closure=False, use_end_table=False, use_first_line=False, use_style=False,
               use_ehabit=False, use_sec_dy=False, use_famrep=False, use_reprefix=False, use_lang=False)
VARIANTS = {'copy 22%': dict(GENERIC, r_copy=0.22), 'copy 35%': dict(GENERIC, r_copy=0.35), 'copy 10%': dict(GENERIC, r_copy=0.10)}   # 27/10: rates explicit (the default r_copy went from 0.35 to 0.22 on 19/10)
SEEDS = (1, 2, 3)


def prepare(path, name, width=45, lines_par=10, lines_page=26):
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
    print(f'{name}: {len(toks)} words, {len(out)} lines, {out[-1]["page"]} pages')


# ---------- added measures ----------
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
    # information between consecutive words of the same line (the K most frequent words; the rest, a single class), minus that of the
    # same text with the words shuffled WITHIN each line (removes the sampling bias and the composition of the line)
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


KEYS = [('Adjacent identical words / chance', 'word repeated right after / chance'), ('Consecutive words at edit distance 1 / shuffled', 'neighbours one glyph apart / shuffled'),
        ('Same word at distance 2 / shuffled', 'same word at distance 2 / shuffled'),
        ('[A1] Words with an edit-distance-1 twin earlier on the page (%)', 'words with a twin earlier on the page (%)'),
        ('Boundary MI, distance 1 (last glyph to next first glyph)', 'boundary rule (bits)'), ('Word types', 'word types'), ('Hapax (% of types)', 'hapax (% of types)'),
        ('[R2.6] Mean word length (glyphs)', 'mean length (glyphs)'), ('[R2.6] SD of word length', 'SD of length'),
        ('Spearman correlation of neighbour word lengths', 'length correlation between neighbours'),
        ('Same first glyph as line n-1 / null', 'same 1st glyph as the line above / null'),
        ('[eye] Strange words (rare trigram in the real text) (%)', 'strange words (%)'),
        ('h1', 'character entropy h1'), ('h2', 'conditional entropy h2'), ('zipf', 'Zipf slope'),
        ('order', 'WORD ORDER: information (bits)')]


def measures(L, seed=0):
    import measures as M
    R = M.evaluate(L, seed=seed)
    s = chars(L)
    R.update(h1=H1(s), h2=H2c(s), zipf=zipf(L), order=word_order(L))
    return {k: float(R[k]) for k, _ in KEYS}


def run(name):
    if name != 'voynich':
        os.environ['SCRIBE_CORPUS'] = os.path.join(HERE, f'{name}.json')
    os.environ['SCRIBE_TRAIN'] = 'odd'
    sys.path.insert(0, os.path.dirname(HERE))
    os.chdir(os.path.dirname(HERE))
    import measures as M
    import scribe as E
    if name != 'voynich':
        M.set_reference(E.L_ALL)
    odd = [l for l in E.L_ALL if E.folio_num(l['page']) % 2 == 1]
    even = [l for l in E.L_ALL if E.folio_num(l['page']) % 2 == 0]
    res = dict(even=measures(even), odd=measures(odd))
    for vn, kw in VARIANTS.items():
        rs = [measures(E.Escriba(**kw).write(seed=s, layout=even), seed=s) for s in SEEDS]
        res[vn] = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
        res[vn + ' (sample)'] = [' '.join(l['ws']) for l in E.Escriba(**kw).write(seed=1, layout=even)[:6]]
    res['even (sample)'] = [' '.join(l['ws']) for l in even[:6]]
    json.dump(res, open(os.path.join(HERE, f'res_{name}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('done', name)


def ok(r, g):
    return (abs(g - r) < 0.01) if abs(r) < 0.02 else (abs(g / r - 1) < 0.25)


def report(names):
    R = {n: json.load(open(os.path.join(HERE, f'res_{n}.json'), encoding='utf-8')) for n in names}
    out = []
    cols = ['odd'] + list(VARIANTS)
    for n in names:
        r = R[n]
        out.append(f'\n### {n}: real even against ... (✓ = within ±25%)')
        out.append(f"{'measure':46}{'even':>9}" + ''.join(f'{c:>16}' for c in cols))
        for k, nm in KEYS:
            out.append(f'{nm[:46]:46}{r["even"][k]:9.3f}' + ''.join(f'{r[c][k]:13.3f} {"✓" if ok(r["even"][k], r[c][k]) else "·"}' for c in cols))
        out.append(f"{'REPRODUCED':46}{'':9}" + ''.join(f'{sum(ok(r["even"][k], r[c][k]) for k, _ in KEYS):>14d}/{len(KEYS)}' for c in cols))
        out.append('real sample:')
        out += ['   ' + x for x in r['even (sample)'][:4]]
        out.append(f'scribe sample ({list(VARIANTS)[0]}):')
        out += ['   ' + x for x in r[list(VARIANTS)[0] + ' (sample)'][:4]]
    print('\n'.join(out))
    open(os.path.join(HERE, 'report_' + '_'.join(names) + '.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'prepare':
        prepare(sys.argv[2], sys.argv[3])
    elif cmd == 'run':
        run(sys.argv[2])
    elif cmd == 'report':
        report(sys.argv[2:])
