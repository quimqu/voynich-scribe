# D'on surten els mots estranys de l'escriba (mot amb algun trigrama de glifs, amb inici i fi, que al real surt ≤3 cops; mesures.py [ull]).
# S'etiqueta cada mot en el moment de produir-lo: nou (taula de contacte), nou de final de línia, còpia intacta, còpia modificada;
# i després les transformacions de lloc (tancament, obertura, prefix, p/f). Ús (des de escriba/): PYTHONIOENCODING=utf-8 py -3 diagnosi_estranys.py
import re, numpy as np
from collections import Counter, defaultdict
import mesures as M, escriba as E
TRI=Counter()
for l in M.load_real():
    for w in l['ws']:
        g=['^']+M.gl(w)+['$']
        for i in range(len(g)-2): TRI[tuple(g[i:i+3])]+=1
def bad_tris(w):
    g=['^']+M.gl(w)+['$']; return [tuple(g[i:i+3]) for i in range(len(g)-2) if TRI.get(tuple(g[i:i+3]),0)<=3]
strange=lambda w: bool(bad_tris(w))
ev=Counter(); evs=Counter(); badpos=Counter(); examples=defaultdict(Counter)
class Diag(E.Escriba):
    def gen_word(self,tab,A,style):
        w=super().gen_word(tab,A,style); k='nou (final de línia)' if tab is self.table_end_cur else 'nou'
        ev[k]+=1; s=bad_tris(w); evs[k]+=bool(s)
        for t in s: badpos[(k,'inici' if t[0]=='^' else 'final' if t[2]=='$' else 'mig')]+=1
        if s: examples[k][w]+=1
        return w
    def modify(self,w):
        w2=super().modify(w); ev['còpia modificada']+=1; s=strange(w2); evs['còpia modificada']+=s; evs['  (el model ja era estrany)']+=strange(w)
        if s and not strange(w): examples['còpia modificada'][w+'→'+w2]+=1
        return w2
    def close(self,w,probs):
        w2=super().close(w,probs)
        if w2!=w: ev['tancament']+=1; evs['tancament']+=(strange(w2) and not strange(w))
        return w2
    def table_end(self,lang):
        self.table_end_cur=super().table_end(lang); return self.table_end_cur
D=Diag(); D.table_end_cur=None
G=D.write(seed=1)
toks=[w for l in G for w in l['ws']]; N=len(toks)
print(f'mots escrits {N}; estranys al final {100*sum(map(strange,toks))/N:.2f}%  (real {100*sum(strange(w) for l in M.load_real() for w in l["ws"])/sum(len(l["ws"]) for l in M.load_real()):.2f}%)')
print('\nper origen (en el moment de produir-lo):')
for k in ev: print(f'  {k:24} {ev[k]:6d} produïts, {evs[k]:5d} estranys ({100*evs[k]/ev[k]:.1f}%)'+('  ← nous que fa la transformació' if k=='tancament' else ''))
print(f'  còpies modificades amb el model ja estrany: {evs["  (el model ja era estrany)"]}')
print('\non és el trigrama rar als mots nous:', dict(badpos))
for k in examples:
    print(f'\nexemples ({k}):',', '.join(f'{w}×{n}' for w,n in examples[k].most_common(25)))
# estranys finals que són a la pàgina com a còpia d'un estrany anterior (propagació per còpia)
from collections import defaultdict as dd
seen=dd(set); prop=0; firsts=0
for l in G:
    for w in l['ws']:
        if strange(w):
            if w in seen[l['page']]: prop+=1
            else: firsts+=1
        seen[l['page']].add(w)
print(f'\nestranys finals: {firsts} primera aparició a la pàgina, {prop} repeticions d\'un estrany ja escrit a la pàgina')
