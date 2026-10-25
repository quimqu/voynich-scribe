# Parisel's test (arXiv 2604.19762): the four boundary signatures, per dialect, on the real text and on the scribe.
# Uses the author's verifier (github.com/labyrinthinesecurity/currier-signatures, commit 5d50101, with the import
# signatures_v26 -> signatures_v27 fixed), which calibrates the reference on his transliteration (RF1b-e) and scores a
# word file (one manuscript line per line) against the dialect's reference.
#   PYTHONIOENCODING=utf-8 py -3 external_tests/parisel/run_parisel.py <path to the currier-signatures clone> [fast]
# Input: scribe/manuscript_out/{real,scribe_seed*}.txt (scribe/manuscript.py). Output: here, words_*.txt, out_*.txt, summary.txt
import os, re, sys, glob, subprocess
HERE=os.path.dirname(os.path.abspath(__file__)); NOV=os.path.abspath(os.path.join(HERE,'..','..'))
CLON=os.path.abspath(sys.argv[1]); FAST=len(sys.argv)>2 and sys.argv[2]=='fast'
sys.path.insert(0,CLON)
# the same folio -> dialect assignment the author uses to calibrate
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
srcs=[('real',os.path.join(NOV,'scribe','manuscript_out','real.txt'))]+\
     [(os.path.basename(p)[:-4],p) for p in sorted(glob.glob(os.path.join(NOV,'scribe','manuscript_out','scribe_seed*.txt')))]
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
with open(os.path.join(HERE,'summary.txt'),'w',encoding='utf-8') as f:
    f.write('source | dialect | words | E->S | MI | bilateral | shape | attestation | verdict\n')
    for r in R: f.write(' | '.join(map(str,r))+'\n')
print('summary.txt written')
