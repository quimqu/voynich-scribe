# Mostres del text real i de tres versions de l'escriba (28/09 edició cega; + memòria de formes; + hàbit e i dy de secció),
# sobre la mateixa maqueta. Els mots estranys (algun trigrama de glifs que al real surt ≤3 cops) van entre [ ].
# Ús (des de escriba/): PYTHONIOENCODING=utf-8 py -3 mostra_memoria_formes.py > mostra_memoria_formes.txt
import re, random
from collections import Counter
import mesures as M
from escriba import Escriba, L_ALL
TRI=Counter()
for l in L_ALL:
    for w in l['ws']:
        g=['^']+M.gl(w)+['$']
        for i in range(len(g)-2): TRI[tuple(g[i:i+3])]+=1
def strange(w):
    g=['^']+M.gl(w)+['$']; return any(TRI.get(tuple(g[i:i+3]),0)<=3 for i in range(len(g)-2))
fmt=lambda ws,gb: ' '.join(('<-> ' if g else '')+(f'[{w}]' if strange(w) else w) for w,g in zip(ws,gb))
OLD=Escriba(mod_contact=0,mod_tries=6,use_ehabit=False,use_sec_dy=False).write(seed=1); MID=Escriba(use_ehabit=False,use_sec_dy=False).write(seed=1); NEW=Escriba().write(seed=1)
VOC=Counter(w for l in L_ALL for w in l['ws'])
for pg in ['f1r','f78r','f88r','f103r']:
    idx=[i for i,l in enumerate(L_ALL) if l['page']==pg][:10]
    for nm,T in [('REAL',L_ALL),("ESCRIBA DEL 28/09 (edició cega)",OLD),('+ MEMÒRIA DE FORMES',MID),('+ HÀBIT e I dy DE SECCIÓ (actual)',NEW)]:
        ns=sum(strange(w) for i in idx for w in T[i]['ws']); nt=sum(len(T[i]['ws']) for i in idx)
        nk=sum(VOC[w]>0 for i in idx for w in T[i]['ws'])
        print(f'\n=== {pg} · {nm}  ({ns} estranys de {nt} mots; {nk} mots que existeixen al manuscrit real)')
        for i in idx: print(('¶ ' if T[i]['ps']==1 else '  ')+fmt(T[i]['ws'],T[i]['gb']))
