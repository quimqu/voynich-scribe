# Memòria de formes a l'escriba (ESTAT_DEL_PROGRAMA §6.2): exploració de les tres peces.
#   mod_lex     probabilitat que una còpia modificada vagi a un veí del repertori (a un glif) en lloc d'una edició cega
#   new_known   probabilitat de refer un mot nou que no és al repertori
#   use_wordrep propensió a la repetició adjacent per mot, no només per família
# Criteri: [ull] mots estranys dins del ±25% del real sense perdre mesures de la bateria.
# Ús (des de escriba/): PYTHONIOENCODING=utf-8 py -3 memoria_formes.py [ràpid]
import sys, json, numpy as np, mesures as M
from escriba import Escriba
Rr=json.load(open('mesures_real.json',encoding='utf-8'))
SEEDS=(1,2) if 'ràpid' in sys.argv else (1,2,3) if 'mitjà' in sys.argv else (1,2,3,4,5)
KS=['[ull] mots estranys (trigrama rar al real) (%)','tipus','hàpax (%)','AA / atzar','quasi(ed=1) / base','mots freq. amb rep >3x atzar (%)','mots freq. amb rep <0.3x (%)','[A1] mots amb bessó (ED≤1) abans a la pàgina (%)']
SH=['estranys','tipus','hàpax','AA/atz','quasi','rep>3x','rep<.3x','bessó']
CONFIGS=[('base',{}),
         ('escrivible ≥3',dict(mod_contact=3,mod_tries=30)),
         ('escrivible ≥3 + rep. per mot',dict(mod_contact=3,mod_tries=30,use_wordrep=True)),
         ('escrivible ≥3 + rep. per mot ^2',dict(mod_contact=3,mod_tries=30,use_wordrep=True,wordrep_pow=2.0)),
         ('escrivible ≥3 + repertori (còpies 0,5)',dict(mod_contact=3,mod_tries=30,mod_lex=0.5,lex_alpha=0.5))]
if len(sys.argv)>1 and '=' in sys.argv[-1]:
    kw={}
    for a in sys.argv[1:]:
        if '=' in a: k,v=a.split('='); kw[k]=(v=='True') if v in ('True','False') else (float(v) if v.replace('.','',1).isdigit() else v)
    CONFIGS=[('prova',kw)]
print(f"{'':36}{'reprod.':>9}{'(de 57)':>8}{'err':>7}"+''.join(f'{s:>9}' for s in SH)); print(f"{'REAL':36}{'':24}"+''.join(f'{Rr[k]:9.2f}' for k in KS))
res={}
for nm,kw in CONFIGS:
    rs=[M.evaluate(Escriba(**kw).write(seed=s),seed=s) for s in SEEDS]; R={k:float(np.mean([r[k] for r in rs])) for k in rs[0]}
    ok=M.compare(Rr,R); n57=sum(v for k,v in ok.items() if not k.startswith('[ull]'))
    err=np.median([abs(np.log(max(abs(R[k]),1e-6)/max(abs(Rr[k]),1e-6))) for k in Rr if abs(Rr[k])>=0.02 and not k.startswith('[ull]')])
    res[nm]=dict(kw=kw,R=R,ok57=n57,err=float(err),fails=[k for k,v in ok.items() if not v])
    print(f'{nm:36}{sum(ok.values()):>6}/{len(ok)}{n57:>6}/57{err:7.3f}'+''.join(f'{R[k]:9.2f}' for k in KS),flush=True)
for nm,r in res.items(): print(f'  {nm}: no reprodueix → '+'; '.join(k[:40] for k in r['fails']))
if len(CONFIGS)>1: json.dump(res,open('resultats_memoria_formes.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
