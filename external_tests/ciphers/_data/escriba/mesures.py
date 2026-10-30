# Bateria de mesures per comparar un text (real o generat) amb el Voynich.
# Part 1: les 27 mesures de nit_2026-09-27_outputs/generator.py (evaluate), copiades aquí sense canvis de fons.
# Part 2: mesures noves, una per regla del reglament (REGLES_DEL_SISTEMA.md), que el generador de la nit no mirava.
# Un text és una llista de línies: dict(page, sheet, lang, ps, pe, ws=[mots], gb=[bool: forat de dibuix abans del mot]).
import re, math, random, json, os, numpy as np, pandas as pd
from collections import Counter, defaultdict
from scipy.stats import spearmanr
GL=re.compile(r'cth|ckh|cph|cfh|ch|sh|[a-z]'); gl=lambda w: GL.findall(w)
GALL={'k','t','p','f','cth','ckh','cph','cfh'}; PF={'p','f','cph','cfh'}; CLOSED=('m','ly','ry','g','sy')
HERE=os.path.dirname(os.path.abspath(__file__)); NOV=os.path.dirname(HERE)   # = ciphers/_data
CSV=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(NOV))),'df_lines_ZL3b_strokes.csv')
# ---------------- dades reals ----------------
def clean(t):
    t=re.sub(r'<%>|<\$>','',str(t)); t=t.replace('<->','#'); t=re.sub(r'<[^>]*>','',t); t=re.sub(r'\[([^:\]]*):[^\]]*\]',r'\1',t); t=re.sub(r'\{([^}]*)\}',r'\1',t); return t   # {…} són lligadures: es conserva el contingut (corregit 14/10: hi havia un byte x01 i els mots amb lligadura es perdien)
OK=set('abcdefghiklmnopqrstyj')
def load_real():
    Z=pd.read_csv(CSV,dtype={'davis_hand':str})
    Z=Z[(Z.is_label==0)&(Z.locus_generic=='P')]
    L=[]
    for r in Z.itertuples():
        parts=[p for p in re.split(r'([.#])',clean(r.text_eva_raw)) if p]; ws=[]; gb=[]; cur=False
        for p in parts:
            if p=='#': cur=True; continue
            if p=='.': continue
            w=p.replace(',','')
            if w and all(c in OK for c in w): ws.append(w); gb.append(cur)
            cur=False
        if ws: L.append(dict(page=r.page_tag,quire=str(r.quire),locus=f'{r.page_tag}.{r.locus_num},{r.locus_full}',sheet=str(r.sheet_id),lang=str(r.currier_language),hand=str(r.davis_hand),section=str(r.section),
                              ps=int(r.paragraph_start),pe=int(r.paragraph_end),ws=ws,gb=gb))
    return L
# ---------------- utilitats ----------------
def lev(a,b):
    d=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        p,d[0]=d[0],i
        for j,cb in enumerate(b,1): p,d[j]=d[j],min(d[j]+1,d[j-1]+1,p+(ca!=cb))
    return d[-1]
def MI(pairs):
    n=len(pairs); xy=Counter(pairs); x=Counter(a for a,_ in pairs); y=Counter(b for _,b in pairs)
    return sum(v/n*math.log2((v/n)/((x[a]/n)*(y[b]/n))) for (a,b),v in xy.items())
def interior_pairs(LINES,k,fa,fb,shuffle=False,rng=None):
    P=[]; pools=defaultdict(list)
    for l in LINES:
        ws=l['ws']
        for i in range(1,len(ws)-1): pools[i].append(ws[i])
    if shuffle:
        for i in pools: rng.shuffle(pools[i])
    it={i:iter(v) for i,v in pools.items()}
    for l in LINES:
        ws=l['ws']; n=len(ws)
        inner=[next(it[i]) if shuffle else ws[i] for i in range(1,n-1)]
        for i in range(len(inner)-k): P.append((fa(inner[i]),fb(inner[i+k])))
    return P
def split_prefix(w):
    if w[0] in 'ao': return 'nu',w
    if w[:2] in ('da','do'): return 'd',w[1:]
    if w[:2] in ('sa','so'): return 's',w[1:]
    if w[:2]=='qo': return 'q',w[1:]
    return None,None
def delvars(w):
    g=gl(w); return {''.join(g[:i]+g[i+1:]) for i in range(len(g))}|{w}
SLOTS=None
def slot_ok(w):
    global SLOTS
    if SLOTS is None: SLOTS=[set(s) for s in json.load(open(os.path.join(NOV,'nit_2026-09-27_outputs','slots.json')))]
    g=re.findall(r'cth|ckh|cph|cfh|ch|sh|e+|i+|[a-z]',w); cur=-1
    for x in g:
        k=next((k for k in range(cur+1,len(SLOTS)) if x in SLOTS[k]),None)
        if k is None: return False
        cur=k
    return True
# ---------------- la bateria ----------------
def evaluate(LINES,seed=0):
    rng=random.Random(seed); R={}
    toks=[w for l in LINES for w in l['ws']]; N=len(toks); c=Counter(toks)
    adj=[(a,b) for l in LINES for a,b in zip(l['ws'],l['ws'][1:])]
    # ===== part 1 (bateria de la nit) =====
    R['AA %']=100*np.mean([a==b for a,b in adj]); R['AA / atzar']=R['AA %']/100/sum((v/N)**2 for v in c.values())
    ip=interior_pairs(LINES,1,lambda w:w,lambda w:w); ips=interior_pairs(LINES,1,lambda w:w,lambda w:w,True,rng)
    R['quasi(ed=1) / base']=np.mean([lev(a,b)==1 for a,b in ip])/np.mean([lev(a,b)==1 for a,b in ips])
    for k in [2,3,5]:
        r=np.mean([a==b for a,b in interior_pairs(LINES,k,lambda w:w,lambda w:w)]); s=np.mean([a==b for a,b in interior_pairs(LINES,k,lambda w:w,lambda w:w,True,rng)])
        R[f'repetició k={k} / base']=r/s
    cnt=Counter(); nx=Counter()
    for a,b in adj: cnt[a]+=1; nx[a]+=(a==b)
    freq=[w for w in cnt if cnt[w]>=80]; ratios=[(nx[w]/cnt[w])/(c[w]/N) for w in freq]
    R['mots freq. amb rep >3x atzar (%)']=100*np.mean([r>3 for r in ratios]) if ratios else np.nan
    R['mots freq. amb rep <0.3x (%)']=100*np.mean([r<0.3 for r in ratios]) if ratios else np.nan
    for k in [1,2,3]:
        r=MI(interior_pairs(LINES,k,lambda w:w[-1],lambda w:w[0])); s=MI(interior_pairs(LINES,k,lambda w:w[-1],lambda w:w[0],True,rng)); R[f'MI frontera k={k}']=r-s
    n=len(adj); xy=Counter((a[-1],b[0]) for a,b in adj); x=Counter(a[-1] for a,_ in adj); y=Counter(b[0] for _,b in adj)
    lift=lambda a,b:(xy[(a,b)]/x[a])/(y[b]/n) if x[a] and y[b] else float('nan')
    R['lift y|q']=lift('y','q'); R['lift r|a']=lift('r','a'); R['lift y|a']=lift('y','a'); R['lift n|q']=lift('n','q')
    fw=[l['ws'][0] for l in LINES if len(l['ws'])>=4]; lw=[l['ws'][-1] for l in LINES if len(l['ws'])>=4]
    R['1r mot comença ch/sh (%)']=100*np.mean([w[:2] in ('ch','sh') for w in fw]); R['1r mot comença y (%)']=100*np.mean([w[0]=='y' for w in fw])
    R['últim mot -m (%)']=100*np.mean([w.endswith('m') for w in lw])
    long_=[l['ws'][-1] for l in LINES if len(l['ws'])>=10]; short=[l['ws'][-1] for l in LINES if 1<=len(l['ws'])<=4]
    R['-m final: línies 10+ / 1-4 mots']=np.mean([w.endswith('m') for w in long_])/max(1e-9,np.mean([w.endswith('m') for w in short]))
    G=[]; cur=[]; prev=None
    for l in LINES:
        if prev is None or l['page']!=prev['page'] or l['ps']==1:
            if len(cur)>=2: G.append(cur)
            cur=[]
        if l['ps']==0: cur.append(gl(l['ws'][0])[0])
        prev=l
    if len(cur)>=2: G.append(cur)
    def same(G,d): return np.mean([(a==b) for g in G for a,b in zip(g,g[d:])])
    for d in [1,2,3]:
        r=same(G,d); s=np.mean([same([rng.sample(g,len(g)) for g in G],d) for _ in range(10)]); R[f'1r glif línia n-{d}=n / nul']=r/s
    R['glifs inicials distints/paràgraf (4+ línies)']=np.mean([len(set(g)) for g in G if len(g)>=4])
    aa1=[a==b for l in LINES if l['ps']==1 for a,b in zip(l['ws'],l['ws'][1:])]; aa0=[a==b for l in LINES if l['ps']==0 for a,b in zip(l['ws'],l['ws'][1:])]
    R['AA 1a línia paràgraf / resta']=np.mean(aa1)/np.mean(aa0)
    R['Spearman longitud veïns']=spearmanr(*zip(*[(len(a),len(b)) for a,b in ip])).correlation
    R['tipus']=len(c); R['hàpax (%)']=100*sum(1 for v in c.values() if v==1)/len(c)
    # ===== part 2 (regles del reglament) =====
    # mot (R2.x, R13.x)
    R['[R2.1] mots dins la gramàtica de slots (%)']=100*np.mean([slot_ok(w) for w in rng.sample(toks,min(6000,N))])
    R['[R2.2] mots amb 2+ gallows (%)']=100*np.mean([sum(g in GALL for g in gl(w))>=2 for w in toks])
    R['[R2.6] longitud mitjana (glifs)']=np.mean([len(gl(w)) for w in toks]); R['[R2.6] desv. típica longitud']=np.std([len(gl(w)) for w in toks])
    R['[R13.7] e i i al mateix mot / esperat']=np.mean([('e' in w and 'i' in w) for w in toks])/(np.mean(['e' in w for w in toks])*np.mean(['i' in w for w in toks]))
    # frontera (R3.3, R3.4)
    T=[]
    for l in LINES:
        for i in range(1,len(l['ws'])):
            k,core=split_prefix(l['ws'][i])
            if k: T.append((gl(l['ws'][i-1])[-1],''.join(gl(core)[:2]),k))
    def Hc(rows,f):
        by=defaultdict(Counter)
        for r in rows: by[f(r)][r[2]]+=1
        n_=len(rows); return sum(sum(cn.values())/n_*(-sum(v/sum(cn.values())*math.log2(v/sum(cn.values())) for v in cn.values())) for cn in by.values())
    R['[R3.3] H(prefix) marginal']=Hc(T,lambda r:0); R['[R3.3] H(prefix | glif anterior, nucli)']=Hc(T,lambda r:(r[0],r[1]))
    after_y=[k for g,c2,k in T if g=='y' and c2[:1]=='o']; R['[R3.3] q- davant o- després de -y (%)']=100*np.mean([k=='q' for k in after_y]) if after_y else np.nan
    pf=[l['ws'][0] for l in LINES if l['ps']==1]; lf=[l['ws'][0] for l in LINES if l['ps']==0]; mid=[w for l in LINES for w in l['ws'][1:-1]]
    R['[R3.4] q- 1r mot de paràgraf (%)']=100*np.mean([w[0]=='q' for w in pf]); R['[R3.4] q- 1r mot de línia (%)']=100*np.mean([w[0]=='q' for w in lf]); R['[R3.4] q- interior (%)']=100*np.mean([w[0]=='q' for w in mid])
    # línia (R4.2, R4.3, R14.1, R14.2, R14.3)
    R['[R4.2] a- a inici de línia (%)']=100*np.mean([w[0]=='a' for w in lf]); R['[R4.2] d/s/y- a inici de línia (%)']=100*np.mean([w[0] in 'dsy' and w[:2]!='sh' for w in lf])
    R['[R14.1] gallows nua a inici de línia (%)']=100*np.mean([gl(w)[0] in GALL for w in lf])
    lastnf=[l['ws'][-1] for l in LINES if l['pe']==0 and len(l['ws'])>1]; lastf=[l['ws'][-1] for l in LINES if l['pe']==1 and len(l['ws'])>1]
    R['[R4.3] tancades a l\'últim mot, línies no finals (%)']=100*np.mean([w.endswith(CLOSED) for w in lastnf]); R['[R4.3] tancades a l\'interior (%)']=100*np.mean([w.endswith(CLOSED) for w in mid])
    R['[R14.2] tancades a l\'últim mot de paràgraf (%)']=100*np.mean([w.endswith(CLOSED) for w in lastf])
    sec=[l['ws'][1] for l in LINES if len(l['ws'])>=5]; R['[R14.3] longitud 2n mot / 1r']=np.mean([len(gl(w)) for w in sec])/np.mean([len(gl(l['ws'][0])) for l in LINES if len(l['ws'])>=5])
    # paràgraf (R5.1, R5.2, R1.3)
    R['[R5.1] gallows al 1r mot de paràgraf (%)']=100*np.mean([any(g in GALL for g in gl(w)) for w in pf])
    def pfsh(ws_):
        g=[x for w in ws_ for x in gl(w) if x in GALL]; return 100*sum(x in PF for x in g)/max(1,len(g))
    R['[R1.3] p/f entre gallows, 1a línia de paràgraf (%)']=pfsh([w for l in LINES if l['ps']==1 for w in l['ws'][1:]]); R['[R1.3] p/f entre gallows, línies interiors (%)']=pfsh([w for l in LINES if l['ps']==0 for w in l['ws']])
    fl=[w for l in LINES if l['ps']==1 for w in l['ws'][1:]]; ol=[w for l in LINES if l['ps']==0 for w in l['ws']]
    R['[R5.2] longitud 1a línia / resta']=np.mean([len(gl(w)) for w in fl])/np.mean([len(gl(w)) for w in ol])
    # dibuix (R6.1, R6.2)
    pre=[l['ws'][i-1] for l in LINES for i in range(1,len(l['ws'])) if l['gb'][i] and i-1>0]; post=[l['ws'][i] for l in LINES for i in range(1,len(l['ws'])) if l['gb'][i] and i<len(l['ws'])-1]
    R['[R6.1] tancades abans del forat (%)']=100*np.mean([w.endswith(CLOSED) for w in pre]) if pre else np.nan
    R['[R6.1] d/s/y- després del forat (%)']=100*np.mean([w[0] in 'dsy' and w[:2]!='sh' for w in post]) if post else np.nan
    R['[R6.1] q- després del forat (%)']=100*np.mean([w[0]=='q' for w in post]) if post else np.nan
    # dissimilació per glif (H8)
    GG=[]; cur=[]; prev=None
    for l in LINES:
        if prev is None or l['page']!=prev['page'] or l['ps']==1:
            if len(cur)>=2: GG.append(cur)
            cur=[]
        if l['ps']==0: cur.append(gl(l['ws'][0])[0])
        prev=l
    if len(cur)>=2: GG.append(cur)
    def same_after(GG,cond):
        P=[(a==b) for g in GG for a,b in zip(g,g[1:]) if cond(a)]; return np.mean(P) if P else np.nan
    rs=same_after(GG,lambda a:a in GALL); ns=np.mean([same_after([rng.sample(g,len(g)) for g in GG],lambda a:a in GALL) for _ in range(10)])
    R['[H8] mateix 1r glif després de gallows / nul']=rs/ns
    # pàgina i full (R7.1, R7.2, R7.4, A1)
    bypage=defaultdict(list)
    for l in LINES: bypage[l['page']].append(l)
    par=0; tot=0; dist=[]
    for pg,ls in bypage.items():
        seen={}
        for li,l in enumerate(ls):
            for w in l['ws']:
                dv=delvars(w); hit=[seen[d] for d in dv if d in seen]
                if hit: par+=1; dist.append(li-max(hit))
                tot+=1
            for w in l['ws']:
                for d in delvars(w): seen[d]=li
    R['[A1] mots amb bessó (ED≤1) abans a la pàgina (%)']=100*par/tot; R['[A1] línies fins al bessó més proper (mediana)']=float(np.median(dist)) if dist else np.nan
    # sobredispersió per pàgina de q- davant o- després de -y (H2)
    pg_rows=defaultdict(list)
    for l in LINES:
        for i in range(1,len(l['ws'])):
            w=l['ws'][i]
            if l['ws'][i-1][-1]=='y' and w[0] in 'oq' and (w[0]=='o' or w[:2]=='qo'): pg_rows[l['page']].append(w[0]=='q')
    allv=[v for vs in pg_rows.values() for v in vs]; p0=np.mean(allv)
    num=sum((sum(vs)-len(vs)*p0)**2 for vs in pg_rows.values()); den=sum(len(vs)*p0*(1-p0) for vs in pg_rows.values())
    R['[H2] sobredispersió per pàgina de q- (després de -y)']=num/den if den else np.nan   # textos de control sense q-
    # full com a sessió (G6): cosinus de vocabulari, altre foli del mateix full / foli adjacent d'un altre full
    vec={pg:Counter(w for l in ls for w in l['ws']) for pg,ls in bypage.items()}; sheet={pg:ls[0]['sheet'] for pg,ls in bypage.items()}
    order=list(bypage); df_=Counter(w for v in vec.values() for w in v); NP=len(vec)
    def cos(a,b):
        A=vec[a]; B=vec[b]; wa={w:v*math.log(NP/df_[w]) for w,v in A.items()}; wb={w:v*math.log(NP/df_[w]) for w,v in B.items()}
        num=sum(wa[w]*wb.get(w,0) for w in wa); return num/(math.sqrt(sum(v*v for v in wa.values()))*math.sqrt(sum(v*v for v in wb.values()))+1e-9)
    fol=lambda p: re.sub(r'[rv]\d*$','',p)
    ss=[cos(a,b) for i,a in enumerate(order) for b in order[i+1:i+40] if sheet[a]==sheet[b] and fol(a)!=fol(b)]
    adjp=[cos(a,b) for i,a in enumerate(order) for b in order[i+1:i+5] if sheet[a]!=sheet[b]]
    R['[G6] cosinus mateix full / pàgines veïnes d\'altres fulls']=np.mean(ss)/np.mean(adjp) if ss and adjp else np.nan
    # ===== part 3: el que veu l'ull (28/09, després de «no s'assemblen de res») =====
    # mots amb un trigrama de glifs (amb inici i fi) que al text real surt ≤ 3 cops: al real n'hi ha un cada 13 mots (7,9%)
    global _TRI
    if _TRI is None:
        _TRI=Counter()
        for l in load_real():
            for w in l['ws']:
                g=['^']+gl(w)+['$']
                for i in range(len(g)-2): _TRI[tuple(g[i:i+3])]+=1
    strange=0
    for w in toks:
        g=['^']+gl(w)+['$']
        if any(_TRI.get(tuple(g[i:i+3]),0)<=3 for i in range(len(g)-2)): strange+=1
    R['[ull] mots estranys (trigrama rar al real) (%)']=100*strange/N
    R['[ull] mots estranys per línia']=strange/len(LINES)
    # ===== part 4 (14/10): el vocabulari de pàgina i els mots llargs, que l'ull nota i les mesures d'abans no =====
    global _SEC
    if _SEC is None: _SEC={l['page']:l['section'] for l in load_real()}
    hasE=lambda w: 'e' in w                     # bloc de mot amb e (-y/-dy) contra sense e (-aiin/-ar/-ol), R2.4
    pg_e=defaultdict(list)
    for l in LINES:
        for w in l['ws']: pg_e[l['page']].append(hasE(w))
    p0=np.mean([v for vs in pg_e.values() for v in vs])
    R['[pàg] sobredispersió per pàgina de mots amb e']=sum((sum(vs)-len(vs)*p0)**2 for vs in pg_e.values())/sum(len(vs)*p0*(1-p0) for vs in pg_e.values())
    bysec=defaultdict(list)
    for l in LINES:
        for w in l['ws']: bysec[_SEC.get(l['page'],'?')].append(w)
    fe=lambda ws: np.mean([hasE(w) for w in ws]) if ws else np.nan
    R['[secció] mots amb e: biològic / herbari']=fe(bysec['biological'])/fe(bysec['herbal'])
    R['[secció] mots en -edy: biològic (%)']=100*np.mean([w.endswith('edy') for w in bysec['biological']]) if bysec['biological'] else np.nan
    R['[pàg] quota del mot més freqüent de la pàgina (mediana, %)']=float(np.median([100*Counter(w for l in ls for w in l['ws']).most_common(1)[0][1]/sum(len(l['ws']) for l in ls) for ls in bypage.values() if sum(len(l['ws']) for l in ls)>=60]))
    R['[ull] mots de 8 glifs o més (%)']=100*np.mean([len(gl(w))>=8 for w in toks])
    # ===== part 5 (19/10): les mesures estàndard i l'abast llarg que va demanar Mauro a voynich.ninja =====
    def _H(c):
        n=sum(c.values()); return -sum(v/n*math.log2(v/n) for v in c.values())
    def _hk(seqs,k):                               # entropia condicional de caràcter d'ordre k (text de línia, amb espais)
        j=Counter(); cx=Counter()
        for t in seqs:
            t=['^']*k+list(t)
            for i in range(k,len(t)): j[tuple(t[i-k:i+1])]+=1; cx[tuple(t[i-k:i])]+=1
        n=sum(j.values()); return -sum(v/n*math.log2(v/cx[key[:-1]]) for key,v in j.items())
    txt=[' '.join(l['ws']) for l in LINES]
    R['[text] entropia de caràcter h1']=_H(Counter(ch for t in txt for ch in t))
    R['[text] entropia condicional h2']=_hk(txt,1); R['[text] entropia condicional h3']=_hk(txt,2)
    fr=np.array(sorted(c.values(),reverse=True),float); rk=np.arange(1,len(fr)+1); m_=rk<=1000
    R['[text] pendent de Zipf (1.000 primers)']=-np.polyfit(np.log(rk[m_]),np.log(fr[m_]),1)[0]
    ln=Counter(len(gl(w)) for w in toks)
    R['[llargada] mots de 2-3 glifs (%)']=100*(ln[2]+ln[3])/N; R['[llargada] mots de 5-6 glifs (%)']=100*(ln[5]+ln[6])/N
    pages=list(dict.fromkeys(l['page'] for l in LINES)); pv=defaultdict(Counter)
    for l in LINES: pv[l['page']].update(l['ws'])
    vi={w:i for i,w in enumerate(c)}; V=np.zeros((len(pages),len(vi)))
    for i,pg in enumerate(pages):
        for w,k_ in pv[pg].items(): V[i,vi[w]]=k_
    V/=np.linalg.norm(V,axis=1,keepdims=True)+1e-12
    cosd=lambda d: float(np.mean(np.sum(V[:-d]*V[d:],axis=1)))
    c1,c10,c100=cosd(1),cosd(10),cosd(100)
    R['[abast] vocabulari compartit, pàgines veïnes (cosinus)']=c1; R['[abast] vocabulari compartit, a 10 pàgines']=c10
    R['[abast] vocabulari compartit, a 100 pàgines']=c100; R['[abast] veïnes / a 100 pàgines']=c1/c100
    pos=defaultdict(list)
    for i,w in enumerate(toks): pos[w].append(i)
    R['[abast] ràfegues dels 50 mots més freqüents (CV dels intervals)']=float(np.mean([np.diff(pos[w]).std()/np.diff(pos[w]).mean() for w,_ in c.most_common(50)]))
    npg=np.array([sum(pv[pg].values()) for pg in pages],float); od=[]
    for w,_ in c.most_common(50):
        x=np.array([pv[pg][w] for pg in pages],float); e=npg*c[w]/N; od.append(((x-e)**2/e).sum()/(len(pages)-1))
    R['[abast] sobredispersió per pàgina dels 50 mots més freqüents']=float(np.mean(od))
    return R
_TRI=None
_SEC=None
def load_corpus(path):
    # un altre text amb la mateixa estructura de línies (controls amb significat conegut, 19/10): JSON amb la llista de línies
    return json.load(open(path,encoding='utf-8'))
def set_reference(L):
    # la referència de les mesures que miren el text real sencer (trigrames rars, secció): per a un text de control, el seu
    global _TRI,_SEC
    _TRI=Counter()
    for l in L:
        for w in l['ws']:
            g=['^']+gl(w)+['$']
            for i in range(len(g)-2): _TRI[tuple(g[i:i+3])]+=1
    _SEC={l['page']:l.get('section','?') for l in L}
def compare(Rr,Rg,tol=0.25):
    """quines mesures reprodueix: |gen/real − 1| < tol (per a valors reals prop de zero, diferència absoluta < 0,01)"""
    ok={}
    for k,v in Rr.items():
        g=Rg.get(k,np.nan)
        if v!=v or g!=g: ok[k]=False; continue
        ok[k]=(abs(g-v)<0.01) if abs(v)<0.02 else (abs(g/v-1)<tol)
    return ok
if __name__=='__main__':
    L=load_real(); R=evaluate(L)
    json.dump({k:float(v) for k,v in R.items()},open(os.path.join(HERE,'mesures_real.json'),'w',encoding='utf-8'),indent=1,ensure_ascii=False)
    for k,v in R.items(): print(f'{k:62} {v:10.3f}')
