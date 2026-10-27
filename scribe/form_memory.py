# Form memory in the scribe (ESTAT_DEL_PROGRAMA §6.2): exploration of the three pieces.
#   mod_lex     probability that a modified copy goes to a neighbour in the repertoire (one glyph away) instead of a blind edit
#   new_known   probability of redoing a new word that is not in the repertoire
#   use_wordrep propensity to adjacent repetition per word, not only per family
# Criterion: [eye] strange words within ±25% of the real value without losing battery measures.
# Usage (from scribe/): PYTHONIOENCODING=utf-8 py -3 form_memory.py [quick]
import sys, json, numpy as np, measures as M
from scribe import Escriba
Rr=json.load(open('measures_real.json',encoding='utf-8'))
SEEDS=(1,2) if 'quick' in sys.argv else (1,2,3) if 'medium' in sys.argv else (1,2,3,4,5)
KS=['[eye] Strange words (rare trigram in the real text) (%)','Word types','Hapax (% of types)','Adjacent identical words / chance','Consecutive words at edit distance 1 / shuffled','Frequent words repeated >3x chance (%)','Frequent words repeated <0.3x chance (%)','[A1] Words with an edit-distance-1 twin earlier on the page (%)']
SH=['strange','Word types','hapax','AA/chance','near','rep>3x','rep<.3x','twin']
CONFIGS=[('base',{}),
         ('writable ≥3',dict(mod_contact=3,mod_tries=30)),
         ('writable ≥3 + per-word repetition',dict(mod_contact=3,mod_tries=30,use_wordrep=True)),
         ('writable ≥3 + per-word repetition ^2',dict(mod_contact=3,mod_tries=30,use_wordrep=True,wordrep_pow=2.0)),
         ('writable ≥3 + repertoire (copies 0.5)',dict(mod_contact=3,mod_tries=30,mod_lex=0.5,lex_alpha=0.5))]
if len(sys.argv)>1 and '=' in sys.argv[-1]:
    kw={}
    for a in sys.argv[1:]:
        if '=' in a: k,v=a.split('='); kw[k]=(v=='True') if v in ('True','False') else (float(v) if v.lstrip('-').replace('.','',1).isdigit() else v)
    CONFIGS=[('trial',kw)]
print(f"{'':36}{'reprod.':>9}{'(of 57)':>8}{'err':>7}"+''.join(f'{s:>9}' for s in SH)); print(f"{'REAL':36}{'':24}"+''.join(f'{Rr[k]:9.2f}' for k in KS))
res={}
for nm,kw in CONFIGS:
    rs=[M.evaluate(Escriba(**kw).write(seed=s),seed=s) for s in SEEDS]; R={k:float(np.mean([r[k] for r in rs])) for k in rs[0]}
    ok=M.compare(Rr,R); n57=sum(v for k,v in ok.items() if not k.startswith('[eye]'))
    err=np.median([abs(np.log(max(abs(R[k]),1e-6)/max(abs(Rr[k]),1e-6))) for k in Rr if abs(Rr[k])>=0.02 and not k.startswith('[eye]')])
    res[nm]=dict(kw=kw,R=R,ok57=n57,err=float(err),fails=[k for k,v in ok.items() if not v])
    print(f'{nm:36}{sum(ok.values()):>6}/{len(ok)}{n57:>6}/57{err:7.3f}'+''.join(f'{R[k]:9.2f}' for k in KS),flush=True)
for nm,r in res.items(): print(f'  {nm}: not reproduced: '+'; '.join(k[:40] for k in r['fails']))
if len(CONFIGS)>1: json.dump(res,open('results_form_memory.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
