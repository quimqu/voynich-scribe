# Vocabulari de pàgina i mots llargs (14/10): exploració de l'hàbit 'e' (família de mot per full/pàgina/secció) i del to de llargada.
# Ús (des de escriba/): PYTHONIOENCODING=utf-8 py -3 vocabulari_pagina.py [mitjà]   (mitjà = 3 llavors; si no, 5)
import sys, json, numpy as np, mesures as M
from escriba import Escriba
Rr=json.load(open('mesures_real.json',encoding='utf-8'))
SEEDS=(1,2,3) if 'mitjà' in sys.argv else (1,2,3,4,5)
KS=['[pàg] sobredispersió per pàgina de mots amb e','[secció] mots amb e: biològic / herbari','[secció] mots en -edy: biològic (%)','[ull] mots de 8 glifs o més (%)','[R2.6] desv. típica longitud','Spearman longitud veïns','[ull] mots estranys (trigrama rar al real) (%)','tipus']
SH=['sobredisp.e','bio/herb e','-edy bio','≥8 glifs','desv.llarg','Spearman','estranys','tipus']
CONFIGS=[('base',{}),
         ('hàbit e',dict(use_ehabit=True)),
         ('hàbit e + dy de secció',dict(use_ehabit=True,use_sec_dy=True)),
         ('e + dy + 3 candidats',dict(use_ehabit=True,use_sec_dy=True,len_cands=3)),
         ('e + dy + to σ 0,45',dict(use_ehabit=True,use_sec_dy=True,sigma_len=0.45)),
         ('e + dy + 4 candidats',dict(use_ehabit=True,use_sec_dy=True,len_cands=4))]
if len(sys.argv)>1 and any('=' in a for a in sys.argv[1:]):
    kw={}
    for a in sys.argv[1:]:
        if '=' in a: k,v=a.split('='); kw[k]=(v=='True') if v in ('True','False') else (float(v) if v.replace('.','',1).isdigit() else v)
    for k in ('len_cands',):
        if k in kw: kw[k]=int(kw[k])
    CONFIGS=[('prova',kw)]
print(f"{'':34}{'reprod.':>8}{'err':>7}"+''.join(f'{s:>12}' for s in SH)); print(f"{'REAL':34}{'':15}"+''.join(f'{Rr[k]:12.2f}' for k in KS))
res={}
for nm,kw in CONFIGS:
    rs=[M.evaluate(Escriba(**kw).write(seed=s),seed=s) for s in SEEDS]; R={k:float(np.mean([r[k] for r in rs])) for k in rs[0]}
    ok=M.compare(Rr,R); err=np.median([abs(np.log(max(abs(R[k]),1e-6)/max(abs(Rr[k]),1e-6))) for k in Rr if abs(Rr[k])>=0.02])
    res[nm]=dict(kw=kw,R=R,fails=[k for k,v in ok.items() if not v])
    print(f'{nm:34}{sum(ok.values()):>4}/{len(ok)}{err:7.3f}'+''.join(f'{R[k]:12.2f}' for k in KS),flush=True)
for nm,r in res.items(): print(f'  {nm}: no reprodueix → '+'; '.join(k[:38] for k in r['fails']))
if len(CONFIGS)>1: json.dump(res,open('resultats_vocabulari_pagina.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
