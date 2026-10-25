# "Standard" measures on the real text and the scribe (question from a voynich.ninja reader, 19/10/2026): character entropies,
# Zipf, length distribution, vocabulary richness, and long-range structure (vocabulary similarity between pages
# by distance, and bursts of the frequent words). Mean of 5 seeds. Usage (from scribe/): PYTHONIOENCODING=utf-8 py -3 standard_measures.py
import math, numpy as np
from collections import Counter, defaultdict
import measures as M
from scribe import Escriba, L_ALL
def chars(L):    # EVA text letter by letter, with the space as a symbol (like h1/h2 in the literature)
    return ' '.join(' '.join(l['ws']) for l in L)
def H1(s): c=Counter(s); n=len(s); return -sum(v/n*math.log2(v/n) for v in c.values())
def H2c(s):
    big=Counter(zip(s,s[1:])); uni=Counter(s[:-1]); n=len(s)-1
    return -sum(v/n*math.log2(v/uni[a]) for (a,b),v in big.items())
def H3c(s):
    tri=Counter(zip(s,s[1:],s[2:])); bi=Counter(zip(s,s[1:])); n=len(s)-2
    return -sum(v/n*math.log2(v/bi[(a,b)]) for (a,b,c),v in tri.items())
def zipf(L):
    f=np.array(sorted(Counter(w for l in L for w in l['ws']).values(),reverse=True),float); r=np.arange(1,len(f)+1)
    k=(r>=1)&(r<=1000); return -np.polyfit(np.log(r[k]),np.log(f[k]),1)[0]
def mattr(L,w=500):
    t=[x for l in L for x in l['ws']]; return np.mean([len(set(t[i:i+w]))/w for i in range(0,len(t)-w,50)])
def glyphlen(L):
    v=[len(M.gl(w)) for l in L for w in l['ws']]; c=Counter(v); n=len(v); return [100*c[k]/n for k in range(1,11)]
def pages(L):
    P=defaultdict(list); order=[]
    for l in L:
        if l['page'] not in P: order.append(l['page'])
        P[l['page']]+=l['ws']
    return [P[p] for p in order if len(P[p])>=60]
def cos(a,b):
    A=Counter(a); B=Counter(b); n=sum(A[w]*B[w] for w in A); return n/math.sqrt(sum(v*v for v in A.values())*sum(v*v for v in B.values()))
def decay(L,ds=(1,2,5,10,20,50,100)):
    P=pages(L); return [np.mean([cos(P[i],P[i+d]) for i in range(len(P)-d)]) for d in ds]
def burst(L,top=50):
    # bursts: coefficient of variation of the gaps between occurrences of the 50 most frequent words (1 = Poisson; >1 = clustered)
    t=[x for l in L for x in l['ws']]; pos=defaultdict(list)
    for i,w in enumerate(t): pos[w].append(i)
    cv=[]
    for w,_ in Counter(t).most_common(top):
        g=np.diff(pos[w]); cv.append(np.std(g)/np.mean(g))
    return float(np.mean(cv))
def run(L):
    s=chars(L); return dict(h1=H1(s),h2=H2c(s),h3=H3c(s),zipf=zipf(L),mattr=mattr(L),burst=burst(L),dec=decay(L),len=glyphlen(L))
R=run(L_ALL); G=[run(Escriba().write(seed=s)) for s in (1,2,3,4,5)]
avg=lambda k: np.mean([g[k] for g in G],axis=0)
out=[]
def P(s): out.append(s); print(s)
P(f"{'':38}{'real':>10}{'scribe':>10}")
for k,nm in [('h1','character entropy h1 (bits)'),('h2','conditional entropy h2 (bits)'),('h3','conditional entropy h3 (bits)'),
             ('zipf','Zipf slope (ranks 1-1000)'),('mattr','MATTR (window of 500 words)'),('burst','bursts: CV of gaps, 50 freq. words')]:
    P(f'{nm:38}{R[k]:10.3f}{avg(k):10.3f}')
P('length distribution (glyphs 1..10, %):')
P('  real   '+' '.join(f'{v:5.1f}' for v in R['len'])); P('  scribe '+' '.join(f'{v:5.1f}' for v in avg('len')))
P('vocabulary similarity (cosine) between pages at distance d = 1, 2, 5, 10, 20, 50, 100:')
P('  real   '+' '.join(f'{v:6.3f}' for v in R['dec'])); P('  scribe '+' '.join(f'{v:6.3f}' for v in avg('dec')))
open('standard_measures_out.txt','w',encoding='utf-8').write('\n'.join(out)+'\n')
