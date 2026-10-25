# Prova de Parisel (arXiv 2604.19762): les quatre signatures de frontera, per dialecte, sobre el text real i sobre l'escriba.
# Fa servir el verificador de l'autor (github.com/labyrinthinesecurity/currier-signatures, commit 5d50101, amb l'import
# signatures_v26 -> signatures_v27 corregit), que calibra la referència sobre la seva transliteració (RF1b-e) i puntua un
# fitxer de mots (una línia del manuscrit per línia) contra la referència del dialecte.
#   PYTHONIOENCODING=utf-8 py -3 proves_externes/parisel/run_parisel.py <camí al clon currier-signatures> [fast]
# Entrada: escriba/manuscrit_out/{real,scribe_seed*}.txt (escriba/manuscrit.py). Sortida: aquí, words_*.txt, out_*.txt, resum.txt
import os, re, sys, glob, subprocess
HERE=os.path.dirname(os.path.abspath(__file__)); NOV=os.path.abspath(os.path.join(HERE,'..','..'))
CLON=os.path.abspath(sys.argv[1]); FAST=len(sys.argv)>2 and sys.argv[2]=='fast'
sys.path.insert(0,CLON)
# la mateixa assignació foli -> dialecte que fa servir l'autor per calibrar
MAP={}
for ln in open(os.path.join(CLON,'verifier.py'),encoding='utf-8'):
    for f,l in re.findall(r'"(f\d+[rv])": "([AB])"',ln): MAP[f]=l
def pages(path):
    P={}; cur=None
    for ln in open(path,encoding='utf-8'):
        if ln.startswith('#') or not ln.strip(): continue
        m=re.match(r'^<(f\d+[rv]\d*)>\s+<!',ln)
        if m: cur=m.group(1); P[cur]=[]; continue
        m=re.match(r'^<[^>]+>\s*(.*)$',ln.rstrip('\n'))
        if not m or cur is None: continue
        t=m.group(1).replace('<%>','').replace('<$>','').replace('<->','.')
        ws=[w for w in t.split('.') if w]
        if ws: P[cur].append(ws)
    return P
def words_file(src,P,L):
    out=os.path.join(HERE,f'words_{src}_{L}.txt'); n=0
    with open(out,'w',encoding='utf-8',newline='\n') as f:
        for pg,lines in P.items():
            folio=re.match(r'(f\d+[rv])',pg).group(1)
            if MAP.get(folio)!=L: continue
            for ws in lines: f.write(' '.join(ws)+'\n'); n+=len(ws)
    return out,n
srcs=[('real',os.path.join(NOV,'escriba','manuscrit_out','real.txt'))]+\
     [(os.path.basename(p)[:-4],p) for p in sorted(glob.glob(os.path.join(NOV,'escriba','manuscrit_out','scribe_seed*.txt')))]
R=[]
for src,path in srcs:
    P=pages(path)
    for L in 'AB':
        wf,n=words_file(src,P,L)
        cmd=['py','-3','verifier.py','--words',wf,'--language',L]+(['--fast'] if FAST else [])
        o=subprocess.run(cmd,cwd=CLON,capture_output=True,text=True,encoding='utf-8',errors='replace',env=dict(os.environ,PYTHONUTF8='1'))
        txt=o.stdout+o.stderr; open(os.path.join(HERE,f'out_{src}_{L}.txt'),'w',encoding='utf-8').write(txt)
        g=lambda rx,d='?': (re.search(rx,txt) or [None,d])[1]
        es=g(r'Sig1\s+E->S:\s+([\d.]+%)'); mi=g(r'Sig3\s+MI:\s+([\d.]+)'); bil=g(r'Generator: Se=(\d+, Ee=\d+\s+→ \w+)'); sh=g(r'Sig4\s+Shape:\s+(\w+\s+R²=[\d.]+\s+CV=[\d.]+)')
        verd='4/4' if 'ALL 4 SIGNATURES PASSED' in txt else f"{txt.count('✓ PASS')}/4"
        att=g(r'Dialect tokens:\s+\d+/\d+\s+\(([\d.]+%)\)')
        R.append((src,L,n,es,mi,bil,sh,att,verd)); print(*R[-1],sep=' | ',flush=True)
with open(os.path.join(HERE,'resum.txt'),'w',encoding='utf-8') as f:
    f.write('font | dialecte | mots | E->S | MI | bilateral | forma | atestació | veredicte\n')
    for r in R: f.write(' | '.join(map(str,r))+'\n')
print('escrit resum.txt')
