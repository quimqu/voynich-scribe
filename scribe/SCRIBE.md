# The skribe: how the Voynich is written, as a procedure

> **26/10/2026, afternoon:** battery of 82 measures (4 new ones on the first line of the paragraph). The skribe now writes the first line in its own register (sh over ch, t over k, rarer words, fewer ee), calibrated on the odd folios only, and no longer needs the rule against repeating on the first line: **78/82, median error 0.060**; on the even folios **69/82 (0.068)**, against 65/82 (0.089) without the register and 73/82 (0.049) between the real halves. No rule broke. See §11.
>
> **26/10/2026:** battery of 78 measures (2 new ones on words that start with a gallows). The skribe now has a line habit for these words, calibrated on the odd folios only: **70/78, median error 0.065**; on the even folios 64/78 (without the habit, 63/78). All the rules were removed one at a time with and without the new habit: none of them changed. See §10.
>
> **19/10/2026:** battery of 76 measures (12 new ones: entropies, Zipf, lengths, long range between pages, bursts). The skribe now has glyph tables per hand and per hand × section and length weights per position, and copies 22% of the words (before: 35%): **69/76, median error 0.05–0.07** (the skribe of 14/10: 69/76, 0.098). See §9.
>
> **14/10/2026:** the battery had a loading error (words with a ligature were lost); the skribe now has form memory in the modified copies (§6) and a word-family habit per sheet and section (§7). Current figures: **58/64 measures, 4.1% strange words (real 4.6%)**. The figures in §1–§5 are those of 28/09.

*28/09/2026. Acid test of the rules (`../RULES.md`): if the rules are good, a skribe who follows them must write a text that cannot be told apart from the Voynich in everything we know how to measure. The skribe writes a whole manuscript with the same layout as the real one (pages, sheets, paragraphs, lines, words per line, drawing gaps, Currier language A/B, hands) and is compared with the real one on 57 measures.*

Files: `scribe.py` (the skribe), `measures.py` (the battery), `compare.py` (comparison and ablations), `holdout.py` (generalisation), `tune_copy.py` and `calibrate_families.py` (calibration), `results_holdout_table.txt`, `results_table.txt`, `results_ablations_table.txt`, `results*.json`, `sample_pages.txt` (pages written by the skribe next to the real ones).

```bash
cd voynich-scribe/scribe
PYTHONIOENCODING=utf-8 py -3 measures.py          # measures of the real text → measures_real.json
PYTHONIOENCODING=utf-8 py -3 compare.py          # real, night generator and skribe (5 seeds)
PYTHONIOENCODING=utf-8 py -3 compare.py ablations
PYTHONIOENCODING=utf-8 py -3 holdout.py         # learned from the odd folios, writes the even ones
```

---

## 1 · The procedure (what the skribe does, in the order in which it does it)

For each sheet, and within the sheet for each page, each paragraph and each line:

1. **Choose the habit of the sheet.** Each sheet has its own rate for four free choices: `t` or `k`, `sh` or `ch`, writing `q-` or not, `-dy` or `-y`. Each page of the sheet resembles it, with a small variation of its own. Within the paragraph, the rate drifts a little from line to line (R7.2, H2, H4, H11).
2. **Choose the language.** A and B use the same glyph contact table with different weights (R7.3).
3. **Choose the tone of the line**: this line will have words a little longer or a little shorter than the average (R14.5).
4. **For each word**, decide whether to **copy** or **write anew**:
   - **Copy** 35% of the time (only 3.5% on the first line of the paragraph). Choose the model among all the words already written on the page, with a preference for the nearby ones (the weight halves every three lines or so), a bonus for the word just above, and a preference for the words that fit the boundary. The immediately preceding word is repeated according to its family: a lot for bench + `o` + `l`/`r` (`chol`), fairly often for gallows + `e` + `(d)y` (`qokedy`), little for `-aiin` and for bench + `e` + `y` (A1, R2.8, R7.1, R9.2).
     - 45% of the copies (always, on the first line) **change one glyph**: substitution, insertion or deletion, with the frequencies of the real pairs of neighbouring words.
     - If the copy has changed, **choose the prefix again** according to the boundary (R3.3).
     - If the model was closed and goes to the interior of the line, open it in half of the cases (R4.3). If it has `p`/`f` and is not on the first line, turn them into `k`/`t` (R1.3). If it comes just after a drawing gap, remove its `q-` (R6.1).
   - **Write anew**, glyph by glyph, with the contact table: each glyph depends on the two previous ones, and the first two of the word also depend on the last glyph of the previous word (R13, R3.3). The table has four start contexts: start of line, start of paragraph, after a drawing gap, and after another word (R4.2, R5.1, R6.1). The habit of the sheet shifts the four free choices. The word is accepted only if:
     - it fits the slot template (R2.1);
     - it does not have two gallows (55% of these are rejected, R2.2);
     - it does not have `e` and `i` at the same time (45% of these are rejected, R13.7).
     
     Five candidates are made and one is chosen according to the length tone of the line. **The last word of the line** is written with a table of its own, learned from the real last words with the closure undone (A4).
5. **First word of each interior line**: if it starts with the same glyph as the line above, it is written again with a probability that depends on the glyph. Always with `ch`, two times out of three with `o` or `q`, half of the time with a gallows, almost never with `s` (R4.5, H8).
6. **First line of a paragraph**: hardly ever copies, avoids repeating the previous word, and changes `k`/`t` into `p`/`f` in 30% of the words (R1.3, R5.2).
7. **Close the last word** of the line with the strength of its hand and according to how many words the line has: `-iin` → `-m`, `-in` → `-m`, `-l` → `-ly`, `-r` → `-ry`, `-s` → `-sy`, `-y` → `-g`. The last word of a paragraph is closed less. **The word before a drawing gap** is closed with a lower strength (R4.3, R14.2, R6.1).

### The strengths, estimated from the real text

| rule | values |
|---|---|
| closure, non-final line | `iin`→`m` 0.60 · `in`→`m` 0.52 · `l`→`ly` 0.21 · `r`→`ry` 0.26 · `s`→`sy` 0.14 · `y`→`g` 0.06 |
| closure, end of paragraph | `iin`→`m` 0.32 · `l`→`ly` 0.25 · `r`→`ry` 0.22 · `s`→`sy` 0.18 |
| closure, before the drawing gap | `iin`→`m` 0.15 · `l`→`ly` 0.16 · `r`→`ry` 0.17 · `s`→`sy` 0.20 |
| closure per hand (`iin`→`m`) | hand 1 0.29 · hand 2 0.64 · hand 3 0.88 |
| avoidance of the first glyph of the line above | `ch` 1.0 · `o` 0.67 · `q` 0.65 · gallows 0.52 · `l` 0.40 · `sh` 0.38 · `d` 0.37 · `y` 0.28 · `s` 0 |
| repetition of the previous word by family | bench+`o`+`l`/`r` ×3.2 · gallows+`e`+`(d)y` ×1.5 · others ×0.8 · `-aiin` ×0.8 · bench+`e`+`y` ×0.55 |
| copying | 35% of the words; 45% with one glyph changed; range ~4 lines; 3.5% on the first line |
| habit of the sheet and the page | deviation 0.45 in log-odds per sheet and 0.45 per page; line drift 0.25 with memory 0.6 |

Everything that is not in the table (the contact table, the line-end table, the edits, the boundary) is learned from the real text. They are large tables. **It is not a ten-line rulebook**: it is a seven-step procedure with a learned local grammar.

## 2 · What it reproduces

57 measures: the 27 of the night generator's battery (`../night_generator/generator.py`) and 30 new ones, one per rule of the rulebook. A measure is considered reproduced if it stays within 25% of the real value (mean of 5 seeds).

| | night generator | **skribe** |
|---|---|---|
| measures reproduced | 32 / 57 | **53 / 57** |
| of the night generator's battery | 18 / 27 | **25 / 27** |
| median error \|log(gen/real)\| | 0.193 (≈ 21%) | **0.074 (≈ 8%)** |

Key measures (real / night / skribe): adjacent repetition over chance 3.09 / 2.91 / 3.33 · repetition at distance 2 3.66 / 2.52 / 3.07 · frequent words repeated more than ×3: 52% / 32% / 41% · `-m` on the last word 15.9% / 9.1% / 16.9% · closed forms on the last word 27.1% / 11.5% / 27.7% · gallows on the first word of a paragraph 93% / 54% / 92% · `p`/`f` on the first line 30.7% / 9.5% / 31.9% · `d/s/y-` after the drawing gap 42% / 13% / 38% · page overdispersion of `q-` 6.3 / 1.3 / 5.6 · word types 7,697 / 10,284 / 7,784 · words with a twin on the page 65% / 61% / 67%.

`sample_pages.txt` has three pages written by the skribe next to the real ones.

## 3 · Which rules are needed (ablations)

Removing each rule one at a time (5 seeds; the measures of `q-` after the drawing gap and on the first word of a paragraph are at the threshold and change by chance, and are not taken into account):

| rule removed | reproduced | what is lost |
|---|---|---|
| — | 53 | |
| copying from the visible field | 43 | all the repetition measures |
| boundary rule | 47 | mutual information at the boundary and the four *lifts*; the median error goes from 0.074 to 0.110 |
| start contexts | 47 | line-start and paragraph-start forms, `a-` at the start, form after the drawing gap |
| first line | 48 | `p`/`f`, fewer repetitions on the first line |
| line length tone | 49 | length correlation between neighbours |
| word rules / slot template | 49 | two gallows, `e`/`i`, length dispersion |
| dissimilation | 49 | first glyph of the line above |
| habit of the sheet / A/B weights | 50 | page overdispersion |
| line-end repertoire / closure | 50–52 | `-m` and closed forms on the last word |
| repetition by family | 52 | adjacent repetition |

## 4 · What it does not reproduce, and the rules that must be missing

1. **Half of the frequent words repeat a lot, and 16% avoid it**: the skribe does 41% and 23%. The propensity by family explains it in part (G7). The rest is word-specific: in the real text, `dal`, `shey`, `saiin`, `cheey` or `qokar` never repeat adjacently, and `okaiin` does so ×5. **Missing rule**: a propensity to repetition per word, finer than the family.
2. **The `-m` according to the length of the line**: in the real text, lines of ten words or more end in `-m` 3.5 times more often than those of one to four; in the skribe, 2.0. The strength of the closure already depends on the number of words, but it is not enough. Besides, **on some pages `-m` is a page habit, also in the interior of the line**: the real f3r has `cham`, `chom`, `cthom`, `shom` in mid-text. **Missing rule**: the closure as a fifth page habit.
3. **End of paragraph and word before the drawing gap** are closed 25–30% too much. These are strength adjustments, not new rules.

## 5 · What it means

- **The Voynich can be written with a seven-step procedure**, without any level of meaning: glyphs with a memory of two and a boundary between words, copying of what is already on the page, position forms (start, end, first line, drawing gap), and a sheet habit that keeps changing. With this, 53 of the 57 measures are reproduced, almost all of those the programme had used to say that the text is *not* language nor cipher.
- **All the rules are needed**: removing any of them loses between 1 and 10 measures.
- **It generalises (`holdout.py`)**: learned only from the odd folios, the skribe writes the layout of the even folios and is compared with the real even ones. 48 of 56 measures come out reproduced, with a median error of 7.7%. As a reference, the two real halves resemble each other in 51 of 56 measures, with 6.6% (the sheet measure is not counted, because with half a manuscript the conjugate folio often falls in the other half). Four of the eight failures of the skribe also appear between the two real halves: they are unstable measures. The skribe's own ones are adjacent repetition, repetition at distance 3, the `-m` according to the length of the line and the closure before the drawing gap. **The rules do not memorise the text: they describe how it is made.**
- **Honest limit**: the skribe uses tables learned from the text: the glyph contact table, the line-end table, the boundary table and the edits. The procedure says how the pieces are combined, not where the contact table comes from. That table is the "glyph grammar" of the manuscript (R13), and reducing it to a few rules is the job of the rulebook (§13), not of the skribe.

---

## 6 · Form memory (14/10/2026)

*Point 2 of ESTAT_DEL_PROGRAMA.md §6. Scripts: `form_memory.py` (exploration), `strange_words_diagnosis.py` (where the strange words come from). Outputs: `results_form_memory.json`, `strange_words_diagnosis_out.txt`, and the tables `results_table.txt`, `results_ablations_table.txt` and `results_holdout_table.txt` redone with the new default value.*

### 6.1 · First of all: an error in the loading of the real text

`measures.clean()` was supposed to keep the content of the ligatures `{…}`, but the substitution had a byte `\x01` instead of `\1`. Words with a ligature were lost whole: 394 groups in 359 lines. Fixed. `measures_real.json` now has 59 measures (the 57 plus the two `[eye]` ones). What changes most are the noisy measures of repetition at a distance (k=2: 3.66 → 3.27; k=3: 2.80 → 3.45). **The eye figures given before (7.9% real, 11.2% skribe) came from a different loading and cannot be compared.** With the corrected loading: **real 4.6%, previous skribe 8.7%**. The previous skribe, measured again, reproduces 51 of 59.

### 6.2 · Where the strange words come from

A word is strange if it has some glyph trigram (with start and end of word) that appears 3 times or fewer in the real text. Previous skribe, seed 1:

| origin | words produced | strange |
|---|---|---|
| new word, glyph by glyph (each candidate) | 107,038 | 2.4% |
| new line-end word (each candidate) | 14,755 | 4.9% |
| **copy with one glyph changed** | 3,642 | **36%** |
| line-end closure (new strange words it creates) | 1,078 | 8.6% |

The main source is the edit of the copy: it changes, inserts or removes a glyph **without looking at the neighbours** (`daiin→daain`, `chedy→chddy`, `ol→oo`). The new words, which the skribe already writes with a memory of two glyphs (R17.3), hardly produce any. With form memory, the strange modified copies go from 36% to 1.7%.

### 6.3 · What was tried (2–3 seeds for the exploration, 5 for the result)

| variant | reproduced | strange words | word types |
|---|---|---|---|
| previous skribe | 53/59 | 8.5% | 7,775 |
| the modified copy goes to a neighbour in the repertoire (known word, one glyph away) | 50–52/59 | 4.2–4.3% | 6,350–6,490 |
| + redo the unknown new words (50% / 80%) | 45 / 43 | 2.9 / 2.2% | 4,710 / 3,350 |
| **the edit must be writable: each glyph possible (≥3 times) after the two previous ones** | **54–55/59** | **4.0–4.1%** | 7,120–7,190 |
| writable with ≥1 time | 48/59 | 5.9% | 7,380 |
| writable + propensity to repetition per word | 50–52/59 | 3.9–4.1% | 7,000–7,130 |
| writable + repertoire in half of the copies | 49–51/59 | 4.0% | 6,860 |

- **The repertoire of whole words is not the answer.** It fixes the eye, but the skribe loses variety (word types −18%) and repetition measures. In the real text, a one-glyph variant of a word on the page is often a new word (hapax), not a known one. Redoing the new words that are not known is even worse (43–45/59).
- **The answer is that the edit is also written by the hand.** The skribe copies the word and changes one glyph, but the change must be writable with the same two-glyph memory with which it writes the new words. It is rule R17.3 applied to the copies as well; no new rule is needed. If no writable edit comes out in 30 attempts, the copy stays intact.
- **The propensity to repetition per word** (observed over expected on the page, shrunk towards that of the family) does not improve `Frequent words repeated <0.3x chance`: 22–30% with this piece, against 16% real and 22–25% without it. Negative result. It stays off (`use_wordrep`).
- **End-of-paragraph closure per hand** (`par_by_hand`, for J1): no measurable effect. Off.

### 6.4 · Result (5 seeds, new default value: `mod_contact=3`, `mod_tries=30`)

| | before (corrected loading) | **with form memory** | real |
|---|---|---|---|
| measures reproduced | 51/59 | **54/59** | |
| of the 57 original ones | 51/57 | **52/57** | |
| median error | 0.061 | 0.064 | |
| strange words | 8.7% | **4.1%** | 4.6% |
| strange words per line | 0.68 | **0.32** | 0.36 |
| word types | 7,859 | 7,150 | 7,915 |

- **Ablation** (`compare.py ablations`): without form memory, 51/59 and 8.7% strange words. All the pieces are still needed: removing any of them costs 1 to 9 measures.
- **Generalisation** (`holdout.py`): the contact table that decides what is writable is learned only from the odd folios, and on the even ones the result is 0.31 strange words per line against 0.35 real. Form memory is not memory of the test text. In total, 47/59 (median error 0.101) against 50/59 (0.066) between the two real halves.
- **What it still does not reproduce**: `Consecutive words at edit distance 1 / shuffled` (1.59 against 2.21: the neighbours one glyph apart), `Frequent words repeated <0.3x chance` (24% against 16%), `Line-end -m: lines of 10+ words / 1-4 words` (1.94 against 3.41) and `q-` on the first word of a paragraph and closure of the last word of a paragraph (at the threshold). For the `-m`, the cause is now located: on short **non-final** lines, the skribe closes in `-m` 11% of the time and the real text 6%. According to J1 (the strength of the closure is a matter of hand and section), the section is missing.

**Reading.** The eye did not ask for a dictionary. It asked for the hand to be the same when it copies and when it writes anew: everything that comes out of the pen, including the variant of a copied word, goes through the two-glyph memory. With this, the skribe makes as many strange words as the real text or fewer. The "form memory" of R16.3 (which words exist as units for the hand) **is not needed for the eye**. If it exists, it has to be looked for in what still fails: repetition per word and the neighbours one glyph apart.

---

## 7 · Page vocabulary: the "e" habit and the section "dy" (14/10/2026, afternoon)

*Scripts: `page_vocabulary.py` (exploration), `calibrate_section_e.py` (shifts per section → `sec_e.json`, `sec_dy.json`, and `*_odd.json` for `holdout.py`), `sample_form_memory.py` (samples of four versions → `sample_form_memory.txt`).*

### 7.1 · What could be seen by eye and the battery did not measure

In the samples, the real f78r is monotonous in `-edy` (`qokedy` ×15) and the skribe's was monotonous in `qokaiin` (×15). The battery now has five new measures (64 in total):

| measure | real | skribe §6 | **current** |
|---|---|---|---|
| page overdispersion of the words with `e` | 24.6 | 9.0 | **20.3** |
| words with `e`, biological / herbal | 2.04 | 1.51 | **1.84** |
| `-edy` words in the biological section | 27.5% | 17.9% | **22.7%** |
| share of the page's most frequent word (median) | 4.7% | 4.7% | 4.9% |
| words of 8 glyphs or more | 5.3% | 7.3% | 7.4% |

- **Page monotony was already good** (the share of the most frequent word matches): what failed was *which* word family dominates each page and each section.
- **Long words have the same structure as the real ones** (gallows 0/1/2+: 20/69/12% against 20/62/18%; `qokeeedy`, `cheodaiin`, `qokeeody`), but there are a third too many of them. It comes from the choice of the "length tone" (the best of 5 candidates), which inflates the tails: the candidates have 5% of them. The edits have nothing to do with it (295 out of 2,295).

### 7.2 · What was added

1. **`e` habit** (`use_ehabit`): a fifth free choice, the `e` after the core (bench or gallows), that is, the word block with `e` (`-y/-dy`) or without (`-aiin/-ar/-ol`) of R2.4. It varies per sheet, page and line like the other four (σ 0.45; its own random generator, so that the rest of the skribe does not change).
2. **Shift per section** of the `e` habit and of the `dy` habit (`-dy` or `-y`), calibrated so that the proportion of each section matches the real one. Values (whole text / odd folios only): `e` herbal −0.41/−0.40, biological +0.36/+0.44, stars +0.37/+0.37, pharmaceutical +1.55/+1.23; `dy` pharmaceutical +2.3/+2.1, biological +0.47/+0.45, stars −0.38/−0.46. **They are stable between halves**: it is a section habit, not noise. Where the skribe was most wrong was the pharmaceutical section: 26% of words with `e` against 47%.

They are parameters fitted to the text (11 in total), like the strengths of §1. What they say is that **the sections are distinguished by the word family that dominates in them**, besides the language and the hand (H2, H4).

### 7.3 · Result (5 seeds)

| | skribe §6 | **current** |
|---|---|---|
| measures reproduced | 55/64 | **58/64** |
| generalisation (learned from the odd folios, on the even ones; real halves 55/64) | 47/59 (with 59 measures) | **51/64** |
| strange words | 4.1% | 4.1% |

- **Ablation**: without the `e` habit, 52/64 and overdispersion 8.9. Without the section `dy`, also 58/64: the `-edy` of the biological section and the closure before a drawing are lost, and two measures that were already unstable are gained (`repetition k=5`, `q-` on the first word of a paragraph). It is kept.
- **Generalisation**: the five new page and section measures are reproduced on the even folios with parameters learned from the odd ones. Only the long-words one fails there.
- The median error (0.07–0.09 depending on the calibration) is not a stable figure: some twenty measures have errors between 0.07 and 0.10 and the median jumps around there.

### 7.4 · What remains

- **Long words** (7.4% against 5.3%). Softening the length tone (4 candidates, σ 0.45) brings them down to 6.3%, but the skribe loses variety (−13% word types) and the length correlation between neighbours. Not applied. A length tone that does not inflate the tails is needed.
- **Words that look ugly to the eye** and that no measure catches: `shedytedy`, `qokaiinsh`, `doraiiny`, `keeyl`. They are concatenations of two word blocks, each one normal. A possible measure: "words that contain two endings".
- The failures from before: `quasi(ed=1)`, `rep <0.3x`, the `-m` of short non-final lines.

---

## 8 · Forum questions (19/10/2026)

### 8.1 · A whole quire (`quire.py`)

```bash
PYTHONIOENCODING=utf-8 py -3 quire.py M 1                         # learned from the whole manuscript
SCRIBE_TRAIN=without_M PYTHONIOENCODING=utf-8 py -3 quire.py M 1   # without having seen quire M (before: calibrate_section_e.py with the same variable)
```

It writes the whole manuscript and extracts the quire from it, so that the sheet habits and the copying work as usual. Format similar to IVTFF, with the ZL3b line identifiers, `<->` at the drawing gaps (copied from the real layout; the skribe does not look at the images) and `<%>`/`<$>` at the paragraphs. It also saves the real text normalised the same way. Done for quire 13 (`quire_M/`, with `README.txt` in English); findings log L1.

`SCRIBE_TRAIN=without_<Q>` (for example `without_M`, or `without_M+N`) removes the quires from the learning. `measures.load_real()` now carries `quire` and `locus` on each line.

### 8.2 · Standard measures (`standard_measures.py`, `standard_measures_out.txt`)

| | real | skribe |
|---|---|---|
| h1 / h2 / h3 (bits per character, space included) | 3.88 / 2.12 / 1.85 | 3.86 / 2.09 / 1.84 |
| Zipf slope (ranks 1–1000) | 1.00 | 1.00 |
| MATTR (window of 500 words) | 0.64 | 0.60 |
| bursts of the 50 most frequent words (coefficient of variation of the gaps) | 1.76 | 1.51 |
| vocabulary similarity between pages at distance 1 / 10 / 100 | 0.35 / 0.26 / 0.17 | 0.29 / 0.24 / 0.19 |

The entropies and Zipf match. The long range does not: in the manuscript there is a vocabulary drift between neighbouring pages that the skribe does not produce (findings log L2).

### 8.3 · Control with known meaning (`controls/`)

See `controls/CONTROLS.md`. The generic skribe applied to the Latin of Cusanus fails where a language fails (7/16 against a ceiling of 13/16), and the battery detects it. To do it with another text:

```bash
PYTHONIOENCODING=utf-8 py -3 controls/control.py prepara <text.txt> <name>
PYTHONIOENCODING=utf-8 py -3 controls/control.py corre <name>
PYTHONIOENCODING=utf-8 py -3 controls/control.py informe voynich <name>
```

`SCRIBE_CORPUS=<file.json>` makes the skribe learn from that text instead of the Voynich. With `measures.set_reference(L)`, the measures that look at the whole real text (the rare trigrams) look at the control text instead.


---

## 9 · Long range, lengths and the vocabulary of each hand (19/10/2026)

*Continuation of §8.2 (findings log L2 → L5): the vocabulary drift between pages that the skribe did not produce. The 12 new measures have been put inside the battery (`measures.py`), with their own definitions; the values differ a little from those of `standard_measures.py`. Scripts: `measures.py` (part 5, 12 new measures), `scribe.py` (tables per hand and per hand × section, length weights), `calibrate_length.py` (→ `len_w.json`, `len_w_odd.json`), `holdout.py` (now accepts `key=value`). Tables: `results_table.txt`, `results_holdout_table.txt`, `results_ablations_19_10_table.txt`.*

### 9.1 · The new measures (battery of 76)

| measure | real | skribe 14/10 |
|---|---|---|
| character entropy h1 / h2 / h3 (line text, with spaces) | 3.91 / 2.14 / 1.86 | 3.89 / 2.11 / 1.84 |
| Zipf slope (first 1,000) | 1.00 | 1.00 |
| words of 2–3 glyphs / of 5–6 glyphs | 21.6% / 41.0% | 28.8% / 33.2% |
| shared vocabulary (cosine): neighbouring pages, 10 apart, 100 apart | 0.33 / 0.25 / 0.155 | 0.27 / 0.22 / 0.163 |
| neighbouring / 100 pages apart | 2.13 | 1.65 |
| bursts of the 50 most frequent words (CV of the gaps) | 1.76 | 1.51 |
| page overdispersion of the 50 most frequent words | 2.06 | 1.87 |

The entropies and Zipf already matched. What failed were the lengths (too many short words: the two-glyph memory makes lengths that are too dispersed; `ol` 2.4 times too many) and the long range: neighbouring pages resemble each other less than in the real text and distant ones more.

### 9.2 · Where the similarity between pages comes from

Decomposition (vocabulary cosine, real / skribe 14/10): same hand and section at 2–10 pages 0.336 / 0.293; different hands at 50–150 pages 0.159 / 0.187; same hand at 50–150 pages 0.231 / 0.221. **It is not the continuity between pages: it is the vocabulary of each hand** (and of each section within the hand), which the skribe did not have because it learned the glyph table per Currier language A/B. It agrees with Schwartz 2026 (the word cores are hardly shared between hands).

Mechanisms tried and discarded (2–3 seeds): copying from the previous pages of the book (it flattens the whole curve, also at 100 pages, and lowers the bursts; 51–53/64); copying from the pages already written on the same sheet (the same); reusing words from the repertoire of the last pages instead of inventing them (it improves the neighbouring page a little and loses measures). They stay in the code, switched off (`r_prev`, `r_sheet`, `r_stock`).

### 9.3 · What was changed

1. **Glyph tables per hand and per hand × section** (`use_hand_tab`, `use_sec_tab`): counts of the hand (or of the hand within the section, if there are ≥40 lines) plus 3 pseudocounts distributed according to the table of the language (or of the hand). With this, the section tone is already there, and the section shifts of 14/10 (`use_sec_e`, `use_sec_dy`) were being counted twice (`-edy` in the biological section 34.7% against 27.5%): they are switched off.
2. **Length of the new word by position in the line** (`use_len_w`): the choice among the five candidates is weighted by length, with weights for the first word, the interior and the last one, calibrated in three passes so that the distribution of the whole text (copies included) matches the real one.
3. **Readjusted strengths**: copy 35% → **22%**, repetition of the previous word by family 0.8 → 0.5, sheet habit σ 0.45 → 0.3, rejection of two gallows 0.55 → 0.35 and of `e`+`i` 0.45 → 0.25, closure before the drawing gap ×0.75 and at the end of a paragraph ×0.75 (`par_scale`, new).

**Reading of the 22%.** With a vocabulary of its own for each hand, the words already repeat more by themselves (repetition at 2 and at 5 words: 4.6 and 5.0 times chance with copying at 35%, against 3.3 and 2.9 in the real text). Part of what looked like copying was the vocabulary of the hand. It is the same thing Schwartz finds: a lot of reuse of one's own repertoire and little recent copying.

### 9.4 · Result (5 seeds, 76 measures)

| version | reproduced | median error | learned from the odd folios, on the even ones (real halves 67/76) |
|---|---|---|---|
| skribe of 14/10 | 69/76 | 0.098 | 62/76 (0.080) |
| **skribe of 19/10** | **69/76** | **0.049–0.067** (two runs) | 61/76 (0.080) |
| without tables per hand and section | 68/76 | 0.062 | |
| without length weights | 67/76 | 0.068 | |

*The two ablations, and the first row of the file `results_ablations_19_10_table.txt`, were made with the section shifts of 14/10 still switched on; the row "without section shifts" of that file is the final configuration.*

- **The count does not improve** (the ±25% criterion is already saturated and has noise between seeds), but **the median error halves** and the new measures pass: words of 2–3 glyphs 23.3% (real 21.6%), neighbouring / 100 pages apart 1.84 (2.13), bursts 1.58 (1.76). The skribe of 14/10 failed the words of 2–3 glyphs and the repetition at 5 words.
- **Generalisation**: the same as before (61–62/76). The 8 new length and long-range measures are all reproduced on the even folios with tables learned from the odd ones.
- **Still fails**: `quasi(ed=1)` (the neighbours one glyph apart: with less copying there are fewer of them), the repetition at 3 words (2.5 against 3.4), the frequent words that repeat a lot or not at all (word-specific, not family-specific), the `-m` of long lines, the `q-` on the first word of a paragraph (at the threshold) and, without the section shift, the page overdispersion of the words with `e` (18.4 against 24.6).
- **Honest limit**: the tables per hand and section are more parameters learned from the text (one contact table for each combination with enough lines). What they say is that **each hand, and each hand in each section, has its own glyph grammar**, not only its own tone; they do not say why.

## 10 · Words that start with a gallows come in lines (20/10 and 26/10/2026)

On voynich.ninja, dashstofsk remarked that the skribe's text has more "gallows words" than the manuscript, and that in the manuscript a gallows word follows another more often than if the words were shuffled, more than in the skribe. He did not say what he counted as a gallows word. Only one reading makes both remarks true in quire 13 (small numbers on a single quire: see the note in `quire_M/README.txt`) (the quire published in `quire_M/`): **a word that starts directly with `t`, `k`, `p` or `f`**. There the skribe had more of them (5.8% against 4.6%) and no clustering (×0.94 against ×1.48). With "any word containing a gallows" the skribe has slightly fewer (50% against 53%) and they cluster the same (×1.09 against ×1.06); nablator's autocorrelation on that definition (consecutive word pairs within the line) gives 7.3% in the real ZL3b text and 7.3% in the skribe (7.6% with the habit below).

### 10.1 · Where the clustering comes from

Leaving out the first word of each line (93% of paragraph-initial words carry a gallows, R5.1, and the skribe already gets the line starts right, 82.6% against 82.2% of paragraph first lines and 8.8% against 8.6% of the other lines):

| the real text, words after the first of the line | gallows-initial after another / chance |
|---|---|
| as written | ×1.45 |
| words shuffled within each line | ×1.46 |
| words shuffled within each page | ×1.16 |
| words shuffled over the whole text | ×1.00 |

The order inside the line does not matter: **the line does**. Some lines are full of these words and others have almost none, and some pages a little more than others. It is not the first line of the paragraph (×1.35 there, ×1.43 in the other lines). Rule R14.7.

The words that start with a bench gallows (`cth-`, `ckh-`, `cph-`, `cfh-`) cluster much more (×3.31), but that is section, not line: they are 8.3% of the words in herbal A and 0.5% in the B sections, shuffling within the page does not change it (×3.32), and within each language they cluster like the others (×1.45 in A, ×1.55 in B). They do not go with the plain ones (×1.08). The skribe makes too few of them (2.1% against 2.7%) and does not concentrate them enough (×2.4): **open**, and probably a calibration of the hand × section tables rather than a missing rule.

### 10.2 · What was added

Two measures (`measures.py`, part 6): the share of words starting with a gallows, not line-initial, and their clustering within the line (pairs from the second word on, against the base rate). And one habit (`scribe.py`, `use_g0`): each page draws a value and each line adds its own, independent of the line before; the sum multiplies the weight of `t`/`k`/`p`/`f` as the **first glyph of a new word**, except the first word of the line. Centred, plus a mean shift `g0_mu` (the skribe already made too few of these words: 4.2% against 5.1%). Copied words are not touched: making the habit also choose what is copied was tried and did not do better (10 seeds, within the noise).

The three parameters were calibrated **on the odd folios only** (27 combinations, 3 seeds each, the skribe trained on and writing the odd folios, against the real odd folios: 5.20%, ×1.59): page 0.4, line 0.7, mean shift 0.35. The real odd folios cluster more than the even ones (×1.30), so the habit overshoots on the even folios.

### 10.3 · Result (5 seeds, 78 measures)

| | real | without the habit | **with the habit** |
|---|---|---|---|
| words starting with a gallows, not line-initial | 5.05% | 4.21% | **4.85%** |
| clustering within the line | ×1.45 | ×1.02 | **×1.55** |
| whole text: reproduced / median error | | 70/78 · 0.069 | **70/78 · 0.065** |
| learned from the odd folios, on the even ones | (real halves 69/78 · 0.052) | 63/78 · 0.082 | **64/78 · 0.083** |
| even folios: share / clustering (real 4.91%, ×1.30) | | 4.03%, ×1.20 | 4.72%, ×1.50 |

Files: `results_table.txt`, `results_holdout_table.txt`, `results_holdout_without_g0*.{json,txt}`.

**What this does and does not show.** The habit reproduces what it was made for, and costs nothing that can be measured. It does not improve the battery as a whole: with 10 seeds (an earlier calibration on the whole text), the median error per seed went from 0.065 ± 0.008 to 0.059 ± 0.010 on the whole text and from 0.084 ± 0.008 to 0.091 ± 0.016 on the even folios, both inside the spread between seeds. The finding is the line habit itself, not the score.

### 10.4 · All the rules again (ablations, 5 seeds)

Every rule removed one at a time, **with** the new habit (`results_ablations_table.txt`) and **without** it (`results_ablations_without_g0_table.txt`). Measures lost relative to the full skribe of each column:

| rule removed | without the habit | with the habit |
|---|---|---|
| boundary rule | −11 | −10 |
| copying | −6 | −9 |
| start contexts | −6 | −5 |
| first line | −6 | −6 |
| closure | −6 | −5 |
| dissimilation | −5 | −5 |
| length mode | −5 | −5 |
| slot template | −4 | −5 |
| word rules | −5 | −3 |
| form memory | −4 | −3 |
| sheet style, e habit, end table, reprefix, word family, closure by word count | −1 to −2 | −1 to −2 |
| language tables, section dy | 0 | 0 |
| gallows-initial line habit | | −2 |

**No rule changed with the new habit** (differences of 1 to 3 measures are the usual noise of 5 seeds). Three things the ablations show that were already there before:

- Two switches do nothing: `use_sec_dy` is off by default since 19/10, and the language tables (A/B) are only a fallback since every hand × section has its own table.
- Six rules (length mode, form memory, word rules, word family, reprefix, closure by word count) fix their own measures but **lower** the median error when removed (−0.01 to −0.02, in both columns). They trade the general fit for a specific measure.
- The count of reproduced measures moves by ±2 between runs; it is the median error and the specific measures that tell rules apart.

### 10.5 · Two measures that are mostly noise

- **The repetitions at distance k** (`Same word at distance k / shuffled`) rest on few events (64 repeats at distance 3 in the even folios) and on **one** shuffle for the denominator. Over 100 shuffles the real value at distance 3 ranges from 2.18 to 3.75 (whole text; median 2.98, the battery uses 3.45), and in the even folios from 2.29 to 4.57. Between seeds the skribe moves ±0.4 to ±1.2. A drop of these measures with a new rule is not evidence on its own. They should use the median of many shuffles (not changed yet, so that the battery stays comparable).
- **H8** (same first glyph after a gallows-initial line) fails in this run (0.43 against 0.61), but over 10 seeds it is 0.54 ± 0.13 without the habit and 0.54 ± 0.20 with it (passing 6/10 and 4/10): the habit does not touch the first word of the line, it only shifts the random draws. The same for `a-` at line start (R4.2: about a dozen lines).

## 11 · The register of the first line (26/10/2026)

Looking for word-specific behaviour (does each word have habits of its own beyond its form, as words with a meaning would?), a token-level logistic model (form, gallows, bench, number of `e`, `p`/`f`, prefix, frequency, hand × section, and their pairwise combinations) left no word-specific preference for the first line, the line end, the line start or self-repetition that the skribe does not also produce (odd/even replication of the per-word residual: first line +0.05 real against −0.04 skribe; line end +0.32 against up to +0.30; line start and repetition the same). Negative for word identity. What it turned up instead is that **the first line of the paragraph is written differently, glyph by glyph**, and the skribe did not do it:

| first line / other lines (without the first word) | real | skribe before |
|---|---|---|
| `sh` among `sh`+`ch` | 35.5% / 26.6% (×1.34; every hand ×1.22 to ×1.82) | ×1.04 |
| `t` among `t`+`k` | 43.0% / 34.9% (×1.23) | ×1.00 |
| words among the most frequent (≥ 0.3% of the text) | 23.4% / 35.3% (×0.66) | ×1.17 |
| words with `ee` | 11.5% / 13.3% (×0.87) | ×1.00 |

Rule R5.2 (amended). Four measures were added (`measures.py`, part 7, as first line / other lines ratios).

### 11.1 · What was added

On the first line of the paragraph (`scribe.py`, `use_fl_style`): the style offsets of `t` and `sh` are raised (`fl_t` 0.3, `fl_sh` 0.6) and that of the `e` after the core lowered (`fl_e` −0.6); among the candidate new words, those with a frequency ≥ 0.3% of the training text are disfavoured (`fl_rare` 0.7, weight × e^−0.7). All four calibrated **on the odd folios only** (27 combinations of the first three, then `fl_e`, 3 seeds each; odd folios real ×1.36 / ×1.19 / ×0.67 / ×0.88, skribe ×1.39 / ×1.16 / ×0.69 / ×0.84).

With the register on, the old rule against repeating a word on the first line (`first_norep`, 0.4) made the first line repeat too little (adjacent repeats first line / rest 0.25 against 0.385). Set to 0 it gives 0.32 on the whole text and 0.37 on the even folios (real 0.37): **the low repetition of the first line follows from its rarer words**, and that rule is no longer needed. The measure is very noisy (0.18 to 0.67 between seeds on the odd folios).

### 11.2 · Result (5 seeds, 82 measures)

| | without the register | **with the register** |
|---|---|---|
| whole text: reproduced / median error | 73/82 · 0.066 | **78/82 · 0.060** |
| learned from the odd folios, on the even ones (real halves 73/82 · 0.049) | 65/82 · 0.089 | **69/82 · 0.068** |

The three-rule baseline: 44/82 (0.254). A first run with `first_norep` still at 0.4 gave 75/82 (0.052) and 69/82 (0.074): the median error moves by about ±0.008 between runs. Files: `results_table.txt`, `results_holdout_table.txt`, `results_holdout_without_fl*`.

Still failing: which frequent words avoid repeating (word-specific: §4), the `-m` of long lines, the `q-` on the first word of a paragraph, and the page overdispersion of words with `e`.

### 11.3 · All the rules again (ablations, 5 seeds)

Measures lost when each rule is removed, with the register (`results_ablations_table.txt`) and without it (`results_ablations_without_fl_table.txt`, with `first_norep` at 0.4 as before):

| rule removed | without the register | with the register |
|---|---|---|
| boundary rule | −10 | −13 |
| first line | −8 | −9 |
| copying | −11 | −8 |
| closure | −6 | −7 |
| start contexts | −6 | −6 |
| first-line register (new) | | −6 |
| sheet style | −1 | −5 |
| word rules | −4 | −5 |
| dissimilation, length mode, closure by word count | −3 to −6 | −5 |
| slot template, form memory | −5 to −7 | −4 |
| gallows-initial line habit | −2 | −3 |
| reprefix, e habit, end table | −3 | −1 to −2 |
| word family, language tables, section dy | 0 to −2 | 0 |

**No rule broke.** As before, several rules cost specific measures but lower the median error when removed (closure −0.014, closure by word count −0.013, e habit −0.010, end table −0.008, form memory −0.008): they fix their own measures at the cost of the general fit. (In the first run with the register, with `first_norep` still at 0.4, some of these had turned positive; with the final configuration they did not.) The repetition by word family (`use_famrep`) now costs nothing (0 measures, error −0.010 without it): a candidate for removal, not removed yet.

## 12 · What follows p and f (27/10/2026)

**Question** (voynich.ninja thread 6231). npcompl33t finds that words with `p`/`f` "lag" words with `k`/`t` along his chronological gradient and reads `p`/`f` as an archaic `k`/`t`; Stolfi answers that the puffs are `k`/`t` written fancy on the head line, at random. The skribe did what Stolfi says: on the first line it turned a `k` into `p` (or a `t` into `f`) at random (`p_pf` 0.30).

**What the real text does.** A plain `p`/`f` is never followed by `e`: 5 `pe`/`fe` in the whole text against 3,589 `ke` and 1,431 `te` (benched `cph`/`cfh` do take `e`: 69 `cphe` against 238 `ckhe`). It holds in every section and on every line; it is not a first-line effect, because `k`/`t` on the first line take `e` as often as elsewhere (35% against 34%). Glyph after the gallows, paragraph text:

| | `e` | `ch`/`sh` | `o` | `a` | `y` | n |
|---|---|---|---|---|---|---|
| `k`/`t`, first line | 35% | 18% | 10% | 24% | 10% | 2,512 |
| `p`/`f`, first line | 5% (benched) | 55% | 12% | 13% | 9% | 1,130 |
| `k`/`t`, other lines | 34% | 13% | 9% | 29% | 13% | 13,130 |
| `p`/`f`, other lines | 8% (benched) | 42% | 16% | 19% | 8% | 368 |

`e` + `ch` comes to about the same share after both (52% and 60%): **where `k`/`t` take `e`, `p`/`f` take `ch`**. What follows `pch` matches what follows `ke` if that `e` becomes `ch` (`ke`+`edy` → `pchdy`, `keedy` → `pchedy`, `key` → `pchy`; after `p`+`ch`: `chedy` 23%, `chdy` 11%, `chy` 11%, `chey` 10%). And `p`/`f` go less before `a` (13% against 24%). The skribe wrote 24% `pe`/`fe` on the first line.

### 12.1 · What was changed

`scribe.py`, `use_pf_noe`: when a first-line gallows becomes `p`/`f`, an `e` right after it becomes `ch`, and before `a` the change is made only half the time (`pf_a` 0.5). The share of the change was raised to compensate (`p_pf` 0.30 → 0.33), and the `e` offset of the first-line register lowered (`fl_e` −0.6 → −0.2), because turning `ke` into `pch` already takes `e` away from the first line (with −0.6 the ratio of words with `ee` fell to 0.77 against 0.86). Both values calibrated on the odd folios (targets 29.4% `p`/`f` on the first line and ×0.876 `ee`; skribe 29.9% and ×0.854). Two measures added (`measures.py`, after R1.3): plain `p`/`f` followed by `e` (real 0.31%) and followed by `ch`/`sh` (real 59.2%). The battery has 84 measures. `compare.py`, `holdout.py` and the other scripts now read negative values in `key=value` (before, `fl_e=-0.4` arrived as text).

### 12.2 · Result (5 seeds, 84 measures)

| | without the rule | **with the rule** |
|---|---|---|
| plain `p`/`f` followed by `e` (real 0.31%) | 18.5% | **0.34%** |
| whole text: reproduced / median error | 79/84 · 0.058 | **77/84 · 0.047** |
| learned from the odd folios, on the even ones (real halves 74/84 · 0.049) | 69/84 · 0.071 | **72/84 · 0.080** |

Honest reading: the rule fixes a categorical feature that no measure was looking at, and the whole text fits better; on the even folios it gains measures but the median error rises by 0.009, about the run-to-run noise (four runs with the rule and different `p_pf`/`fl_e` gave 0.079–0.088, two without 0.071–0.073). The counts move by ±2 between runs on the noisy measures (neighbours one glyph apart, frequent words repeated, H8, repeats on the first line). Three-rule baseline: 45/84 (0.254). Files: `results_table.txt`, `results_holdout_table.txt`, `results_ablations_table.txt` (column "without pf_noe").

Ablations (`results_ablations_table.txt`, 5 seeds; full skribe 77/84 · 0.047). Measures lost and median error when each rule is removed:

| rule removed | measures | median error |
|---|---|---|
| boundary rule | −8 | 0.075 |
| first line | −7 | 0.071 |
| first-line register | −7 | 0.065 |
| copying | −7 | 0.062 |
| length mode | −7 | 0.060 |
| closure | −5 | 0.047 |
| start contexts | −4 | 0.062 |
| sheet style, slot template, word rules, form memory | −3 | 0.054 to 0.065 |
| dissimilation | −2 | 0.063 |
| end table | −1 | 0.050 |
| language tables, closure by word count, section dy | 0 | 0.047 to 0.052 |
| gallows-initial line habit, reprefix | +1 | 0.048, 0.053 |
| **p/f followed by ch (new)** | **+2** | **0.058** |
| word family, e habit | +2 | 0.052, 0.044 |

No rule broke: every rule that cost measures before still costs them, or (gallows habit, reprefix) moves by one, inside the noise. Removing the new rule loses its own two measures (`p`/`f` + `e` 18.5%, + `ch` 34.6%) and gains four noisy ones, so the count goes up by two while the median error rises from 0.047 to 0.058. The e habit again costs nothing and lowers the error when removed (0.044); the word family costs nothing and raises it a little (0.052). Both remain candidates for removal, not removed yet.

### 12.3 · And npcompl33t's arrows?

His test rebuilt (`external_tests/npcompl33t/pf_vectors.py`, `EXTERNAL_TESTS.md` §11): the skribe, with no chronology, draws the same "`p`/`f` behind `k`/`t`" arrows as the real text, with the rule and without it. So the arrows are not evidence of an archaic `p`/`f`, but the rule about `e` does not explain them either.

## 13 · What the glyph-pair scan found (27/10/2026)

**The scan** (`scribe/pairs/`). Pass 1 (`forbidden_pairs.py`): every glyph pair inside a word that is written at most 20% of what the frequencies of the two glyphs give. 216 such pairs; all are covered by a rule (R1.4, R1.5, R2.2, R13.x) or follow from the word template, and the current skribe respects all of them (the skribe of 26/10 broke exactly one: `pe`, 200 against 3). Pass 2 (`context_pairs.py`, pre-registered in `CONTEXT_PAIRS_PREREG.md`): the pairs whose rate changes with the place of the word (place in the line, line type, hand, section, language) differently in the real text and in the skribe, replicated on odd and even folios. The positive control works (the skribe of 26/10 is flagged for `p` → `e` on the first line, z −14.9). With the skribe of 27/10, four things:

| | real | skribe before |
|---|---|---|
| line-final `-m` written `-am` (not `-im`) | 495 against 29 | 561 against 164 (`daim`) |
| line-final `-y` → `-g` after `d`, `k`, `t` | 1%, 1%, 0% | `-dg`, `qokg`: the most common `-g` |
| plain `p` among plain `p`+`f`, first line | 79% | 71% |
| last line of the paragraph: `q-` after `-y` before `o` / other lines | 0.49 / 0.61 (every hand) | 0.57 / 0.61 |
| last line of the paragraph: `ch-` words / other lines | 23.9% / 19.0% | 19.9% / 20.0% |

The first two are R4.3 made in the wrong form: an `-aiin` that missed the `-iin` → `-m` closure got a second chance as `-in` → `-m` and became `-aim`; and `-y` → `-g` was applied after any glyph, while in the real text it follows `o` (65%), `e` (12%), `ch` (9%), `l` (8%). The third is R1.3 with the wrong balance. The last is new: rule R14.8, the last line of the paragraph has a register of its own (less `q`, the glyph of going on, more bench words), as the first line does (R5.2).

### 13.1 · What was changed

`scribe.py`: `close_once` (one closure per word, by its most specific ending; for `-iin` the probability is the one the two chances gave together, so the closure rate stays and only the form changes; `-y` → `-g` weighted by the glyph before the `y`, `YG_MULT`, smoothed towards the overall rate); `pf_f` 0.4 (a `t` becomes `f` at 0.4 times the rate of `k` → `p`) with `p_pf` 0.33 → 0.42 to keep the share of `p`/`f` among the gallows of the first line; `use_ll_style` with `ll_q` −0.5 (the `q` style offset on the last line) and `ll_ch` 0.3 (the weight of `ch` as the first glyph of a new word on the last line). `pf_f`, `p_pf`, `ll_q` and `ll_ch` calibrated **on the odd folios only** (skribe trained on and writing the odd folios, 3 seeds; real odd: `p` 77.0%, `p`/`f` among gallows 29.4%, last line `q` ×0.79, `ch-` ×1.23; skribe 79.0%, 30.0%, ×0.80, ×1.19). Four measures added (`measures.py`, part 8): `-am` among line-final `-am`+`-im`, plain `p` among plain `p`+`f` on the first line, and the two last-line ratios. The battery has 88 measures. In `compare.py` the ablations also remove `use_ll_style` and `close_once`.

### 13.2 · Result (5 seeds, 88 measures)

| | without the changes | **with them** |
|---|---|---|
| line-final `-am` / (`-am`+`-im`) (real 94.5%) | 75.0% | **96.6%** |
| plain `p` among `p`+`f`, first line (real 75.4%) | 62.6% | **79.5%** |
| last line: `q-` ×, `ch-` × (real ×0.81, ×1.25) | ×0.98, ×0.97 | **×0.83, ×1.20** |
| whole text: reproduced / median error | 79/88 · 0.048 | **81/88 · 0.046** |
| learned from the odd folios, on the even ones (real halves 78/88 · 0.047) | 75/88 · 0.076 | **75/88 · 0.070** |

Three-rule baseline: 49/88 (0.245). A first run without the combined `-iin` probability closed too little on the last line of the paragraph on the even folios (12.5% against 17.5%) and gave 70/88; with it, 16.3%. Still missed on the whole text: near twins, which frequent words repeat (>3× and <0.3× chance), `-m` by line length, the page overdispersion of `q-` and of `e`-words, and plain `p`/`f` followed by `e` (0.45% against 0.31%: about six cases per seed against five in the whole manuscript, mostly `pesh-` inside the line). Note that the new measures are loose at ±25%: the skribe without the changes already passes all four (75.0% against 94.5% is inside the band); what tells the versions apart is the values, in the table above. Files: `results_table.txt`, `results_holdout_table.txt`.

### 13.3 · All the rules again (ablations, 5 seeds, 88 measures)

`results_ablations_table.txt` (full skribe 81/88 · 0.046). Measures lost when each rule is removed, and the median error without it:

| rule removed | measures | median error |
|---|---|---|
| boundary rule | −9 | 0.058 |
| first line | −8 | 0.074 |
| copying | −6 | 0.063 |
| first-line register | −6 | 0.052 |
| word rules | −5 | 0.040 |
| length mode | −5 | 0.058 |
| sheet style | −3 | 0.068 |
| closure | −3 | 0.048 |
| *e* after *p*/*f* becomes *ch* | −3 | 0.051 |
| start contexts, dissimilation | −2 | 0.057, 0.054 |
| slot template, form memory, *e* habit | −1 | 0.046, 0.041, 0.052 |
| one closure per word (new) | 0 | 0.053 |
| reprefix, end table, closure by word count, section dy | 0 | 0.044 to 0.053 |
| language tables, word family, last-line register (new) | +1 | 0.042, 0.046, 0.046 |
| gallows-initial line habit | +3 | 0.049 |

No rule broke. The two new pieces do not show in the count: the one-closure rule fixes a form that no measure at ±25% separates (75% `-am` already passes against 94.5%) and lowers the median error from 0.053 to 0.046; the last-line register costs one noisy measure and leaves the error as it is, while its own two ratios pass loosely without it (×0.98 and ×0.97 against ×0.81 and ×1.25 are inside the band): the values, not the count, show it (§13.2). Removing the gallows-initial line habit gains three noisy measures and raises the error a little, as on 26/10. Word rules and form memory again lower the error when removed (0.040, 0.041): they fix their own measures at the cost of the general fit.
