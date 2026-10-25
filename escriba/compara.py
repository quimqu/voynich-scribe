# Compara el text real amb generadors, mesura a mesura. Ús (des de escriba/):
#   py -3 compara.py                   → real, generador de la nit (gen3) i l'escriba per defecte
#   py -3 compara.py ablacions         → l'escriba amb cada mòdul tret
#   py -3 compara.py clau=valor ...    → l'escriba amb paràmetres canviats
import sys, json, os, numpy as np
import mesures as M
from escriba import Escriba, L_REAL
HERE=os.path.dirname(os.path.abspath(__file__))
Rr=json.load(open(os.path.join(HERE,'mesures_real.json'),encoding='utf-8'))
def run(kw,seeds=(1,2,3,4,5)):
    rs=[M.evaluate(Escriba(**kw).write(seed=s),seed=s) for s in seeds]; return {k:float(np.mean([r[k] for r in rs])) for k in rs[0]}
def gen3():
    # generador de tres regles de la nit del 27/09 (night_generator/generator3.py), sobre la mateixa maqueta
    src=open(os.path.join(M.NOV,'night_generator','generator.py'),encoding='utf-8').read().split("if __name__=='__main__':")[0]
    g3=open(os.path.join(M.NOV,'night_generator','generator3.py'),encoding='utf-8').read().split("Rr=json.load")[0].split('\n',2)[2]
    cwd=os.getcwd(); os.chdir(M.NOV); ns={}; exec(src+'\n'+g3,ns); os.chdir(cwd)
    rs=[]
    for s in (1,2,3,4,5):
        G=ns['generate3'](seed=s,first_line_factor=0.35,reset_par=True)
        if len(G)!=len(L_REAL): raise SystemExit(f'gen3: {len(G)} línies contra {len(L_REAL)}')
        G=[dict(g,sheet=r['sheet'],lang=r['lang'],gb=r['gb'] if len(r['gb'])==len(g['ws']) else [False]*len(g['ws'])) for g,r in zip(G,L_REAL)]
        rs.append(M.evaluate(G,seed=s))
    return {k:float(np.mean([r[k] for r in rs])) for k in rs[0]}
def table(cols):
    names=list(cols); keys=list(Rr)
    print(f"{'mesura':62}{'REAL':>9}"+''.join(f'{n[:14]:>15}' for n in names))
    for k in keys:
        row=f'{k[:62]:62}{Rr[k]:9.3f}'
        for n in names:
            v=cols[n].get(k,np.nan); ok=M.compare({k:Rr[k]},{k:v})[k]; row+=f'{v:13.3f} {"✓" if ok else "·"}'
        print(row)
    print(f"{'REPRODUÏDES (±25%)':62}{'':9}"+''.join(f'{sum(M.compare(Rr,cols[n]).values()):>13d}/{len(Rr)}' for n in names))
    part1=[k for k in keys if not k.startswith('[')]
    err=lambda c: np.median([abs(np.log(max(abs(c[k]),1e-6)/max(abs(Rr[k]),1e-6))) for k in keys if abs(Rr[k])>=0.02 and c.get(k)==c.get(k)])
    print(f"{'ERROR MEDIÀ |log(gen/real)| (sense les mesures ~0)':62}{'':9}"+''.join(f'{err(cols[n]):>15.3f}' for n in names))
    print(f"{'  de les 27 de la nit':62}{'':9}"+''.join(f'{sum(v for k,v in M.compare(Rr,cols[n]).items() if k in part1):>13d}/{len(part1)}' for n in names))
if __name__=='__main__':
    args=sys.argv[1:]
    if args and args[0]=='ablacions':
        mods=['use_lang','use_slots','use_word_rules','use_contexts','use_style','use_copy','use_first_line','use_closure','use_dissim','use_len_mode','use_boundary','use_reprefix','use_end_table','use_famrep','closure_by_nwords']
        cols={'escriba':run({})}
        for m in mods: cols['sense '+m[4:]]=run({m:False})
        cols['sense mem. formes']=run({'mod_contact':0,'mod_tries':6})
        cols['sense hàbit e']=run({'use_ehabit':False})
        cols['sense dy de secció']=run({'use_sec_dy':False})   # còpia modificada amb l'edició cega d'abans del 14/10
        json.dump(cols,open(os.path.join(HERE,'resultats_ablacions.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
        table(cols)
    else:
        kw={}
        for a in args:
            k,v=a.split('='); kw[k]=(v=='True') if v in ('True','False') else (float(v) if v.replace('.','',1).isdigit() else v)
        cols={}
        if not kw: cols['gen3 (nit)']=gen3()
        cols['escriba']=run(kw)
        json.dump(cols,open(os.path.join(HERE,'resultats.json' if not kw else 'resultats_prova.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
        table(cols)
