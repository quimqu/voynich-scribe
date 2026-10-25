# Escriu el manuscrit sencer (text de paràgraf) amb l'escriba, i el text real normalitzat igual, en format semblant a l'IVTFF
# (identificadors de línia del ZL3b), per a les proves externes (Parisel, Davis-Layfield; 25/10/2026).
#   PYTHONIOENCODING=utf-8 py -3 manuscrit.py 1 2 3 4 5   → manuscrit_out/real.txt, manuscrit_out/scribe_seed<k>.txt
# Capçalera de pàgina: <f1r> <! $Q=quadern $L=llengua $H=mà $S=secció $F=full>
import os, sys, time
SEEDS=[int(s) for s in sys.argv[1:]] or [1]
from escriba import Escriba, L_ALL
OUT='manuscrit_out'; os.makedirs(OUT,exist_ok=True)
def fmt(l):
    t='.'.join(('<->' if g else '')+w for w,g in zip(l['ws'],l['gb'])).replace('.<->','<->')
    return f"<{l['locus']}>".ljust(18)+('<%>' if l['ps']==1 else '')+t+('<$>' if l['pe']==1 else '')
COMMON=['Paragraph text only (no labels), EVA, on the layout of the ZL3b transliteration (Zandbergen-Landini).',
        "Normalised: comments removed, first reading of alternatives kept, ligature braces kept as letters, uncertain spaces joined,",
        "words with extended or unreadable glyphs dropped. '.' = space, '<->' = drawing gap, '<%>' and '<$>' = paragraph start and end.",
        'Page header: $Q quire, $L Currier language, $H Davis hand, $S section, $F sheet (quire + bifolium).']
def write(path,T,title,notes):
    with open(path,'w',encoding='utf-8',newline='\n') as f:
        f.write(f'# {title}\n'); [f.write(f'# {n}\n') for n in notes+COMMON]
        f.write(f'# {len(L_ALL)} lines, {sum(len(t["ws"]) for t in T)} words, {len(set(l["page"] for l in L_ALL))} pages\n#\n')
        page=None
        for i,l in enumerate(L_ALL):
            if l['page']!=page:
                page=l['page']; f.write(f'<{page}>'.ljust(18)+f'<! $Q={l["quire"]} $L={l["lang"]} $H={l["hand"]} $S={l["section"]} $F={l["sheet"]}>\n')
            f.write(fmt(dict(T[i],locus=l['locus']))+'\n')
if not os.path.exists(f'{OUT}/real.txt'):
    write(f'{OUT}/real.txt',L_ALL,'REAL text, normalised the same way as the generated files',[])
for s in SEEDS:
    t=time.time(); G=Escriba().write(seed=s)
    write(f'{OUT}/scribe_seed{s}.txt',G,f'Text written by "the scribe" (seed {s}), trained on the whole manuscript',
          ['Same layout as the real manuscript: same pages, lines, words per line, drawing gaps, paragraph starts and ends. Only the words are generated.'])
    print(f'fet: {OUT}/scribe_seed{s}.txt ({len(G)} línies, {time.time()-t:.0f} s)',flush=True)
