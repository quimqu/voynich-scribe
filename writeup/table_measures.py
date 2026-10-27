# Generates the table of the measures (real, 3-rule generator, scribe) in Markdown for THE_SCRIBE.md.
# The measure names are the keys of scribe/measures_real.json (already in English); '|' inside a name is escaped for the Markdown table.
# Usage (from the repository root): PYTHONIOENCODING=utf-8 py -3 writeup/table_measures.py   → fills the <!-- TABLE --> block of writeup/THE_SCRIBE.md
import json, re, sys
sys.path.insert(0,'scribe'); import measures as M
R=json.load(open('scribe/measures_real.json',encoding='utf-8')); C=json.load(open('scribe/results.json',encoding='utf-8'))
G3=C['3-rule generator']; S=C['scribe']
keys=list(R); N=len(keys); assert N==84, N
ok3=M.compare(R,G3); okS=M.compare(R,S)
f=lambda v: f'{v:,.0f}' if abs(v)>=1000 else (f'{v:.3f}' if abs(v)<1 else f'{v:.2f}')
rows=['| # | Measure | Real | 3-rule generator | Skribe |','|---|---|---|---|---|']
for i,k in enumerate(keys,1):
    rows.append(f"| {i} | {k.replace('|','\\|')} | {f(R[k])} | {f(G3[k])} {'✓' if ok3[k] else '✗'} | {f(S[k])} {'✓' if okS[k] else '✗'} |")
rows.append(f"| | **Reproduced (±25%)** | | **{sum(ok3.values())}/{N}** | **{sum(okS.values())}/{N}** |")
p='writeup/THE_SCRIBE.md'; s=open(p,encoding='utf-8').read()
s=re.sub(r'<!-- TABLE -->.*?<!-- /TABLE -->',lambda m: '<!-- TABLE -->\n'+'\n'.join(rows)+'\n<!-- /TABLE -->',s,flags=re.S)
open(p,'w',encoding='utf-8').write(s); print('ok',sum(okS.values()))
