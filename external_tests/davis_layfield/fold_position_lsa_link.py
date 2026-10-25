# Link between the fold test and the LSA: copies injected into the scribe (existing one-glyph variants of line-final words of the
# left page placed as the first word of lines of the right page, hand 2 inner faces). Does such copying raise the LSA inner-outer
# difference of hand 2, and does the fold test see it? Real text for reference. Output: fold_position_lsa_link.txt
#   PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/fold_position_lsa_link.py
import os, sys, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
fp=open(os.path.join(HERE,'fold_position.py'),encoding='utf-8').read().split('srcs = ')[0]
la=open(os.path.join(HERE,'lsa_anatomy.py'),encoding='utf-8').read().split('srcs = ')[0]
A={'__file__':os.path.join(HERE,'x.py')}; sys.argv=['x']; exec(la,A)
F={'__file__':os.path.join(HERE,'x.py')}; exec(fp,F)
add=open(os.path.join(HERE,'fold_position.py'),encoding='utf-8').read().split('# ---------- positive control')[1].split("say('')")[0]
exec('\n'.join(add.split('\n')[1:]),F)   # edit1, inject, primary
def lsa_h2(Pl):
    P={pg:dict(d,words=[w for l in d['lines'] for w in l]) for pg,d in Pl.items()}
    Sp=A['Space'](P); B=[t for t in A['bifolia'](P) if P[t[1]+'r']['H']=='2']
    return float(A['paired'](Sp,B).mean())
NOV=A['NOV']
for seed in (1,2,3):
    path=os.path.join(NOV,'scribe','manuscript_out',f'scribe_seed{seed}.txt'); P0=F['read'](path); B0=F['bifolia'](P0)
    row=[]
    for f in (0,0.05,0.1,0.2,0.3,0.5):
        vals=[]; pos=[]
        for r in range(4):
            Q=F['inject'](P0,B0,f) if f else P0
            vals.append(lsa_h2(Q)); pos.append(F['primary'](Q,B0)[0]<0.05)
        row.append(f'f={f:.2f}: LSA hand2 {np.mean(vals):+.3f}, fold test detects {100*np.mean(pos):.0f}%')
    print(f'seed{seed} | '+' | '.join(row), flush=True)
print('real text, LSA hand 2:', f"{lsa_h2(F['read'](os.path.join(NOV,'scribe','manuscript_out','real.txt'))):+.3f}")
