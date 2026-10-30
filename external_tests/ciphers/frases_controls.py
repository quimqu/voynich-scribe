# Frases repetides (seqüències de 2-5 mots seguits a la mateixa línia que surten 2 cops o més) al Voynich, a textos coneguts de la
# mateixa mida (32.284 mots abocats a les mateixes llargades de línia), als xifrats de §3 i a l'skribe. XIFRATS.md §9.
# Textos de Project Gutenberg, baixats una vegada a CORPUS (per defecte C:\Temp\corpus).   py -3 frases_controls.py
import sys, re, os, glob, json, urllib.request
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); CORPUS = os.environ.get('CORPUS', os.path.join(HERE, '_corpus')); os.makedirs(CORPUS, exist_ok=True)
for gid in (16439, 8102, 49513, 2000, 45334, 1012, 10, 2591):
    if not os.path.exists(os.path.join(CORPUS, f'g{gid}.txt')):
        urllib.request.urlretrieve(f'https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt', os.path.join(CORPUS, f'g{gid}.txt'))
SCRIBE = (os.environ.get('SCRIBE') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scribe'))
sys.path.insert(0, SCRIBE); os.chdir(SCRIBE)
import scribe as SC
os.chdir(CORPUS)
real = SC.L_ALL; LENS = [len(l['ws']) for l in real]; N = sum(LENS)
def pour(ws):
    out = []; i = 0
    for n in LENS:
        if i >= len(ws): break
        out.append(ws[i:i + n]); i += n
    return out
def gut(f, skip=1500):
    t = open(f, encoding='utf-8', errors='ignore').read()
    a = t.find('*** START'); b = t.find('*** END'); t = t[t.find('\n', a) if a >= 0 else 0: b if b > 0 else None]
    ws = re.findall(r"[a-zà-ÿæœ]+", t.lower()); return ws[skip:skip + N]
def sortida(name):
    L = []
    for line in open(os.path.join(HERE, 'sortides', f'{name}.txt'), encoding='utf-8'):
        if '>' in line: L.append(line.split('>', 1)[1].split())
    return L
T = {'Voynich real': [l['ws'] for l in real]}
for f, nm in [('g16439.txt', 'Apicius, receptari llatí'), ('g8102.txt', 'Forme of Cury, receptari anglès c.1390'), ('g49513.txt', 'Culpeper, herbari anglès 1652'),
              ('g2000.txt', 'Quixot (castellà)'), ('g45334.txt', 'Promessi sposi (italià)'), ('g1012.txt', 'Divina Commedia (italià, vers)'),
              ('g10.txt', 'Bíblia King James (anglès)'), ('g2591.txt', 'Grimm (anglès)')]:
    ws = gut(f); T[f'{nm} [{len(ws)} mots]'] = pour(ws)
T['De docta ignorantia (llatí), maqueta'] = [l['ws'] for l in json.load(open(os.path.join(HERE, '_data', 'escriba', 'controls', 'llati.json'), encoding='utf-8'))]
for nm in ['Nomenclàtor_rang', 'Nomenclàtor_+_homòfons_+_contacte', 'Tipus_Naibbe_1-2_lletres-mot', 'PM-Cipher_notebook']:
    T['xifrat: ' + nm.replace('_', ' ')] = sortida(nm)
for s in (1,):
    T['skribe sol'] = [l['ws'] for l in SC.Escriba().write(seed=1)]
def grams(L, n): return Counter(tuple(l[i:i + n]) for l in L for i in range(len(l) - n + 1))
print('%-48s %7s %7s | %13s %13s %13s %13s' % ('text', 'mots', 'tipus', '2 mots', '3 mots', '4 mots', '5 mots'))
for nm, L in T.items():
    ws = [w for l in L for w in l]; cs = [grams(L, n) for n in (2, 3, 4, 5)]
    print('%-48s %7d %7d | ' % (nm[:48], len(ws), len(set(ws))) + ' '.join('%13s' % f'{sum(v >= 2 for v in c.values())} ({sum(v >= 3 for v in c.values())})' for c in cs))
print()
for nm in ['Apicius', 'Forme of Cury', 'Culpeper', 'Nomenclàtor_+', 'Nomenclàtor_rang']:
    k = next(k for k in T if nm.replace('_', ' ') in k); c3 = grams(T[k], 3); c4 = grams(T[k], 4)
    print(k[:40], '| trios:', ', '.join(f"{' '.join(g)} ({v})" for g, v in c3.most_common(8)), '| quatriots:', ', '.join(f"{' '.join(g)} ({v})" for g, v in c4.most_common(5)))
