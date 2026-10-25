# Escriu un quadern sencer amb l'escriba sobre la maqueta real, en format semblant a l'IVTFF (identificadors de línia del ZL3b),
# i el text real del mateix quadern normalitzat igual. Petició d'un lector de voynich.ninja (quadern 13, 19/10/2026).
#   PYTHONIOENCODING=utf-8 py -3 quadern.py M 1                         → escriba après de tot el manuscrit, llavor 1
#   ESCRIBA_TRAIN=sense_M PYTHONIOENCODING=utf-8 py -3 quadern.py M 1   → escriba que no ha vist el quadern M (calibra_seccio_e.py abans)
# Sortides a escriba/quadern_<Q>/: real_<Q>.txt, scribe_<Q>_all.txt o scribe_<Q>_blind.txt
import os, sys
Q=sys.argv[1] if len(sys.argv)>1 else 'M'; SEED=int(sys.argv[2]) if len(sys.argv)>2 else 1
from escriba import Escriba, L_ALL, L_REAL, _TR
OUT=f'quadern_{Q}'; os.makedirs(OUT,exist_ok=True)
idx=[i for i,l in enumerate(L_ALL) if l['quire']==Q]
def fmt(l):
    t='.'.join(('<->' if g else '')+w for w,g in zip(l['ws'],l['gb'])).replace('.<->','<->')
    return f"<{l['locus']}>".ljust(18)+('<%>' if l['ps']==1 else '')+t+('<$>' if l['pe']==1 else '')
def write(path,T,title,notes):
    pages=[]
    with open(path,'w',encoding='utf-8',newline='\n') as f:
        f.write(f'# {title}\n'); [f.write(f'# {n}\n') for n in notes]
        f.write(f'# {len(idx)} lines, {sum(len(T[i]["ws"]) for i in idx)} words, {len(set(L_ALL[i]["page"] for i in idx))} pages\n#\n')
        page=None
        for i in idx:
            if L_ALL[i]['page']!=page:
                page=L_ALL[i]['page']; l=L_ALL[i]; f.write(f'<{page}>'.ljust(18)+f'<! $Q={Q} $L={l["lang"]} $H={l["hand"]} sheet={l["sheet"]}>\n')
            f.write(fmt(dict(T[i],locus=L_ALL[i]['locus']))+'\n')
COMMON=['Paragraph text only (no labels), EVA, from the ZL3b transliteration (Zandbergen-Landini).',
        "Normalised: comments removed, first reading of alternatives kept, ligature braces kept as letters, uncertain spaces joined,",
        "words with extended or unreadable glyphs dropped. '.' = space, '<->' = drawing gap, '<%>' and '<$>' = paragraph start and end.",
        'Line identifiers are the ZL3b ones, so lines can be compared one to one.']
if not os.path.exists(f'{OUT}/real_{Q}.txt'):
    write(f'{OUT}/real_{Q}.txt',L_ALL,f'Quire {Q}: REAL text, normalised the same way as the generated files',COMMON)
blind=_TR==f'sense_{Q}'
G=Escriba().write(seed=SEED)
name=f'scribe_{Q}_'+('blind' if blind else 'all')+(f'_seed{SEED}' if SEED!=1 else '')+'.txt'
write(f'{OUT}/{name}',G,f'Quire {Q}: text written by "the scribe" (seed {SEED})',
      ["Trained on the whole manuscript EXCEPT this quire: it has never seen these pages (nor the biological section's habits)." if blind
       else "Trained on the whole manuscript, this quire included."]+
      ['Same layout as the real quire: same lines, words per line, drawing gaps, paragraph starts and ends. Only the words are generated.',
       'The whole manuscript is generated and this quire is extracted, so sheet habits and copying work as in a normal run.']+COMMON)
print('fet:',f'{OUT}/{name}',len(G),'línies al manuscrit; quadern',len(idx),'línies')
