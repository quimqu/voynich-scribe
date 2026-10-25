#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_df.py: ZL3b (IVTFF 2.0, Eva-) -> dataframe of lines with a stroke transliteration.
Sources: voynich.nu (IVTFF_format.pdf 2.0.1, IVTT_manual 2.4, transcr.html); file ZL3b-n.txt.
Space policy (quimqu's decision, phase X): comma (uncertain space) -> removed, and the
glyphs are joined; the position of each join is recorded in comma_join_positions.
"""
import re, json, collections, sys
import pandas as pd

SRC = 'ZL3b-n.txt'

# ---------------------------------------------------------------- stroke maps
# Primitives (upper case, disjoint from lower-case EVA):
#  C curve · I minim · L leg/tall stem · O loop · B bar/bench · U tail up
#  J tail down · Q tail-loop · F tall flourish · P plume · X cross · V vertex
#  G foot hook · T platform · M short high bar · R mirror curve · D small ring
#  ' (in code: `) allograph/capital mark · W+id weirdo · ? GAP (illegible)
STROKES = {  # EVA glyph -> (primitives, status)  status: ok | review
    'e':('C','ok'), 'i':('I','ok'), 'o':('O','ok'), 'a':('CI','ok'),
    'c':('CB','ok'), 'h':('BC','ok'), 'ch':('CBC','ok'), 'sh':('CBCP','ok'),
    'n':('IU','ok'), 'b':('CU','ok'), 'r':('IF','ok'), 's':('CF','ok'),
    'd':('OO','ok'), 'y':('OJ','ok'), 'l':('OU','review'), 'g':('CQ','review'),
    'm':('IQ','ok'), 'q':('LB','review'),
    'f':('LBO','ok'), 'k':('LLBO','ok'), 'p':('LBOO','ok'), 't':('LLBOO','ok'),
    'ckh':('CBLLBOBC','ok'), 'cth':('CBLLBOOBC','ok'),
    'cfh':('CBLBOBC','ok'), 'cph':('CBLBOOBC','ok'),
    'x':('X','ok'), 'v':('V','review'), 'j':('OOJ','review'),
    'u':('CC','review'), 'z':('IJ','review'),
    "'":('P','ok'),      # detached plume (unofficial EVA): modifier of the previous glyph
    '?':('?','ok'),      # GAP: illegible character in the transcription
}
# Extended EVA (@nnn;): families proposed in phase X; all 'review' until validated by quimqu.
EXT_STROKES = {
    130:'LLBOGG', 131:'LM', 132:'LBB', 133:'LBG', 134:'LLBB', 136:'D',
    148:'OLLBOO', 165:'LG', 169:'LOD', 171:'LLBOP', 175:'LOB', 172:'IF`',
    177:'LLBOT', 182:'LT', 183:'GL', 185:'LLM', 196:'LTO', 199:'LLBOOP',
    202:'LBLBOO', 204:'MJ', 215:'LLB', 221:'O^', 222:'OJ^', 223:'L',
    240:'OM', 246:'T',
}
GLYPH_RE = re.compile(r'@\d{3};|ckh|cth|cfh|cph|ch|sh|[a-z\'?]|[A-Z]')

def glyph_tokens(word):
    out, i = [], 0
    while i < len(word):
        m = GLYPH_RE.match(word, i)
        if not m:
            out.append(('<BAD:%s>' % word[i], None)); i += 1; continue
        g = m.group(0); i = m.end()
        if g.startswith('@'):
            out.append((g, int(g[1:-1])))
        elif g.isupper():                       # capitalised EVA -> base + `
            out.append((g.lower()+'`', None))
        else:
            out.append((g, None))
    return out

def strokes_for(g, ext):
    if ext is not None:
        return ('W%d' % ext) if ext not in EXT_STROKES else EXT_STROKES[ext]
    cap = g.endswith('`') and len(g) > 1
    base = g[:-1] if cap else g
    s = STROKES.get(base)
    if s is None: return 'W?'
    return s[0] + ('`' if cap else '')

# ------------------------------------------------------------------- parsing
page_hdr_re = re.compile(r'^<([^.>,;]+)>\s+<!(.*)>\s*$')
locus_re    = re.compile(r'^<([^.>]+)\.(\d+[a-z]?),(.{3})(?:;(\w))?>\s*(.*)$')
var_re      = re.compile(r'\$(\w)=(\S+)')

SECTION = {'A':'astro','B':'biological','C':'cosmological','H':'herbal',
           'P':'pharmaceutical','S':'stars','T':'text_only','Z':'zodiac'}

rows, cur = [], {}
page_seq = 0
raw_lines = open(SRC, encoding='utf-8').read().split('\n')
# join '/' continuations
merged, buf = [], None
for ln in raw_lines:
    if buf is not None:
        assert ln.startswith('/'), 'continuation without /'
        buf = buf[:-1] + ln[1:]
        if not buf.endswith('/'): merged.append(buf); buf = None
        continue
    if not ln.startswith('#') and ln.rstrip().endswith('/') and locus_re.match(ln):
        buf = ln.rstrip(); continue
    merged.append(ln)

par_idx = 0; line_in_par = 0
for ln in merged:
    if ln.startswith('#') or not ln.strip(): continue
    m = page_hdr_re.match(ln)
    if m:
        page_seq += 1
        cur = {'page_tag': m.group(1), 'page_seq': page_seq}
        cur.update({k: v for k, v in var_re.findall(m.group(2))})
        par_idx = 0; line_in_par = 0
        continue
    m = locus_re.match(ln)
    if not m:
        if ln.startswith('<'): print('WARNING unrecognised line:', ln[:60])
        continue
    page, num, code, transcriber, txt = m.groups()
    assert page == cur.get('page_tag'), 'locus outside its page: %s' % ln[:40]

    rec = dict(
        page_tag=page, page_seq=cur['page_seq'], locus_num=num,
        locus_full=code, locus_locator=code[0], locus_type=code[1:],
        locus_generic=code[1], is_label=int(code[1] == 'L'),
        transcriber=transcriber,
        quire=cur.get('Q'), page_in_quire=cur.get('P'), folio_in_quire=cur.get('F'),
        bifolio_num=cur.get('B'),
        sheet_id=(cur.get('Q','') + cur.get('B','')) or None,
        illustration=cur.get('I'), section=SECTION.get(cur.get('I')),
        currier_language=cur.get('L'), davis_hand=cur.get('H'),
        currier_hand=cur.get('C'), extraneous=cur.get('X'),
        text_eva_raw=txt,
    )
    t = txt
    # paragraphs
    rec['paragraph_start'] = int('<%>' in t)
    rec['paragraph_end']   = int('<$>' in t)
    if rec['paragraph_start']: par_idx += 1; line_in_par = 0
    line_in_par += 1
    rec['par_index_in_page'] = par_idx if code[1] == 'P' else None
    rec['line_in_par'] = line_in_par if code[1] == 'P' else None
    t = t.replace('<%>', '').replace('<$>', '')
    # free comments <!...>
    rec['inline_comments'] = '; '.join(re.findall(r'<!([^>]*)>', t)) or None
    t = re.sub(r'<![^>]*>', '', t)
    # drawing intrusion <-> = space (recorded); other short tags, recorded and removed
    rec['n_drawing_gaps'] = t.count('<->')
    t = t.replace('<->', '.')
    other = re.findall(r'<[^>]{1,4}>', t)
    rec['inline_other_tags'] = '; '.join(other) or None
    for o in other: t = t.replace(o, '')
    # alternative readings [a:b] -> the first one (IVTT option -u1)
    alts = re.findall(r'\[([^\]]*)\]', t)
    rec['alt_readings'] = '; '.join(alts) or None
    rec['n_alt'] = len(alts)
    t = re.sub(r'\[([^:\]]*)(?::[^\]]*)?\]', r'\1', t)
    # ligatures {xyz}: content kept, span recorded
    ligs = re.findall(r'\{([^}]*)\}', t)
    rec['ligature_groups'] = '; '.join(ligs) or None
    rec['n_ligatures'] = len(ligs)
    t = re.sub(r'\{([^}]*)\}', r'\1', t)
    t = t.strip('.').strip()
    rec['text_eva'] = t                       # canonical, with commas
    # comma policy: glyphs joined, positions recorded
    joins, out, widx, cpos = [], [], 0, 0
    for w in t.split('.'):
        if not w: continue
        while ',' in w:
            k = w.index(','); joins.append((widx, k)); w = w[:k] + w[k+1:]
        out.append(w); widx += 1
    rec['text'] = '.'.join(out)
    rec['comma_join_positions'] = '; '.join('%d:%d' % j for j in joins) or None
    rec['n_comma_joins'] = len(joins)
    # glyphs and strokes
    words = rec['text'].split('.') if rec['text'] else []
    seg_words, flat_words, n_g, n_w, n_gap = [], [], 0, 0, 0
    ext_used = []
    for w in words:
        toks = glyph_tokens(w)
        segs = []
        for g, ext in toks:
            s = strokes_for(g, ext)
            if s.startswith('W'): n_w += 1
            if ext is not None: ext_used.append(str(ext))
            if s == '?': n_gap += 1
            segs.append(s); n_g += 1
        seg_words.append('|'.join(segs)); flat_words.append(''.join(segs))
    rec['n_words'] = len(words)
    rec['n_glyphs'] = n_g
    rec['text_strokes_seg'] = '.'.join(seg_words)
    rec['text_strokes_flat'] = '.'.join(flat_words)
    rec['n_weirdo'] = n_w; rec['n_gap'] = n_gap
    rec['extended_used'] = ';'.join(ext_used) or None
    rows.append(rec)

df = pd.DataFrame(rows)

# ------------------------------------------------------- invertibility assert
REV = {v[0]: k for k, v in STROKES.items()}
assert len(REV) == len(STROKES), 'stroke code collision between glyphs!'
_all = list(REV.keys()) + list(EXT_STROKES.values())
assert len(_all) == len(set(_all)), 'glyph<->extended collision in the stroke map!'
REV_EXT = {v: k for k, v in EXT_STROKES.items()}
bad = 0
for _, r in df.iterrows():
    if not r['text']: continue
    for w_eva, w_seg in zip(r['text'].split('.'), r['text_strokes_seg'].split('.')):
        back = []
        for s in w_seg.split('|'):
            if s.startswith('W') and s[1:].isdigit(): back.append('@%s;' % s[1:])
            elif s in REV_EXT: back.append('@%d;' % REV_EXT[s])
            elif s.endswith('`') and s[:-1] in REV: back.append(REV[s[:-1]].upper())
            elif s in REV: back.append(REV[s])
            else: back.append('<?>')
        if ''.join(back) != w_eva: bad += 1
print('ROUNDTRIP seg->EVA: non-invertible words =', bad, 'of', int(df.n_words.sum()))
assert bad == 0, 'the seg column must be invertible'

# ------------------------------------------------------------------ summaries
tok = int(df.n_words.sum())
run = int(df[df.locus_generic == 'P'].n_words.sum())
lab = int(df[df.is_label == 1].n_words.sum())
circ = int(df[df.locus_generic.isin(['C', 'R'])].n_words.sum())
gly = int(df.n_glyphs.sum())
cov = 1 - (df.n_weirdo.sum() + df.n_gap.sum()) / gly
print(f'loci={len(df)}  pages={df.page_seq.nunique()}  tokens={tok} '
      f'(P={run}, labels={lab}, C/R={circ})')
print(f'glyphs={gly}  stroke coverage (without W or GAP) = {cov:.4%}')
print('commas joined =', int(df.n_comma_joins.sum()),
      '| ligatures =', int(df.n_ligatures.sum()),
      '| alternatives =', int(df.n_alt.sum()),
      '| gaps <-> =', int(df.n_drawing_gaps.sum()))
print('\nlocators:', dict(df.locus_locator.value_counts()))
print('language:', dict(df.currier_language.value_counts(dropna=False)))
print('Davis hands:', dict(df.davis_hand.value_counts(dropna=False)))

df.to_csv('df_lines_ZL3b_strokes.csv', index=False)
json.dump({'primitives': {
    'C':'curve','I':'minim','L':'leg/tall stem','O':'loop','B':'bar/bench',
    'U':'tail up','J':'tail down','Q':'tail-loop','F':'tall flourish','P':'plume',
    'X':'cross','V':'vertex','G':'foot hook','T':'platform','M':'short high bar',
    'R':'mirror curve','D':'small ring','`':'allograph/capital mark','?':'GAP','W':'weirdo+id'},
    'glyphs': {k: {'strokes': v[0], 'status': v[1]} for k, v in STROKES.items()},
    'extended': {str(k): {'strokes': v, 'status': 'review'} for k, v in EXT_STROKES.items()}},
    open('stroke_map.json', 'w'), ensure_ascii=False, indent=1)

# review CSV of the extended glyphs by actual frequency
ec = collections.Counter()
for s in df.extended_used.dropna():
    for e in s.split(';'): ec[int(e)] += 1
pd.DataFrame([{'code': c, 'count': n,
               'proposed_strokes': EXT_STROKES.get(c, ''),
               'status': 'review' if c in EXT_STROKES else 'UNMAPPED->W'}
              for c, n in ec.most_common()]
             ).to_csv('extended_review.csv', index=False)
print('\nfiles: df_lines_ZL3b_strokes.csv, stroke_map.json, extended_review.csv')
