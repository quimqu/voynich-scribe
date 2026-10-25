# Page vocabulary and long words (14/10): exploration of the 'e' habit (word family per sheet/page/section) and of the length tone.
# Usage (from scribe/): PYTHONIOENCODING=utf-8 py -3 page_vocabulary.py [medium]   (medium = 3 seeds; otherwise 5)
import sys, json, numpy as np, measures as M
from scribe import Escriba
Rr=json.load(open('measures_real.json',encoding='utf-8'))
SEEDS=(1,2,3) if 'medium' in sys.argv else (1,2,3,4,5)
KS=['[page] Page overdispersion of e-words','[section] e-words: biological / herbal','[section] -edy words in biological (%)','[eye] Words of 8+ glyphs (%)','[R2.6] SD of word length','Spearman correlation of neighbour word lengths','[eye] Strange words (rare trigram in the real text) (%)','Word types']
SH=['e overdisp.','bio/herb e','-edy bio','≥8 glyphs','length SD','Spearman','strange','Word types']
CONFIGS=[('base',{}),
         ('e habit',dict(use_ehabit=True)),
         ('e habit + section dy',dict(use_ehabit=True,use_sec_dy=True)),
         ('e + dy + 3 candidates',dict(use_ehabit=True,use_sec_dy=True,len_cands=3)),
         ('e + dy + tone σ 0.45',dict(use_ehabit=True,use_sec_dy=True,sigma_len=0.45)),
         ('e + dy + 4 candidates',dict(use_ehabit=True,use_sec_dy=True,len_cands=4))]
if len(sys.argv)>1 and any('=' in a for a in sys.argv[1:]):
    kw={}
    for a in sys.argv[1:]:
        if '=' in a: k,v=a.split('='); kw[k]=(v=='True') if v in ('True','False') else (float(v) if v.replace('.','',1).isdigit() else v)
    for k in ('len_cands',):
        if k in kw: kw[k]=int(kw[k])
    CONFIGS=[('trial',kw)]
print(f"{'':34}{'reprod.':>8}{'err':>7}"+''.join(f'{s:>12}' for s in SH)); print(f"{'REAL':34}{'':15}"+''.join(f'{Rr[k]:12.2f}' for k in KS))
res={}
for nm,kw in CONFIGS:
    rs=[M.evaluate(Escriba(**kw).write(seed=s),seed=s) for s in SEEDS]; R={k:float(np.mean([r[k] for r in rs])) for k in rs[0]}
    ok=M.compare(Rr,R); err=np.median([abs(np.log(max(abs(R[k]),1e-6)/max(abs(Rr[k]),1e-6))) for k in Rr if abs(Rr[k])>=0.02])
    res[nm]=dict(kw=kw,R=R,fails=[k for k,v in ok.items() if not v])
    print(f'{nm:34}{sum(ok.values()):>4}/{len(ok)}{err:7.3f}'+''.join(f'{R[k]:12.2f}' for k in KS),flush=True)
for nm,r in res.items(): print(f'  {nm}: not reproduced: '+'; '.join(k[:38] for k in r['fails']))
if len(CONFIGS)>1: json.dump(res,open('results_page_vocabulary.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
