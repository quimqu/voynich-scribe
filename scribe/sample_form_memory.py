# Samples of the real text and of three versions of the scribe (28/09 blind edit; + form memory; + e habit and section dy),
# on the same layout. Strange words (some glyph trigram that appears <=3 times in the real text) are between [ ].
# Usage (from scribe/): PYTHONIOENCODING=utf-8 py -3 sample_form_memory.py > sample_form_memory.txt
import re, random
from collections import Counter
import measures as M
from scribe import Escriba, L_ALL
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
    for nm,T in [('REAL',L_ALL),("SCRIBE OF 28/09 (blind edit)",OLD),('+ FORM MEMORY',MID),('+ e HABIT AND SECTION dy (current)',NEW)]:
        ns=sum(strange(w) for i in idx for w in T[i]['ws']); nt=sum(len(T[i]['ws']) for i in idx)
        nk=sum(VOC[w]>0 for i in idx for w in T[i]['ws'])
        print(f'\n=== {pg} · {nm}  ({ns} strange of {nt} words; {nk} words that exist in the real manuscript)')
        for i in idx: print(('¶ ' if T[i]['ps']==1 else '  ')+fmt(T[i]['ws'],T[i]['gb']))
