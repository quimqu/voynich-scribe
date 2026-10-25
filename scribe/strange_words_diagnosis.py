# Where the scribe's strange words come from (a word with some glyph trigram, start and end included, that appears <=3 times in the real text; measures.py [eye]).
# Each word is tagged at the moment it is produced: new (contact table), new at line end, intact copy, modified copy;
# and then the positional transformations (closure, opening, prefix, p/f). Usage (from scribe/): PYTHONIOENCODING=utf-8 py -3 strange_words_diagnosis.py
import re, numpy as np
from collections import Counter, defaultdict
import measures as M, scribe as E
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
        w=super().gen_word(tab,A,style); k='new (line end)' if tab is self.table_end_cur else 'new'
        ev[k]+=1; s=bad_tris(w); evs[k]+=bool(s)
        for t in s: badpos[(k,'start' if t[0]=='^' else 'end' if t[2]=='$' else 'middle')]+=1
        if s: examples[k][w]+=1
        return w
    def modify(self,w):
        w2=super().modify(w); ev['modified copy']+=1; s=strange(w2); evs['modified copy']+=s; evs['  (the model was already strange)']+=strange(w)
        if s and not strange(w): examples['modified copy'][w+'→'+w2]+=1
        return w2
    def close(self,w,probs):
        w2=super().close(w,probs)
        if w2!=w: ev['closure']+=1; evs['closure']+=(strange(w2) and not strange(w))
        return w2
    def table_end(self,lang):
        self.table_end_cur=super().table_end(lang); return self.table_end_cur
D=Diag(); D.table_end_cur=None
G=D.write(seed=1)
toks=[w for l in G for w in l['ws']]; N=len(toks)
print(f'words written {N}; strange at the end {100*sum(map(strange,toks))/N:.2f}%  (real {100*sum(strange(w) for l in M.load_real() for w in l["ws"])/sum(len(l["ws"]) for l in M.load_real()):.2f}%)')
print('\nby origin (at the moment of producing the word):')
for k in ev: print(f'  {k:24} {ev[k]:6d} produced, {evs[k]:5d} strange ({100*evs[k]/ev[k]:.1f}%)'+('  ← new ones made by the transformation' if k=='closure' else ''))
print(f'  modified copies whose model was already strange: {evs["  (the model was already strange)"]}')
print('\nwhere the rare trigram is in the new words:', dict(badpos))
for k in examples:
    print(f'\nexamples ({k}):',', '.join(f'{w}×{n}' for w,n in examples[k].most_common(25)))
# final strange words that are on the page as a copy of an earlier strange word (propagation by copying)
from collections import defaultdict as dd
seen=dd(set); prop=0; firsts=0
for l in G:
    for w in l['ws']:
        if strange(w):
            if w in seen[l['page']]: prop+=1
            else: firsts+=1
        seen[l['page']].add(w)
print(f'\nfinal strange words: {firsts} first occurrence on the page, {prop} repetitions of a strange word already written on the page')
