# Exploratory follow-up of lsa_whitening.py (not pre-registered). DEV against the hand x section norm: (1) split into shared
# excess (both pages above their norm) and shared deficit, and its relation to page length; (2) the words and bifolia that carry the
# shared excess on the inner face.
#   PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/shared_excess.py > external_tests/davis_layfield/shared_excess.txt
print('== 1 · excess against deficit, and page length')
import os, glob, numpy as np
from collections import Counter
from scipy.stats import wilcoxon, spearmanr
HERE=os.path.dirname(os.path.abspath(__file__))
ns={'__file__':os.path.join(HERE,'x.py')}; exec(open(os.path.join(HERE,'sheet_order.py'),encoding='utf-8').read().split('srcs = ')[0],ns)
def cos(a,b):
    na,nb=np.linalg.norm(a),np.linalg.norm(b); return float(a@b/(na*nb)) if na>0 and nb>0 else 0.0
def one(x): x=np.asarray(x); return wilcoxon(x,alternative='greater').pvalue
def run(path):
    P=ns['read'](path); B=ns['bifolia'](P); rows=[]
    for q,a,b in B:
        pl=[a+'r',a+'v',b+'r',b+'v']; key=lambda p:(P[p]['H'],P[p]['S'])
        norm=[p for p in P if key(p)==key(pl[0]) and p not in pl and P[p]['lines']]
        if len(norm)<6: continue
        L={p:sum(len(l) for l in P[p]['lines']) for p in pl}
        rel={}
        for p in norm+pl:
            ws=[w for l in P[p]['lines'] for w in l]; c=Counter(ws); m=len(ws) or 1; rel[p]={w:v/m for w,v in c.items()}
        used=Counter(w for p in norm for w in rel[p]); vocab=sorted(w for w,c in used.items() if c>=5)
        M=np.array([[rel[p].get(w,0) for w in vocab] for p in norm]); mu=M.mean(0); sd=M.std(0); sd[sd==0]=1
        Z={p:(np.array([rel[p].get(w,0) for w in vocab])-mu)/sd for p in pl}
        f=lambda g:(cos(g(Z[a+'v']),g(Z[b+'r']))-cos(g(Z[b+'v']),g(Z[a+'r'])))
        rows.append(dict(h=P[a+'r']['H'],all=f(lambda z:z),excess=f(lambda z:np.clip(z,0,None)),deficit=f(lambda z:np.clip(z,None,0)),
            dlen=(L[a+'v']+L[b+'r'])-(L[b+'v']+L[a+'r']), minlen_in=min(L[a+'v'],L[b+'r']), minlen_out=min(L[b+'v'],L[a+'r']),
            dmin=min(L[a+'v'],L[b+'r'])-min(L[b+'v'],L[a+'r'])))
    return rows
for p in [os.path.join(ns['NOV'],'scribe','manuscript_out','real.txt')]+sorted(glob.glob(os.path.join(ns['NOV'],'scribe','manuscript_out','scribe_seed*.txt')))[:3]:
    R=run(p); nm=os.path.basename(p)[:-4]
    print(nm, ' | '.join(f"{k} {np.mean([r[k] for r in R]):+.4f} (p {one([r[k] for r in R]):.3f})" for k in ('all','excess','deficit')))
    if nm=='real':
        for k in ('dlen','dmin'):
            s=spearmanr([r['all'] for r in R],[r[k] for r in R]); print(f'   DEV inner-outer vs {k}: Spearman {s.statistic:+.2f} (p {s.pvalue:.3f}); mean {k} {np.mean([r[k] for r in R]):+.1f}')
        s=spearmanr([r['deficit'] for r in R],[r['dmin'] for r in R]); print(f'   deficit part vs dmin: Spearman {s.statistic:+.2f} (p {s.pvalue:.3f})')
print(); print('== 2 · words and bifolia of the shared excess (real)')
from collections import Counter
HERE=os.path.dirname(os.path.abspath(__file__))
ns={'__file__':os.path.join(HERE,'x.py')}; exec(open(os.path.join(HERE,'sheet_order.py'),encoding='utf-8').read().split('srcs = ')[0],ns)
P=ns['read'](os.path.join(ns['NOV'],'scribe','manuscript_out','real.txt')); B=ns['bifolia'](P)
C=Counter(); Nb=Counter(); per_bif=[]; n=0
for q,a,b in B:
    pl=[a+'r',a+'v',b+'r',b+'v']; key=lambda p:(P[p]['H'],P[p]['S'])
    norm=[p for p in P if key(p)==key(pl[0]) and p not in pl and P[p]['lines']]
    if len(norm)<6: continue
    n+=1; rel={}
    for p in norm+pl:
        ws=[w for l in P[p]['lines'] for w in l]; c=Counter(ws); m=len(ws) or 1; rel[p]={w:v/m for w,v in c.items()}
    used=Counter(w for p in norm for w in rel[p]); vocab=sorted(w for w,c in used.items() if c>=5)
    M=np.array([[rel[p].get(w,0) for w in vocab] for p in norm]); mu=M.mean(0); sd=M.std(0); sd[sd==0]=1
    Z={p:np.clip((np.array([rel[p].get(w,0) for w in vocab])-mu)/sd,0,None) for p in pl}
    t=lambda x,y: Z[x]*Z[y]/(np.linalg.norm(Z[x])*np.linalg.norm(Z[y]))
    d=t(a+'v',b+'r')-t(b+'v',a+'r'); per_bif.append((f'{a}|{b}',P[a+'r']['H'],P[a+'r']['S'],d.sum(),[vocab[i] for i in np.argsort(-d)[:4] if d[i]>0]))
    for w,v,zi,zj in zip(vocab,d,Z[a+'v'],Z[b+'r']):
        C[w]+=v
        if zi>1 and zj>1: Nb[w]+=1
tot=sum(C.values())
print('top words (contribution per bifolium; bifolia where BOTH inner pages are > 1 sd above their hand+section norm):')
for w,v in C.most_common(15): print(f'  {w:10} {v/n:+.4f}  both well above: {Nb[w]}')
pos=sorted([v for v in C.values() if v>0],reverse=True); print('words for half the positive mass:',int(np.searchsorted(np.cumsum(pos),sum(pos)/2))+1)
print('bifolia, largest inner-outer shared excess:')
for r in sorted(per_bif,key=lambda r:-r[3])[:10]: print(f'  {r[0]:10} hand {r[1]} {r[2]:12} {r[3]:+.3f}  {", ".join(r[4])}')
