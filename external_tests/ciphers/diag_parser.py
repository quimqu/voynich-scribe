# Diagnosi: què feia malament el parser del notebook pm-cipher.ipynb respecte del df net de l'escriba (df_lines_ZL3b_strokes.csv).
import os, sys, re, io, contextlib
from collections import Counter
HERE=os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); sys.path.insert(0,os.path.join(HERE,'_data','escriba'))
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('notebook_parser_vell.py',encoding='utf-8').read())
import mesures
old=df.copy()
old_words=[w for s in old['text'].astype(str) for w in s.split()]
old_kept=[w for w in old_words if '?' not in w and 'I' not in w]
L=mesures.load_real(); new_words=[w for l in L for w in l['ws']]
nonascii=[w for w in old_kept if any(ord(c)>127 for c in w)]
print('PARSER VELL (tot el manuscrit, abans del filtre de secció)')
print(f'  línies: {len(old)}  mots: {len(old_words)}  després del filtre ?/I: {len(old_kept)}')
print(f'  mots amb caràcters PUA (comentaris <!@nnn;> o @nnn; convertits en glif): {len(nonascii)}  ex: {[w.encode("unicode_escape").decode() for w in nonascii[:4]]}')
lab=old[old['tag'].str.len()>0]
print('PARSER ESCRIBA: només paràgraf (sense etiquetes, cercles ni radis), comes unides, <-> = espai')
print(f'  mots: {len(new_words)}  tipus: {len(set(new_words))}')
# 1) <-> enganxava mots: comprova-ho
raw=open(os.path.join(os.path.dirname(os.path.dirname(HERE)), 'ZL3b-n.txt'),encoding='utf-8').read()
print(f'  intrusions de dibuix <-> al fitxer: {raw.count("<->")} (el parser vell les esborrava sense espai: dos mots en feien un)')
# 2) etiquetes i text circular/radial dins el corpus vell
loc=re.findall(r'^<f[^.>]+\.\d+[a-z]?,.(.)',raw,re.M); print('  loci per tipus al fitxer:',Counter(loc).most_common())
# 3) el notebook filtrava la secció Biological; comparació de glifs
oldB=[w for s in old[old.section=='Biological (balneological)']['text'].astype(str) for w in s.split() if '?' not in w and 'I' not in w]
newB=[w for l in L if l['section']=='biological' for w in l['ws']]
print(f'SECCIÓ BIOLÒGICA: vell {len(oldB)} mots, {len(set("".join(oldB)))} glifs | net {len(newB)} mots, {len(set("".join(newB)))} glifs')
co=Counter(oldB); cn=Counter(newB)
print('  mots que només surten al vell (top):',[(w.encode("unicode_escape").decode(),c) for w,c in (co-cn).most_common(12)])
print('  mots que només surten al net (top):',(cn-co).most_common(12))
