# Genera la taula de les 64 mesures (real, generador de 3 regles, escriba) en Markdown i en anglès per a THE_SCRIBE.md.
# Ús (des de novetats/): PYTHONIOENCODING=utf-8 py -3 writeup/taula_mesures.py   → omple el bloc <!-- TAULA --> de writeup/THE_SCRIBE.md
import json, re, sys
sys.path.insert(0,'escriba'); import mesures as M
R=json.load(open('escriba/mesures_real.json',encoding='utf-8')); C=json.load(open('escriba/resultats.json',encoding='utf-8'))
G3=C['gen3 (nit)']; S=C['escriba']
EN=["Adjacent identical words (%)","Adjacent identical words / chance","Consecutive words at edit distance 1 / shuffled","Same word at distance 2 / shuffled","Same word at distance 3 / shuffled","Same word at distance 5 / shuffled",
"Frequent words repeated >3× chance (%)","Frequent words repeated <0.3× chance (%)","Boundary MI, distance 1 (last glyph → next first glyph)","Boundary MI, distance 2","Boundary MI, distance 3",
"Lift -y | q-","Lift -r | a-","Lift -y | a-","Lift -n | q-","First word of line starts ch/sh (%)","First word of line starts y (%)","Last word of line ends -m (%)","Line-end -m: lines of 10+ words / 1–4 words",
"Same first glyph as line n−1 / null","Same first glyph as line n−2 / null","Same first glyph as line n−3 / null","Distinct initial glyphs per paragraph (4+ lines)","Adjacent repeats: first line of paragraph / rest","Spearman correlation of neighbour word lengths",
"Word types","Hapax (% of types)","Words fitting the slot grammar (%)","Words with 2+ gallows (%)","Mean word length (glyphs)","SD of word length","e and i in the same word / expected",
"H(prefix), marginal","H(prefix | previous glyph, core)","q- before o- after -y (%)","q- on first word of paragraph (%)","q- on first word of line (%)","q- inside the line (%)",
"a- at line start (%)","d-/s-/y- at line start (%)","Bare gallows at line start (%)","Closed last word, non-final lines (%)","Closed forms inside the line (%)","Closed last word of paragraph (%)",
"Length of 2nd word / 1st word","Gallows on first word of paragraph (%)","p/f among gallows, first line of paragraph (%)","p/f among gallows, other lines (%)","Word length, first line / rest",
"Closed word before a drawing gap (%)","d-/s-/y- after a drawing gap (%)","q- after a drawing gap (%)","Same first glyph after a gallows-initial line / null",
"Words with an edit-distance-1 twin earlier on the page (%)","Lines back to the nearest twin (median)","Page overdispersion of q- (after -y)","Vocabulary cosine: same sheet / neighbouring pages of other sheets",
"Strange words (%)","Strange words per line","Page overdispersion of e-words","e-words: biological / herbal","-edy words in biological (%)","Share of the page's most frequent word (median, %)","Words of 8+ glyphs (%)"]
keys=list(R); assert len(keys)==len(EN)==64, (len(keys),len(EN))
ok3=M.compare(R,G3); okS=M.compare(R,S)
f=lambda v: f'{v:,.0f}' if abs(v)>=1000 else (f'{v:.3f}' if abs(v)<1 else f'{v:.2f}')
rows=['| # | Measure | Real | 3-rule generator | Scribe |','|---|---|---|---|---|']
for i,(k,en) in enumerate(zip(keys,EN),1):
    rows.append(f"| {i} | {en} | {f(R[k])} | {f(G3[k])} {'✓' if ok3[k] else '✗'} | {f(S[k])} {'✓' if okS[k] else '✗'} |")
rows.append(f"| | **Reproduced (±25%)** | | **{sum(ok3.values())}/64** | **{sum(okS.values())}/64** |")
p='writeup/THE_SCRIBE.md'; s=open(p,encoding='utf-8').read()
s=re.sub(r'<!-- TAULA -->.*?<!-- /TAULA -->','<!-- TAULA -->\n'+'\n'.join(rows)+'\n<!-- /TAULA -->',s,flags=re.S)
open(p,'w',encoding='utf-8').write(s); print('ok',sum(okS.values()))
