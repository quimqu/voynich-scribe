# The Scribe: a rule-based procedure that writes a Voynich-like text

*What it reproduces, what it doesn't, and what it suggests about how the Voynich Manuscript was written.*
*Written on 14 October 2026. Revised on 25 October 2026 for the scribe of 19 October, the battery of 76 measures, the controls and the external tests.*

---

## Summary

- **The scribe** is a generator that writes a whole synthetic manuscript on the **same layout** as the real one: the same pages, sheets, paragraphs, lines, words per line, drawing gaps, Currier language and Davis hand. Only the words are new. There is no layer of meaning anywhere in it.
- It is compared with the real text on **76 measures**: repetition, near-duplicates, word-boundary agreement, line-start and line-end forms, first-line effects, vertical dissimilation, page and sheet habits, word shape, what the eye sees, and, since 19 October, character entropies, the Zipf slope, word lengths, long-range similarity between pages and bursts of frequent words. It reproduces **69/76** within ±25% (mean of 5 seeds), with a median error of 0.067. A simpler three-rule generator reproduces 39/76 (median error 0.26); its three rules are (1) new words glyph by glyph from a single two-glyph table for the whole manuscript, (2) copying of words from the same line or the two lines above, mostly changed by one glyph, and (3) a memory that is emptied at each page and paragraph (details in §3).
- Learnt **only from odd folios** and asked to write the even ones, it reproduces **61/76**. The two real halves reproduce each other at 67/76.
- Two results I did not expect (14 October):
  1. **The eye did not need a dictionary.** To stop producing impossible-looking words, the scribe did not need a lexicon of known words. It needed its edits to copied words to obey the same 2-glyph memory it already uses to write new words.
  2. **The word family is a habit of the sheet.** The choice between words with *e* (*-edy*, *-ey*) and words without (*-aiin*, *-ar*, *-ol*) is shared by the pages of a sheet, including the conjugate folio far away in reading order, and not by neighbouring pages. In the herbal section, where every page shows a different plant: z = −7.0 for the conjugate folio, −0.7 for the neighbouring page of another sheet.
- One correction since then (19 October). The scribe used to copy 35% of its words from the page. Once each hand, and each section within a hand, got its own glyph tables, the right amount of copying fell to **22%**: part of what looked like copying was the hand's own vocabulary. The same change explains the long-range similarity between pages: it is hand and section vocabulary, not a drift along the book.
- Controls and external tests (19 and 25 October). The same generic procedure applied to a Latin text fails where a language should fail (7/16 against a ceiling of 13/16; on the Voynich, 12/16 against 16/16). The scribe passes Parisel's four boundary signatures in Currier A and in Currier B, in all five seeds, and it reproduces the LSA pattern that Layfield and Davis read as evidence against the quire structure.

This does **not** show that the manuscript is meaningless. It shows that a concrete, meaningless writing procedure is *sufficient* to produce almost everything we currently know how to measure.

## The rules, in short

These are the regularities measured on the real text before building the scribe. "System" means all five Davis hands follow the rule; "habit" means its form is shared, but its strength varies by hand, page or sheet. The identifiers in square brackets are those of the rulebook (`RULES.md`).

### Glyphs and words

- **Allographs.** *k~t*, *ch~sh* and *p~f* behave as one sign each in different places. Which one is used is decided by place and by the page's habit (0.009 bits of context). System. [R1.2]
- **Glyph positions.** *q* is always followed by *o* and is always word-initial (98%). *e, i, n, m* never start a word, and *e, a, i, ch, q* never end one. System. [R1.4, R1.5]
- **The template.** A word is `[prefix] [core] [e…] [ending]`:
  - prefix: *qo-, o-, y-, d-, s-, ch-, l-* or none, and never before a bench;
  - core: a gallows or a bench, or nothing;
  - one to three *e*;
  - an ending.

  A 23-slot grammar learnt from the data covers 98.8% of the tokens. There is at most one gallows per word (two in 1.8% of words, three never). System. [R2.1, R2.2, R2.3]
- **Two blocks.** Words with *e* end in *-y/-dy* (*qokeedy, chedy*); words without *e* end in *-aiin, -ain, -ar, -al, -ol* (*qokaiin, okal*). *e* and *i* avoid each other (0.15 of expected). These are two routes through the template, not a paradigm: the mutual information between core and ending is 0.83 bits, against 0.28 for the null. System. The choice between the blocks is a habit of the sheet (§5). [R2.4, R13.7, R16.7]
- **Contact rules.** *i* runs only as *a + i(1–3) + n/r/m* (99%); *n* and *m* are word-final (95%); only *e* and *i* double; *l* is the only tail glyph that can precede a gallows or a bench. System. [R13.2, R13.3, R13.6, R13.11]
- **Two-glyph memory.** With eight functional classes (*o, a, i, d, q*; the *e*/bench class; gallows; and the endings *y n m g l r s*), the next glyph is predicted almost as well as with all 22 glyphs (2.33 vs 2.24 bits). What a memory of two adds is exactly the template: prefix, *qo-* + gallows, runs of *e* and *i*, final *o*. System. [R17.1, R17.3]
- **Near twins.** 95.6% of tokens have a word at edit distance ≤ 1 already written on the same page, typically three lines above. Process. [R2.8]

### Between words

- **The space is a glyph rule.** It can be guessed 87% of the time from two glyphs on each side. Some boundaries are firm (*-y|q-*, *-n|ch-*); others are weak (*r|a, o|l*: transcribers hesitate 28–45% of the time). System. [R3.1, R3.2]
- **Boundary agreement.** The prefix of a word depends on the last glyph of the previous word and on the word's own first two glyphs, and on nothing else:
  - after *-y*, an *o-* word takes *q-* 56% of the time and an *a-* word takes *d-* 73%;
  - after *-r* or *-s*, both take nothing 79–89% of the time.

  What matters is the *stroke* the previous word ends with: it carries 91% of the information of the whole glyph. The form is system; the strength is habit (hand 1: *q-* after *-y* 0.14; hands 2–3: 0.33). [R3.3, R17.4]
- ***q-* is the continuation form**: 1% in labels, 4% on the first word of a paragraph, 13% on the first word of a line, 18% inside a line. System. [R3.4]
- **No syntax.** Beyond the contact glyph, no word predicts the next one: 0.16 bits at distance 1, 0.009 at distance 2. No resegmentation changes this. System. [R3.5]

### The line

- **The line is the unit.** All sequential structure lives in the first word, the last word and the repetitions. System. [R4.1]
- **Start forms.** The first word starts with *d-, s-* or *y-* 40% of the time (13% inside the line) and almost never with *a-* (0.3% against 4.3%). A bare gallows is a line-start form. System. [R4.2, R14.1]
- **End forms.** The last word is closed: *-iin→-m* 60% (7% inside), *-l→-ly* and *-r→-ry* 25% (2–4% inside), *-s→-sy*, *-y→-g*. Overall, 25% of line-final words against 2.3% inside. It depends neither on the distance to the margin (measured with coordinates) nor on the number of words once the hand is controlled. The form is system; the strength is habit (*-m* for *-iin*: hand 1 0.37, hand 5 0.85). [R4.3, R15.1]
- **Vertical dissimilation.** Consecutive lines avoid starting with the same glyph (ratio 0.60, z −10), and only the first glyph. It is strongest after *ch* or a gallows. It does not depend on line spacing or alignment, and it does not decay with the length of the line above. Habit. [R4.5, R4.6]

### Paragraphs and drawings

- **Paragraph start.** The first word carries a gallows 93% of the time, and almost never *q-*. System. [R5.1]
- **First-line register.** In the first line, 35% of gallows are *p/f* (3% elsewhere), more when there is free space above. Words are longer and newer, and repeats are half as frequent. System. [R1.3, R5.2]
- **A drawing is a margin.** The word before a drawing gap half-closes (10% closed forms against 2% inside); the word after it opens like a new line (*d-/s-/y-* 41%). The boundary agreement breaks there. Gaps almost never split a word. The text was written after the drawings. System. [R6.1, R6.2]

### Page and sheet

- **Copying from the page.** About one word in five (22% in the scribe; 35% before each hand had its own tables) is a copy of a word written a few lines above, often with one glyph changed. The rest of the repetition comes from the vocabulary of the hand. [R2.8, R16.5, R16.6]
- **Each hand has its own glyph grammar**, and each section within a hand. The similarity of vocabulary between pages (0.35 for neighbouring pages, 0.26 at ten pages, 0.17 at a hundred) is explained by hand and section, not by a drift from page to page: copying from previous pages flattens the whole curve. Found on 19 October; this is the same picture as Schwartz (2026), who finds that word cores are hardly shared between hands.
- **Page rates.** Each page has its own rate for every free choice (*k/t, ch/sh, q-, -y/-dy*, word family): overdispersion z +10 to +58 beyond language, section and hand. The rate drifts over a few lines. Habit. [R7.2, R16.7]
- **The sheet is the session.** The pages of a sheet, including the conjugate folio, share vocabulary, free-choice rates, word family, letter size and line spacing. The neighbouring folio of another sheet does not. Habit. [R7.4]
- **A and B** are the same system with different weights: slot grammars learnt on each language cover each other 98%. [R7.3]

## The instructions, as the master of the workshop might have given them

The same rules, spoken as the person who ran the workshop might have spoken them to the people who filled the pages. Each instruction ends with the rule it stands for, so it can be checked in `RULES.md`.

> The drawings are done. You write around them, afterwards. [R6.1]
>
> **To begin.** Start a paragraph with a word that carries a gallows, never with *q*. In that first line write the tall gallows, *p* and *f*, where you would otherwise write *k* and *t*, and more so when the space above is empty. [R5.1, R1.3] In the first line write longer, newer words: none taken from the page, none repeated, none used again in the second line. [R5.2]
>
> **To make a word.** A word has four places: a start if it needs one (*qo, o, y, d, s, ch, l*), a core that is a gallows or a bench or nothing, one to three *e*, and an ending. No start before a bench, one gallows at most. [R2.1, R2.3, R2.2] Decide the family before you write: with *e* the word ends in *y* or *dy*; without *e*, in *aiin, ain, ar, al* or *ol*. Never put *e* and *i* together. [R2.4, R13.7] Four to six glyphs is the usual size. [R2.6] To choose the next glyph, remember only the two before it. [R17.3] *q* goes only before *o* and only at the start; *e, i, n, m* never begin a word and *e, a, i, ch, q* never end one. [R1.4, R1.5] Between *k* and *t*, *ch* and *sh*, *p* and *f*, choose by the place and by the taste of the day, not by the word. [R1.2, R7.2]
>
> **What to put in front.** If the last word ended in *y* and the next begins with *o*, put *q* in front; if it begins with *a*, put *d*. After *r* or *s*, nothing. It is the last stroke of the pen that decides, not the word. [R3.3, R17.4] *q* is for going on: not to begin a paragraph, little at the start of a line, never in a label. [R3.4, R8.1] The word itself tells you nothing about the next. [R3.5]
>
> **The line.** Begin with *d, s* or *y*, or with a bare gallows, never with *a*. [R4.2, R14.1] Do not begin with the glyph the line above begins with; the line two above does not matter. [R4.5, R4.6] Make the second word short. [R14.3] If the first word came out long, keep the others long; if short, short. [R14.5] Close the last word: *aiin* becomes *am*, *ol* becomes *oly*, *ar* becomes *ary*, *y* becomes *g*, *s* becomes *sy*. Keep it short, close it whether you reach the margin or not, and do not squeeze the letters to get there. [R4.3, R4.4, R15.1] Do not close a word in the middle of the line, and in the last line of a paragraph close less. [R4.3, R14.2]
>
> **When the drawing is in the way.** Half close the word before it and start again after it as if it were a new line; there you may begin with *a*. Do not break a word across it. [R6.1, R6.2]
>
> **The habits of the day.** Write the four pages of a sheet in one sitting, with the same size of letter and the same choices: *k* or *t*, *ch* or *sh*, *q* or not, *dy* or *y*, and whether you lean to the words with *e* or to the others. Let them drift a little from line to line, but keep them for the sheet. [R7.2, R7.4, R16.7]
>
> **Copying and making up.** About one word in five, take a word you can see on the page, mostly from the few lines above, and change one glyph if you like, but only as your hand would write it after the two glyphs before, like any new word. [R2.8, R16.5, R16.6] The rest, write as you always write; the page fills with your own words. [R7.1] Now and then repeat a word right after itself, in the middle of the line: *chol* and *qokedy* bear it, *daiin* does not. [R9.1, R9.2]
>
> **Never.** Never begin a line with *a*, never two gallows in a word, never *e* with *i*, never *q* away from the start or without its *o*. [R4.2, R2.2, R13.7, R1.4]

What this shows, and what it does not. The sheet is enough: a scribe who follows it with the tables of his hand writes a text that passes 69 of our 76 measures; the three-rule generator that does not follow it passes 39. Nothing on it refers to meaning: every instruction is about shape, place or process, and none tells the scribe what to say. Whether anyone ever gave such instructions, the statistics cannot tell: the same numbers would come out if the habits grew in one hand without a word spoken, or if a meaningful procedure left this surface. What the text does say is that the five hands follow the same sheet with different strength: the forms are the same in all five (where a line may begin, where *p* and *f* go) and the strengths differ (how often *q* follows *y*, how firmly the last word is closed).

---

## 1. Data and method

- **Text**: ZL3b transliteration (Zandbergen–Landini, IVTFF 2.0), paragraph text only (no labels, no circular or radial text), in EVA. Benches and gallows (*ch, sh, cth, ckh, cph, cfh*) count as single glyphs. Ligature braces `{…}` keep their content.
- **Metadata**: Currier language A/B, Lisa Fagin Davis' scribal hands, quires and sheets (bifolios) from the standard codicological reconstruction.
- **Comparison**: every scribe figure is the mean of 5 random seeds. A measure is *reproduced* if it lies within ±25% of the real value (within 0.01 absolute for values near zero). The median error is the median of |log(scribe / real)| over the measures that are not near zero. The full list of 76 measures is in the appendix: the 64 of 14 October plus character entropies h1, h2 and h3, the Zipf slope, the share of words of 2–3 and of 5–6 glyphs, the vocabulary shared by pages 1, 10 and 100 pages apart and their ratio, the bursts of the 50 most frequent words and their page overdispersion.
- **Controls**:
  - **Ablation**: remove each rule in turn and count the measures lost.
  - **Hold-out**: learn every table and fitted parameter from odd folios only, then write the layout of the even folios and compare with the real even folios. The real odd folios against the real even folios give the natural difference between halves.
  - **A real language**: the same generic procedure applied to a Latin text (§8).
- **Strange words**: a word is *strange* if it contains a glyph trigram (word start and end included) that occurs ≤ 3 times in the whole real text. In the real text, 4.6% of words are strange (0.36 per line). It is a crude stand-in for "this word looks wrong".

---

## 2. The procedure

For every sheet, page, paragraph and line, in this order:

1. **Sheet habit.** Each sheet has its own rate for five free choices: *k* vs *t*, *ch* vs *sh*, *q-* or not, *-dy* vs *-y*, and the *e*-word family vs the *e*-less family (a deviation of 0.3 in log-odds per sheet, 0.45 per page). Each page of the sheet varies a little around it, and within a paragraph the rate drifts from line to line (memory 0.6).
2. **Hand and section tables.** The glyph-contact table, which says which glyph can follow the two before, is learnt separately for each Davis hand, and for each hand within each section when there are at least 40 lines of it: the counts of the hand plus three pseudocounts spread according to the table of the language (or of the hand). This was added on 19 October. With it, the per-section offsets of 14 October for the *e* and *-dy* habits (§5) counted the section twice (*-edy* in the biological section came out at 34.7% against 27.5% real) and are switched off.
3. **Language.** A and B are the prior behind the hand tables: the same glyph-contact table with different weights.
4. **Line length tone.** This line will have slightly longer or shorter words than average. On top of it, the length of a new word is weighted by its position in the line (first word, inside, last), with weights calibrated in three passes so that the length distribution of the whole text, copies included, matches the real one.
5. **Each word is copied or written new.**
   - **Copied** (22% of words; 35% until 19 October; 3.5% in the first line of a paragraph). The source is any word already written on the page, weighted by:
     - proximity: the weight halves every ~3 lines;
     - a bonus for the word just above;
     - fit with the boundary of the previous word;
     - a word-family repetition propensity for the immediately preceding word, weaker than before.

     In 45% of copies **one glyph is changed** (substitution, insertion or deletion, with the frequencies seen between neighbouring real words). The edit must be *writable* (see §4). After an edit, the prefix is chosen again by the boundary rule. Copies placed inside a line are "opened" if they carried a line-end form. Copies outside the first line lose *p/f*, and copies right after a drawing gap lose *q-*.
   - **New**, glyph by glyph, with the table of the hand and section. Each glyph depends on the previous two. The first two glyphs also depend on the last glyph of the previous word (boundary agreement). There are four start contexts: line start, paragraph start, after a drawing gap, and after a word. The word must fit the slot template prefix · core · *e*/*i* run · ending. Words with two gallows are rejected 35% of the time (55% before) and words with both *e* and *i* 25% (45% before): the hand tables already make fewer of them. Five candidates are made and one is chosen according to the line's length tone and the position weights. The last word of a line is written from its own table, learnt from real line-final words with their closure undone.
6. **Line start.** If the first word starts with the same glyph as the line above, it is rewritten with a probability that depends on the glyph: always for *ch*, about two in three for *o* and *q*, about half for gallows, almost never for *s*.
7. **First line of a paragraph.** Almost no copying, no immediate repeats, and *p/f* instead of *k/t* in about 30% of words.
8. **Line end.** The last word is closed (*-iin→-m, -in→-m, -l→-ly, -r→-ry, -s→-sy, -y→-g*) with a strength that depends on the hand and on the number of words in the line. Paragraph-final lines, and the word before a drawing gap, close at three quarters of that strength.

The glyph-contact tables, the line-end table, the edit frequencies, the boundary table and the length weights are **learnt from the text**. The scribe says how the pieces combine; it does not explain where the glyph grammar itself comes from. The hand and section tables are more parameters learnt from the text (one contact table for every combination with enough lines); what they say is that each hand, and each hand in each section, has its own glyph grammar, not only its own tone.

---

## 3. Results

A selection of measures (`scribe/results_table.txt`). All 76 are in the appendix.

**The baseline, "3-rule generator".** To know how much of the score the full rulebook earns, the scribe is always shown next to a simpler generator written on the night of 27 September (`night_generator/generator3.py`), on the same layout. It has three rules: (1) **new words glyph by glyph**, with a single table for the whole manuscript in which each glyph depends on the previous two, and the first glyph of a word on the last glyph of the word before; (2) **copying from the visible field**: about a third of the words are taken from the same line or the two lines above (weight 1, ½, ¼), preferring words whose first glyph fits the end of the previous word, and most of them (85%) changed by one glyph; (3) **a page layer**: the copying memory is emptied at each new page and paragraph, and the first line of a paragraph copies a third as much. On top of that it has two small touches from the first measurements: the first glyph of a line avoids the first glyph of the line above about half the time, and *-iin* becomes *-m* on the last word, more often in long lines. It has no hands, no sections, no sheet habits, no free choices, no line-start or paragraph forms and no drawing gaps. It passes 39 of the 76 measures; the scribe passes 69.

| Measure | Real | 3-rule generator | Scribe |
|---|---|---|---|
| Adjacent identical words / chance | 3.09 | 2.91 | 2.52 |
| Same word at distance 2 / shuffled | 3.27 | 2.52 | 3.40 |
| Frequent words repeated >3× chance (%) | 51.8 | 31.7 | 33.7 |
| Words with an edit-distance-1 twin earlier on the page (%) | 64.5 | 61.2 | 66.3 |
| Boundary MI (last glyph → next word's first glyph) | 0.155 | 0.132 | 0.149 |
| Last word of line closed (-m/-ly/-ry/-g/-sy), non-final lines (%) | 27.1 | 11.5 | 30.1 |
| Gallows on first word of paragraph (%) | 93.2 | 53.9 | 93.5 |
| p/f among gallows, first line of paragraph (%) | 31.0 | 9.5 | 31.5 |
| d-/s-/y- right after a drawing gap (%) | 41.3 | 13.5 | 41.4 |
| Same first glyph as the line above / null | 0.58 | 0.69 | 0.56 |
| Page overdispersion of q- (after -y) | 6.3 | 1.3 | 5.3 |
| Vocabulary cosine: same sheet / neighbouring pages of other sheets | 1.30 | 0.99 | 1.23 |
| Word types | 7,915 | 10,284 | 7,325 |
| Strange words (%) | 4.6 | 13.7 | 4.2 |
| Strange words per line | 0.36 | 1.07 | 0.33 |
| Page overdispersion of e-words | 24.6 | 1.6 | 18.4 |
| e-words: biological / herbal | 2.04 | 1.00 | 1.73 |
| -edy words in the biological section (%) | 27.5 | 10.9 | 26.7 |
| Character entropy h1 / h2 / h3 (bits) | 3.91 / 2.14 / 1.86 | 3.90 / 2.28 / 2.02 | 3.90 / 2.10 / 1.81 |
| Zipf slope (first 1,000 types) | 1.005 | 0.993 | 0.996 |
| Words of 2–3 glyphs (%) | 21.6 | 28.5 | 23.1 |
| Words of 8+ glyphs (%) | 5.3 | 9.9 | 5.7 |
| Shared vocabulary: neighbouring pages / 10 apart / 100 apart | 0.330 / 0.253 / 0.155 | 0.241 / 0.232 / 0.224 | 0.303 / 0.243 / 0.166 |
| Neighbouring / 100 pages apart | 2.13 | 1.08 | 1.83 |
| Bursts of the 50 most frequent words (CV of intervals) | 1.76 | 1.03 | 1.59 |
| **Reproduced (±25%)** | | **39/76** | **69/76** |
| **Median error** | | 0.261 | 0.067 |

**Hold-out**: learnt on odd folios, written on even folios: 61/76 (median error 0.080); the real halves against each other: 67/76 (0.049). The eight new length and long-range measures are all reproduced in the hold-out with tables learnt from the odd folios. Of the 15 measures the hold-out scribe misses, six are also missed between the two real halves, or cannot be computed on half a manuscript (the sheet measure: the conjugate folio often falls in the other half). Its own misses are adjacent repeats against chance, near twins, which words repeat, *-m* by line length, *q-* at line start, closures inside the line and before a gap, repeats in the first line, and the page overdispersion of *e*-words.

**The scribe of 14 October against the scribe of 19 October.** Both score 69/76. What changed is the median error, from 0.098 to 0.049–0.067 depending on the run, and which measures pass: the old scribe made too many short words (2–3 glyphs 28.8% against 21.6%) and a long-range curve that was too flat (neighbouring over 100 pages apart 1.65 against 2.13); the new one passes those and loses the page overdispersion of *e*-words.

**Standard measures** (`scribe/standard_measures_out.txt`, with their own definitions): h1 / h2 / h3 3.88 / 2.12 / 1.85 real against 3.88 / 2.08 / 1.81; Zipf slope 1.005 against 0.996; MATTR (window of 500 words) 0.64 against 0.62; bursts 1.76 against 1.59; vocabulary similarity between pages at distance 1 / 10 / 100: real 0.35 / 0.26 / 0.17, scribe 0.33 / 0.26 / 0.19 (0.29 / 0.24 / 0.19 before the hand tables). Pages far apart are still a little too similar: there is some difference between parts of the book that hands and sections do not explain.

**The boundary coupling per hand** (`scribe/boundary_per_hand_out.txt`). Schwartz (2026) reports that no generator reproduces the mutual information between the last glyph of a word and the first of the next, which differs by hand. Measured the same way on the real text and corrected for a shuffled text, hand 1 gives 0.089 bits and hand 2 0.205. The scribe gives 0.097 ± 0.006 and 0.171 ± 0.009; without the boundary rule, 0.002 and 0.008.

---

## 4. Finding 1: the eye did not need a dictionary

*(14 October; the counts in this section are on the battery of 59 and 64 measures of that date.)*

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
- **Ablation** (battery of 64): without this rule, 53/64 and 8.7% strange.
- **Hold-out**: with the contact table learnt from odd folios, the even folios get 0.31 strange words per line against 0.36 real.
- **Still true on 19 October**: strange words 4.2% against 4.6%, 0.33 per line against 0.36, with the copying down to 22%.

**Caveat.** The measure and the rule both work at the level of glyph trigrams, so a match is partly expected. The informative parts are that the edits were the only offender, and that a lexicon is the wrong fix.

---

## 5. Finding 2: the word family is a habit of the sheet

*(14 October; the counts are on the battery of 64 measures of that date.)*

Reading generated pages side by side with real ones, f78r (biological) is monotonous in *-edy* (*qokedy* ×15), while the scribe's f78r was monotonous in *qokaiin*. The *amount* of monotony was right: the most frequent word covers 4.7% of a page in both texts. The *family* was wrong.

Voynich words fall into two blocks: words with *e* end in *-y/-dy*; words without *e* end in *-aiin/-ar/-ol*; *e* and *i* avoid each other. I added the choice between the two blocks as a fifth free habit (per sheet, page and line) with a per-section offset, fitted so that each section's share matched the real one (11 numbers in total; fitted on all folios or on odd folios only, they came out almost the same: herbal −0.41 / −0.40, biological +0.36 / +0.44, stars +0.37 / +0.37, pharmaceutical +1.55 / +1.23 for the *e* habit). Result: 55 → 58/64. All three new page and section measures were reproduced, also in the hold-out; without the habit, 52/64.

In the scribe of 19 October the per-section offsets are switched off: the glyph tables per hand and section carry the section preference by themselves (*-edy* in the biological section 26.7% against 27.5% real; *e*-words biological / herbal 1.73 against 2.04), and the sheet habit of the word family stays. The one measure that dropped out with the offsets is the page overdispersion of *e*-words (18.4 against 24.6, §9).

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

The first four blocks of f78r and the two of f88r are from 14 October: the same layout and seed for every version, strange words in [brackets]. The last block is the scribe of 19 October, taken from the generated manuscript in `scribe/manuscript_out/` (seed 1); strange words are not marked there.

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

**f78r, scribe of 14 October**
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

**f88r, scribe of 14 October**
```
kchey oky os sol dy s aiin dal
dchey keodaiin okeeody okeoy qokshoy teey cheo chey dal
daiin chal aiisoiin daiiin okeey dchey qoteor chey qockheod qockheod sy
ycheody okey keey kees ar okeey keedy chey chea
```

**f78r, scribe of 19 October (seed 1)**
```
pchey qoky lchedy qokaiin qokeedy qolcthdy
qokain dar chedy dor olchdy qol okl
tchol shedy okeey qokeedy okorshedy qokain olchedy
qotedy chey qoky qokolshedy qokain shcthy qokar otl
dalshldol checkhdy qokal olchey olshedy qokcheey qolkal
```

You can still tell them apart: some concatenations look wrong (*shedytedy*, *qokaiinsh*, *okorshedy*, *dalshldol*) even though each half is a normal word, and no measure catches them yet. The excess of long words of 14 October is gone (§9).

---

## 7. Ablation: every rule is needed

**The changes of 19 October** (`scribe/results_ablations_19_10_table.txt`, 5 seeds). The count of reproduced measures is saturated and moves with the seed; the median error is what separates the versions.

| Version | Reproduced /76 | Median error | What is lost |
|---|---|---|---|
| scribe of 19 October (final configuration, section offsets off) | 69 | 0.049 | |
| the same with the section offsets of 14 October still on | 69 | 0.059 | *-edy* in the biological section overshoots (34.7% against 27.5%) |
| without the glyph tables per hand and section | 68 | 0.062 | adjacent repeats against chance (2.30 against 3.09), page overdispersion of *q-* (3.8 against 6.3) |
| without the length weights by position | 67 | 0.068 | words of 2–3 glyphs (29.3% against 21.6%), words of 8+ glyphs (7.8% against 5.3%), *e* with *i* (0.32 against 0.24), *a-* at line start, the length correlation between neighbours |
| scribe of 14 October | 69 | 0.098 | words of 2–3 glyphs (28.8%), words of 8+ glyphs (7.4%), repeats at distance 5 (3.81 against 2.85), raw adjacent repeats (1.17% against 0.90%) |

The run of `compare.py` behind `results_table.txt` gives the final configuration 69/76 with a median error of 0.067; the two figures differ because about twenty measures have errors between 0.05 and 0.10 and the median jumps among them.

**Rule by rule** (14 October, battery of 64, `scribe/results_ablations_table.txt`). These ablations were not repeated on the battery of 76; the rules have not changed since.

| Rule removed | Reproduced /64 |
|---|---|
| none (full scribe of 14 October) | 58 |
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

## 8. Controls and external tests

### 8.1 A real language: the scribe applied to Latin

A reader of voynich.ninja asked: applied to half of Moby-Dick, would the scribe not produce English-like text that passes the same checks? The control (`scribe/controls/CONTROLS.md`) answers with Latin, Nicholas of Cusa's *De docta ignorantia* (37,138 words), given an artificial layout of lines of about 45 characters, paragraphs of 10 lines, pages of 26 lines and sheets of 4 pages (226 pages). A **generic** version of the scribe, the same for both texts, keeps what is not specific to the Voynich: copying from the page with writable edits, the two-glyph memory, the boundary agreement, the line-start contexts, the length tone and the dissimilation. The *q-*, the gallows, the closures, *p/f* and the sheet habits are left out. It learns from the odd folios and writes the even ones, and it is scored on 16 generic measures, one of them new: the information carried by the order of the words (the mutual information between consecutive words of a line, 200 most frequent words, minus the same on the text shuffled within each line). The ceiling is the real odd half against the real even half. Three seeds.

| | Voynich | Latin |
|---|---|---|
| Real odd against real even (ceiling) | 16/16 | 13/16 |
| Generic scribe, copying 35% | **12/16** | **7/16** |
| Generic scribe, copying 10% | 10/16 | 7/16 |
| Adjacent repeats / chance, real → scribe | 3.15 → 4.61 | 0.04 → 4.63 |
| Word types, real → scribe | 4,850 → 4,412 | 3,897 → 8,451 |
| Word order (bits), real → scribe | 0.082 → 0.021 | 0.274 → 0.000 |

On both texts the scribe matches the character entropies, the Zipf slope and the mean word length: those measures distinguish nothing, any letter model passes them. The measures that separate the Voynich from a language are repetition, vocabulary size and word order, and on Latin the scribe fails all of them, and the battery sees it. **This is why the control matters**: the same procedure that passes on the Voynich fails on a real language exactly where a language should fail, so the battery tells syntax from its imitation, and what the Voynich and the scribe share (repetition 3.15 against 0.04 in Latin, near twins 2.26 against 0.59, and a link between consecutive words concentrated in the contact glyph) is what Latin does not have.

Where the link between consecutive words lives, measured as mutual information over the within-line shuffle: in Latin the whole previous word says 0.274 bits about the next one and its last letter 0.134, so the information is in the word, which is syntax. In the Voynich the whole word says 0.082 and the last glyph alone 0.106: all the dependence between consecutive words is in the contact glyph, and knowing the word adds nothing. The full scribe reaches 0.093 of the 0.106 in the contact glyph, but only 0.031 of the 0.082 per word: its frequent words do not concentrate the link as the real ones do. That measure is not yet in the battery of 76.

Limits: the Latin layout is artificial, so the line measures say nothing for Latin; Moby-Dick itself was not run.

### 8.2 Parisel's four boundary signatures

C. Parisel (*Evidence of Layered Positional and Directional Constraints in the Voynich Manuscript*, arXiv 2604.19762, v2, June 2026) defines four signatures of the boundary between consecutive words, calibrated separately for Currier A and B on the RF1b-e transliteration: the rate of boundaries that go from an "end" glyph to a "start" glyph (reference 71.0% in A, 64.3% in B), the presence of glyphs that almost only start or almost only end a word, on both sides (bilateral), the mutual information between the last glyph of a word and the first of the next (0.586 in A, 0.498 in B), and the shape of the frequency curve of the boundary glyphs (a power law in A, intermediate in B). A parametric slot generator (more than 2,000 runs) and a Cardan grille (15 configurations) pass all four at once in neither dialect, because the end-to-start rate and the mutual information pull in opposite directions when one knob has to produce both. He asks for generators where these traits come from independent mechanisms.

His verifier was run as published (one import fixed), on the scribe's text split by dialect with his own folio assignment, and on the real ZL3b text as a control (`external_tests/parisel/`).

| Text | Dialect | End→start | MI | Bilateral | Shape | Verdict |
|---|---|---|---|---|---|---|
| real (ZL3b) | A | 66.4% | 0.584 | yes | Zipfian | **4/4** |
| real (ZL3b) | B | 65.8% | 0.499 | yes | intermediate | **4/4** |
| scribe, 5 seeds | A | 68.1–70.5% | 0.526–0.541 | yes | Zipfian | **4/4 × 5** |
| scribe, 5 seeds | B | 63.3–65.6% | 0.454–0.470 | yes | intermediate | **4/4 × 5** |

The scribe passes the four signatures in both dialects and in all five seeds, with values close to the reference, not just inside the margins, and nothing in it is tuned to the boundary distribution. The mechanisms Parisel asks to be independent are independent in the scribe by construction: the end-to-start rate and the mutual information come from the boundary agreement [R3.3] and from the endings as closing marks [R2.7]; the shape from the word template [R2.1] and the two-glyph memory [R13]; the bilaterality from the glyphs that only open or only close a word [R1.5]. Reservations: the scribe's tables are learnt from the text, and 21–28% of the scribe's words are not in the dialect's word list (they are new words; the verifier reports it but does not penalise it).

### 8.3 Layfield and Davis: the similarity between pages

C. Layfield and L. Fagin Davis (*Singulion Structure and the Voynich Manuscript*, Digital Medievalist 19, 2026) hold that the manuscript was made of loose bifolia that were never meant to be nested in quires, and that the present binding is wrong. Their textual evidence is latent semantic analysis (documents of 40 words per page, TF-IDF, SVD with k = 75, cosine between pages): in the Voynich, pages on the inner face of a bifolium (conjoint) are more similar (0.433) than recto and verso of the same leaf (confoliate, 0.383), and both more than pages that face each other in the present order (facing, 0.298), while in two Latin control manuscripts facing pages are the most similar. They then reorder the bifolia of quires 13 and 20 to maximise the facing similarity (gains of 12% and 20%).

Torsten Timm's review (*The Singulion and the Sequence*, July 2026) had already read the similarity within the bifolium as **proximity of production** rather than continuity of meaning, and had asked for a permutation null for the reordering. Forum members (Wladimir D, pfeaster, oshfdk, dashstofsk) had pointed in the same direction. What was missing was a meaningless control text with sheet habits, which is what the scribe is: it has sheet habits and hand vocabulary and no notion of reading order.

The same LSA, rebuilt on the ZL3b paragraph text and run on the real text and on the scribe, in their quires (`external_tests/davis_layfield/`):

| Text | Confoliate | Conjoint | Facing | p conf/fac | p fac/conj | p conf/conj |
|---|---|---|---|---|---|---|
| Layfield and Davis (ZL 2a) | 0.383 | 0.433 | 0.298 | 0.005 | 0.000 | 0.168 |
| real (ZL3b, here) | 0.225 | 0.284 | 0.154 | 0.008 | 0.000 | 0.100 |
| scribe (5 seeds) | 0.147 ± 0.009 | 0.145 ± 0.012 | 0.091 ± 0.017 | < 0.07 in 4 of 5 | 0.03–0.18 | 0.48–0.97 |

The absolute values differ because the space is another; the order and the p values are what count. On the real text their pattern and their p values come out. On the scribe, a text with no meaning and no reading order, the pages of the same bifolium (0.145) are also far more similar than the facing pages of different bifolia (0.091). The similarity between pages measures the writing session, the production reading, and it cannot decide whether the binding order is right or wrong. Their reordering, done their way (mean facing similarity of the nested order against the maximum over all permutations of the bifolia), gains 33% on quire 13 and 50% on quire 20 for the real text, and 61 ± 26% and 78 ± 19% for the scribe, which has no correct order to recover: the maximum of 120 or 720 permutations of a noisy number always goes up. The codicological part of their argument (stains, drawings crossing the gutter, alternating hands) is untouched by this; the text cannot vote on it.

**An asymmetry within the bifolium that did not survive.** In the LSA numbers the inner face of the real bifolium (0.284) is more similar than the outer face (0.183): +0.096 paired by bifolium, 68% of the 37 bifolia, and the scribe does not do it (+0.001), which looked like a missing rule and would fit Timm's suggestion that the inner pages were visible together while writing. On the same pages and bifolia, with the contrast paired so that hand, language, section and quire are identical on both sides, five other measures see nothing: TF-IDF without SVD +0.026 (p 0.07), Jaccard of word types +0.002 (p 0.61), Jaccard at equal length +0.002, exact twins +0.004 (p 0.74), near twins at edit distance 1 +0.005 (p 0.72), the five free choices +0.020 (p 0.70). Within the LSA the effect belongs to hands 2 and 3 (15 bifolia); hand 1 (21 bifolia) gives +0.026, p 0.65. One post-hoc representation against five negative replications on the same data: not confirmed.

---

## 9. What it does not reproduce

The seven measures the scribe of 19 October misses (`scribe/results_table.txt`):

| Measure | Real | Scribe |
|---|---|---|
| Consecutive words at edit distance 1 / shuffled | 2.21 | 1.64 |
| Same word at distance 3 / shuffled | 3.45 | 2.51 |
| Frequent words repeated >3× chance (%) | 51.8 | 33.7 |
| Frequent words repeated <0.3× chance (%) | 16.1 | 26.6 |
| Line-end -m: lines of 10+ words / lines of 1–4 words | 3.41 | 2.49 |
| q- on the first word of a paragraph (%) | 4.2 | 6.1 |
| Page overdispersion of e-words | 24.6 | 18.4 |

- **Near twins.** Consecutive words at edit distance 1 are now too few. With the copying down to 22% there are fewer of them; the hand vocabulary does not make them.
- **Which words repeat.** The overall amount of repetition is right, but in the real text *dal*, *shey*, *saiin* never repeat adjacently and *okaiin* does ×5. Half of the frequent words repeat a lot and 16% avoid it; the scribe knows families of words, not single words. A per-word propensity estimated from the text did not help (§4). Repetition at distance 3 moves between runs (3.12 in another run of the same configuration) and is borderline.
- **Line-end -m.** The real effect turns out to be a mix of hands: hand 1 writes short lines and closes little, hand 3 writes long lines and closes a lot. Within hand × section it is flat (observed minus expected per word-count bin between −0.03 and +0.05, all compatible with zero). The scribe's remaining error is in short non-final lines: 11% *-m* against 6%.
- **Paragraph-initial q-** moves between seeds and is borderline.
- **Page overdispersion of e-words.** It was reproduced with the per-section offsets of 14 October (20.3) and dropped out when they were switched off in favour of the hand and section tables (§5). The share of *e*-words by section is right; the spread between pages of the same section is a little too small.
- **Long words**, the failure of 14 October (7.4% against 5.3%), are fixed by the length weights by position: 5.7%.

---

## 10. What it suggests about how the manuscript was written

Read as a description of an act of writing, the procedure looks like a **craft** with place rules and session habits, rather than composition sentence by sentence:

- **The writer looks at what is already on the page**, takes a nearby word and varies it, about one word in five. The rest he writes from the vocabulary of his own hand. This is very close to Torsten Timm's self-citation hypothesis (Timm & Schinner), reached here by a different route (measurement first, generator later), and to Schwartz (2026): much reuse of one's own repertoire, little recent copying. I read the convergence as support for it.
- **Words are written with a slot template and a 2-glyph memory**, and variants are made on the fly with the same memory. No word list is needed.
- **The line is the unit of work.** There are start forms and end forms. The first glyph avoids the previous line's first glyph. A drawing is treated as a margin, which means the text was written after the drawings.
- **The sheet is the session.** The free choices, the word family, the vocabulary and the letter size are shared within the sheet. The five Davis hands share the shape rules, but each has its own strength and its own glyph grammar.

What it does **not** say:

- **Sufficient is not necessary.** A meaningful process that produced this surface would give the same numbers. Ruling out languages and ciphers needs its own tests with positive controls and minimum detectable effects; the generator does not replace them. The Latin control (§8.1) is one such test for the battery, not for the manuscript.
- **The glyph grammar is copied from the text.** Why the grammar is this one, and why it differs by hand and section, remains open.
- **Room for a small message remains.** The free choices could still carry a small hidden message. My estimate of the blind capacity is a few KB at most, and an earlier test would have detected a message that broke the rules from roughly 650–2,500 bits, depending on the choice.

---

## 11. Side results

- **Vertical dissimilation does not decay.** The ratio is the same whether the line above has 29, 41 or 50 glyphs (0.65 / 0.63 / 0.66; ×0.90 [0.70–1.13] per doubling). The first glyph above was written 20–60 glyphs earlier, far beyond the 2-glyph word memory, so this is not a fading short memory. The line two above is *not* avoided: the ratio is 1.11 once the immediate avoidance is built into the null. It looks like a one-slot rule ("don't start like the last line") rather than general visual avoidance.
- **Line-end closure is position plus hand.** It depends neither on the physical distance to the margin (measured with line coordinates) nor on the number of words in the line once the hand is controlled.
- **Drawing gaps almost never split a word.** The concatenation of the words on both sides of a `<->` is an attested word no more often than across a normal space, and far less often than across an uncertain space: at most ~4% of the 745 gaps. The excess of *-d/-s* before gaps is mostly a lone *s* (31 cases before gaps, 13 after) that does not behave like a detached prefix.
- **Pieces on either side of a drawing are correctly paired.** On f1v the text to the right of the plant sits almost one line lower than the text on the left. No pairing of left and right pieces shows boundary agreement, neither as transcribed nor shifted by one line, while a positive control does. The gap really breaks the word boundary, as if each piece started a new line.
- **Quire 13 written blind.** Asked by a reader, the scribe wrote quire 13 (f75r–f84v, biological, hand 2) twice: learnt from the whole manuscript, and without having seen the quire. *e*-words: real 50.6%, scribe 50.3%, blind scribe 41.2%; strange words 3.0%, 3.0% and 3.6%. The blind scribe does not know the habit of the biological section, because it lives only in those pages. The three texts are in `scribe/quire_M/`.

---

## A note on tools

I used **Claude Code** (Anthropic) as a *code scribe*: it wrote most of the analysis and generator code. That saved me many hours of programming and let me concentrate on what matters, which is checking the results, questioning them and changing things quickly when something did not hold up. The questions, the decisions and the verification of every figure are mine.

## How to reproduce

Python 3 with pandas, numpy and scipy. On Windows the author runs everything with `py -3`; elsewhere use `python3`. The scribe's scripts are run from inside `scribe/`; the appendix table from the repository root.

| Step | Command |
|---|---|
| Enter the folder | `cd scribe` |
| Real measures | `py -3 measures.py` → `measures_real.json` |
| Scribe vs real (5 seeds) | `py -3 compare.py` → `results.json`, `results_table.txt` |
| Hold-out (odd → even) | `py -3 holdout.py` → `results_holdout_table.txt` |
| The whole manuscript, five seeds | `py -3 manuscript.py 1 2 3 4 5` → `manuscript_out/` |
| Ablations | `py -3 compare.py ablations` |
| Appendix table | from the repository root, `py -3 writeup/table_measures.py` |

Other scripts in `scribe/`: `standard_measures.py` (entropies, Zipf, MATTR, bursts, page similarity by distance), `boundary_per_hand.py`, `controls/control.py` (the Latin control, see `controls/CONTROLS.md`), `quire.py` (one quire, also blind), `calibrate_length.py` (the length weights), `strange_words_diagnosis.py` and `sample_form_memory.py` (§4 and §6). The external tests are in `external_tests/` with their own instructions in `EXTERNAL_TESTS.md`. Variable names and comments in the code are in Catalan.

---

## Appendix: all 76 measures

✓ = within ±25% of the real value (or within 0.01 absolute near zero); mean of 5 seeds.

<!-- TABLE -->
| # | Measure | Real | 3-rule generator | Scribe |
|---|---|---|---|---|
| 1 | Adjacent identical words (%) | 0.902 | 0.793 ✓ | 0.824 ✓ |
| 2 | Adjacent identical words / chance | 3.09 | 2.91 ✓ | 2.52 ✓ |
| 3 | Consecutive words at edit distance 1 / shuffled | 2.21 | 2.38 ✓ | 1.64 ✗ |
| 4 | Same word at distance 2 / shuffled | 3.27 | 2.52 ✓ | 3.39 ✓ |
| 5 | Same word at distance 3 / shuffled | 3.45 | 2.46 ✗ | 2.51 ✗ |
| 6 | Same word at distance 5 / shuffled | 2.85 | 2.20 ✓ | 3.09 ✓ |
| 7 | Frequent words repeated >3x chance (%) | 51.79 | 31.70 ✗ | 33.69 ✗ |
| 8 | Frequent words repeated <0.3x chance (%) | 16.07 | 24.39 ✗ | 26.62 ✗ |
| 9 | Boundary MI, distance 1 (last glyph to next first glyph) | 0.155 | 0.132 ✓ | 0.149 ✓ |
| 10 | Boundary MI, distance 2 | 0.009 | 0.000 ✓ | 0.004 ✓ |
| 11 | Boundary MI, distance 3 | 0.003 | -0.001 ✓ | 0.002 ✓ |
| 12 | Lift -y \| q- | 1.69 | 1.71 ✓ | 1.66 ✓ |
| 13 | Lift -r \| a- | 3.12 | 2.97 ✓ | 3.16 ✓ |
| 14 | Lift -y \| a- | 0.194 | 0.276 ✗ | 0.213 ✓ |
| 15 | Lift -n \| q- | 0.472 | 0.501 ✓ | 0.574 ✓ |
| 16 | First word of line starts ch/sh (%) | 8.15 | 8.73 ✓ | 7.71 ✓ |
| 17 | First word of line starts y (%) | 14.33 | 13.90 ✓ | 15.47 ✓ |
| 18 | Last word of line ends -m (%) | 15.87 | 9.07 ✗ | 19.59 ✓ |
| 19 | Line-end -m: lines of 10+ words / 1-4 words | 3.40 | 3.88 ✓ | 2.49 ✗ |
| 20 | Same first glyph as line n-1 / null | 0.583 | 0.689 ✓ | 0.559 ✓ |
| 21 | Same first glyph as line n-2 / null | 1.30 | 1.13 ✓ | 1.30 ✓ |
| 22 | Same first glyph as line n-3 / null | 1.16 | 1.17 ✓ | 1.09 ✓ |
| 23 | Distinct initial glyphs per paragraph (4+ lines) | 4.36 | 4.94 ✓ | 4.51 ✓ |
| 24 | Adjacent repeats: first line of paragraph / rest | 0.385 | 1.24 ✗ | 0.342 ✓ |
| 25 | Spearman correlation of neighbour word lengths | 0.160 | 0.051 ✗ | 0.194 ✓ |
| 26 | Word types | 7,915 | 10,284 ✗ | 7,325 ✓ |
| 27 | Hapax (% of types) | 71.32 | 76.11 ✓ | 66.46 ✓ |
| 28 | [R2.1] Words fitting the slot grammar (%) | 97.70 | 94.65 ✓ | 99.91 ✓ |
| 29 | [R2.2] Words with 2+ gallows (%) | 1.80 | 5.34 ✗ | 1.88 ✓ |
| 30 | [R2.6] Mean word length (glyphs) | 4.80 | 4.78 ✓ | 4.76 ✓ |
| 31 | [R2.6] SD of word length | 1.71 | 2.20 ✗ | 1.75 ✓ |
| 32 | [R13.7] e and i in the same word / expected | 0.244 | 0.413 ✗ | 0.224 ✓ |
| 33 | [R3.3] H(prefix), marginal | 1.54 | 1.52 ✓ | 1.53 ✓ |
| 34 | [R3.3] H(prefix \| previous glyph, core) | 0.918 | 0.959 ✓ | 0.926 ✓ |
| 35 | [R3.3] q- before o- after -y (%) | 57.26 | 53.65 ✓ | 57.95 ✓ |
| 36 | [R3.4] q- on first word of paragraph (%) | 4.19 | 13.22 ✗ | 6.08 ✗ |
| 37 | [R3.4] q- on first word of line (%) | 14.87 | 13.03 ✓ | 16.79 ✓ |
| 38 | [R3.4] q- inside the line (%) | 17.94 | 16.21 ✓ | 19.34 ✓ |
| 39 | [R4.2] a- at line start (%) | 0.354 | 0.260 ✗ | 0.277 ✓ |
| 40 | [R4.2] d-/s-/y- at line start (%) | 47.98 | 39.49 ✓ | 47.68 ✓ |
| 41 | [R14.1] Bare gallows at line start (%) | 8.97 | 22.21 ✗ | 9.16 ✓ |
| 42 | [R4.3] Closed last word, non-final lines (%) | 27.11 | 11.51 ✗ | 30.08 ✓ |
| 43 | [R4.3] Closed forms inside the line (%) | 2.34 | 5.06 ✗ | 2.30 ✓ |
| 44 | [R14.2] Closed last word of paragraph (%) | 17.31 | 8.41 ✗ | 18.57 ✓ |
| 45 | [R14.3] Length of 2nd word / 1st word | 0.877 | 0.965 ✓ | 0.912 ✓ |
| 46 | [R5.1] Gallows on first word of paragraph (%) | 93.24 | 53.92 ✗ | 93.46 ✓ |
| 47 | [R1.3] p/f among gallows, first line of paragraph (%) | 31.03 | 9.47 ✗ | 31.53 ✓ |
| 48 | [R1.3] p/f among gallows, other lines (%) | 2.73 | 10.19 ✗ | 2.74 ✓ |
| 49 | [R5.2] Word length, first line / rest | 1.08 | 0.989 ✓ | 0.991 ✓ |
| 50 | [R6.1] Closed word before a drawing gap (%) | 10.16 | 5.00 ✗ | 10.85 ✓ |
| 51 | [R6.1] d-/s-/y- after a drawing gap (%) | 41.33 | 13.55 ✗ | 41.43 ✓ |
| 52 | [R6.1] q- after a drawing gap (%) | 3.57 | 16.14 ✗ | 4.28 ✓ |
| 53 | [H8] Same first glyph after a gallows-initial line / null | 0.612 | 0.691 ✓ | 0.536 ✓ |
| 54 | [A1] Words with an edit-distance-1 twin earlier on the page (%) | 64.47 | 61.19 ✓ | 66.32 ✓ |
| 55 | [A1] Lines back to the nearest twin (median) | 2.00 | 2.00 ✓ | 2.00 ✓ |
| 56 | [H2] Page overdispersion of q- (after -y) | 6.32 | 1.30 ✗ | 5.31 ✓ |
| 57 | [G6] Vocabulary cosine: same sheet / neighbouring pages of other sheets | 1.30 | 0.988 ✓ | 1.23 ✓ |
| 58 | [eye] Strange words (rare trigram in the real text) (%) | 4.59 | 13.74 ✗ | 4.23 ✓ |
| 59 | [eye] Strange words per line | 0.359 | 1.07 ✗ | 0.331 ✓ |
| 60 | [page] Page overdispersion of e-words | 24.57 | 1.65 ✗ | 18.41 ✗ |
| 61 | [section] e-words: biological / herbal | 2.04 | 0.996 ✗ | 1.73 ✓ |
| 62 | [section] -edy words in biological (%) | 27.48 | 10.90 ✗ | 26.72 ✓ |
| 63 | [page] Share of the page's most frequent word (median, %) | 4.71 | 3.21 ✗ | 4.80 ✓ |
| 64 | [eye] Words of 8+ glyphs (%) | 5.25 | 9.92 ✗ | 5.72 ✓ |
| 65 | [text] Character entropy h1 | 3.91 | 3.90 ✓ | 3.90 ✓ |
| 66 | [text] Conditional entropy h2 | 2.14 | 2.28 ✓ | 2.09 ✓ |
| 67 | [text] Conditional entropy h3 | 1.86 | 2.02 ✓ | 1.81 ✓ |
| 68 | [text] Zipf slope (first 1,000 types) | 1.00 | 0.993 ✓ | 0.996 ✓ |
| 69 | [length] Words of 2-3 glyphs (%) | 21.61 | 28.49 ✗ | 23.12 ✓ |
| 70 | [length] Words of 5-6 glyphs (%) | 41.00 | 32.12 ✓ | 39.09 ✓ |
| 71 | [range] Shared vocabulary, neighbouring pages (cosine) | 0.330 | 0.241 ✗ | 0.303 ✓ |
| 72 | [range] Shared vocabulary, 10 pages apart | 0.253 | 0.232 ✓ | 0.243 ✓ |
| 73 | [range] Shared vocabulary, 100 pages apart | 0.155 | 0.224 ✗ | 0.166 ✓ |
| 74 | [range] Neighbouring / 100 pages apart | 2.13 | 1.08 ✗ | 1.83 ✓ |
| 75 | [range] Bursts of the 50 most frequent words (CV of gaps) | 1.75 | 1.03 ✗ | 1.59 ✓ |
| 76 | [range] Page overdispersion of the 50 most frequent words | 2.06 | 1.08 ✗ | 1.80 ✓ |
| | **Reproduced (±25%)** | | **39/76** | **69/76** |
<!-- /TABLE -->
