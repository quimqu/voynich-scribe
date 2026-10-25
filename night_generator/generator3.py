exec(open('night_generator/generator.py',encoding='utf-8').read().split("if __name__=='__main__':")[0])
import json
def generate3(r_copy=0.3,r_mod=0.85,q_vert=0.45,m_strength=0.12,first_line_factor=1.0,reset_par=False,seed=0):
    random.seed(seed)
    out=[]; prev_lines=[]; prev_page=None; above_first=None
    for l in REAL:
        n=len(l['ws'])
        if l['page']!=prev_page: prev_lines=[]; above_first=None; prev_page=l['page']
        if l['ps']==1:
            above_first=None
            if reset_par: prev_lines=[]
        rc=r_copy*(first_line_factor if l['ps']==1 else 1.0)
        ws=[]
        for i in range(n):
            hist=('^','^') if i==0 else (ws[-1][-1],' ')
            pool=[];wts=[]
            for w in ws: pool.append(w); wts.append(1.0)
            for k,pl in enumerate(prev_lines[::-1][:2]):
                for w in pl: pool.append(w); wts.append(0.5 if k==0 else 0.25)
            if i>0 and pool and random.random()<rc:
                c=ctx.get(hist,Counter()); tot=sum(c.values()) or 1
                w=random.choices(pool,weights=[wt*(c[w[0]]/tot+1e-4) for w,wt in zip(pool,wts)])[0]
                if random.random()<r_mod: w=modify(w)
            else:
                w=gen_word(hist)
                if i==0 and above_first is not None and random.random()<q_vert:
                    for _ in range(4):
                        if gl(w)[0]!=above_first: break
                        w=gen_word(hist)
            ws.append(w)
        if ws[-1].endswith('iin') and random.random()<min(0.9,max(0,m_strength*(n-3))): ws[-1]=ws[-1][:-3]+'m'
        above_first=gl(ws[0])[0]
        out.append(dict(page=l['page'],ps=l['ps'],pe=l['pe'],ws=ws)); prev_lines.append(ws)
    return out
Rr=json.load(open(SP+'gen_real.json'))
variants={'final':dict(first_line_factor=0.35,reset_par=True),'no first-line rule':dict()}
res={}
for nm,kw in variants.items():
    rs=[evaluate(generate3(seed=s,**kw)) for s in (1,2,3)]
    res[nm]={k:np.mean([r[k] for r in rs]) for k in rs[0]}
json.dump(res,open(SP+'gen_results3.json','w'))
keys=[k for k in Rr if k not in ('identical: same line / same page',)]
print(f"{'measure':46}{'REAL':>9}{'final':>12}{'no 1st-line rule':>16}{'  final/real':>12}")
for k in keys:
    fr=res['final'][k]/Rr[k] if Rr[k] not in (0,) else float('nan')
    print(f'{k:46}{Rr[k]:9.3f}{res["final"][k]:12.3f}{res["no first-line rule"][k]:16.3f}{fr:12.2f}')
# sample of generated text
random.seed(7); G=generate3(seed=11,first_line_factor=0.35,reset_par=True)
print('\ngenerated sample (one page):')
pg=G[40]['page']
for l in G:
    if l['page']==pg: print(('  ¶ ' if l['ps']==1 else '    ')+' '.join(l['ws']))
print('the same real page:')
for l in REAL:
    if l['page']==pg: print(('  ¶ ' if l['ps']==1 else '    ')+' '.join(l['ws']))
