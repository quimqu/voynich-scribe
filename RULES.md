# The rules of the Voynich writing system

*A rulebook, not a report. It collects, as explicit rules, everything that the program (phases 1-4w, July 2026; sessions 27-28/09/2026) has measured with controls. Each rule carries: its **strength** (percentage of compliance or ratio against chance), whether it is **system** (the same in all five hands) or **habit** (varies by hand or by page), and its **source** (script or findings log entry). Data: ZL3b, 32,284 paragraph words, 7,915 word types. Numbers from 28/09/2026 (`sessio_2026-09-28/regles_compliment_out.txt`) unless stated otherwise.*

*Sections 13 and 14: added on the afternoon of 28/09 (second mining pass); R14.7 added on 26/10/2026. How to read it: "always" means ≥ 98%; "almost always" 90-98%; "by preference" a strong bias but with normal exceptions. There is no rule of meaning: all of them are rules of form, of place and of process.*

*Sources: identifiers in square brackets (A1, G6, H14, R7.4 ...) are entries of the findings log and of this rulebook; the script paths in the sources (`sessio_2026-09-28/`, `coordenades/`, `proves_seccio5/` ...) belong to the lab notebook of the project, which is not part of this repository. The rules that the skribe implements are reproduced by the code in `scribe/`.*

---

## 0 · The three background rules

**R0.1 · It is a writing system, not a written language.** The glyphs inside a word are very predictable (h2 2.3 bits against 3.4 for Latin, in EVA), but the vocabulary is as varied as a language's (word entropy 10.6 bits against 9.8 for Latin); word order carries 0.08 bits per pair of consecutive words above chance, below 19 texts in 12 languages (0.2–1.5 bits, including a Latin text with a larger vocabulary: 0.23) and close to the skribe (0.04), and what it carries is the glyph contact, not the word (amended 25/10/2026); there is no class of function words ("cement words": articles, prepositions); no cipher of a tested language reproduces its statistics. [A9, A11, B1, B2]

**R0.2 · The rules are at three levels: glyph, word and place.** Everything that is regular is decided by looking, at most, at three glyphs on either side of a space, and at where the word is within the line, the page and the sheet. No rule looks beyond the neighbouring word. [G2, H1, §3]

**R0.3 · System versus habit.** Some rules are identical in all five hands (system); others have the same direction but a different strength (habit). The rulebook marks this on each rule. [G10, night1]

---

## 1 · The alphabet

**R1.1 · Glyph families.** The gallows form a grid of 2 legs × 2 loops (`k t p f`) plus the variant with a bench (`ckh cth cph cfh`); the benches are `ch sh`; the minims `i n m` and the curves `e a o y`; the tails `l r s d`; the connector `q`. System. [A12]

**R1.2 · Allographs: pairs that are the same sign in different places.** `ch~sh`, `k~t`, `p~f` (and `ckh~cth`) merge without loss (percentile ~0 of the null). The choice between them is dictated by place, with only 0.009 bits of context. System. [A7, V3, U1]

**R1.3 · `p` and `f` are the first-line gallows.** In the first line of a paragraph, 35% of the gallows are `p`/`f`; in interior lines, 3%. System (30-54% in all hands). **And they depend on the free space above**: in the rest of the first line (without the first word), 42% if it is the first line of the page, 34% if the paragraph has space above it, 22% if it is pressed against the previous one (difference +12 points, CI +7 to +17, in all sections and hands). The first word carries them just the same (51-56%), the number of gallows does not change, and interior lines with space above do not do it. [V5, G4, night1, H9] **Amended on 27/10/2026:** a plain `p`/`f` is never followed by `e`: 5 `pe`/`fe` in the whole text against 3,589 `ke` and 1,431 `te`, in every section and in every line (benched `cph`/`cfh` do take `e`). Where `k`/`t` take `e`, `p`/`f` take `ch`/`sh`: after `k`/`t` of the first line `e` 35% and `ch`/`sh` 18%, after `p`/`f` 0% and 55%, so `e` + `ch` is about the same share after both; `p`/`f` also go less before `a` (13% against 24%). So `p`/`f` are not `k`/`t` written fancy at random (that would leave a third of them before `e`): the `e` that follows becomes `ch` (`ke`→`pch`, `keedy`→`pchedy`, `key`→`pchy`). System. [thread 6231 on voynich.ninja; `scribe/SCRIBE.md` §12] **And `p` is the usual one** (27/10): among plain `p` and `f` on the first line, `p` 79%, while `k` is only 57% of plain `k`+`t` there (R5.2): `t` becomes `f` much less often than `k` becomes `p`.

**R1.4 · `q` is always followed by `o` and is always initial.** 97.8% and 98.5%. System. [regles_compliment]

**R1.5 · Glyphs that neither start nor end a word.** `e`, `i`, `n`, `m` never start a word (< 0.5%); `e`, `a`, `i`, `ch`, `q`, `ckh` never end one. System. [regles_compliment]

**R1.6 · Ligatures for the convenience of the pen**, unrelated to order (gallows + bench, above all in the herbal section). [A12, Y5]

---

## 2 · The word

**R2.1 · Template.** A word is `[prefix] [core] [e…] [suffix]`, where the core is a gallows or a bench (or none), the `e` are one to three, and the suffix is one of the endings of R2.4. The simplest template covers 74% of the tokens; the slot grammar of 23 positions learned from the data covers 98.8% (`night_generator/slots.json`). System (A and B have the same skeleton, mutual coverage 98%). [G1, night1]

**R2.2 · One gallows per word.** 0 gallows 46%, 1 gallows 52%, 2 gallows 1.8%, 3 never. System. [regles_compliment]

**R2.3 · The prefixes.** `qo-` (4,176 of the 16,000 words with a gallows), `o-` (3,946), none (3,135), `y-` (967), `ch-` (577), `l-` (447), `cho-`, `ol-`. Before a bench there is no prefix (5,705 of 5,705). System. [night1]

**R2.4 · The suffixes and the two blocks.** Main suffixes: `-y`, `-dy`, `-aiin`, `-ol`, `-ar`, `-ain`, `-al`, `-or`. The word chooses between **two blocks**: the `e/d/y` block (core with `e` → `-y`, `-dy`: `kee`→`y`/`dy` in 75%; `ke`, `te`→`dy`) and the `a/ii/n` block (bare core `k`/`t` → `-aiin`, `-ain`, `-ar`, `-al`). They are not inflectional paradigms: they are two routes. MI core~suffix 0.83 bits (null 0.28). System, but B makes more "closed" words (`qokeedy`) than A (excess 0.69 against 0.25). [G9, night1]

**R2.5 · Order within the word.** There is a directed positional order (56 consistent precedences, all already implied by the slots or by the terminator; none new) and it has no reading direction of its own (ten orthogonal orders are equally good). System. [A6, Y2]

**R2.6 · Length.** A narrow bell: 3 glyphs 15%, 4 glyphs 21%, 5 glyphs 24%, 6 glyphs 18%, 7 glyphs 9%; mean 4.8; 8 or more, 5%. It is not lognormal like the additive notations. System. [A12, S1]

**R2.7 · The endings are closing punctuation, not letters.** The only feature of the body that predicts the final glyph is the count of minims (z +229); removing the endings shrinks the vocabulary by 32% (Latin 12%). System. [A5]

**R2.8 · Almost every word has a twin nearby.** 95.6% of the tokens have a word at edit distance ≤ 1 already written on the same page, median 3 lines higher up, with a bias towards the same horizontal height. System (process). [A1, W1]

---

## 3 · The space and the boundary between words

**R3.1 · The space is a glyph rule.** A letter bigram with the space as a symbol reproduces all the boundary pairs; the space is guessed 87% of the time from two letters on each side. System. [G2]

**R3.2 · Strong and weak boundaries.** After `-y` before `q-`, or after `-n` before `o-`/`ch-`, the space is certain (1% transcriber doubt). Between `o|l`, `l|k`, `s|a`, `r|a` it is weak (28-45% doubt). Words in `a-` carry a doubtful space in front of them 27% of the time; words in `q-`, 1%. System. [G2, prefix2]

**R3.3 · The boundary agreement (the prefix rule).** The prefix of a word with core `a-`/`o-` depends on the final glyph of the previous word and on the first two glyphs of the core, and on nothing else:

| the previous word ends in | core `a-` takes | core `o-` takes |
|---|---|---|
| `-y` | `d-` 73%, `s-` 15%, none 10% | `q-` 56%, none 39% |
| `-n` | `d-` 51%, none 44% | none 77%, `q-` 20% |
| `-r` | none 79%, `d-` 18% | none 81%, `q-` 16% |
| `-l` | `d-` 70%, none 20% | none 63%, `q-` 28% |
| `-s` | none 89% | none 84% |

And within the core `o-` after `-y`: `ok-` takes `q-` 72% of the time, `ot-` 48%, `ol-` 26%, `or-` 7%. This explains 35% of the choice; the whole previous word, the next word, the position and the previous choice add nothing. The rest is page rate and coin toss (R7.2). **Habit in the strength** (hand 1: `q` after `-y` 0.14; hands 2-3: 0.33), **system in the form**. [G3, H1, H2]

**R3.4 · `q-` is the continuation form.** 1% in labels, 4% in the first word of a paragraph, 13% in the first word of a line, 18% in the interior, 8.5% in the last word of a line. System. [G3, allography A2]

**R3.5 · There is no word syntax.** No word is predicted from the previous word beyond the contact glyph (0.16 bits at distance 1, 0.009 at distance 2, 0 across the line break). No resegmentation changes this. System. [A4, G2]

---

## 4 · The line

**R4.1 · The line is the unit.** All the sequential structure lives in the first and last word of the line and in the repetitions; once these are fixed, the gain of an HMM dies (replicated three times). System. [A4, R3]

**R4.2 · Line start: start forms.** The first word starts with `d-`, `s-` or `y-` 40% of the time (interior 13%), and with `a-` 0.3% (interior 4.3%: **forbidden**). System (all five hands: `a-` 0.000-0.003 except hand 5, 0.033). [G10, night1]

**R4.3 · Line end: closed forms.** In the last word of the line, `-iin` closes into `-m` (60%, against 7% in the interior), `-l` into `-ly` (25% against 4%), `-r` into `-ry` (25% against 2%), `-s` into `-sy`, `-y` into `-g` (5% against 0.2%). Closed forms as a whole: 25% in the last word, 2.3% in the interior. It does not happen before `q-` within the line: it is the physical end. It does **not** depend on physical proximity to the margin: with coordinates, the last word closes the same whether or not it reaches the margin (29% against 25-28%), also where there are no drawings. It is a form of position, not an abbreviation for lack of space (corrected on 28/09, `coordenades/REGLES_DE_LLOC.md` §A). **Nor does it depend on the number of words in the line** (corrected on 14/10): the rise of `-m` from 7% to 32% with line length in words is a composition of hands (hand 1 writes short lines and closes little, hand 3 writes long lines and closes a lot). Within each hand and section, observed minus expected by word-count bands: −0.03 to +0.05, all compatible with zero; coefficient of the word count with a hand fixed effect, +0.03 [−0.07, +0.27] (`proves_seccio5/PROVES_SECCIO5.md` §5.2). System in the form, **habit in the strength** (final `m/iin`: hand 1 0.37, hand 5 0.85). [G4, allography A1, night1, J1] **Amended on 27/10/2026 (the form of the closure):** `-aiin` closes into `-am`, the whole `i` run goes: 495 line-final `-am` against 29 `-im`. And `-y` → `-g` depends on the glyph before the `y`: after `o` 65% of the line-final words (`-og`), after `e` 12%, `ch` 9%, `l` 8%, but after `d` and `k` 1% and never after `t` or a benched gallows. [`scribe/pairs/CONTEXT_PAIRS_PREREG.md`]

**R4.4 · The last word is shorter and anomalous.** z −8.9 in length on intermediate lines; +0.14 bits of surprise in characters. System. [LAAFU, B, U5]

**R4.5 · Vertical dissimilation.** Two consecutive lines of the same paragraph avoid starting with the same glyph: 8.8% against 14.7% (ratio 0.60, z −10). Only the first glyph; nothing else is copied from the line above (ratio 1.0 at all other indices). After an initial `ch`, the next line starts with `ch` 0.8% of the time (expected 13.7%); after an initial gallows, ratio 0.21. **It does not depend on geometry**: it is the same with narrow or wide line spacing and with the line start aligned or offset relative to the line above. **Nor does it decay with time** (14/10): the ratio is the same whether the line above has 29, 41 or 50 glyphs (0.65 / 0.63 / 0.66; ×0.90 [0.70-1.13] per doubling). The first glyph above was written 20-60 glyphs ago, far beyond the two-glyph memory of the word (R17.3). So it is not short stroke memory: it is a **record of the last line start** that does not fade (the line two above is no longer avoided, R4.6). Sight is not excluded, but it does not explain why the line two above, which is also in sight, is not avoided (`proves_seccio5/PROVES_SECCIO5.md` §5.3). **Habit** (hand 1 0.41, hand 5 0.84). [G5, H8, J2]

**R4.6 · The line two above is not avoided; it is slightly attracted.** Raw, the first glyph coincides with that of the line two above 1.33 times the expected. Most of this is mechanical: if the middle one is avoided, with few possible initials the top one gets repeated (A-B-A). With a null that preserves the composition of the paragraph and imposes adjacent dissimilation, 1.11 remains (z +2.9) at distance 2 and nothing at distance 3 (1.02) or 4 (1.00). Corrected on 14/10: the earlier version (0.19 against 0.13 at distances 2 and 3) compared against a Markov chain that did not preserve the composition of the paragraph. Habit. [G5, J2]

---

## 5 · The paragraph

**R5.1 · The paragraph starts with a gallows.** The first word of the paragraph carries a gallows 93% of the time (first word of an interior line: 44%). And it does not start with `q-` (4%). System. [V5, G3]

**R5.2 · The first line is a register of its own.** Besides `p`/`f` (R1.3): half the repetitions given its vocabulary (0.58), more hapaxes (18.8% against 13.2%), longer words (5.38 against 5.16), and the second line does not reuse its words (4.7% against 7.1%). System. [G8] **Amended on 26/10/2026:** it is also written with the tall variants and with fewer frequent words. Leaving out the first word: `sh` is 35.5% of `sh`+`ch` against 26.6% in the other lines (×1.34; ×1.22 to ×1.82 in every hand), `t` is 43.0% of `t`+`k` against 34.9% (×1.23), words among the most frequent (≥ 0.3% of the text) are 23.4% against 35.3% (×0.66), and words with `ee` 11.5% against 13.3% (×0.87). The fewer repetitions follow from the rarer words: once the skribe writes the first line with rarer words, it no longer needs a separate rule against repeating there. System in the direction, habit in the strength. [`scribe/SCRIBE.md` §11]

**R5.3 · The first word of a paragraph does not dissimilate** from that of the previous paragraph (ratio 1.00): rule R4.5 is a rule of line within paragraph. [G5]

---

## 6 · The drawings

**R6.1 · The drawing gap is a margin.** The word before the gap closes like a half line end (closed forms 10% against 2% in the interior and 25% at the margin; `r→ry` 19% against 2%; shorter words). The word after it opens like a full line start (`d-/s-/y-` 41% = line start 40%; `q-` 4%). The boundary agreement (R3.3) breaks at the gap: after `-y`, `q-` drops from 49% to 12%. **Consequence: the text was written after the drawing.** System (same pattern in herbal, biological and pharmaceutical). **The gap almost never splits a word** (14/10): the concatenation of the words on either side is an attested word as often as across a normal space (excess +0.018 against +0.016), far from the doubtful space (+0.10). At most 4% of the gaps (~30 of 745). The excess of `-d/-s` before the gap does not come from split words: it is above all the lone `s` (31 cases before and 13 after the gap), which does not behave like a separate prefix (`proves_seccio5/PROVES_SECCIO5.md` §5.5). [H5, J3]

**R6.2 · But `a-` can indeed start after a gap** (1.9%, the same as in the interior). The prohibition of `a-` (R4.2) belongs to the physical left margin; the start forms `d-/s-/y-` belong to the start of a unit. [H5]

**R6.3 · Label words are not in the text of their own page** any more than in that of other pages of the section (z +1.0). There is no link label → text of the page. [G7]

---

## 7 · The page and the sheet

**R7.1 · The vocabulary belongs to the page.** Shuffling the words within each page, the excess of adjacent repetitions drops from ×3.1 to ×1.23: most of the repetition is local vocabulary. System (process). [G7, A1]

**R7.2 · Each page has its own rate for each free choice.** The proportion of `q-` (given R3.3), of `k` against `t`, of `ch` against `sh`, of `-dy` against `-y` varies by page far more than a binomial (z +10 to +58), beyond language, section and hand. Within the page, the choices are coins without memory (prefix) or with contagion from the immediate neighbour and drift over a few lines (`k/t`, `-y/-dy`). **Habit.** [H2, H4]

**R7.3 · A and B are the same system with different weights.** Same skeleton of slots (mutual coverage 98%); B fills in more `e`, `d`, `y` (`qokeedy`), A fills in the second `o` and leaves 44-49% of the words open (`-l/-r/-o/-s`) against 30-36% for B. `q` before `o-` after `-y`: A 0.46, B 0.59. Habit (of hand and of section). [G1, G4, H2]

**R7.4 · The sheet is the session.** Recto, verso and conjugate folio of the same bifolium share vocabulary and graphic habits (z +2 to +6 in all sections); the adjacent folio of another sheet does not. They also share **the size of the lettering** and, with it, the line spacing and the number of lines (line spacing: z −6.4 within the sheet, z +0.1 with the neighbouring folio of another sheet); the ratio of line spacing to letter size is constant throughout the manuscript. The vocabulary drifts continuously along the codex with jumps at the boundaries of hand and quire. System (process). [G6, A2, W3, H11]

**R7.5 · The text has no arrow of time.** No chain copying: asymmetry 0.496 with demonstrated power. Copying is radial (from anything visible), not linear. [A3, Q2]

**R7.6 · The four pages of a sheet were written with identical rules and similar rates** (R7.2 weakly shared within the sheet, z +2.3). [H2]

---

## 8 · The labels

**R8.1 · Labels are citation forms.** They start with `o-` 56% of the time (text 21%), with `q-` 1% (text 16%); they close with `-y`/`-ly`/`-ry` (10.9% against 1.6%): the word `otal` of the text is `otaly` in the label. The `o-` words of the labels are the ones that go with `qo-` in the text. System. [G4]

**R8.2 · A closed repertoire.** 45 labels recur as labels on three pages or more (`otaly`, `otedy`, `okol` on 7). [G7]

**R8.3 · The zodiac labels are not counters.** No position-to-position alignment between signs, no period within a ring, and identical labels do not share a position; the test would see a shared code followed by half of the labels. Neighbouring labels resemble each other by copying, not by numbering. [H6, W8, V2]

---

## 9 · The repetitions

**R9.1 · A word is repeated immediately after itself 0.94% of the time** (×3.1 chance), with 11 triples; they fall in the middle of the line, not at the start or the end; they are not dittography or filler. Habit in the strength (×1.7 to ×2.3 by hand). [G7, night1]

**R9.2 · Which words repeat and which are avoided.** Under a page null: bench+`o`+`l/r` (`chol`) ×2.6; gallows+`e`+`dy/y` (`qokedy`) ×2.3; `-aiin/-ain` (`daiin`) ×0.7. A large part follows from R3.3: `-y` admits `q-` after it (a word in `-y` can follow itself), `-n` does not admit `d-`. [G3, G7]

**R9.3 · Nothing is copied glyph by glyph from the line above** (ratio 1.0 at all indices except the first, 0.52 by R4.5). Word reuse is a matter of memory and page, not of alignment. [G5, night2]

---

## 10 · System versus habit (Davis's five hands)

| rule | hand 1 | hand 2 | hand 3 | hand 4 | hand 5 | verdict |
|---|---|---|---|---|---|---|
| `a-` at line start | 0.001 | 0.003 | 0.003 | 0.000 | 0.033 | system |
| `d/s/y-` at line start | 0.37 | 0.41 | 0.44 | 0.50 | 0.39 | system |
| `p/f` in the first line (among gallows) | 0.41 | 0.38 | 0.30 | 0.23 | 0.54 | system |
| `q-` in the first word of a paragraph | 0.05 | 0.06 | 0.03 | 0.00 | 0.00 | system |
| `m/iin` at line end | 0.37 | 0.66 | 0.78 | 0.60 | 0.85 | system in the form, habit in the strength |
| `q` after `-y` | 0.14 | 0.33 | 0.32 | 0.13 | 0.17 | habit |
| vertical dissimilation (ratio) | 0.41 | 0.60 | 0.78 | 0.64 | 0.84 | habit |
| repetition `AA` / chance | 1.8 | 1.7 | 2.3 | 1.9 | 2.1 | habit |

(hand 1: herbal A and pharmaceutical; hand 2: herbal B and biological; hand 3: stars; hand 4: astronomical and zodiac; hand 5: text-only pages and herbal B.) [night1, G10]

---

## 11 · How to write a page following the rulebook (the recipe)

1. Start the paragraph with a word that has a gallows, by preference `p` or `f`, never with `q-`; if there is free space above, use `p`/`f` in the rest of the first line too, and write the `e` after a `p`/`f` as `ch` (R5.1, R1.3).
2. In the first line, choose longer and rarer words, prefer `sh` to `ch` and `t` to `k`, use fewer `ee`, and do not repeat its words in the second line (R5.2).
3. Each word: prefix + core + `e` + suffix, one gallows at most, 4-6 glyphs, and decide the block: with `e` → `-y`/`-dy`; without → `-aiin`/`-ar`/`-ol` (R2.1-R2.6).
4. If the previous word ends in `-y` and the next one starts with `o`, put `q-` (at this page's rate); if it ends in `-r` or `-s`, put nothing; if the next one starts with `a`, put `d-` (R3.3).
5. To choose `k` or `t`, `ch` or `sh`: the page rate and the word next to it; nothing else (R7.2, R1.2).
6. Start each line with `d-`, `s-` or `y-` by preference, never with `a-`, and do not repeat the first glyph of the line above (R4.2, R4.5).
7. In the last word of each line that is not the last of the paragraph, close: `-iin` → `-m`, `-l` → `-ly`, `-r` → `-ry`, and make the word short, whether or not there is space at the margin. Do not squeeze the lettering to fit anything in (R4.3, R4.4, R14.2, R15.1).
8. If you run into a drawing, close a little before it and start again after it as if it were a new line, but here you may start with `a-` (R6.1, R6.2).
9. Take the words from those you have in sight on the page, changing one glyph (R2.8, R7.1); now and then repeat one in the middle of the line (R9.1).
10. Write the four pages of the sheet in the same session, with the same vocabulary and the same letter size (R7.4). In the labels, drop the `q-` and close with `-y` (R8.1).
11. At the start of each line, decide whether it will be a line of words that start with a gallows (`t`, `k`, `p`, `f`) or not, a little according to the page (R14.7).

A generator that follows rules 3, 4, 5 and 9 reproduces 16 of 27 measures of the manuscript; what it lacks is above all the production layer (drift, sheet, first line) and the contagion between neighbours. [G11]

---

## 13 · Rules of contact between glyphs (second pass, 28/09; `sessio_2026-09-28/mineria_regles*.py`)

*What can follow what within the word. "Never" means fewer than one case per thousand. All of them are system.*

**R13.1 · `q` only goes before `o`** (98%; the remaining 1%, `qe`). It is not doubled, it is never final, it is never interior.

**R13.2 · `n` and `m` are terminal.** `n` ends the word 95% of the time (99% with `no`, `na`); `m`, 95%. Neither of them ever goes before `e`, `i`, a gallows, `q`, `s`. `m` and `n` do not coexist in the same word (ratio 0.14).

**R13.3 · The minim group is `a` + `i`(1-3) + `n`/`r`/`m`.** The 6,609 runs of `i` are preceded by `a` (95%) or `o` (4%) 99.1% of the time, and followed by `n` (86%), `r` (10%), `m` (1%) 97% of the time. `i` never goes before `o`, `e`, `y`, `a`, a bench, `q`, a gallows. The runs are of 1 (2,389), 2 (4,048) or 3 (171); of 4, once.

**R13.4 · `a` only goes before minims and tails.** After `a`: `i` 49%, `r` 22%, `l` 21%, `m` 5.5%, `n`, `s`. Never `o`, `e`, `y`, `a`, a bench, a gallows.

**R13.5 · The `e` live between the core and the ending.** The 13,382 runs of `e` are preceded by a bench (53%) or a gallows (41%) 95% of the time, and followed by `d` (36%), `y` (28%), `o` (22%) 85% of the time. `e` never goes before `i`, `l`, `r`, `n`, `q`, `m`. Runs of 1 (9,103), 2 (3,927), 3 (345); of 4, seven times.

**R13.6 · Only `e` and `i` are doubled.** `ee` 26% of the `e`, `ii` 40% of the `i`; `oo`, `ll`, `dd` below 0.4%; `k`, `t`, `p`, `f`, `n`, `q`, `m`, `cth`, `ckh` are never doubled.

**R13.7 · `e` and `i` do not coexist** (ratio 0.15): this is the glyph level of the two blocks of R2.4 (`e`→`-y/-dy` against `i`→`-aiin/-ain`).

**R13.8 · `y` is final or prefix.** After `y`: end of word (95% with `yk`, `yt`), and otherwise a gallows or a bench (initial `y-`, R13.12). Never `e`, `y`, `i`, `n`, `m`.

**R13.9 · The gallows are preceded by `o`, by the start of the word, by `y`, `l`, `e` or a bench** (55% / 17% / 8% / 8% / 5% / 4%); never by another gallows, `n`, `m`. They are followed by `e` (31%), `a` (26%), a bench (16%), `y` (12%), `o` (11%); never by `i`, `r`, `n`, `q`, `m`, another gallows. Two different gallows do not coexist (`k`+`t` 0.12; `ckh`+`t` 0.07).

**R13.10 · `p` and `f` prefer a bench after them** (`pch`, `fsh`: attraction 2.5); `ckh` prefers `y` (2.75).

**R13.11 · `l` is the connector.** After `l`: end of word, `k`, a bench, `o`, `d`, `y`, `sh`, `a`. It is the only tail glyph that can go before a gallows (`lk`, `lt`) and before a bench (`lch`, `lsh`). `r` and `s`, by contrast, are almost always final (`ra`, `ro`, `sa`, `so` aside).

**R13.12 · Initial `y-` is a prefix.** 1,544 tokens; the word without the `y` is attested 68% of the time; it is followed by a gallows (64%) or a bench (22%).

**R13.13 · The `a-` words are loose endings.** 1,321 tokens, 287 word types (`aiin`, `ar`, `al`, `ain`, `am`, `air`); without a gallows (91%) or a bench (95%), 3.8 glyphs. They are the suffix without a core, and that is why they take `d-`/`s-` (R3.3): `daiin` = `d` + `aiin`.

**R13.14 · The benches never go before `i`, `n`, `q`, or another bench** (`chsh` never), and do go before `e`, `o`, `y`, `d`, `a`, `ckh`.

## 14 · More rules of line and paragraph

**R14.1 · The bare gallows is a line-start form.** A word that starts directly with a gallows (without `o-`, `qo-`, `y-`, `l-`) is the first of the line 22.6% of the time, against 7.8% in the interior and 7.6% in the last word: it joins `d-/s-/y-` (R4.2) as a start form. System.

**R14.2 · Closure is a matter of position, not of margin (corrected on 28/09 with coordinates).** The last word of the last line of the paragraph closes less (17% against 27%; `-m` 9% against 17%) and is longer (5.16 against 4.75). The first version of this rule attributed this to not reaching the margin, with an indirect indicator (words in the line relative to the median). **Measured physically, this is not so**: the last line closes less even when it reaches the margin (13%, n = 69), and non-final lines close the same whether or not they reach the margin. The last line of the paragraph is a position of its own with less closure. System. [H10; `coordenades/REGLES_DE_LLOC.md` §A]

**R14.3 · The second word is the shortest and the least prefixed.** Length 4.61 (first 5.26, rest 4.7-4.8); `d/s/y-` 9% (first 40%, interior 13%); `-y` 45.5% (first 35%). It does not depend on whether the first word carries a prefix (10% against 9%). `q-` peaks at the third word (21.5%). System.

**R14.4 · Dissimilation is only vertical.** Two consecutive words of the same line share the initial glyph slightly **more** than chance (ratio 1.04, z +3), as well as the final glyph (1.03, z +4.5) and the first two glyphs (1.08, z +4.5): horizontally, neighbours attract each other (R2.8, contagion); vertically, the first glyph is avoided (R4.5, ratio 0.60).

**R14.5 · Length belongs to the line.** If the first word is long (≥ 6), the second is 4.88; if it is short (≤ 4), 4.26. Habit.

**R14.6 · Words per line by section** (intermediate lines): herbal 6.9, biological 8.1, stars 10.3, pharmaceutical 10.1, text-only pages 10.0. This is the width the drawings leave, not a writing rule.

**R14.7 · Words that start with a gallows come in lines** (20/10/2026, after a remark by dashstofsk on voynich.ninja). Leaving out the first word of the line (R5.1, R14.1), 5.1% of the words start directly with `t`, `k`, `p` or `f`. After one of them, the next word is one too 1.45 times more often than chance. Shuffling the words within each line leaves it at 1.46; shuffling within the page brings it to 1.16; shuffling the whole text, to 1.0. So it is not one word calling the next: some lines are full of these words and others have almost none, a little more on some pages than on others. It holds in the first lines of paragraphs (×1.35) and in the other lines (×1.43). It does not appear if a "gallows word" is any word containing a gallows (×1.06, the same in the skribe), nor for gallows right after a prefix (`qok-`, `ot-`: ×1.05). The words that start with a bench gallows (`cth-`, `ckh-`) cluster much more (×3.3), but that is section, not line: 8.3% of the words in herbal A, 0.5% in the B sections, and ×1.5 within each language; it is a different habit (×1.08 between the two kinds) and the skribe does not reproduce it yet (×2.4). Habit (of line and page). [`scribe/SCRIBE.md` §10]

**R14.8 · The last line of the paragraph has a register of its own too** (27/10/2026, glyph-pair scan, `scribe/pairs/`). Leaving out the first word: `q-` after `-y` before `o` (R3.3) 0.49 against 0.61 in the other lines, in every hand (hand 1 0.33 against 0.55, hand 2 0.51 against 0.64, hand 3 0.51 against 0.59); and words starting with `ch` 23.9% against 19.0%. With R14.2 (the last word of the paragraph closes less), the paragraph ends with less `q`, the glyph of going on, and more bench words. System in the direction, habit in the strength. [`scribe/SCRIBE.md` §13]

---

## 15 · Rules of place with coordinates (28/09; `coordenades/REGLES_DE_LLOC.md`)

**R15.1 · The skribe does not squeeze the lettering to reach the margin.** Lines that reach the right margin are no denser than those that fall short (1.66 against 1.66-1.75 glyphs per unit of line spacing). With R4.3 corrected: no sign of planning the line end for space.

**R15.2 · Letter size belongs to the sheet** (see R7.4). Line spacing follows it.

## 16 · The rulebook as a procedure: the skribe (28/09; `scribe/SCRIBE.md`)

A synthetic skribe that follows this rulebook, with the strengths estimated from the text, writes a manuscript with the same layout that reproduces **53 of 57 measures** (median error 7.4%; the night generator, 32 of 57 and 21%). Trained only on the odd folios, it reproduces the even ones in 48 of 56 (7.7%), almost as well as one real half reproduces the other (51 of 56, 6.6%). Removing any rule loses measures (up to 10 without copying and 6 without the boundary agreement). Rules that had to be added or refined relative to this rulebook:

**R16.1 · The strength of the closure depends on the hand and on the number of words in the line** (hand 1: from 0.14 with 2-5 words to 0.35 with 12 or more; hand 3: from 0.31 to 0.40), not on physical space (R14.2). This is not enough to fully reproduce the relation with line length. **Corrected on 14/10 (J1):** within each hand and section, the number of words adds nothing; the difference between word-count bands of the same hand is a composition of sections. In the skribe, what does not fit is the `-m` on short non-final lines (11% against 6% real).
**R16.2 · The last word of the line has a repertoire of its own**, besides the closure (A4): written with the interior table, it comes out with too little `-m`.
**R16.3 · Repetition of the previous word depends on the family** (bench+`o`+`l`/`r` ×3.2; gallows+`e`+`(d)y` ×1.5; `-aiin` and bench+`e`+`y` ≤ ×0.8), and also on the particular word (`dal`, `shey`, `saiin` are never repeated; `okaiin` ×5), which the skribe does not yet do: a per-word propensity estimated from the text and shrunk towards that of its family does not improve the measure (14/10, `scribe/SCRIBE.md` §6.3).
**R16.4 · Closure is also a page habit**: some pages (f3r) carry `-m` even in the interior of the line. The skribe does not do this.
**R16.5 · Copying comes from the whole page, with a preference for what is near**, not from the two previous lines: 35% of the words, with a reach of about four lines and one glyph changed in 45% of them. It is the quantitative form of A1 and R7.1.
**R16.7 · The word family is also habit** (14/10, J7). Like the four free choices of R7.2, the choice between the block with `e` (`-y/-dy`) and the block without (`-aiin/-ar/-ol`) has a sheet rate and a page rate, and a stable section shift (herbal towards `-aiin`, biological and pharmaceutical towards `e`; the pharmaceutical, in addition, towards `-y` more than `-dy`). Habit.
**R16.6 · Modified copying is also written by the hand** (14/10, J4). The glyph that is changed, added or removed when copying a word must be writable after the two previous glyphs (≥3 times in the text in that context), like any new word (R17.3). Without this condition, 36% of the modified copies come out with a glyph sequence that the manuscript does not have, and the page looks fake (8.7% strange words against 4.6% real); with it, 4.1%. No repertoire of whole words is needed: a repertoire fixes the eye but removes variety and measures.

## 17 · The ductus: what the glyph grammar is made of (28/09; `ductus/DUCTUS.md`)

**R17.1 · Eight functional letters.** For contact between glyphs, the Voynich has 8 classes: `o`, `a`, `i`, `d`, `q` (on their own), E (`e` and the benches, with and without gallows), K (the gallows) and T (the terminals `y n m g l r s`). With 8 classes the entropy of the next glyph is 2.33 bits against 2.24 with the 22 glyphs; with 12 (separating `l`, `r`/`s`, `p`/`f`, `ch`/`sh` from `e`), 2.25. Which glyph is chosen within the class does not affect what comes next: that is allography (R1.2) and the habit of the sheet (R7.2).
**R17.2 · Thirty-five transitions.** With a memory of one glyph, 35 transitions between classes have ≥ 1% of the mass (23 cover 95%): T → end; E → E, `o`, T, `d`; `o` → K, T, `d`; K → E, `a`, `o`; `a` → `i`, T; `i` → T, `i`; `d` → T, `a`; `q` → `o`.
**R17.3 · The memory of two is the slot.** What a memory of two classes adds (0.65 bits per glyph) is almost all in five places: the first glyph of the word is a prefix (an initial T wants K or E), `qo-` wants a gallows, two `e` close, two `i` close, and `o` after the core is terminal. This is the prefix · core · run · ending template of R2.1.
**R17.4 · The boundary agreement is the final stroke.** The stroke with which the previous word ends (tail down, tail up, flourish, loop) explains 91% of what the whole glyph explains about the prefix of the next word; random classes of glyphs explain nothing. It refines R3.3: what counts is the gesture with which the pen finishes.
**R17.5 · Contact within the word is not kinematic.** The final stroke explains only 45% of the 93 prohibitions between glyphs (`ki` forbidden, `or` allowed, same junction): what rules is the class (gallows and bench want `e`/`a`/`o`/`y`). A syllabic template, not ergonomics.
**R17.6 · The skribe writes with the ductus.** With 8 classes and a memory of two (90 transitions), the skribe reproduces 49 of 57 measures (median error 0.081) against 53 (0.074) with the full table of 22 glyphs. It loses only measures of repetition of particular words. With a memory of one, 35 of 57: without the slot the words come out malformed.

---

## 12 · What the rules do not say

- No rule decides the next word beyond the contact glyph: there is no sentence. [R3.5]
- No rule carries measurable content: the residue of the free choices is a coin toss with a page rate; a message that imitated the coins would fit in it (≤ 6.6 KB of blind capacity) and could not be seen. There is no sign of one. [H3, H4, D1]
- No rule states the intention. [D6]
