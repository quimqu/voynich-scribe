# The Scribe: a rule-based procedure that writes a Voynich-like text

> **Version note (26 October 2026).** This document describes the scribe of 14 October 2026 and its battery of 64 measures (58 of 64 reproduced). The code in this repository is the version of 19 October (per-hand vocabulary, length by position, 22% copying) scored on a battery of 76 measures: 69 of 76, see the repository README and `escriba/ESCRIBA.md` §9. The rules, the procedure and the findings below are unchanged; only the figures moved.


*What it reproduces, what it doesn't, and what it suggests about how the Voynich Manuscript was written.*
*October 2026.*

---

## Summary

- **The scribe** is a generator that writes a whole synthetic manuscript on the **same layout** as the real one: the same pages, sheets, paragraphs, lines, words per line, drawing gaps, Currier language and Davis hand. Only the words are new. There is no layer of meaning anywhere in it.
- It is compared with the real text on **64 measures**: repetition, near-duplicates, word-boundary agreement, line-start and line-end forms, first-line effects, vertical dissimilation, page and sheet habits, word shape, and what the eye sees. It reproduces **58/64** within ±25% (mean of 5 seeds). A simpler three-rule generator reproduces 33/64.
- Learnt **only from odd folios** and asked to write the even ones, it reproduces **51/64**. The two real halves reproduce each other at 55/64.
- Two results I did not expect:
  1. **The eye did not need a dictionary.** To stop producing impossible-looking words, the scribe did not need a lexicon of known words. It needed its edits to copied words to obey the same 2-glyph memory it already uses to write new words.
  2. **The word family is a habit of the sheet.** The choice between words with *e* (*-edy*, *-ey*) and words without (*-aiin*, *-ar*, *-ol*) is shared by the pages of a sheet, including the conjugate folio far away in reading order, and not by neighbouring pages. In the herbal section, where every page shows a different plant: z = −7.0 for the conjugate folio, −0.7 for the neighbouring page of another sheet.

This does **not** show that the manuscript is meaningless. It shows that a concrete, meaningless writing procedure is *sufficient* to produce almost everything we currently know how to measure.

## The rules, in short

These are the regularities measured on the real text before building the scribe. "System" means all five Davis hands follow the rule; "habit" means its form is shared, but its strength varies by hand, page or sheet.

### Glyphs and words

- **Allographs.** *k~t*, *ch~sh* and *p~f* behave as one sign each in different places. Which one is used is decided by place and by the page's habit (0.009 bits of context). System.
- **Glyph positions.** *q* is always followed by *o* and is always word-initial (98%). *e, i, n, m* never start a word, and *e, a, i, ch, q* never end one. System.
- **The template.** A word is `[prefix] [core] [e…] [ending]`:
  - prefix: *qo-, o-, y-, d-, s-, ch-, l-* or none, and never before a bench;
  - core: a gallows or a bench, or nothing;
  - one to three *e*;
  - an ending.

  A 23-slot grammar learnt from the data covers 98.8% of the tokens. There is at most one gallows per word (two in 1.8% of words, three never). System.
- **Two blocks.** Words with *e* end in *-y/-dy* (*qokeedy, chedy*); words without *e* end in *-aiin, -ain, -ar, -al, -ol* (*qokaiin, okal*). *e* and *i* avoid each other (0.15 of expected). These are two routes through the template, not a paradigm: the mutual information between core and ending is 0.83 bits, against 0.28 for the null. System. The choice between the blocks is a habit of the sheet (§5).
- **Contact rules.** *i* runs only as *a + i(1–3) + n/r/m* (99%); *n* and *m* are word-final (95%); only *e* and *i* double; *l* is the only tail glyph that can precede a gallows or a bench. System.
- **Two-glyph memory.** With eight functional classes (*o, a, i, d, q*; the *e*/bench class; gallows; and the endings *y n m g l r s*), the next glyph is predicted almost as well as with all 22 glyphs (2.33 vs 2.24 bits). What a memory of two adds is exactly the template: prefix, *qo-* + gallows, runs of *e* and *i*, final *o*. System.
- **Near twins.** 95.6% of tokens have a word at edit distance ≤ 1 already written on the same page, typically three lines above. Process.

### Between words

- **The space is a glyph rule.** It can be guessed 87% of the time from two glyphs on each side. Some boundaries are firm (*-y|q-*, *-n|ch-*); others are weak (*r|a, o|l*: transcribers hesitate 28–45% of the time). System.
- **Boundary agreement.** The prefix of a word depends on the last glyph of the previous word and on the word's own first two glyphs, and on nothing else:
  - after *-y*, an *o-* word takes *q-* 56% of the time and an *a-* word takes *d-* 73%;
  - after *-r* or *-s*, both take nothing 79–89% of the time.

  What matters is the *stroke* the previous word ends with: it carries 91% of the information of the whole glyph. The form is system; the strength is habit (hand 1: *q-* after *-y* 0.14; hands 2–3: 0.33).
- ***q-* is the continuation form**: 1% in labels, 4% on the first word of a paragraph, 13% on the first word of a line, 18% inside a line. System.
- **No syntax.** Beyond the contact glyph, no word predicts the next one: 0.16 bits at distance 1, 0.009 at distance 2. No resegmentation changes this. System.

### The line

- **The line is the unit.** All sequential structure lives in the first word, the last word and the repetitions. System.
- **Start forms.** The first word starts with *d-, s-* or *y-* 40% of the time (13% inside the line) and almost never with *a-* (0.3% against 4.3%). A bare gallows is a line-start form. System.
- **End forms.** The last word is closed: *-iin→-m* 60% (7% inside), *-l→-ly* and *-r→-ry* 25% (2–4% inside), *-s→-sy*, *-y→-g*. Overall, 25% of line-final words against 2.3% inside. It depends neither on the distance to the margin (measured with coordinates) nor on the number of words once the hand is controlled. The form is system; the strength is habit (*-m* for *-iin*: hand 1 0.37, hand 5 0.85).
- **Vertical dissimilation.** Consecutive lines avoid starting with the same glyph (ratio 0.60, z −10), and only the first glyph. It is strongest after *ch* or a gallows. It does not depend on line spacing or alignment, and it does not decay with the length of the line above. Habit.

### Paragraphs and drawings

- **Paragraph start.** The first word carries a gallows 93% of the time, and almost never *q-*. System.
- **First-line register.** In the first line, 35% of gallows are *p/f* (3% elsewhere), more when there is free space above. Words are longer and newer, and repeats are half as frequent. System.
- **A drawing is a margin.** The word before a drawing gap half-closes (10% closed forms against 2% inside); the word after it opens like a new line (*d-/s-/y-* 41%). The boundary agreement breaks there. Gaps almost never split a word. The text was written after the drawings. System.

### Page and sheet

- **Copying from the page.** About a third of the words are copies of a word written a few lines above, often with one glyph changed.
- **Page rates.** Each page has its own rate for every free choice (*k/t, ch/sh, q-, -y/-dy*, word family): overdispersion z +10 to +58 beyond language, section and hand. The rate drifts over a few lines. Habit.
- **The sheet is the session.** The pages of a sheet, including the conjugate folio, share vocabulary, free-choice rates, word family, letter size and line spacing. The neighbouring folio of another sheet does not. Habit.
- **A and B** are the same system with different weights: slot grammars learnt on each language cover each other 98%.

---

## 1. Data and method

- **Text**: ZL3b transliteration (Zandbergen–Landini, IVTFF 2.0), paragraph text only (no labels, no circular or radial text), in EVA. Benches and gallows (*ch, sh, cth, ckh, cph, cfh*) count as single glyphs. Ligature braces `{…}` keep their content.
- **Metadata**: Currier language A/B, Lisa Fagin Davis' scribal hands, quires and sheets (bifolios) from the standard codicological reconstruction.
- **Comparison**: every scribe figure is the mean of 5 random seeds. A measure is *reproduced* if it lies within ±25% of the real value (within 0.01 absolute for values near zero). The full list is in the appendix.
- **Controls**:
  - **Ablation**: remove each rule in turn and count the measures lost.
  - **Hold-out**: learn every table and fitted parameter from odd folios only, then write the layout of the even folios and compare with the real even folios. The real odd folios against the real even folios give the natural difference between halves.
- **Strange words**: a word is *strange* if it contains a glyph trigram (word start and end included) that occurs ≤ 3 times in the whole real text. In the real text, 4.6% of words are strange (0.36 per line). It is a crude stand-in for "this word looks wrong".

---

## 2. The procedure

For every sheet, page, paragraph and line, in this order:

1. **Sheet habit.** Each sheet has its own rate for five free choices: *k* vs *t*, *ch* vs *sh*, *q-* or not, *-dy* vs *-y*, and the *e*-word family vs the *e*-less family. Each page of the sheet varies a little around it, and within a paragraph the rate drifts from line to line (memory 0.6).
2. **Section offset.** The *e* and *-dy* habits get a per-section offset, fitted so that each section's share matches the real one (11 numbers in total). Fitted on all folios or on odd folios only, they come out almost the same:

   | | *e* habit (all / odd only) | *-dy* habit (all / odd only) |
   |---|---|---|
   | herbal | −0.41 / −0.40 | +0.60 / +0.62 |
   | biological | +0.36 / +0.44 | +0.47 / +0.45 |
   | stars | +0.37 / +0.37 | −0.38 / −0.46 |
   | pharmaceutical | +1.55 / +1.23 | +2.28 / +2.10 |

3. **Language.** A and B use the same glyph-contact table with different weights.
4. **Line length tone.** This line will have slightly longer or shorter words than average.
5. **Each word is copied or written new.**
   - **Copied** (35% of words; 3.5% in the first line of a paragraph). The source is any word already written on the page, weighted by:
     - proximity: the weight halves every ~3 lines;
     - a bonus for the word just above;
     - fit with the boundary of the previous word;
     - a word-family repetition propensity for the immediately preceding word.

     In 45% of copies **one glyph is changed** (substitution, insertion or deletion, with the frequencies seen between neighbouring real words). The edit must be *writable* (see §4). After an edit, the prefix is chosen again by the boundary rule. Copies placed inside a line are "opened" if they carried a line-end form. Copies outside the first line lose *p/f*, and copies right after a drawing gap lose *q-*.
   - **New**, glyph by glyph. Each glyph depends on the previous two. The first two glyphs also depend on the last glyph of the previous word (boundary agreement). There are four start contexts: line start, paragraph start, after a drawing gap, and after a word. The word must fit the slot template prefix · core · *e*/*i* run · ending. Words with two gallows (55%) or with both *e* and *i* (45%) are rejected. Five candidates are made and one is chosen according to the line's length tone. The last word of a line is written from its own table, learnt from real line-final words with their closure undone.
6. **Line start.** If the first word starts with the same glyph as the line above, it is rewritten with a probability that depends on the glyph: always for *ch*, about two in three for *o* and *q*, about half for gallows, almost never for *s*.
7. **First line of a paragraph.** Almost no copying, no immediate repeats, and *p/f* instead of *k/t* in about 30% of words.
8. **Line end.** The last word is closed (*-iin→-m, -in→-m, -l→-ly, -r→-ry, -s→-sy, -y→-g*) with a strength that depends on the hand and on the number of words in the line. Paragraph-final lines close less. The word before a drawing gap is closed weakly.

The glyph-contact table, the line-end table, the edit frequencies and the boundary table are **learnt from the text**. The scribe says how the pieces combine; it does not explain where the glyph grammar itself comes from.

---

## 3. Results

A selection of measures. All 64 are in the appendix.

| Measure | Real | 3-rule generator | Scribe |
|---|---|---|---|
| Adjacent identical words / chance | 3.09 | 2.91 | 3.31 |
| Same word at distance 2 / shuffled | 3.27 | 2.52 | 3.62 |
| Frequent words repeated >3× chance (%) | 51.8 | 31.7 | 41.2 |
| Words with an edit-distance-1 twin earlier on the page (%) | 64.5 | 61.2 | 68.3 |
| Boundary MI (last glyph → next word's first glyph) | 0.155 | 0.132 | 0.146 |
| Last word of line closed (-m/-ly/-ry/-g/-sy) (%) | 27.1 | 11.5 | 27.3 |
| Gallows on first word of paragraph (%) | 93.2 | 53.9 | 91.8 |
| p/f among gallows, first line of paragraph (%) | 31.0 | 9.5 | 31.0 |
| d-/s-/y- right after a drawing gap (%) | 41.3 | 13.5 | 38.5 |
| Same first glyph as the line above / null | 0.58 | 0.69 | 0.59 |
| Page overdispersion of q- (after -y) | 6.3 | 1.3 | 5.7 |
| Vocabulary cosine: same sheet / neighbouring pages of other sheets | 1.30 | 0.99 | 1.20 |
| Word types | 7,915 | 10,284 | 7,131 |
| Strange words (%) | 4.6 | 13.7 | 4.1 |
| Strange words per line | 0.36 | 1.07 | 0.32 |
| Page overdispersion of e-words | 24.6 | 1.6 | 20.3 |
| e-words: biological / herbal | 2.04 | 1.00 | 1.84 |
| -edy words in the biological section (%) | 27.5 | 10.9 | 22.7 |
| **Reproduced (±25%)** | | **33/64** | **58/64** |

**Hold-out**: learnt on odd folios, written on even folios: 51/64; the real halves against each other: 55/64. The new page and section measures are reproduced in the hold-out too. Only the long-word measure fails there.

---

## 4. Finding 1: the eye did not need a dictionary

An earlier version already matched most statistics, but its pages looked wrong. The strange-word measure agreed: 8.7% of its words were strange against 4.6% in the real text. Tagging every word by how it was produced showed where they came from:

| Origin | Strange |
|---|---|
| New word, glyph by glyph (per candidate) | 2.4% |
| New line-final word (per candidate) | 4.9% |
| **Copied word with one glyph changed** | **36%** |

Almost all of it came from the copy edits. The changed glyph ignored its neighbours: *daiin→daain*, *chedy→chddy*, *ol→oo*, *qokeedy→qokdedy*.

I tried four fixes, each with 2–3 seeds for exploration and 5 seeds for the chosen one. The counts are out of the 59 measures the battery had at that point.

| Variant | Reproduced | Strange | Word types |
|---|---|---|---|
| Before (blind edit) | 51/59 | 8.7% | 7,859 |
| Edited copy must land on a known word (lexicon) | 50–52/59 | 4.2% | ~6,400 |
| + reject new words that are not known | 43–45/59 | 2–3% | 3,300–4,700 |
| Per-word repetition propensity (on top of writable edits) | 50–52/59 | 3.9–4.1% | ~7,100 |
| **Edit must be writable: every glyph possible after the previous two (seen ≥3 times in that context in the text)** | **54/59** | **4.1%** | 7,150 |
| Real | | 4.6% | 7,915 |

- **A lexicon fixes the eye but kills variety.** In the real text, the one-glyph variant of a word on the page is very often a word that occurs nowhere else, not a known word. Rejecting unknown new words is worse still.
- **What works is making the edit obey the same 2-glyph memory** the scribe already uses for new words. Everything that comes out of the pen, including a variation of a copied word, goes through the same short-memory process. Strange modified copies drop from 36% to 1.7%.
- **Ablation**: without this rule, 53/64 and 8.7% strange.
- **Hold-out**: with the contact table learnt from odd folios, the even folios get 0.31 strange words per line against 0.36 real.

**Caveat.** The measure and the rule both work at the level of glyph trigrams, so a match is partly expected. The informative parts are that the edits were the only offender, and that a lexicon is the wrong fix.

---

## 5. Finding 2: the word family is a habit of the sheet

Reading generated pages side by side with real ones, f78r (biological) is monotonous in *-edy* (*qokedy* ×15), while the scribe's f78r was monotonous in *qokaiin*. The *amount* of monotony was right: the most frequent word covers 4.7% of a page in both texts. The *family* was wrong.

Voynich words fall into two blocks: words with *e* end in *-y/-dy*; words without *e* end in *-aiin/-ar/-ol*; *e* and *i* avoid each other. I added the choice between the two blocks as a fifth free habit (per sheet, page and line) with a per-section offset (§2). Result: 55 → 58/64. All three new page and section measures are reproduced, also in the hold-out; without the habit, 52/64.

**Habit or topic?** In the herbal section every page shows a different plant. If the share of *e*-words depended on the page's content, the pages of one sheet would be no more alike than any neighbouring pages. If it is a habit of the writing session, the sheet should dominate. The two folios of a sheet are usually far apart in reading order, so "same sheet" and "close by" can be told apart.

Method: mean absolute difference of the share between pairs of pages (≥60 words) with the same relation, against 400 permutations of pages within section × language. Negative z means more alike than chance.

| Relation | e-family | k/t | ch/sh | q- | -dy |
|---|---|---|---|---|---|
| All sections: neighbouring page, other sheet (120 pairs) | −1.6 | −2.1 | −0.3 | +1.4 | +0.2 |
| All sections: **conjugate folio, same sheet** (157) | **−6.5** | −2.1 | −3.7 | −2.5 | −1.5 |
| All sections: same folio, recto/verso (89) | −6.0 | −2.0 | −1.8 | −0.8 | −1.0 |
| Herbal: neighbouring page, other sheet (64) | −0.7 | −1.6 | −0.2 | +0.4 | −2.1 |
| Herbal: **conjugate folio** (94) | **−7.0** | −0.8 | −0.3 | −0.5 | −0.4 |
| Herbal: same folio (51) | −6.2 | −2.3 | −0.1 | +0.7 | −0.1 |
| Herbal, same Davis hand only: **conjugate folio** (94) | **−6.3** | −0.9 | −0.7 | −0.4 | −0.7 |

- The word family has the **strongest sheet effect of all the free choices**, and it comes neither from proximity nor from the hand.
- Within a page it drifts like the other habits: consecutive lines are more alike than lines five or more apart (product of deviations +0.0045 against −0.0021; *k/t*: +0.0050 against −0.0031).
- It fits two earlier results from line coordinates measured on the Beinecke scans: the sheet also shares vocabulary (cosine ratio 1.30), and it shares letter size and line spacing (in scan pixels; conjugate folio z −4.0 for letter size and −6.4 for line spacing, against +0.1 and −0.9 for the neighbouring folio of another sheet).
- **Not excluded**: that whole sheets were planned around plants of the same kind. Testing that needs a plant classification.

---

## 6. Samples

The same layout and seed for every version. Strange words in [brackets].

**f78r, real**
```
tshedor shedy qopchedy qokedy dyqokol oky
qokeedy qokedy shedy tchedy otar olkedy dam
[qckhedy] cheky dol chedy qokedy qokain olkedy
yteedy qotal dolshedy qokedar chcthey otor dor or
qokal otedy qokedy qokedy dal qokedy qokedy
```

**f78r, scribe with blind edits (before)**
```
pshd qokeey [qyrchey] shey qokchedy dam
par ol [edam] shey [qyrchdy] lchedy qokeey
qokedy ol qoeey qokeey shey or oly
ol qokeey qokeey qokar shedy okor sheey [qyrchey]
ysheeky qor chekedy qokchedy qor okor [qokyr]
```

**f78r, scribe with writable edits, no word-family habit**
```
pol qopal qokaiin shckhedy qol qopam
qokeecheo or qokaiin qokal qol qokey oly
dol ykeedy qokaiir ol or okalkchedy qokag
qokchey qokaiin she tshy oteey chedy qokchy qokchey
scheo qolos sheckhdy qotaiin okeeey qokaiin shedal
```

**f78r, scribe now**
```
qokod chol qokeey chedy qopar otom
o ral ydain shedy qody chody chals
qokedy qotedy qokedy qokeey qolal shedytedy ytam
tchdy shor qokeey [qokaiinsh] qokedy shedy qokaiin qoted
sor oral qokar air shedy qokaloir chey
```

**f88r (pharmaceutical), real**
```
dorsheoy ctheol qockhey dory sheor sholfchor dal chcthol
ralsheom keolchear shekor qokor daiin sar saiin oky sam
oain or om otam okeom cheeor qokeody dar or om cheody
qokeol cheol saiin cheos cheol doleeey or cheom [cheojam]
```

**f88r, scribe now**
```
kchey oky os sol dy s aiin dal
dchey keodaiin okeeody okeoy qokshoy teey cheo chey dal
daiin chal aiisoiin daiiin okeey dchey qoteor chey qockheod qockheod sy
ycheody okey keey kees ar okeey keedy chey chea
```

You can still tell them apart:
- some concatenations look wrong (*shedytedy*, *qokaiinsh*, *doraiiny*) even though each half is a normal word, and no measure catches them yet;
- long words are too frequent (§8).

---

## 7. Ablation: every rule is needed

| Rule removed | Reproduced /64 |
|---|---|
| none (full scribe) | 58 |
| copy from the visible page | 47 |
| start contexts (line / paragraph / after gap) | 51 |
| sheet and page habits | 51 |
| first-line register | 51 |
| language A/B weights | 52 |
| word-family habit | 52 |
| word rules (two gallows, e with i) | 53 |
| boundary agreement | 53 |
| writable edits | 53 (and 8.7% strange) |
| line-end closure | 54 |
| repetition propensity by word family | 54 |
| vertical dissimilation | 55 |
| closure strength by words per line | 55 |
| slot template | 56 |
| line length tone | 56 |
| line-end repertoire | 56 |
| re-choosing the prefix of edited copies | 57 |
| -dy section offset | 58 (loses -edy in biological, gains two unstable measures) |

---

## 8. What it does not reproduce

| Measure | Real | Scribe |
|---|---|---|
| Adjacent identical words (%) | 0.90 | 1.17 |
| Same word at distance 5 / shuffled | 2.85 | 3.81 |
| Frequent words repeated <0.3× chance (%) | 16.1 | 20.8 |
| Line-end -m: lines of 10+ words / lines of 1–4 words | 3.41 | 1.94 |
| q- on the first word of a paragraph (%) | 4.2 | 6.2 |
| Words of 8+ glyphs (%) | 5.3 | 7.4 |

- **Which words repeat.** The overall amount is right, but in the real text *dal*, *shey*, *saiin* never repeat adjacently and *okaiin* does ×5. A per-word propensity estimated from the text did not help. Near-neighbour pairs (consecutive words at edit distance 1) only just pass: 1.68 against 2.21.
- **Line-end -m.** The real effect turns out to be a mix of hands: hand 1 writes short lines and closes little, hand 3 writes long lines and closes a lot. Within hand × section it is flat (observed minus expected per word-count bin between −0.03 and +0.05, all compatible with zero). The scribe's remaining error is in short non-final lines: 11% *-m* against 6%.
- **Long words** have the same structure as the real ones: gallows 0/1/2+ is 20/69/12% in the scribe against 20/62/18% in the real text (*qokeeedy*, *cheodaiin*, *qokeeody*). There are simply a third too many. This comes from how the line length tone picks among candidates. Softening it brings them down to 6.3%, but costs 13% of the word types.
- **Paragraph-initial q- and repetition at distance 5** move between seeds and are borderline.

---

## 9. What it suggests about how the manuscript was written

Read as a description of an act of writing, the procedure looks like a **craft** with place rules and session habits, rather than composition sentence by sentence:

- **The writer looks at what is already on the page**, takes a nearby word and varies it. This is very close to Torsten Timm's self-citation hypothesis (Timm & Schinner), reached here by a different route (measurement first, generator later). I read the convergence as support for it.
- **Words are written with a slot template and a 2-glyph memory**, and variants are made on the fly with the same memory. No word list is needed.
- **The line is the unit of work.** There are start forms and end forms. The first glyph avoids the previous line's first glyph. A drawing is treated as a margin, which means the text was written after the drawings.
- **The sheet is the session.** The free choices, the word family, the vocabulary and the letter size are shared within the sheet. The five Davis hands share the shape rules, but each has its own strength.

What it does **not** say:

- **Sufficient is not necessary.** A meaningful process that produced this surface would give the same numbers. Ruling out languages and ciphers needs its own tests with positive controls and minimum detectable effects; the generator does not replace them.
- **The glyph grammar is copied from the text.** Why the grammar is this one remains open.
- **Room for a small message remains.** The free choices could still carry a small hidden message. My estimate of the blind capacity is a few KB at most, and an earlier test would have detected a message that broke the rules from roughly 650–2,500 bits, depending on the choice.

---

## 10. Side results

- **Vertical dissimilation does not decay.** The ratio is the same whether the line above has 29, 41 or 50 glyphs (0.65 / 0.63 / 0.66; ×0.90 [0.70–1.13] per doubling). The first glyph above was written 20–60 glyphs earlier, far beyond the 2-glyph word memory, so this is not a fading short memory. The line two above is *not* avoided: the ratio is 1.11 once the immediate avoidance is built into the null. It looks like a one-slot rule ("don't start like the last line") rather than general visual avoidance.
- **Line-end closure is position plus hand.** It depends neither on the physical distance to the margin (measured with line coordinates) nor on the number of words in the line once the hand is controlled.
- **Drawing gaps almost never split a word.** The concatenation of the words on both sides of a `<->` is an attested word no more often than across a normal space, and far less often than across an uncertain space: at most ~4% of the 745 gaps. The excess of *-d/-s* before gaps is mostly a lone *s* (31 cases before gaps, 13 after) that does not behave like a detached prefix.
- **Pieces on either side of a drawing are correctly paired.** On f1v the text to the right of the plant sits almost one line lower than the text on the left. No pairing of left and right pieces shows boundary agreement, neither as transcribed nor shifted by one line, while a positive control does. The gap really breaks the word boundary, as if each piece started a new line.

---

## A note on tools

I used **Claude Code** (Anthropic) as a *code scribe*: it wrote most of the analysis and generator code. That saved me many hours of programming and let me concentrate on what matters, which is checking the results, questioning them and changing things quickly when something did not hold up. The questions, the decisions and the verification of every figure are mine.

## How to reproduce

Python 3 with pandas, numpy and scipy. Run from the `novetats/` folder unless stated otherwise.

| Step | Command |
|---|---|
| Real measures | `escriba/mesures.py` → `mesures_real.json` |
| Scribe vs real (5 seeds) | `escriba/compara.py` |
| Ablations | `escriba/compara.py ablacions` |
| Hold-out (odd → even) | `escriba/holdout.py` |
| Section offsets | `escriba/calibra_seccio_e.py` (with `ESCRIBA_TRAIN=senars` for the hold-out) |
| Where strange words come from | `escriba/diagnosi_estranys.py` |
| Samples | `escriba/mostra_memoria_formes.py` |
| Sheet vs topic test | `prediccions/p1_familia_habit_o_tema.py [mà]` |
| Pairing of drawing-gap pieces | `prediccions/p2_aparellament_trossos.py` |

Run the `escriba/` scripts from inside `escriba/`. Variable names and comments in the code are in Catalan.

---

## Appendix: all 64 measures

✓ = within ±25% of the real value (or within 0.01 absolute near zero); mean of 5 seeds.

<!-- TAULA -->
| # | Measure | Real | 3-rule generator | Scribe |
|---|---|---|---|---|
| 1 | Adjacent identical words (%) | 0.902 | 0.793 ✓ | 1.17 ✗ |
| 2 | Adjacent identical words / chance | 3.09 | 2.91 ✓ | 3.31 ✓ |
| 3 | Consecutive words at edit distance 1 / shuffled | 2.21 | 2.38 ✓ | 1.68 ✓ |
| 4 | Same word at distance 2 / shuffled | 3.27 | 2.52 ✓ | 3.62 ✓ |
| 5 | Same word at distance 3 / shuffled | 3.45 | 2.46 ✗ | 3.45 ✓ |
| 6 | Same word at distance 5 / shuffled | 2.85 | 2.20 ✓ | 3.81 ✗ |
| 7 | Frequent words repeated >3× chance (%) | 51.79 | 31.70 ✗ | 41.22 ✓ |
| 8 | Frequent words repeated <0.3× chance (%) | 16.07 | 24.39 ✗ | 20.80 ✗ |
| 9 | Boundary MI, distance 1 (last glyph → next first glyph) | 0.155 | 0.132 ✓ | 0.146 ✓ |
| 10 | Boundary MI, distance 2 | 0.009 | 0.000 ✓ | 0.004 ✓ |
| 11 | Boundary MI, distance 3 | 0.003 | -0.001 ✓ | 0.003 ✓ |
| 12 | Lift -y | q- | 1.69 | 1.71 ✓ | 1.68 ✓ |
| 13 | Lift -r | a- | 3.12 | 2.97 ✓ | 3.10 ✓ |
| 14 | Lift -y | a- | 0.194 | 0.276 ✗ | 0.198 ✓ |
| 15 | Lift -n | q- | 0.472 | 0.501 ✓ | 0.550 ✓ |
| 16 | First word of line starts ch/sh (%) | 8.15 | 8.73 ✓ | 9.25 ✓ |
| 17 | First word of line starts y (%) | 14.33 | 13.90 ✓ | 13.16 ✓ |
| 18 | Last word of line ends -m (%) | 15.87 | 9.07 ✗ | 16.73 ✓ |
| 19 | Line-end -m: lines of 10+ words / 1–4 words | 3.40 | 3.88 ✓ | 1.94 ✗ |
| 20 | Same first glyph as line n−1 / null | 0.583 | 0.689 ✓ | 0.585 ✓ |
| 21 | Same first glyph as line n−2 / null | 1.30 | 1.13 ✓ | 1.22 ✓ |
| 22 | Same first glyph as line n−3 / null | 1.16 | 1.17 ✓ | 1.11 ✓ |
| 23 | Distinct initial glyphs per paragraph (4+ lines) | 4.36 | 4.94 ✓ | 4.62 ✓ |
| 24 | Adjacent repeats: first line of paragraph / rest | 0.385 | 1.24 ✗ | 0.344 ✓ |
| 25 | Spearman correlation of neighbour word lengths | 0.160 | 0.051 ✗ | 0.181 ✓ |
| 26 | Word types | 7,915 | 10,284 ✗ | 7,131 ✓ |
| 27 | Hapax (% of types) | 71.32 | 76.11 ✓ | 63.99 ✓ |
| 28 | Words fitting the slot grammar (%) | 97.70 | 94.65 ✓ | 99.88 ✓ |
| 29 | Words with 2+ gallows (%) | 1.80 | 5.34 ✗ | 1.43 ✓ |
| 30 | Mean word length (glyphs) | 4.80 | 4.78 ✓ | 4.65 ✓ |
| 31 | SD of word length | 1.71 | 2.20 ✗ | 1.92 ✓ |
| 32 | e and i in the same word / expected | 0.244 | 0.413 ✗ | 0.252 ✓ |
| 33 | H(prefix), marginal | 1.54 | 1.52 ✓ | 1.49 ✓ |
| 34 | H(prefix | previous glyph, core) | 0.918 | 0.959 ✓ | 0.920 ✓ |
| 35 | q- before o- after -y (%) | 57.26 | 53.65 ✓ | 58.47 ✓ |
| 36 | q- on first word of paragraph (%) | 4.19 | 13.22 ✗ | 6.24 ✗ |
| 37 | q- on first word of line (%) | 14.87 | 13.03 ✓ | 15.14 ✓ |
| 38 | q- inside the line (%) | 17.94 | 16.21 ✓ | 19.79 ✓ |
| 39 | a- at line start (%) | 0.354 | 0.260 ✗ | 0.407 ✓ |
| 40 | d-/s-/y- at line start (%) | 47.98 | 39.49 ✓ | 46.25 ✓ |
| 41 | Bare gallows at line start (%) | 8.97 | 22.21 ✗ | 10.21 ✓ |
| 42 | Closed last word, non-final lines (%) | 27.11 | 11.51 ✗ | 27.33 ✓ |
| 43 | Closed forms inside the line (%) | 2.34 | 5.06 ✗ | 2.11 ✓ |
| 44 | Closed last word of paragraph (%) | 17.31 | 8.41 ✗ | 21.57 ✓ |
| 45 | Length of 2nd word / 1st word | 0.877 | 0.965 ✓ | 0.966 ✓ |
| 46 | Gallows on first word of paragraph (%) | 93.24 | 53.92 ✗ | 91.76 ✓ |
| 47 | p/f among gallows, first line of paragraph (%) | 31.03 | 9.47 ✗ | 31.03 ✓ |
| 48 | p/f among gallows, other lines (%) | 2.73 | 10.19 ✗ | 2.53 ✓ |
| 49 | Word length, first line / rest | 1.08 | 0.989 ✓ | 0.993 ✓ |
| 50 | Closed word before a drawing gap (%) | 10.16 | 5.00 ✗ | 12.17 ✓ |
| 51 | d-/s-/y- after a drawing gap (%) | 41.33 | 13.55 ✗ | 38.54 ✓ |
| 52 | q- after a drawing gap (%) | 3.57 | 16.14 ✗ | 4.12 ✓ |
| 53 | Same first glyph after a gallows-initial line / null | 0.612 | 0.691 ✓ | 0.601 ✓ |
| 54 | Words with an edit-distance-1 twin earlier on the page (%) | 64.47 | 61.19 ✓ | 68.27 ✓ |
| 55 | Lines back to the nearest twin (median) | 2.00 | 2.00 ✓ | 2.00 ✓ |
| 56 | Page overdispersion of q- (after -y) | 6.32 | 1.30 ✗ | 5.72 ✓ |
| 57 | Vocabulary cosine: same sheet / neighbouring pages of other sheets | 1.30 | 0.988 ✓ | 1.20 ✓ |
| 58 | Strange words (%) | 4.59 | 13.74 ✗ | 4.08 ✓ |
| 59 | Strange words per line | 0.359 | 1.07 ✗ | 0.319 ✓ |
| 60 | Page overdispersion of e-words | 24.57 | 1.65 ✗ | 20.26 ✓ |
| 61 | e-words: biological / herbal | 2.04 | 0.996 ✗ | 1.84 ✓ |
| 62 | -edy words in biological (%) | 27.48 | 10.90 ✗ | 22.66 ✓ |
| 63 | Share of the page's most frequent word (median, %) | 4.71 | 3.21 ✗ | 4.83 ✓ |
| 64 | Words of 8+ glyphs (%) | 5.25 | 9.92 ✗ | 7.43 ✗ |
| | **Reproduced (±25%)** | | **33/64** | **58/64** |
<!-- /TAULA -->
