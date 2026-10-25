import pandas as pd, numpy as np, re, random, math, sys, json
from collections import Counter, defaultdict
from scipy.stats import spearmanr
SP='nit_2026-09-27_outputs/'
random.seed(0); np.random.seed(0)
# ===================== dades reals =====================
Z=pd.read_csv('df_lines_ZL3b_strokes.csv'); Z=Z[(Z.is_label==0)&(Z.locus_generic=='P')].copy()
def clean_eva(t):
    t=re.sub(r'<[^>]*>','',t); t=re.sub(r'\[([^:\]]*):[^\]]*\]',r'\1',t); t=re.sub(r'\{[^}]*\}','',t); return t
OK=set('abcdefghiklmnopqrstyj'); GL=re.compile(r'cth|ckh|cph|cfh|ch|sh|[a-z]')
REAL=[]
for r in Z.itertuples():
    ws=[w.replace(',','') for w in clean_eva(str(r.text_eva)).split('.') if w]; ws=[w for w in ws if w and all(c in OK for c in w)]
    if ws: REAL.append(dict(page=r.page_tag,ps=int(r.paragraph_start),pe=int(r.paragraph_end),ws=ws))
gl=lambda w: GL.findall(w)
def lev(a,b):
    d=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        p,d[0]=d[0],i
        for j,cb in enumerate(b,1): p,d[j]=d[j],min(d[j]+1,d[j-1]+1,p+(ca!=cb))
    return d[-1]
# ===================== model de glifs (ordre 2, lletres + espai) =====================
ORDER=2
ctx=defaultdict(Counter)
for l in REAL:
    s=['^']*ORDER+list(' '.join(l['ws']))+['$']
    for i in range(ORDER,len(s)): ctx[tuple(s[i-ORDER:i])][s[i]]+=1
BIG=set()
for l in REAL:
    for w in l['ws']:
        for a,b in zip('^'+w,w+'$'): BIG.add((a,b))
def wellformed(w): return len(w)>0 and all((a,b) in BIG for a,b in zip('^'+w,w+'$'))
def gen_word(hist):
    """genera un mot a partir de l'historial (2 símbols); retorna mot"""
    h=list(hist); out=''
    for _ in range(20):
        c=ctx.get(tuple(h[-ORDER:]))
        if not c: break
        nx=random.choices(list(c),weights=list(c.values()))[0]
        if nx in (' ','$'):
            if out: break
            else: continue
        out+=nx; h.append(nx)
    return out if out else 'o'
# ===================== estadístiques d'edició empíriques =====================
sub=Counter(); ins=Counter(); dele=Counter(); nsub=nins=ndel=0
for l in REAL:
    for a,b in zip(l['ws'],l['ws'][1:]):
        ga,gb=gl(a),gl(b)
        if ga==gb: continue
        if len(ga)==len(gb):
            d=[(x,y) for x,y in zip(ga,gb) if x!=y]
            if len(d)==1: sub[d[0]]+=1; sub[(d[0][1],d[0][0])]+=1; nsub+=1
        elif len(gb)==len(ga)+1:
            for i in range(len(gb)):
                if gb[:i]+gb[i+1:]==ga: ins[gb[i]]+=1; nins+=1; break
        elif len(ga)==len(gb)+1:
            for i in range(len(ga)):
                if ga[:i]+ga[i+1:]==gb: dele[ga[i]]+=1; ndel+=1; break
subby=defaultdict(Counter)
for (x,y),c in sub.items(): subby[x][y]+=c
def modify(w):
    g=gl(w)
    for _ in range(6):
        r=random.random()*(nsub+nins+ndel); g2=g[:]
        if r<nsub:
            i=random.randrange(len(g2)); c=subby.get(g2[i])
            if not c: continue
            g2[i]=random.choices(list(c),weights=list(c.values()))[0]
        elif r<nsub+nins:
            i=random.randrange(len(g2)+1); g2.insert(i,random.choices(list(ins),weights=list(ins.values()))[0])
        else:
            if len(g2)<2: continue
            del g2[random.randrange(len(g2))]
        w2=''.join(g2)
        if w2!=w and wellformed(w2): return w2
    return w
# ===================== generador =====================
def generate(r_copy=0.15,r_mod=0.5,vertical=True,recency=(1.0,0.5,0.25),m_rule=True,seed=0):
    random.seed(seed)
    out=[]; prev_lines=[]; prev_page=None; above_first=None
    for l in REAL:
        n=len(l['ws'])
        if l['page']!=prev_page: prev_lines=[]; above_first=None; prev_page=l['page']
        if l['ps']==1: above_first=None
        ws=[]
        for i in range(n):
            hist=('^','^') if i==0 else (ws[-1][-1],' ')
            pool=[];wts=[]
            for w in ws: pool.append(w); wts.append(recency[0])
            for k,pl in enumerate(prev_lines[::-1][:2]):
                for w in pl: pool.append(w); wts.append(recency[k+1])
            if i>0 and pool and random.random()<r_copy:
                w=random.choices(pool,weights=wts)[0]
                if random.random()<r_mod: w=modify(w)
            else:
                w=gen_word(hist)
                if i==0 and vertical and above_first is not None:
                    for _ in range(4):
                        if gl(w)[0]!=above_first: break
                        w=gen_word(hist)
            ws.append(w)
        if m_rule and ws[-1].endswith('iin') and random.random()<min(0.7,max(0,0.06*(n-3))): ws[-1]=ws[-1][:-3]+'m'
        above_first=gl(ws[0])[0]
        out.append(dict(page=l['page'],ps=l['ps'],pe=l['pe'],ws=ws)); prev_lines.append(ws)
    return out
# ===================== bateria d'avaluació =====================
def H(c):
    n=sum(c.values()); return -sum(v/n*math.log2(v/n) for v in c.values()) if n else 0
def MI(pairs):
    n=len(pairs); xy=Counter(pairs); x=Counter(a for a,_ in pairs); y=Counter(b for _,b in pairs)
    return sum(v/n*math.log2((v/n)/((x[a]/n)*(y[b]/n))) for (a,b),v in xy.items())
def interior_pairs(LINES,k,fa,fb,shuffle=False):
    P=[]; pools=defaultdict(list)
    for l in LINES:
        ws=l['ws']; n=len(ws)
        for i in range(1,n-1): pools[i].append(ws[i])
    if shuffle:
        for i in pools: random.shuffle(pools[i])
    it={i:iter(v) for i,v in pools.items()}
    for l in LINES:
        ws=l['ws']; n=len(ws)
        inner=[next(it[i]) if shuffle else ws[i] for i in range(1,n-1)]
        for i in range(len(inner)-k): P.append((fa(inner[i]),fb(inner[i+k])))
    return P
def evaluate(LINES,full=True):
    R={}
    toks=[w for l in LINES for w in l['ws']]; N=len(toks); c=Counter(toks)
    adj=[(a,b) for l in LINES for a,b in zip(l['ws'],l['ws'][1:])]
    R['AA %']=100*np.mean([a==b for a,b in adj]); R['AA / atzar']=R['AA %']/100/sum((v/N)**2 for v in c.values())
    ip=interior_pairs(LINES,1,lambda w:w,lambda w:w); ips=interior_pairs(LINES,1,lambda w:w,lambda w:w,True)
    R['quasi(ed=1) / base']=np.mean([lev(a,b)==1 for a,b in ip])/np.mean([lev(a,b)==1 for a,b in ips])
    if not full: return R
    for k in [2,3,5]:
        r=np.mean([a==b for a,b in interior_pairs(LINES,k,lambda w:w,lambda w:w)]); s=np.mean([a==b for a,b in interior_pairs(LINES,k,lambda w:w,lambda w:w,True)])
        R[f'repetició k={k} / base']=r/s
    # especificitat de mot
    cnt=Counter(); nx=Counter()
    for a,b in adj: cnt[a]+=1; nx[a]+=(a==b)
    freq=[w for w in cnt if cnt[w]>=80]
    ratios=[(nx[w]/cnt[w])/(c[w]/N) for w in freq]
    R['mots freq. amb rep >3x atzar (%)']=100*np.mean([r>3 for r in ratios]); R['mots freq. amb rep <0.3x (%)']=100*np.mean([r<0.3 for r in ratios])
    # MI frontera
    for k in [1,2,3]:
        r=MI(interior_pairs(LINES,k,lambda w:w[-1],lambda w:w[0])); s=MI(interior_pairs(LINES,k,lambda w:w[-1],lambda w:w[0],True)); R[f'MI frontera k={k}']=r-s
    n=len(adj); xy=Counter((a[-1],b[0]) for a,b in adj); x=Counter(a[-1] for a,_ in adj); y=Counter(b[0] for _,b in adj)
    lift=lambda a,b:(xy[(a,b)]/x[a])/(y[b]/n) if x[a] and y[b] else float('nan')
    R['lift y|q']=lift('y','q'); R['lift r|a']=lift('r','a'); R['lift y|a']=lift('y','a'); R['lift n|q']=lift('n','q')
    # posició
    fw=[l['ws'][0] for l in LINES if len(l['ws'])>=4]; lw=[l['ws'][-1] for l in LINES if len(l['ws'])>=4]
    R['1r mot comença ch/sh (%)']=100*np.mean([w[0] in 'cs' and w[:2] in ('ch','sh') for w in fw]); R['1r mot comença y (%)']=100*np.mean([w[0]=='y' for w in fw])
    R['últim mot -m (%)']=100*np.mean([w.endswith('m') for w in lw])
    long_=[l['ws'][-1] for l in LINES if len(l['ws'])>=10]; short=[l['ws'][-1] for l in LINES if 1<=len(l['ws'])<=4]
    R['-m final: línies 10+ / 1-4 mots']=np.mean([w.endswith('m') for w in long_])/max(1e-9,np.mean([w.endswith('m') for w in short]))
    # dissimilació vertical
    G=[]; cur=[]; prev=None
    for l in LINES:
        if prev is None or l['page']!=prev['page'] or l['ps']==1:
            if len(cur)>=2: G.append(cur)
            cur=[]
        if l['ps']==0: cur.append(gl(l['ws'][0])[0])
        prev=l
    if len(cur)>=2: G.append(cur)
    def same(G,d):
        P=[(a==b) for g in G for a,b in zip(g,g[d:])]; return np.mean(P)
    for d in [1,2,3]:
        r=same(G,d); s=np.mean([same([random.sample(g,len(g)) for g in G],d) for _ in range(10)]); R[f'1r glif línia n-{d}=n / nul']=r/s
    R['glifs inicials distints/paràgraf (4+ línies)']=np.mean([len(set(g)) for g in G if len(g)>=4])
    # primera línia de paràgraf: AA
    aa1=[a==b for l in LINES if l['ps']==1 for a,b in zip(l['ws'],l['ws'][1:])]; aa0=[a==b for l in LINES if l['ps']==0 for a,b in zip(l['ws'],l['ws'][1:])]
    R['AA 1a línia paràgraf / resta']=np.mean(aa1)/np.mean(aa0)
    # longitud veïns
    R['Spearman longitud veïns']=spearmanr(*zip(*[(len(a),len(b)) for a,b in ip])).correlation
    # jerarquia: idèntics mateixa línia vs mateixa pàgina altra línia
    allw=[(w,l['page'],i) for i,l in enumerate(LINES) for w in l['ws']]
    def samp(cond,n=40000):
        k=0;s=0;t=0
        while k<n and t<n*40:
            t+=1; a=random.choice(allw); b=random.choice(allw)
            if a is b or not cond(a,b): continue
            k+=1; s+=(a[0]==b[0])
        return s/k
    R['idèntics mateixa línia / mateixa pàgina']=samp(lambda a,b:a[2]==b[2])/samp(lambda a,b:a[1]==b[1] and a[2]!=b[2])
    R['tipus']=len(c); R['hàpax (%)']=100*sum(1 for v in c.values() if v==1)/len(c)
    return R
if __name__=='__main__':
    print('avaluant el text real...'); Rr=evaluate(REAL)
    json.dump(Rr,open(SP+'gen_real.json','w'))
    # ---- graella per ajustar r_copy, r_mod sobre AA i quasi ----
    print('\n### graella (només AA/atzar i quasi/base):  objectiu real AA/atzar=%.2f  quasi/base=%.2f'%(Rr['AA / atzar'],Rr['quasi(ed=1) / base']))
    best=None
    for rc in [0.05,0.10,0.15,0.20,0.30]:
        for rm in [0.3,0.5,0.7,0.85]:
            Rg=evaluate(generate(rc,rm,seed=1),full=False)
            err=abs(math.log(Rg['AA / atzar']/Rr['AA / atzar']))+abs(math.log(Rg['quasi(ed=1) / base']/Rr['quasi(ed=1) / base']))
            print(f'  r_copy={rc:.2f} r_mod={rm:.2f}: AA/atzar {Rg["AA / atzar"]:.2f}  quasi/base {Rg["quasi(ed=1) / base"]:.2f}  err {err:.2f}')
            if best is None or err<best[0]: best=(err,rc,rm)
    print('millor:',best)
    rc,rm=best[1],best[2]
    print('\n### avaluació completa: real vs generador (mitjana de 3 llavors) vs ablacions')
    variants={'generador':dict(r_copy=rc,r_mod=rm),'sense còpia':dict(r_copy=0.0,r_mod=rm),'sense regla vertical':dict(r_copy=rc,r_mod=rm,vertical=False),'sense regla m':dict(r_copy=rc,r_mod=rm,m_rule=False)}
    res={}
    for nm,kw in variants.items():
        rs=[evaluate(generate(seed=s,**kw)) for s in (1,2,3)]
        res[nm]={k:np.mean([r[k] for r in rs]) for k in rs[0]}
    json.dump(res,open(SP+'gen_results.json','w'))
    keys=list(Rr.keys())
    print(f"{'mesura':46}{'REAL':>9}"+''.join(f'{nm:>20}' for nm in variants))
    for k in keys:
        print(f'{k:46}{Rr[k]:9.3f}'+''.join(f'{res[nm][k]:20.3f}' for nm in variants))
