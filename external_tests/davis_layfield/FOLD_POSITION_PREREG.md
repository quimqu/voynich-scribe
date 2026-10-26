# Fold position test: pre-registration (25/10/2026, written before running `fold_position.py`)

**Hypothesis.** The LSA inner-face asymmetry (EXTERNAL_TESTS.md §5) comes from a scribe of hand 2 copying words, with one glyph changed, from one page to the facing page of the open, folded sheet. If so, the words involved should sit near the fold: at the end of the line on the left page (verso) and at the start of the line on the right page (recto).

**Data.** ZL3b paragraph text (`scribe/manuscript_out/real.txt`), the 37 complete bifolia of quires 1–7, 13 and 20. Position of a word = its index in the line divided by (words in line − 1); one-word lines are left out. Fold proximity = position on a verso, 1 − position on a recto (1 = at the fold).

**Measure (fixed in advance).** For a pair of pages (left verso L, right recto R), a token is *linked* if its word type is used on at most 40 pages of the manuscript and the other page has a type at edit distance exactly 1 (not the same word). Per face, the statistic is the mean fold proximity of linked tokens minus that of the unlinked tokens of the same two pages (tokens of the same band). Inner face: L = a-v, R = b-r. Outer face (control, same geometry when the sheet is flat): L = b-v, R = a-r.

**Primary test.** Hand 2 (10 bifolia): paired per bifolium, inner minus outer, one-sided Wilcoxon (inner greater), alpha 0.05.
**Prediction if copying across the open sheet:** inner > outer in hand 2, and inner > 0.
**Secondary (reported, not decisive):** all bifolia, hand 1; the same on the five skribe seeds (no cross-page copying, so ≈ 0); the vertical alignment of linked pairs (|difference in line fraction|) against all cross-page pairs.

Any other cut of these data is exploratory and will be labelled as such.


---

## Outcome (added after running, 25/10/2026)

**Primary test: not met.** Hand 2, inner minus outer: −0.004, one-sided p 0.58, 5 of 10 bifolia positive; inner alone −0.010 (p 0.69). The skribe seeds give −0.037 to +0.056 (one seed p 0.024). Secondary: all bifolia +0.006 (p 0.98); hand 1 +0.005 (p 0.84); linked pairs are not at the same height (0.98 inner, 0.96 outer, 1.00 hand 2).

**Power (added afterwards, not pre-registered).** Injecting into the real hand-2 inner faces copies that are existing one-glyph variants of a line-final word of the left page, placed as the first word of lines of the right page: detected in 0–5% of runs with 5–20% of lines, 20% with 30%, 95% with 50%. The test only excludes heavy copying at the fold.

**Link with the LSA (`fold_position_lsa_link.py`, exploratory).** The same injection into the skribe does not raise the hand-2 LSA inner-outer difference at any rate, up to half the lines (seed 1: +0.073 → +0.068; seed 2: +0.019 → +0.004; seed 3: +0.058 → +0.054; real +0.186). Copying words at the fold, even in the amounts the fold test would see, is not what makes the LSA signal.
