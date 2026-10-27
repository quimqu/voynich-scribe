# Glyph pairs that change with the place: pre-registration (27/10/2026, written before running `context_pairs.py`)

**Question.** Pass 1 (`forbidden_pairs.txt`) found no near-forbidden pair that the rules or the word template do not already cover, and the current skribe respects them all. Rules like "after a plain `p`/`f` the `e` is written `ch`" can also be of another kind: a pair that is allowed but whose rate changes with where the word is. Pass 2 looks for those, everywhere, against the skribe, which already carries the known place rules.

**Units.** Every glyph transition inside a word, word start `^` and end `$` included (glyphs as in the rest of the programme: `cth ckh cph cfh ch sh` are one glyph). Paragraph text, ZL3b. The real text against the current skribe (27/10, five seeds, same layout).

**Contexts** (one value per word):
- **word place**: first word of the line, last word, the word right after a drawing gap, the word right before one, any other word;
- **line type**: first line of a paragraph, last line, other lines;
- **hand** (Davis 1–5), **section**, **Currier language**.

**Statistic, per cell** (glyph a, context variable, value c, next glyph b): the contrast P(b | a, c) − P(b | a, not c) in the real text, minus the same contrast in the skribe (all five seeds pooled): a difference in differences. A cell that the skribe already reproduces gives about 0; a general miss of the skribe that does not depend on the place also gives about 0. z = that difference over the binomial standard error of both contrasts. Cells with at least 80 real transitions from a in c.

**Criterion (pre-registered).** A cell is flagged if |z| ≥ 4.5 on the whole text (about a Bonferroni bound for the few thousand cells) **and** the same sign with |z| ≥ 2 on the odd folios and on the even folios separately (each half against the skribe on the same half).

**Positive control.** The same scan with the skribe texts of 26/10 (`manuscript_out/`, before the `p`/`f` rule) must flag `p` → `e` (and `p` → `ch`) on the first line of the paragraph. If it does not, the scan is not sensitive enough and its silence means nothing.

**Reading.** Flagged cells are candidates for new place rules, or for known rules the skribe makes with the wrong strength. Each will be looked at by hand (which words carry it, whether one hand or one section makes all of it) before it is called a rule. If nothing is flagged with the current skribe and the positive control works, the skribe already carries all the place-dependence of glyph pairs that this scan can see.

Any other cut is exploratory and will be labelled as such.

---

## Outcome (added after running, 27/10/2026)

**Positive control: works.** With the skribe of 26/10 the scan flags `p` → `e` on the first line of the paragraph (z −14.9) and inside the line (z −27.1), and `p` → `ch` (z +13.9) (`context_pairs_control_2610.txt`).

**Current skribe: 115 of 8,264 cells flagged** (`context_pairs_skribe_2710.txt`). Looked at by hand (exploratory), they fall into a few groups:
- **Transliteration oddities**: rare glyphs (`c`, `b`, word-initial `g`) that the real text has and the skribe never writes. Not rules.
- **Line-end closure, wrong form.** The real text closes `-aiin` into `-am` (495 `-am`, 29 `-im` among the 4,100 line-final words); the skribe writes 164 `-im` (`daim`), and too few `-om` (56 against 93). And `-g` in the real text follows `e`, `l`, `o`, `a` (or stands alone); the skribe puts it after `d`, `k`, `t` (`-dg`, `qokg`), which the real text almost never does. A known rule (R4.3) made in the wrong form.
- **`p` against `f` on the first line.** Real `p` share 0.79 among plain `p`+`f`; skribe 0.71. A known rule (R1.3) with the wrong balance.
- **The last line of the paragraph (new).** Words after the first: `q-` after `-y` before `o` 0.49 against 0.61 in the other lines, and `ch-` words 0.239 against 0.190; in every hand (hand 1: 0.33 against 0.55; hand 2: 0.51 against 0.64; hand 3: 0.51 against 0.59). The skribe does neither (0.57; 0.199). With the first line (`sh` over `ch`, rarer words) and the last line closing less (R14.2), this is a second end-of-paragraph register. Candidate rule; not yet in RULES.md.
- **Smaller ones**: words right before a drawing gap end in `-d` more often (13% against 4%), the `cth-` words of herbal A (known, open), and the A/B difference in `ch` → `e` slightly under-made by the skribe.

**Reading.** No new categorical rule like `pe`. One new place rule (the last line of the paragraph: less `q`, more `ch-`), and three known rules that the skribe makes in the wrong form (`-im` for `-am`, `-g` after `d/k/t`, too much `f`). These are the next fixes for the skribe.
