# The scribe: a generator that writes a "Voynich" following the rulebook (RULES.md), module by module.
# Each module is a rule and can be removed (ablation) to see what it contributes. The layout (pages, sheets, paragraphs, lines,
# words per line, drawing gaps, Currier language A/B) is that of the real manuscript. All tables are estimated from the real text.
import re, math, random, numpy as np
from collections import Counter, defaultdict
import os
import measures as M
gl=M.gl; GALL=M.GALL
import os
L_ALL=M.load_corpus(os.environ['SCRIBE_CORPUS']) if os.environ.get('SCRIBE_CORPUS') else M.load_real()   # SCRIBE_CORPUS: another text (controls, 19/10)
def folio_num(pg):
    m=re.search(r'(\d+)',pg); return int(m.group(1)) if m else 0
# SCRIBE_TRAIN=odd|even: the scribe learns all the tables only from these folios (generalisation test, holdout.py)
_TR=os.environ.get('SCRIBE_TRAIN','')
def _train_ok(l):
    if not _TR: return True
    if _TR.startswith('without_'): return l['quire'] not in _TR[6:].split('+')   # SCRIBE_TRAIN=without_M: everything except quire M (13)
    return folio_num(l['page'])%2==(1 if _TR=='odd' else 0)
L_REAL=[l for l in L_ALL if _train_ok(l)]
# ================= rulebook tables, estimated from the real text =================
def seq_ctx(A,g,j):
    """context for glyph j of a word: j=0 (A,'_'); j=1 (A,g0), the glyph before the word still weighs on the second glyph (R3.3); j>=2 (g[j-2],g[j-1])"""
    if j==0: return (A,'_')
    if j==1: return (A,g[0])
    return (g[j-2],g[j-1])
def start_tag(l,i,prev_word):
    if i==0: return '¶' if l['ps']==1 else '^'
    if l['gb'][i]: return '|'
    return '<'+gl(prev_word)[-1]
TAB={}
for lang in ('A','B','*'):
    t=defaultdict(Counter)
    for l in L_REAL:
        if lang!='*' and l['lang']!=lang: continue
        n_=len(l['ws'])
        for i,w in enumerate(l['ws']):
            if i==n_-1 and n_>1: continue                      # last word of the line: position form (R4.3)
            if i+1<n_ and l['gb'][i+1]: continue                # word before the drawing gap (R6.1)
            if l['ps']==1 and i>0: continue                     # rest of the first line: its own register (R1.3, R5.2)
            A=start_tag(l,i,l['ws'][i-1] if i else None); g=gl(w)+['$']
            for j,x in enumerate(g): t[seq_ctx(A,g,j)][x]+=1
    TAB[lang]=t
INTERIOR=Counter(w for l in L_REAL for w in l['ws'][1:-1])
def declose(w):
    # open form of a line-end closed form: -m -> -iin/-in (whichever is more frequent inside the line), -ly/-ry/-sy -> -l/-r/-s, -g -> -y
    if w.endswith('m'):
        a,b=w[:-1]+'iin',w[:-1]+'in'; return a if INTERIOR[a]>=INTERIOR[b] else b
    for c_,o in (('ly','l'),('ry','r'),('sy','s')):
        if w.endswith(c_): return w[:-len(c_)]+o
    if w.endswith('g'): return w[:-1]+'y'
    return w
TAB_END={}
for lang in ('A','B','*'):
    t=defaultdict(Counter)
    for l in L_REAL:
        if (lang!='*' and l['lang']!=lang) or len(l['ws'])<2: continue
        i=len(l['ws'])-1; A=start_tag(l,i,l['ws'][i-1]); g=gl(declose(l['ws'][i]))+['$']
        for j,x in enumerate(g): t[seq_ctx(A,g,j)][x]+=1
    TAB_END[lang]=t
# tables per hand (19/10): each hand has its own vocabulary, more than the language does (pages of the same hand and section, cosine 0.34 in the real text
# against 0.29 with per-language tables; different hands far apart, 0.16 against 0.19). Counts of the hand plus HAND_K pseudocounts
# spread according to the language table, so that contexts rarely seen by the hand are not left empty.
HAND_K=3.0
def _hand_tables(base_tabs,build_lines,end=False):
    out={}
    hands=Counter(l.get('hand') for l in L_REAL)
    for h,nl in hands.items():
        if h in (None,'nan','None') or nl<60: continue
        t=defaultdict(Counter)
        for l in L_REAL:
            if l.get('hand')!=h: continue
            build_lines(l,t)
        lang=Counter(l['lang'] for l in L_REAL if l.get('hand')==h).most_common(1)[0][0]
        base=base_tabs.get(lang,base_tabs['*']); mixed=defaultdict(Counter)
        for ctx in set(base)|set(t):
            b=base.get(ctx,Counter()); tb=sum(b.values()) or 1
            m=Counter(t.get(ctx,Counter()))
            for x,v in b.items(): m[x]+=HAND_K*v/tb
            mixed[ctx]=m
        out[h]=mixed
    return out
def _lines_interior(l,t):
    n_=len(l['ws'])
    for i,w in enumerate(l['ws']):
        if i==n_-1 and n_>1: continue
        if i+1<n_ and l['gb'][i+1]: continue
        if l['ps']==1 and i>0: continue
        A=start_tag(l,i,l['ws'][i-1] if i else None); g=gl(w)+['$']
        for j,x in enumerate(g): t[seq_ctx(A,g,j)][x]+=1
def _lines_end(l,t):
    if len(l['ws'])<2: return
    i=len(l['ws'])-1; A=start_tag(l,i,l['ws'][i-1]); g=gl(declose(l['ws'][i]))+['$']
    for j,x in enumerate(g): t[seq_ctx(A,g,j)][x]+=1
TAB_H=_hand_tables(TAB,_lines_interior); TAB_END_H=_hand_tables(TAB_END,_lines_end)
def _hand_sec_tables(hand_tabs,build_lines,min_lines=40):
    # hand x section, with the hand table as fallback (same mix of pseudocounts)
    out={}
    for (h,sec),nl in Counter((l.get('hand'),l.get('section')) for l in L_REAL).items():
        if h not in hand_tabs or nl<min_lines: continue
        t=defaultdict(Counter)
        for l in L_REAL:
            if l.get('hand')==h and l.get('section')==sec: build_lines(l,t)
        base=hand_tabs[h]; mixed=defaultdict(Counter)
        for ctx in set(base)|set(t):
            b=base.get(ctx,Counter()); tb=sum(b.values()) or 1; m=Counter(t.get(ctx,Counter()))
            for x,v in b.items(): m[x]+=HAND_K*v/tb
            mixed[ctx]=m
        out[(h,sec)]=mixed
    return out
TAB_HS=_hand_sec_tables(TAB_H,_lines_interior); TAB_END_HS=_hand_sec_tables(TAB_END_H,_lines_end)
# backoff: context without the glyph before the word
BACK=defaultdict(Counter)
for (a,b),c in TAB['*'].items(): BACK[('*',b) if a.startswith('<') else (a,b)].update(c)
# single-glyph edits (copying with modification): empirical tables from pairs of neighbouring words at distance 1
sub=Counter(); ins=Counter(); dele=Counter()
for l in L_REAL:
    for a,b in zip(l['ws'],l['ws'][1:]):
        ga,gb_=gl(a),gl(b)
        if len(ga)==len(gb_) and ga!=gb_:
            d=[(x,y) for x,y in zip(ga,gb_) if x!=y]
            if len(d)==1: sub[d[0]]+=1; sub[d[0][::-1]]+=1
        elif len(gb_)==len(ga)+1:
            for i in range(len(gb_)):
                if gb_[:i]+gb_[i+1:]==ga: ins[gb_[i]]+=1; break
        elif len(ga)==len(gb_)+1:
            for i in range(len(ga)):
                if ga[:i]+ga[i+1:]==gb_: dele[ga[i]]+=1; break
subby=defaultdict(Counter)
for (x,y),c in sub.items(): subby[x][y]+=c
NS,NI,ND=sum(sub.values()),sum(ins.values()),sum(dele.values())
# closure: probability of turning the open form into the closed form on the last word of the line (R4.3), on the last word of the paragraph (R14.2) and before a drawing gap (R6.1)
PAIRS=[('iin','m'),('in','m'),('l','ly'),('r','ry'),('s','sy'),('y','g')]
def closure_probs(words_close,words_mid):
    out={}
    for o,c_ in PAIRS:
        def rate(ws):
            nc=sum(w.endswith(c_) for w in ws); no=sum(w.endswith(o) and not w.endswith(c_) for w in ws); return nc/(nc+no) if nc+no else 0
        rl,rm=rate(words_close),rate(words_mid); out[(o,c_)]=max(0.0,(rl-rm)/(1-rm)) if rm<1 else 0
    return out
mid=[w for l in L_REAL for w in l['ws'][1:-1] if True]
CL_LINE=closure_probs([l['ws'][-1] for l in L_REAL if l['pe']==0 and len(l['ws'])>1],mid)
NW_BINS=[(1,3),(4,5),(6,7),(8,9),(10,11),(12,99)]
def nw_bin(n): return next((b for b in NW_BINS if b[0]<=n<=b[1]),None)
CL_HAND_NW={}
for h in set(l['hand'] for l in L_REAL):
    md=[w for l in L_REAL if l['hand']==h for w in l['ws'][1:-1]]
    for b in NW_BINS:
        lw=[l['ws'][-1] for l in L_REAL if l['hand']==h and l['pe']==0 and b[0]<=len(l['ws'])<=b[1]]
        if len(lw)>=60: CL_HAND_NW[(h,b)]=closure_probs(lw,md)
CL_PAR_NW={}
for b in NW_BINS:
    lw=[l['ws'][-1] for l in L_REAL if l['pe']==1 and b[0]<=len(l['ws'])<=b[1]]
    if len(lw)>=60: CL_PAR_NW[b]=closure_probs(lw,mid)
CL_HAND={}
for h in set(l['hand'] for l in L_REAL):
    lw=[l['ws'][-1] for l in L_REAL if l['hand']==h and l['pe']==0 and len(l['ws'])>1]; md=[w for l in L_REAL if l['hand']==h for w in l['ws'][1:-1]]
    if len(lw)>=150: CL_HAND[h]=closure_probs(lw,md)
CL_PAR=closure_probs([l['ws'][-1] for l in L_REAL if l['pe']==1 and len(l['ws'])>1],mid)
# paragraph end per hand (14/10, J1: the strength of the closure belongs to each hand, also on the last line of the paragraph)
CL_PAR_HAND={}
for h in set(l['hand'] for l in L_REAL):
    lw=[l['ws'][-1] for l in L_REAL if l['hand']==h and l['pe']==1 and len(l['ws'])>1]; md=[w for l in L_REAL if l['hand']==h for w in l['ws'][1:-1]]
    if len(lw)>=60: CL_PAR_HAND[h]=closure_probs(lw,md)
CL_GAP=closure_probs([l['ws'][i-1] for l in L_REAL for i in range(2,len(l['ws'])) if l['gb'][i]],mid)
PREF=defaultdict(Counter)
for l in L_REAL:
    for i in range(1,len(l['ws'])):
        k_,core=M.split_prefix(l['ws'][i])
        if k_: PREF[(gl(l['ws'][i-1])[-1],''.join(gl(core)[:2]))][k_]+=1
PREF_BACK=defaultdict(Counter)
for (g1,c2),c in PREF.items(): PREF_BACK[(g1,c2[:1])].update(c)
PFX={'nu':'','d':'d','s':'s','q':'q'}
def family(w):
    if re.fullmatch(r'(ch|sh|cth|ckh|cph|cfh)o(l|r)',w): return 'banc+o+l/r'
    if re.search(r'[ktpf]e+(dy|y)$',w) and not re.search(r'(ch|sh)e+(dy|y)$',w): return 'gallows+e+dy/y'
    if re.search(r'(ch|sh)e+(dy|y)$',w): return 'banc+e+y/dy'
    if re.search(r'a?i+n$',w): return '-aiin/-ain'
    return 'altres'
FAMREP={'banc+o+l/r':3.2,'gallows+e+dy/y':1.5,'altres':0.8,'banc+e+y/dy':0.55,'-aiin/-ain':0.8}   # calibrated with calibrate_families.py (starting point: G7)
# ---------- form memory (R16.3; 14/10/2026, form_memory.py) ----------
# The repertoire: the words the hand knows (word types seen >= LEX_MIN times in the training text). A copy that changes one glyph
# lands on a neighbour in the repertoire (one glyph away), not on a blind edit; a new word that is not in the repertoire can be redrawn.
LEX=Counter(w for l in L_REAL for w in l['ws']); LEX_MIN=2; LEXN=sum(LEX.values())
def _dels(g): return [tuple(g[:i]+g[i+1:]) for i in range(len(g))]
_BY_DEL=defaultdict(set)
for _w,_c in LEX.items():
    if _c<LEX_MIN: continue
    _g=gl(_w); _BY_DEL[tuple(_g)].add(_w)
    for _d in _dels(_g): _BY_DEL[_d].add(_w)
_NB={}
def lex_neighbors(w):
    if w not in _NB:
        g=gl(w); cand=set()
        for k in [tuple(g)]+_dels(g): cand|=_BY_DEL.get(k,set())
        cand.discard(w); _NB[w]=[x for x in cand if M.lev(gl(x),g)==1]
    return _NB[w]
# propensity to adjacent repetition per word (G7, ESCRIBA §4.1): observed / expected within the page, shrunk towards that of the family
def word_rep_ratios(L,shrink=3.0):
    obs=Counter(); exp=Counter(); pc=defaultdict(Counter); pn=Counter()
    for l in L:
        pc[l['page']].update(l['ws']); pn[l['page']]+=len(l['ws'])
    for l in L:
        for a,b in zip(l['ws'],l['ws'][1:]):
            obs[b]+=(a==b); exp[b]+=(pc[l['page']][b]-1)/max(1,pn[l['page']]-1)
    fo=Counter(); fe=Counter()
    for w in exp: fo[family(w)]+=obs[w]; fe[family(w)]+=exp[w]
    fr={f:fo[f]/fe[f] for f in fe if fe[f]>0}
    return {w:((obs[w]+shrink*fr[family(w)])/(exp[w]+shrink))/fr[family(w)] for w in exp if fr.get(family(w),0)>0}, fr
WREP,_=word_rep_ratios(L_REAL)
# the modified copy is also written by the hand: every glyph must be possible after the two before it (memory of two, R17.3)
def contact_ok(w,min_c=1):
    g=gl(w)+['$']
    if len(g)>=2 and BACK.get(('*',g[0]),Counter())[g[1]]<min_c: return False
    return all(TAB['*'].get((g[j-2],g[j-1]),Counter())[g[j]]>=min_c for j in range(2,len(g)))
# vertical dissimilation per glyph (R4.5, H8): probability of avoiding a repeat of the first glyph of the line above
def avoid_table():
    GG=[]; cur=[]; prev=None
    for l in L_REAL:
        if prev is None or l['page']!=prev['page'] or l['ps']==1:
            if len(cur)>=2: GG.append(cur)
            cur=[]
        if l['ps']==0: cur.append(gl(l['ws'][0])[0])
        prev=l
    if len(cur)>=2: GG.append(cur)
    same=Counter(); tot=Counter(); expc=Counter()
    for g in GG:
        cg=Counter(g); n=len(g)
        for a,b in zip(g,g[1:]): tot[a]+=1; same[a]+=(a==b); expc[a]+=(cg[a]-1)/(n-1)
    out={}
    for a in tot:
        if tot[a]>=30 and expc[a]>0: out[a]=float(np.clip(1-same[a]/expc[a],0,1))
    return out
AVOID=avoid_table()
for g_ in ('k','f','cth','ckh','cph','cfh'): AVOID.setdefault(g_,AVOID.get('t',0.5))   # gallows with little data: like t
# ================= the scribe =================
DEFAULT=dict(r_copy=0.22,r_mod=0.45,tau=4.0,vert_bonus=2.0,first_copy=0.1,p_pf=0.30,sigma_style=0.3,sigma_line=0.25,rho_line=0.6,
             sigma_len=0.6,len_cands=5,rej_2gall=0.35,rej_ei=0.25,use_word_rules=True,first_norep=0.0,gap_scale=0.75,declose_p=0.55,gap_noq=0.9,use_famrep=True,adj_boost=0.5,avoid_scale=1.2,closure_by_nwords=True,closure_by_hand=True,use_reprefix=True,use_end_table=True,pf_back=0.75,
             use_lang=True,use_slots=True,use_contexts=True,use_style=True,use_copy=True,use_first_line=True,use_closure=True,
             use_dissim=True,use_len_mode=True,use_boundary=True,
             mod_lex=0.0,lex_alpha=1.0,new_known=0.0,use_wordrep=False,wordrep_pow=1.0,mod_contact=3,mod_tries=30,mod_fallback='keep',par_by_hand=False,use_ehabit=True,sigma_e=0.45,use_sec_e=False,use_sec_dy=False,r_prev=0.0,h_prev=3.0,n_prev=12,r_sheet=0.0,r_stock=0.0,h_stock=3.0,use_hand_tab=True,use_sec_tab=True,use_len_w=True,len_w=None,par_scale=0.75,use_g0=True,sigma_g0_pg=0.4,sigma_g0_line=0.7,g0_mu=0.35,use_fl_style=True,fl_t=0.3,fl_sh=0.6,fl_rare=0.7,fl_rare_min=0.003,fl_e=-0.6)   # 26/10: first-line register calibrated on the odd folios only (t 0.3, sh 0.6, rare 0.7, e -0.6) — with it, first_norep (0.4 before) is no longer needed: the first line repeats less because its words are rarer   # 26/10: gallows-initial habit calibrated on the odd folios only (pg 0.4, line 0.7, mu 0.35)   # 19/10: tables per hand and section, length by position; strengths readjusted (before: r_copy 0.35, sigma_style 0.45, rej_2gall 0.55, rej_ei 0.45, adj_boost 0.8, gap_scale 1.0)   # e habit and section dy: on by default since 14/10 (page_vocabulary.py)   # mod_contact=3: form memory on modified copies (14/10; before 0 and 6 tries)
STYLE_DIMS=['t','sh','q','dy']
# 'e' habit (14/10): word block with e (-y/-dy) or without (-aiin/-ar/-ol), R2.4, per sheet, page, line and section; its own random generator
NUC={'ch','sh','k','t','p','f','cth','ckh','cph','cfh'}
import json as _json
_SFX=('_'+_TR) if _TR else ''   # with SCRIBE_TRAIN, the section offsets are calibrated only on those folios
try: SEC_E=_json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),f'sec_e{_SFX}.json'),encoding='utf-8'))
except Exception: SEC_E={}
try: LEN_W=_json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),f'len_w{_SFX}.json'),encoding='utf-8'))   # length weights by position (19/10, calibrate_length.py)
except Exception: LEN_W={}
try: SEC_DY=_json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),f'sec_dy{_SFX}.json'),encoding='utf-8'))
except Exception: SEC_DY={}
class Escriba:
    def __init__(self,**kw):
        self.p=dict(DEFAULT); self.p.update(kw); self.famrep=dict(FAMREP); self.famrep.update(kw.get('famrep',{})); self.sec_e=dict(SEC_E); self.sec_e.update(kw.get('sec_e',{})); self.sec_dy=dict(SEC_DY); self.sec_dy.update(kw.get('sec_dy',{}))
    def table(self,lang,hand=None,sec=None):
        if self.p['use_sec_tab'] and (hand,sec) in TAB_HS: return TAB_HS[(hand,sec)]
        if self.p['use_hand_tab'] and hand in TAB_H: return TAB_H[hand]
        return TAB[lang] if (self.p['use_lang'] and lang in TAB) else TAB['*']
    def table_end(self,lang,hand=None,sec=None):
        if self.p['use_sec_tab'] and (hand,sec) in TAB_END_HS: return TAB_END_HS[(hand,sec)]
        if self.p['use_hand_tab'] and hand in TAB_END_H: return TAB_END_H[hand]
        return TAB_END[lang] if (self.p['use_lang'] and lang in TAB_END) else TAB_END['*']
    def next_glyph(self,tab,ctx,g,style):
        c=tab.get(ctx)
        if not self.p['use_boundary'] and ctx[0].startswith('<'): c=BACK.get(('*',ctx[1]))
        if not c or sum(c.values())<5: c=BACK.get((('*' if ctx[0].startswith('<') else ctx[0]),ctx[1])) or c
        if not c: return '$'
        ks=list(c); ws=np.array([c[k] for k in ks],float)
        if style is not None:
            for i,k in enumerate(ks):
                if k=='t' and 'k' in c: ws[i]*=math.exp(style['t'])
                elif k=='sh' and 'ch' in c: ws[i]*=math.exp(style['sh'])
                elif k=='q' and len(g)==0: ws[i]*=math.exp(style['q'])
                elif k=='d' and g and g[-1]=='e': ws[i]*=math.exp(style['dy'])
                elif k=='e' and g and g[-1] in NUC and 'e' in style: ws[i]*=math.exp(style['e'])
                elif k in ('t','k','p','f') and len(g)==0 and style.get('g0'): ws[i]*=math.exp(style['g0'])
        return self.rng.choices(ks,weights=ws.tolist())[0]
    def gen_word(self,tab,A,style):
        for _ in range(15):
            g=[]
            for j in range(13):
                x=self.next_glyph(tab,seq_ctx(A,g,j),g,style)
                if x=='$': break
                g.append(x)
            w=''.join(g)
            if not w: continue
            if self.p['use_slots'] and not M.slot_ok(w): continue
            if self.p['new_known']>0 and LEX[w]<LEX_MIN and self.rng.random()<self.p['new_known']: continue   # form memory: the unknown word is redrawn
            if self.p['use_word_rules']:
                if sum(x in GALL for x in g)>=2 and self.rng.random()<self.p['rej_2gall']: continue
                if 'e' in g and 'i' in g and self.rng.random()<self.p['rej_ei']: continue
            return w
        return w or 'o'
    def modify(self,w):
        if self.p['mod_lex']>0 and self.rng.random()<self.p['mod_lex']:
            nb=lex_neighbors(w)
            if self.p['use_slots']: nb=[x for x in nb if M.slot_ok(x)]
            if nb: return self.rng.choices(nb,weights=[LEX[x]**self.p['lex_alpha'] for x in nb])[0]
        g=gl(w)
        for _ in range(int(self.p['mod_tries'])):
            r=self.rng.random()*(NS+NI+ND); g2=g[:]
            if r<NS:
                i=self.rng.randrange(len(g2)); c=subby.get(g2[i])
                if not c: continue
                g2[i]=self.rng.choices(list(c),weights=list(c.values()))[0]
            elif r<NS+NI: g2.insert(self.rng.randrange(len(g2)+1),self.rng.choices(list(ins),weights=list(ins.values()))[0])
            else:
                if len(g2)<2: continue
                del g2[self.rng.randrange(len(g2))]
            w2=''.join(g2)
            if w2==w or (self.p['use_slots'] and not M.slot_ok(w2)): continue
            if self.p['mod_contact']>0 and not contact_ok(w2,self.p['mod_contact']): continue   # the edit must be writable with the memory of two
            if self.p['use_word_rules'] and sum(x in GALL for x in g2)>=2 and sum(x in GALL for x in g)<2 and self.rng.random()<self.p['rej_2gall']: continue
            return w2
        if self.p['mod_fallback']=='lex':                 # no writable edit: a known neighbour, if there is one
            nb=[x for x in lex_neighbors(w) if (not self.p['use_slots'] or M.slot_ok(x))]
            if nb: return self.rng.choices(nb,weights=[LEX[x]**self.p['lex_alpha'] for x in nb])[0]
        return w
    def close(self,w,probs):
        for (o,c_),p in probs.items():
            if w.endswith(o) and not w.endswith(c_) and self.rng.random()<p: return w[:-len(o)]+c_
        return w
    def write(self,seed=0,layout=None):
        p=self.p; self.rng=random.Random(seed); np_rng=np.random.default_rng(seed)
        e_rng=np.random.default_rng(seed+7919); sheet_e={}; e_page=None; e_page_line=None; e_pg=0.0; e_line=0.0; g0_page=None; g0_pg=0.0; g0_line=0.0
        sheet_style=defaultdict(lambda: {d:float(np_rng.normal(0,p['sigma_style'])) for d in STYLE_DIMS})
        out=[]; page=None; prev_pages=[]; sheet_words=defaultdict(list); cur_sheet=None   # memory across pages (19/10): the last pages of the book (prev_pages) and the pages already written on the same sheet (sheet_words)
        for l in (layout if layout is not None else L_ALL):
            if l['page']!=page:
                if page is not None and (p['r_prev']>0 or p['r_stock']>0) and page_words: prev_pages=([[w for w,_,_ in page_words]]+prev_pages)[:int(p['n_prev'])]
                if page is not None and page_words: sheet_words[cur_sheet].extend(w for w,_,_ in page_words)
                cur_sheet=l['sheet']
                page=l['page']; page_words=[]; lines_on_page=[]; above_first=None
                ps_=sheet_style[l['sheet']]; pg_style={d:ps_[d]+float(np_rng.normal(0,p['sigma_style'])) for d in STYLE_DIMS}
                line_dev={d:0.0 for d in STYLE_DIMS}
            if l['ps']==1: above_first=None; line_dev={d:0.0 for d in STYLE_DIMS}
            line_dev={d:p['rho_line']*line_dev[d]+float(np_rng.normal(0,p['sigma_line'])) for d in STYLE_DIMS}
            style={d:pg_style[d]+line_dev[d] for d in STYLE_DIMS} if p['use_style'] else None
            if style is not None and p['use_ehabit']:
                if l['page']!=e_page:
                    e_page=l['page']; e_pg=sheet_e.setdefault(l['sheet'],float(e_rng.normal(0,p['sigma_e'])))+float(e_rng.normal(0,p['sigma_e']))
                if l['ps']==1 or l['page']!=e_page_line: e_line=0.0; e_page_line=l['page']
                e_line=p['rho_line']*e_line+float(e_rng.normal(0,p['sigma_line']))
                style['e']=e_pg+e_line+(self.sec_e.get(l.get('section',''),0.0) if p['use_sec_e'] else 0.0)
            if style is not None and p['use_sec_dy']: style['dy']+=self.sec_dy.get(l.get('section',''),0.0)   # -dy or -y: also a section habit
            if style is not None and p['use_g0']:
                # gallows-initial habit (20/10): lines full of words starting with t/k/p/f and lines without; a page value plus a line value,
                # independent for each line (shuffling within the line does not remove the real clustering; shuffling within the page partly does).
                # Centred so that the mean frequency does not move, plus g0_mu. The first word of the line is left alone (already set by the boundary)
                if l['page']!=g0_page: g0_page=l['page']; g0_pg=float(np_rng.normal(0,p['sigma_g0_pg']))
                g0_line=g0_pg+float(np_rng.normal(0,p['sigma_g0_line']))-(p['sigma_g0_pg']**2+p['sigma_g0_line']**2)/2+p['g0_mu']
            tab=self.table(l['lang'],l.get('hand'),l.get('section')); lam=float(np_rng.normal(0,p['sigma_len'])) if p['use_len_mode'] else 0.0
            first_line=(l['ps']==1) and p['use_first_line']
            if style is not None and first_line and p['use_fl_style']:
                # first-line register (26/10): the first line of the paragraph prefers the tall variants, sh over ch and t over k
                # (sh 50% against 31% in the other lines, t 43% against 35%), on top of p/f (R1.3)
                style['t']+=p['fl_t']; style['sh']+=p['fl_sh']
                if 'e' in style: style['e']+=p['fl_e']   # and fewer words with e after the core (ee: 11.5% against 13.3%)
            ws=[]; li=len(lines_on_page)
            for i in range(len(l['ws'])):
                A=start_tag(l,i,ws[i-1] if i else None) if p['use_contexts'] else ('<'+gl(ws[i-1])[-1] if i else '^')
                if style is not None and p['use_g0']: style['g0']=g0_line if i>0 else 0.0
                rc=p['r_copy']*(p['first_copy'] if first_line else 1.0)
                w=None
                if p['use_copy'] and i>0 and page_words and self.rng.random()<rc:
                    # visible field: the words already written on the page; weight by proximity in lines, bonus for the same position on the line above,
                    # and compatibility with the boundary (probability of the first glyph in this context)
                    c=tab.get((A,'_'),Counter()); tot=sum(c.values()) or 1
                    wts=[math.exp(-(li-lj)/p['tau'])*(p['vert_bonus'] if (li-lj==1 and abs(ij-i)<=1) else 1.0)*(c[gl(pw)[0]]/tot+1e-4)
                         *((self.famrep.get(family(pw),1.0)*p['adj_boost']*(WREP.get(pw,1.0)**p['wordrep_pow'] if p['use_wordrep'] else 1.0)) if (p['use_famrep'] and lj==li and ij==i-1) else 1.0) for pw,lj,ij in page_words]
                    w=self.rng.choices([pw for pw,_,_ in page_words],weights=wts)[0]
                    if p['r_sheet']>0 and sheet_words[l['sheet']] and self.rng.random()<p['r_sheet']:
                        w=self.rng.choice(sheet_words[l['sheet']])   # the session vocabulary: pages already written on the same sheet (G6)
                    elif prev_pages and self.rng.random()<p['r_prev']:
                        # copying from an earlier page: the weight of each page halves every h_prev pages (vocabulary drift)
                        pw_=[2.0**(-k/p['h_prev']) for k in range(len(prev_pages))]
                        pg_=self.rng.choices(prev_pages,weights=pw_)[0]
                        if pg_: w=self.rng.choice(pg_)
                    edited=False
                    if first_line or self.rng.random()<p['r_mod']: w2=self.modify(w); edited=(w2!=w); w=w2
                    if i<len(l['ws'])-1 and p['use_closure'] and self.rng.random()<p['declose_p']: w=declose(w)
                    if l['gb'][i] and w.startswith('qo') and self.rng.random()<p['gap_noq']: w=w[1:]          # after the drawing gap, start form: no q- (R6.1)          # closure is a matter of position (R4.3): inside the line, open form
                    if p['use_reprefix'] and edited and not l['gb'][i]:
                        # the prefix is decided by the boundary, also on copied words (R3.3)
                        k_,core=M.split_prefix(w)
                        if k_:
                            key=(gl(ws[-1])[-1],''.join(gl(core)[:2])); c=PREF.get(key)
                            if not c or sum(c.values())<8: c=PREF_BACK.get((key[0],key[1][:1]))
                            if c:
                                ks_=list(c); wt_=[c[k2]*(math.exp(style['q']) if (style is not None and k2=='q') else 1.0) for k2 in ks_]
                                kk=self.rng.choices(ks_,weights=wt_)[0]
                                if kk in PFX and not (kk=='q' and core[0]!='o'): w=PFX[kk]+core
                    if not first_line and p['use_first_line'] and self.rng.random()<p['pf_back']:
                        # p/f is the first-line variant of any gallows (R1.3): outside the first line it goes back to k/t
                        w=w.replace('cph','ckh').replace('cfh','cth').replace('p','k').replace('f','t')
                if w is None and p['r_stock']>0 and prev_pages and 0<i<len(l['ws'])-1 and not first_line and self.rng.random()<p['r_stock']:
                    # reuse of the recent repertoire (19/10): instead of inventing, a word from the last pages; the weight of each page
                    # halves every h_stock pages. Interior form (no closure) and prefix according to the boundary
                    pg_=self.rng.choices(prev_pages,weights=[2.0**(-k/p['h_stock']) for k in range(len(prev_pages))])[0]
                    if pg_:
                        w=self.rng.choice(pg_)
                        if p['use_closure']: w=declose(w)
                        if p['use_reprefix'] and not l['gb'][i]:
                            k_,core=M.split_prefix(w)
                            if k_:
                                key=(gl(ws[-1])[-1],''.join(gl(core)[:2])); c=PREF.get(key)
                                if not c or sum(c.values())<8: c=PREF_BACK.get((key[0],key[1][:1]))
                                if c:
                                    kk=self.rng.choices(list(c),weights=list(c.values()))[0]
                                    if kk in PFX and not (kk=='q' and core[0]!='o'): w=PFX[kk]+core
                        if p['use_first_line']: w=w.replace('cph','ckh').replace('cfh','cth').replace('p','k').replace('f','t')
                if w is None:
                    tb=self.table_end(l['lang'],l.get('hand'),l.get('section')) if (i==len(l['ws'])-1 and len(l['ws'])>1 and p['use_end_table']) else tab
                    cands=[self.gen_word(tb,A,style) for _ in range(p['len_cands'] if p['use_len_mode'] else 1)]
                    if len(cands)>1:
                        wt=np.array([math.exp(lam*(len(gl(x))-4.8)) for x in cands])
                        if p['use_len_w']:
                            # the length of the new word according to its position in the line (19/10): the two-glyph memory makes words too short and too spread out
                            lw=(p['len_w'] or LEN_W).get('first' if i==0 else ('last' if i==len(l['ws'])-1 else 'mid'),{})
                            wt=wt*np.array([lw.get(str(min(len(gl(x)),10)),1.0) for x in cands])
                        if first_line and i>0 and p['use_fl_style'] and p['fl_rare']>0:
                            # and it prefers rarer words (R5.2): frequent words (>= fl_rare_min of the training text) are disfavoured among the candidates
                            wt=wt*np.array([math.exp(-p['fl_rare']) if LEX[x]>=p['fl_rare_min']*LEXN else 1.0 for x in cands])
                        w=cands[int(self.rng.choices(range(len(cands)),weights=wt)[0])]
                    else: w=cands[0]
                    if i==0 and l['ps']==0 and p['use_dissim'] and above_first is not None and gl(w)[0]==above_first and self.rng.random()<min(1.0,p['avoid_scale']*AVOID.get(above_first,0.4)):
                        for _ in range(6):
                            w2=self.gen_word(tab,A,style)
                            if gl(w2)[0]!=above_first: w=w2; break
                if first_line and i>0 and w==ws[-1] and self.rng.random()<p['first_norep']:
                    for _ in range(4):
                        w2=self.gen_word(tab,A,style)
                        if w2!=ws[-1]: w=w2; break
                if first_line and i>0 and self.rng.random()<p['p_pf']:
                    w=w.replace('ckh','cph').replace('cth','cfh') if ('ckh' in w or 'cth' in w) else w.replace('k','p',1) if 'k' in w else w.replace('t','f',1)
                ws.append(w); page_words.append((w,li,i))          # the word enters the visible field as it is written
            if p['use_closure']:
                if l['pe']==1: cp=CL_PAR_HAND.get(l['hand'],CL_PAR) if p['par_by_hand'] else CL_PAR; cp={k:v*p['par_scale'] for k,v in cp.items()}
                elif p['closure_by_hand']: cp=CL_HAND_NW.get((l['hand'],nw_bin(len(ws))),CL_HAND.get(l['hand'],CL_LINE)) if p['closure_by_nwords'] else CL_HAND.get(l['hand'],CL_LINE)
                else: cp=CL_LINE
                ws[-1]=self.close(ws[-1],cp)
                for i in range(2,len(ws)):
                    if l['gb'][i]: ws[i-1]=self.close(ws[i-1],{k:v*p['gap_scale'] for k,v in CL_GAP.items()})
            above_first=gl(ws[0])[0]
            for k_,w in enumerate(ws): page_words[len(page_words)-len(ws)+k_]=(w,li,k_)   # final forms (closure) in the visible field
            lines_on_page.append(ws)
            out.append(dict(page=l['page'],sheet=l['sheet'],lang=l['lang'],ps=l['ps'],pe=l['pe'],ws=ws,gb=l['gb']))
        return out
if __name__=='__main__':
    import sys, json, time
    t=time.time(); G=Escriba().write(seed=1); print(f'generated in {time.time()-t:.0f} s')
    for l in G[:14]: print(('¶ ' if l['ps']==1 else '  ')+' '.join(w if not g else '<-> '+w for w,g in zip(l['ws'],l['gb'])))
