# Llengües sense articles (llatí, finès, polonès) i textos sense els 100 mots més freqüents: XIFRATS.md §9.   py -3 frases_sense_articles.py
import os
__file__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frases_controls.py'); exec(open(__file__, encoding='utf-8').read().split('def grams')[0])
for gid in (11940, 7000, 31536):
    if not os.path.exists(os.path.join(CORPUS, f'g{gid}.txt')):
        urllib.request.urlretrieve(f'https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt', os.path.join(CORPUS, f'g{gid}.txt'))
def grams(L, n): return Counter(tuple(l[i:i + n]) for l in L for i in range(len(l) - n + 1))
re_w = re.compile(r"[a-zà-ÿæœąćęłńóśźżäöå]+")
def gut2(f, skip=1500):
    t = open(f, encoding='utf-8', errors='ignore').read(); a = t.find('*** START'); b = t.find('*** END')
    t = t[t.find('\n', a) if a >= 0 else 0: b if b > 0 else None]; ws = re_w.findall(t.lower()); return ws[skip:skip + N]
for f, nm in [('g11940.txt', 'Seitsemän veljestä (finès, novel·la)'), ('g7000.txt', 'Kalevala (finès, vers)'), ('g31536.txt', 'Pan Tadeusz (polonès, vers)')]:
    ws = gut2(f); T[f'{nm} [{len(ws)} mots]'] = pour(ws)
keep = [k for k in T if not k.startswith('xifrat') and 'Bíblia' not in k and 'Grimm' not in k]
print('Sense articles a la llengua: llatí (Apicius, De docta), finès, polonès.  «sense els 100 mots més freqüents»: es treuen del text i es')
print('compten els trios dels mots que queden, seguits dins de la línia (una aproximació a «només mots de contingut»).\n')
print('%-46s %7s | %10s %10s %10s | %24s' % ('text', 'tipus', '3 mots', '4 mots', '5 mots', 'sense els 100 freqüents: 3 · 4'))
for nm in keep:
    L = T[nm]; ws = [w for l in L for w in l]; top = {w for w, _ in Counter(ws).most_common(100)}
    Lc = [[w for w in l if w not in top] for l in L]
    c = [grams(L, n) for n in (3, 4, 5)]; cc = [grams(Lc, n) for n in (3, 4)]
    print('%-46s %7d | ' % (nm[:46], len(set(ws))) + ' '.join('%10d' % sum(v >= 2 for v in x.values()) for x in c) + ' | %15d %8d' % tuple(sum(v >= 2 for v in x.values()) for x in cc))
for nm in [k for k in T if 'finès' in k or 'polonès' in k]:
    print(nm[:30], '| trios:', ', '.join(f"{' '.join(g)} ({v})" for g, v in grams(T[nm], 3).most_common(6)))
