# External tests: the skribe against two 2026 papers (25 October 2026)

*Two tests that we did not design ourselves, applied exactly as their authors publish them to the real text (ZL3b, paragraph text, normalised as in `scribe/manuscript.py`) and to the skribe's text (`scribe/scribe.py`, 5 seeds, the whole manuscript, same layout). No parameter of the skribe was touched for these tests: it is the skribe of 19 October (findings log L5). Scripts and outputs are in this folder; the input is `scribe/manuscript_out/` (`real.txt`, `scribe_seed1..5.txt`).*

---

## 1 · Parisel (2026): the four boundary signatures

**The paper.** C. Parisel, *Evidence of Layered Positional and Directional Constraints in the Voynich Manuscript: Implications for Cipher-Like Structure*, arXiv 2604.19762 (v2, June 2026). It measures what happens at the boundary between two consecutive words and derives four signatures from it, calibrated separately for Currier A and B on his transliteration (RF1b-e), which any Voynich generator should reproduce all at once:

| signature | what it is | reference A | reference B |
|---|---|---|---|
| Sig1 E→S | boundaries that go from an "end" glyph to a "start" glyph (classes by a 2:1 position ratio) | 71.0 % [56, 86] | 64.3 % [50, 79] |
| Sig2 bilateral | glyphs with a position ratio > 100:1 on both sides (start and end) | yes | yes |
| Sig3 MI | mutual information between the last glyph of a word and the first glyph of the next | 0.586 (≥ 0.29) | 0.498 (≥ 0.25) |
| Sig4 shape | frequency distribution of the boundary glyphs: power law, not plateau | Zipfian | intermediate |

He tests two generators (a parametric slot generator, > 2,000 runs, and a Cardan grille in Rugg's manner, 15 configurations): **none passes all four at once** for either dialect, because the E→S rate and the MI (or the shape) demand opposite settings of the same lever. He calls for generators in which these traits come from independent mechanisms.

**What we did.** The author's verifier (`github.com/labyrinthinesecurity/currier-signatures`, commit 5d50101; the import `signatures_v26` → `signatures_v27` must be corrected) calibrates the reference on RF1b-e and scores a word file, one manuscript line per line, against the reference of the dialect. We give it the real text and the text of each seed of the skribe, split by dialect with **the same folio assignment he uses** (`run_parisel.py`). The real text serves as control: with our normalisation it must pass.

**Result (`parisel/summary.txt`, full reports in `parisel/out_*.txt`).**

| text | dialect | words | E→S | MI | bilateral | shape | attestation | verdict |
|---|---|---|---|---|---|---|---|---|
| real (ZL3b) | A | 10,378 | 66.4 % | 0.584 | yes (3, 3) | Zipfian 0.857 | 91 % | **4/4** |
| real (ZL3b) | B | 21,380 | 65.8 % | 0.499 | yes (5, 8) | intermediate 0.815 | 93 % | **4/4** |
| skribe, 5 seeds | A | 10,378 | 68.1–70.5 % | 0.526–0.541 | yes (3–5, 4–5) | Zipfian 0.866–0.879 | 72 % | **4/4 × 5** |
| skribe, 5 seeds | B | 21,380 | 63.3–65.6 % | 0.454–0.470 | yes (4–5, 5–9) | intermediate 0.818–0.826 | 79 % | **4/4 × 5** |

(*attestation*: fraction of the words of the text that exist in the RF1b-e dialect; in the real text it is not 100 % because the transliterations differ.)

**Reading.** The skribe passes the four signatures for both dialects, at all five seeds, and not merely within the margins: the values are close to the reference (MI 0.92× at A and 0.93× at B; E→S within ±3 points; the shape is that of the dialect). It is not tuned for any of these measures. The mechanisms that Parisel asks to be independent are independent in the skribe by construction: E→S and MI come from the boundary agreement (R3.3) and from the endings as closure (R2.7); the shape, from the word template (R2.1) and from the two-glyph memory (R13); and the bilaterality, from the glyphs that only open or only close (R1.5). It is the first time a published generator passes this benchmark. **It confirms by an external route** that the boundary coupling is a contact-glyph phenomenon (H14, K2), not a matter of word grammar.

Reservations: the skribe's tables are learned from the text (like all the skribe's tables); 21–28 % of the skribe's words are not in the RF1b-e dialect (they are new words, A12/R16), which the verifier reports but does not penalise.

---

## 2 · Layfield and Davis (2026): page similarity and the "singulion" structure

**The paper.** C. Layfield and L. Fagin Davis, *Singulion Structure and the Voynich Manuscript*, Digital Medievalist 19 (10 July 2026, doi 10.4000/16k0a). They hold that the manuscript was made with loose bifolia ("singulions") that were never meant to be nested in quires, and that the current binding is wrong. The textual evidence: latent semantic analysis (LSA: documents of 40 words per page, TF-IDF, SVD with k = 75, cosine between pages folded into the space) and the mean similarity between pages according to their physical relation:

- **confoliate**: recto and verso of the same folio;
- **conjoint**: the two pages of the inner face of the bifolium (a-v | b-r), physically continuous across the fold;
- **facing**: consecutive pages in the current order (v | r).

In two Latin control manuscripts (the Aberdeen Bestiary, *Speculum*) facing ≈ confoliate > conjoint, as befits a text that is read straight through. In the Voynich (quires 1–7, 13 and 20) they find conjoint 0.433 > confoliate 0.383 > facing 0.298 (p conf/fac 0.005; fac/conj 0.000; conf/conj 0.168): neighbouring pages in the current order resemble each other less than pages of the same bifolium. They deduce from this that the current order is wrong, and reorder the bifolia of quires 13 and 20 seeking the maximum facing (gains of 12 % and 20 %). They do not control for hand, language or section: they say so, and treat it qualitatively.

**What had been said before (voynich.ninja).** The idea that within-bifolium similarity is production and not reading is not new: Wladimir D (2018–2019, "volume of overlapping information" per bifolium: the text was written before sewing), pfeaster (2022, "bifolio as a functional unit", strange alignments per bifolium), oshfdk (December 2025: "the statistics point to the order of writing, bifolium by bifolium, not to the order of reading"), dashstofsk (February 2026: page correlations in Q13 and Q20, "written sheet by sheet, first one face and then the other") and, above all, Torsten Timm's review (*The Singulion and the Sequence*, July 2026): the within-bifolium similarity is real, its reading as reading order is underdetermined, and the reordering lacks a permutation null and a calibration with shuffled known text. Timm also proposes (13 and 15 July 2026) that the pages of the inner face are the most similar "because they were seen together". What was missing was a meaningless control text with sheet habits, which is what the skribe provides.

**Our previous reading.** The programme had already measured that **the sheet is the writing session**: recto, verso and conjugate folio share vocabulary, habits and letter size, and the neighbouring folio from another sheet does not (G6, H11, R7.4). The skribe has sheet habits and vocabulary by hand and section, and no notion of reading order.

**What we did (`davis_layfield/lsa_singulion.py`).** The same LSA (documents of 40 words, remainder ≥ 20, TF-IDF, df ≥ 2, k = 75, pages folded, cosine) on the real text and on the skribe's text, in the same quires (A–G, M, T). Besides their three pair types, we add two: the **outer face** of the bifolium (b-v | a-r) and the **diagonals** (a-r | b-r, a-v | b-v). Mann-Whitney test between pair types, as they do.

| text | confoliate | conjoint | outer | diag | facing | p conf/fac | p conf/conj | p fac/conj | p conj/outer |
|---|---|---|---|---|---|---|---|---|---|
| Layfield-Davis (real, ZL 2a) | 0.383 | 0.433 | n/a | n/a | 0.298 | 0.005 | 0.168 | 0.000 | n/a |
| **real (ZL3b, here)** | 0.225 | 0.284 | 0.183 | 0.208 | 0.154 | 0.008 | 0.100 | 0.000 | 0.015 |
| **skribe (5 seeds)** | 0.147 ± 0.009 | 0.145 ± 0.012 | 0.143 ± 0.018 | 0.152 ± 0.011 | 0.091 ± 0.017 | 0.001–0.43 (4/5 < 0.07) | 0.48–0.97 | 0.03–0.18 | 0.60–0.95 |

(n: confoliate 76, conjoint 38, outer 37, diag 75, facing 68. The absolute values are not comparable with theirs because the space is a different one; the order and the p-values are. With k = 50, or removing the 20 most frequent words, the same.)

1. **The replication holds.** On the real text we reproduce their pattern and their p-values: conjoint > confoliate > facing, with facing significantly below both and conjoint not distinguishable from confoliate.
2. **The skribe reproduces their evidence against the quire structure.** In a meaningless text, the pages of the same bifolium (0.145) also resemble each other much more than the neighbouring pages of different bifolia (0.091; p < 0.07 at 4 of 5 seeds). Page similarity measures the writing session, not the reading order: **the signal they use cannot decide whether the order is right or wrong.** It is the null that Timm's review asked for.
3. **The reordering is not informative.** Doing as they do (mean facing of the nested order against the maximum over all permutations of the bifolia at the junctions), the real text gains 33 % at M and 50 % at T; the skribe, which has no right order to recover, gains 61 ± 26 % and 78 ± 19 % (`bifolium_asymmetry.py`). The maximum of 120 or 720 permutations of a noisy measure always goes up.
4. **A within-bifolium asymmetry that is not confirmed** (§3): with the LSA, the inner face of the real text (0.284) is more similar than the outer one (0.183), and the skribe does not do this; but no other measure reproduces it.

**Reading.** Layfield and Davis may be right about the binding for codicological reasons (stains, drawings that jump across pages, alternating hands), but the textual part of their argument is a production effect that the programme had already measured, that others had pointed out, and that a meaningless text reproduces.

---

## 3 · The within-bifolium asymmetry: examined and not confirmed

**Where it comes from.** From looking at the table in §2 (post hoc, not pre-registered): with the LSA, the inner face of the bifolium (a-v | b-r) is more similar than the outer one (b-v | a-r), +0.096 paired by bifolium, Wilcoxon p = 0.019, 68 % of the 37 bifolia; and if the folded sheet is written in the order a-r, a-v, b-r, b-v, the similarity falls with the writing distance (1: 0.246; 2: 0.208; 3: 0.183; slope per bifolium p = 0.048). The skribe does not do this (+0.001), because the sheet habit treats the four pages alike. Two readings were possible: vocabulary drift over the time spent writing the folded sheet, or copying of the visible field across the fold with the sheet open (Timm's proposal of July 2026).

**The critical test (`bifolium_asymmetry2.py`, `asymmetry2.txt`).** The same pages and the same 37 bifolia, with six similarity measures instead of one. The contrast is paired by bifolium (inner − outer), so hand, language, section and quire are identical on both sides; only the pairing of the four pages changes.

| measure | inner | outer | inner − outer (real) | sign-test p | % bifolia > 0 | skribe |
|---|---|---|---|---|---|---|
| LSA k = 75 (cosine) | 0.284 | 0.183 | **+0.096** | 0.024 | 68 % | +0.001 |
| TF-IDF without SVD (cosine) | 0.221 | 0.188 | +0.026 | 0.073 | 59 % | +0.003 |
| Jaccard of word types | 0.108 | 0.103 | +0.002 | 0.61 | 49 % | 0.000 |
| Jaccard at equal length (the 4 pages trimmed to the shortest, 20 draws) | 0.103 | 0.099 | +0.002 | 0.61 | 49 % | 0.000 |
| exact twins (fraction of words with the same word type on the other page) | 0.307 | 0.296 | +0.004 | 0.74 | 46 % | 0.000 |
| near-twins at distance 1 (A1) | 0.658 | 0.648 | +0.005 | 0.72 | 54 % | −0.005 |
| the five free choices (L1 distance of rates, sign inverted) | | | +0.020 | 0.70 | 43 % | +0.004 |

The slope by writing distance is negative only with the LSA (p 0.048) and the TF-IDF (p 0.031); with the other four measures it is not (p 0.15–0.80). Within the LSA, the effect belongs to hand 2 (10 bifolia, +0.186, p 0.004) and hand 3 (5 bifolia, +0.174); in hand 1 (21 bifolia) it is +0.026, p 0.65. The correlation of (inner − outer) with the difference in word count between the two pairs is +0.52 for the TF-IDF, +0.45 for the twins and +0.18 for the LSA: part of what is measured is which page has more text. The vertical alignment of the exact twins between pages (|Δ line fraction| against shuffled lines) is 0.96–1.01 for all pair types: the twins from one page to the other are not at the same height.

**Verdict.** The asymmetry is an effect of a single representation (the 75 axes of the LSA, which weight a handful of frequent words), concentrated in 15 bifolia of hands 2 and 3, that does not appear in any of the five direct measures of shared vocabulary, nor in the copying at distance 1, which is the route by which the "copying of the visible field" would have to act, nor in the free choices, which is where the "drift of the hand" would have to act. With one post hoc measure and five negative replications on the same data, it cannot be said that the inner face is more similar. **NOT CONFIRMED.** Timm's proposal (the inner pages more similar because they were seen together) finds no support in the network of near-twins, which is where it ought to have it. If it is ever taken up again: a pre-registered measure would be needed, and probably the coordinates (if there is copying across the fold, the models should be near the fold).

---

## 4 · Singulion against the best nesting (Koen's question, 25/10/2026)

**The question** (voynich.ninja, thread 6219): the current binding is easy to beat, because it is known to be disturbed; the real test is whether a singulion structure beats the best alternative *nesting*.

**What we did (`davis_layfield/singulion_vs_nesting.py`, output `singulion_vs_nesting.txt`).** Nine quires with at least three complete bifolia (1–7, 13 and 20; in 20 only its five complete bifolia). For each, all n! orders of the bifolia, scored nested (outer → central) and as singulions (each bifolium read a-r a-v b-r b-v). Both structures have 2n−1 facing pairs, so mean facing similarity is directly comparable. Best singulion (S\*) against best nesting (N\*), with three representations: Layfield and Davis's LSA (k = 75), TF-IDF without SVD, and shared word types (cosine of presence vectors, no weights). Controls: structures with the singulion's combinatorics but another same-sheet pair facing (outer face, the two rectos, the two versos, the two sides of a leaf).

| measure | best nesting vs current, real (skribe) | S\* beats N\*: real | skribe (5 seeds) | S\*/N\* real | skribe | sham same-sheet pairs, real |
|---|---|---|---|---|---|---|
| LSA k = 75 | (not meaningful: the current order is near 0 or negative in some quires) | **8/9** | 2–5/9 | **1.26** | 0.84–1.02 | 4–6/9, 1.04–1.19 |
| TF-IDF | +22 % (+36 to +49 %) | 8/9 | 2–7/9 | 1.06 | 0.95–1.04 | 3–6/9, 0.99–1.04 |
| shared types | +15 % (+15 to +30 %) | 5/9 | 4–5/9 | 1.02 | 0.99–1.01 | 4–6/9, 0.98–1.03 |

1. **Koen's point holds.** The best nesting beats the current binding by a wide margin in the real text and in the skribe, which has no correct order at all.
2. **With LSA, the singulion beats the best nesting in the real text (8/9 quires, +26 %) and not in the skribe.** This is the one part of the textual argument the skribe does not reproduce.
3. **It is the inner face of the bifolium, not the sheet.** The sham structures, which put another pair of the same sheet face to face, do not win (4–6/9). A singulion puts every inner face (a-v | b-r) face to face; a nesting only the central one. The win is therefore the within-bifolium asymmetry of §3.
4. **It is not in the shared vocabulary.** With shared word types the real text behaves like the skribe (5/9, +2 %). Shared rare words, inner minus outer face paired per bifolium, in four frequency bands (words used on 2–3, 4–10, 11–40, > 40 pages): no difference (p 0.15–0.95; the skribe, p 0.06–0.97).

**Reading.** On their LSA, the answer to Koen is yes; on what the pages actually share, no. As in §3, the effect lives in the weighting (LSA, and weakly TF-IDF) and not in any direct measure of shared words, rare or frequent. It cannot be used for or against singulions until it is found with a representation that does not go through the SVD.

---

## 5 · What the LSA sees and the shared vocabulary does not (25/10/2026)

**Question.** The inner face of the bifolium is more similar than the outer face with LSA (+0.096, §3) and in no direct measure; that is also all that makes the singulion win in §4. Folding a page into the space is v = q U_k / S_k, so the similarity of two pages is q_x M q_y with M = U_k S_k^-2 U_k^T: the LSA counts shared words (the diagonal of M) and also pairs of *different* words that co-vary across documents (off the diagonal). Script `davis_layfield/lsa_anatomy.py`, output `lsa_anatomy.txt`. Real text and the five seeds of the skribe, 37 bifolia.

1. **Three quarters of it is pairs of different words.** Diagonal (shared words) +0.023 (p 0.15); off-diagonal +0.072 (p 0.034). Skribe: +0.002 and -0.002.
2. **It is not the weak dimensions inflated by 1/S.** The difference is spread over dimensions 6-75 (the 8 largest carry half). It holds for k = 25-150 (p 0.02-0.06) and disappears at k = 10. Folding without the division (q U) keeps two thirds of it (+0.067, p 0.03); folding with the standard document scaling (q U S, which weights the first dimensions, like plain TF-IDF) leaves +0.027 (p 0.06).
3. **It is not a few frequent words.** Removing the 10, 20 or 50 most frequent words of the manuscript does not change it (+0.086 to +0.100). It is spread over about 60 mid-frequency words (frequency rank 4 to 200), mostly Currier B vocabulary (`sho`, `chdy`, `lchedy`, `qokeey`, `qokedy`, `qokeedy`, `chol`, `qoty`, `qol`). The word pairs that carry most of it are **one-glyph variants** of each other: `dchy~kchy`, `chdy~kchdy`, `chor~tchor`, `chol~kchol`, `cheor~chor`, `qokeedy~qoteedy`, `sho~shody`.
4. **It is hand 2.** Hand 2: 10 bifolia, +0.186, p 0.004, 9 of 10 positive. Hand 1 (21): +0.026, p 0.61. Hand 3 (5): two large positive and two negative. By language: B +0.186 (p 0.003), A +0.026. Leave one bifolium out: p 0.006-0.032; removing the two largest: p 0.054. Not related to text length (Spearman +0.06).
5. **Hair or flesh side: not measurable from the scans.** Two pages on the same face of the sheet are not closer in parchment colour than the two sides of a leaf (brightness 7.9 against 6.6), so colour does not identify the face; it does not correlate with the difference either (p 0.24, 0.08). L. Fagin Davis has written (voynich.ninja, 22/04/2026) that the sides are almost indistinguishable in this manuscript.
6. **The direct version of point 3 does not reproduce it.** Fraction of word types with a one-glyph variant (not the same word) on the other page, by frequency band, inner minus outer: all bifolia p 0.07-0.85; one cell of twelve below 0.05 (Currier B, words on 2-40 pages, +0.061, p 0.018), and the skribe produces cells of the same size (one seed, hand 2, p 0.002).
7. **Nor do the free choices per hand.** Of twenty cells (5 choices x 4 groups) one is below 0.05 (hand 2, the `q-` rate, p 0.01); the skribe has cells at p 0.02-0.04.

**Reading.** What the LSA sees is a *diffuse* co-variation: many mid-frequency words of hand 2 and their one-glyph variants, each a little more present on the inner face, none enough on its own. The direct measures look at one word, one band or one habit at a time and stay in the noise; the SVD adds up dozens of correlated small differences into one number, which is what it is built to do. That is a real possibility, but the evidence is weak: it is post hoc, it rests on ten bifolia of one hand (half of them in quire 13), it needs the two largest to stay below 0.05, and every direct test of the mechanism that the LSA points to (one-glyph variants, the free choices) gives single cells that the skribe matches. If it is real, the place to look is hand 2: cross-page copying with one-glyph changes, as in the copying within a page (A1), across the inner face that is open when the sheet is folded. A pre-registered test on hand 2 alone (one measure, one band, fixed in advance), or the glyph coordinates (copies across the fold should sit near the gutter), could decide it.

---

## 6 · Copies at the fold? (pre-registered, 25/10/2026)

**Idea** (Q. Quadrada): if a hand-2 skribe copied words from one page to the facing page of the open sheet, the copies should sit near the fold: at the end of the lines on the left page (verso) and at the start of the lines on the right page (recto). The outer face, with the same geometry when the sheet is flat, is the control. The test was written down before running (`davis_layfield/FOLD_POSITION_PREREG.md`); script `fold_position.py`, output `fold_position.txt`.

**Measure.** A token is *linked* if its word is used on at most 40 pages and the facing page has a word at exactly one glyph from it. Per face: mean closeness to the fold of linked tokens minus that of the other tokens.

| | inner − outer, hand 2 (primary) | all bifolia | hand 1 |
|---|---|---|---|
| real | −0.004 (one-sided p 0.58, 5/10 > 0) | +0.006 (p 0.98) | +0.005 (p 0.84) |
| skribe, 5 seeds | −0.037 to +0.056 (p 0.02–0.94) | p 0.51–0.83 | p 0.22–0.86 |

1. **Primary prediction not met.** The words with a variant on the facing page are not nearer the fold on the inner face than on the outer face, and not nearer than the other words.
2. **The test is weak** (positive control, injected copies that are existing one-glyph variants): it detects copying in 0–5% of runs if 5–20% of the right-page lines start with a copy, 20% at 30%, 95% at 50%. Over a hundred words per face have a one-glyph relative on the other page by chance, and a few copies drown in them.
3. **But fold copying cannot be what the LSA sees.** Injecting the same copies into the skribe, up to half the lines, does not raise its hand-2 LSA difference at all (seed 1 +0.073 → +0.068, seed 2 +0.019 → +0.004, seed 3 +0.058 → +0.054; real +0.186). A few copied words per page change the page vectors very little. Whatever the LSA picks up is spread over the vocabulary of the whole page, not concentrated at the fold.
4. **The null for hand 2 is not zero.** The LSA inner-outer difference in the skribe's hand-2 bifolia is −0.022 to +0.073 (one seed p 0.049); with only ten bifolia, a subset of one hand moves a lot. The real +0.186 is 2.5 times the largest seed.

**Reading.** The copying-across-the-open-sheet reading of the LSA asymmetry (Timm's proposal) loses its most direct prediction: nothing at the fold, and the kind of copying that would put something at the fold does not move the LSA. What remains is a page-wide, LSA-only difference in ten hand-2 bifolia, above the skribe but post hoc.

---

## 7 · Writing order within the sheet (pre-registered, 25/10/2026)

**Question** (Q. Quadrada). With LSA the six page pairs of a bifolium line up as if the folded sheet had been written as a booklet a-r, a-v, b-r, b-v: inner face 0.284 > the two leaves 0.234, 0.221 > the diagonals 0.207, 0.208 > outer face 0.183 (flat in the skribe). Two readings: **time** (the hand drifts while writing; pages written one after the other are closer) and **time + sight** (a-v and b-r, besides being consecutive, are visible together on the open sheet, so they should beat the two leaves). Pre-registered in `davis_layfield/SHEET_ORDER_PREREG.md`, script `sheet_order.py`, output `sheet_order.txt`. Two new measures that are not latent models (glyph trigrams G3; cross-entropy gain of a glyph-bigram model of one page on the other, XE), a second latent model (NMF, 20 topics), LSA for reference. Tests: **P1** pairs written one after the other > outer face; **P2** inner face > the two leaves; **P3** continuity across the page turn with half pages (bottom of a page closer to the top of the next).

| | P1 time | P2 sight | P3 page turn |
|---|---|---|---|
| G3 (primary) | +0.015, p 0.15 | −0.004, p 0.75 | +0.009, p 0.10 |
| XE (primary) | +0.005, p 0.29 | +0.005, p 0.37 | +0.002, p 0.31 |
| NMF | +0.061, p 0.036 | p 0.26 | −0.033, p 0.97 |
| LSA (reference) | +0.058, p 0.012 | +0.056, p 0.050 | −0.005, p 0.65 |

1. **No primary test holds** (Holm 0.58–1.00). With glyph trigrams and with cross-entropy the six pairs are flat; the ordering is in the two latent models only (LSA and, for P1, NMF).
2. **There is no continuity across the page turn, not even with LSA.** The bottom of a page is not closer to the top of the next one (LSA −0.005; hand 2 −0.040).
3. **And the measures can see drift at that scale** (validation, not pre-registered): inside a page, the adjacent thirds are closer than the top and bottom thirds for all four measures (real p ≤ 0.0005; the skribe too, from its copying of the lines above). So what draws neighbouring lines together inside a page stops at the page turn. That fits copying from the visible page (A1, R2.8), which the skribe already does, and not a slow drift of the hand that would run through the four pages in writing order.

**Reading.** Neither "time" nor "time + sight" explains the LSA ordering: the two measures built on glyph habits do not see it, and the continuity that a writing-order drift would leave at the page turns is absent while the same measures see it inside every page. What remains is a property of latent word models (LSA, partly NMF) on whole pages, carried by hand 2 (P1 with LSA p 0.003), for which we have no mechanism. With ten bifolia and several readings already tested, the most economical reading is chance amplified by the LSA; the alternative, a real page-level effect of hand 2 that only a latent model sees, would need new data (another transliteration, or the hand-2 bifolia outside these quires) to be tested without reusing these pages.

---

## 8 · The same pairs with LDA (exploratory, 25/10/2026)

**Why.** The author's own topic studies of 2025 (voynich.ninja thread 4834) used LDA, BERTopic and NMF, and found topics that follow the scribal hand more than the Currier language ("stylistic clusters rather than semantic topics"). LDA is a different topic model from LSA: probabilistic, every topic is a positive distribution over words, no negative weights. Script `davis_layfield/lda_pairs.py`, output `lda_pairs.txt`: 40-word documents with word counts, a page folded in as its topic proportions, cosine and 1 − Hellinger, 5 and 9 topics (as in 2025), 20 and 50, three random starts each, and 9 topics without the 15 frequent words of the 2025 list.

| LDA | inner − outer, all (p) | hand 2 (p) | P1 time (p) | P2 sight (p) |
|---|---|---|---|---|
| k = 5 | +0.011 (0.42) | +0.015 (0.50) | −0.007 (0.93) | +0.027 (0.10) |
| k = 9 | +0.040 (0.32) | +0.031 (0.54) | +0.014 (0.68) | +0.039 (0.16) |
| k = 20 | −0.027 (0.57) | +0.008 (0.42) | −0.024 (0.76) | −0.003 (0.13) |
| k = 50 | +0.002 (0.54) | +0.044 (0.39) | +0.019 (0.22) | −0.024 (0.78) |
| k = 9, without the 15 frequent words | −0.051 (0.79) | +0.005 (0.58) | −0.040 (0.92) | −0.017 (0.66) |

(cosine; Hellinger gives the same. The skribe, five seeds × three starts: single runs reach p 0.00–0.05 everywhere, as expected from 15 runs per cell.)

**Reading.** LDA does not see the inner-face asymmetry, nor the ordering of the six pairs, at any number of topics, with or without the frequent words, in all bifolia or in hand 2. The real text behaves like the skribe. Of the latent models, the signal is in LSA (strongly) and NMF (only P1, p 0.036), and not in LDA. What LSA has that LDA does not: topics with negative weights (contrasts such as "more of these words, fewer of those") and, in the Layfield-Davis folding, the same weight for weak topics as for strong ones (§5: without the division by S two thirds remain, with the standard scaling a quarter). LDA, like the standard scaling, is dominated by the main styles of hand and section, which the four pages of a sheet share. The inner-face asymmetry is therefore a property of how the Layfield-Davis LSA weighs small contrasts, not something topic models see in general.

---

## 9 · What the LSA measures: shared bursts on the inner face (pre-registered in part, 25/10/2026)

**Hypothesis** (`davis_layfield/WHITENING_PREREG.md`). Folding with the division by S makes the LSA a *whitened* similarity: it divides out the large directions of variation (the styles of hand and section, shared by the four pages of a sheet) and compares pages on how they deviate from them. Primary measure, transparent and without SVD: **DEV**, the cosine of the pages' deviations from their hand's usual word frequencies. Script `lsa_whitening.py`, output `lsa_whitening.txt`; follow-up `shared_excess.py`.

| inner − outer | all bifolia | hand 2 | skribe |
|---|---|---|---|
| DEV, hand norm (primary) | +0.025, p 0.15 | +0.047, p 0.080 | p 0.14–0.61 |
| DEV, hand × section norm | **+0.064, p 0.018** | +0.105, p 0.037 | p 0.24–0.88 |
| ridge-whitened, full rank | +0.021, p 0.017 | p 0.014 | p 0.07–0.85 |
| cosine without the top 5 directions | +0.031, p 0.007 | p 0.002 | p 0.05–0.84 |
| cosine without the top 25 directions | +0.014, p 0.066 | p 0.12 | p 0.13–0.65 |
| LSA (Layfield-Davis) | +0.096, p 0.009 | p 0.002 | p 0.02–0.73 |

1. **The primary test is not met** (hand norm: p 0.15; hand 2 p 0.080). Same direction.
2. **Against the norm of hand *and* section, a transparent measure sees it** (+0.064, p 0.018; skribe flat), as do the full-rank whitening and a plain cosine once the 5–10 largest directions are removed. The signal is not in the SVD truncation; it is in what is left after the dominant styles are taken away, and it fades when the next 15 directions are removed too.
3. **It is shared excess, not shared absence** (exploratory): both inner pages use the same words *more* than their hand and section normally do (+0.075, p 0.007); shared deficit contributes nothing (p 0.55); page length does not explain it (p 0.29).
4. **Each bifolium has its own family** (exploratory): f108|f111 the *-eedy* family (`lkeedy qokeedy qoteedy keedy`), f33|f40 `oky okar dal chdy`, f50|f55 `chody otar ykar okal`, f4|f5 the *sho-* family (`shody sho shodaiin`), f104|f115 `qokchedy cheos cheedy cheey`. These are the bifolia at the top of the LSA list (§5). Because the family changes from sheet to sheet, no test of one word, one band or one fixed rate can see it; any measure that adds up deviations across the vocabulary can.

**Reading.** What the Layfield-Davis LSA measures, beyond the shared sheet habit, is a **burst of a word family that runs across the inner face**: the two pages of the open sheet both lean towards the same family, more than their hand and section do and more than the two outer pages. That fits the bursts of frequent words that the real text has and the skribe lacks (L2, "long range": frequent words cluster more in the real text). The evidence is a secondary measure (p 0.018) and an exploratory split, so it is a lead, not a result. What would test it: a pre-registered burst measure (one family per sheet, fixed rule) on hand 2 and 3 alone, and whether the burst runs across the page turn at the bottom of a-v and top of b-r.

---

## 10 · npcompl33t's seriation: horseshoe or no horseshoe? (27/10/2026)

**Question** (Mauro, voynich.ninja thread 6219). npcompl33t (threads 6182, 6215, 6223) builds for each page the glyph transition counts (within words, and along the line without spaces), measures how different two pages are with a weighted Jensen-Shannon divergence of P(next glyph | glyph), and maps the pages with MDS. The first two dimensions draw a Guttman "horseshoe", the third an S or W, and the pages of a bifolium sit very close on the first dimension; he reads this as a production gradient. Rebuilt from his descriptions, not from his code (`npcompl33t/seriation.py`, figures `npcompl33t/figures.py`); paragraph text only, our glyph units, no curve fitting.

| | pages | arch on MDS1 × MDS2 | order of the sections along MDS1 | same-bifolium pages, |ΔMDS1| / range |
|---|---|---|---|---|
| real | 163 | yes, pharmaceutical at the top | herbal < pharmaceutical < … < stars < biological | 5.6% |
| skribe, 5 seeds | 162–167 | yes, the same shape | the same in all five | 5.3–6.1% |

**Reading.** The skribe, which has no chronology (hand and section habits, one taste per sheet, pages within a section interchangeable), draws the same horseshoe, the same S/W on MDS3 and the same bifolium closeness. Neither is evidence of a production order on its own. Within herbal A the real pages seem to drift with the folio number (Spearman +0.39, p 0.002), but it is the herbal pages bound in the pharmaceutical quires (f87–f96), which lean towards the pharmaceutical style; without them +0.23 (p 0.09), inside the skribe's range (−0.24 to +0.18). The skribe writes those pages like any other herbal page.

---

## 11 · npcompl33t's p/f arrows: is p/f an archaic k/t? (27/10/2026)

**Question** (voynich.ninja thread 6231). npcompl33t keeps only the words with a gallows, writes every gallows as G, pools per bifolium the words whose gallows are `p`/`f` and those whose gallows are `k`/`t`, and places both pools on his MDS of glyph transitions. In nearly every bifolium the arrow from the `p`/`f` pool to the `k`/`t` pool points the way his gradient runs, and the distance grows along the gradient. He reads this as `p`/`f` following older word construction than `k`/`t`, from a phase before the manuscript. Rebuilt from his description (`npcompl33t/pf_vectors.py`): the gradient is MDS1 of all the words of each sheet (B to the right); one MDS of every `p`/`f` and `k`/`t` pool; for each sheet with at least 120 glyphs of `p`/`f` words, the cosine between the arrow `p`/`f` → `k`/`t` and the direction in which the pools move with the gradient. Three skribes, 3 seeds each: the skribe of 27/10 (a first-line `p`/`f` never followed by `e`, `scribe/SCRIBE.md` §12), the same with the old random `k`→`p` swap, and that one without the first-line register.

| | sheets | mean cos | `k`/`t` ahead | gap grows with the gradient, r |
|---|---|---|---|---|
| real | 26 | 0.16 | 92% | +0.51 |
| skribe 27/10 | 16–20 | 0.08 to 0.11 | 68–80% | −0.25 to −0.12 |
| skribe, random swap | 19 | 0.31 to 0.38 | 89–100% | −0.39 to −0.19 |
| skribe, random swap, no first-line register | 18–26 | −0.03 to 0.31 | 56–95% | −0.41 to 0.00 |
| real, both pools from head lines only | 13 | −0.05 | 31% | +0.01 |
| real, control: `k`/`t` words of head lines against those of other lines | 20 | 0.00 | 50% | −0.46 |

**Reading.** The arrows point "forward" in the skribe as well, which has no chronology: hand and section habits, one taste per sheet, `p`/`f` made from `k`/`t` on the head line. So the direction of the arrows is not evidence of an archaic `p`/`f`. Nor does the rule about `e` explain them: the random swap gives them just as well. What the skribe does not reproduce is the gap growing along the gradient (real r +0.51, skribe negative in all nine runs). In the real text that growth, and the arrows themselves, vanish when both pools are taken from head lines only (31% ahead, r +0.01), but only 13 sheets are left, so this is a lead, not a result. Position alone does not make `k`/`t` lag (control, 50%).

The fact underneath, from the same thread: a plain `p`/`f` is never followed by `e` (5 cases against about 5,000 `ke`/`te`), in every section and on every line; where `k`/`t` take `e`, `p`/`f` take `ch`. That rules out a puff being a `k`/`t` swapped at random (a third would be followed by `e`) and also a plain `p` = `ke` (then `pe` = `kee`, which is common). Rule R1.3, amended; `scribe/SCRIBE.md` §12.

---

## 12 · Do two text-based orders of the bifolia agree? (27/10/2026)

**Question** (Mauro, voynich.ninja): npcompl33t's seriation is said to agree with the Layfield–Davis order of quires 13 and 20, odds 1/720 and 1/120 at face value. If both read the same signal, they would agree even on a text with no order. `npcompl33t/order_agreement.py`: in quires 1–7, 13 and 20, the order of the bifolia rebuilt as Layfield and Davis do (LSA, the permutation with the most similar pages at the junctions) and with npcompl33t's measure (the same search with his Jensen-Shannon of glyph transitions; and the order along his MDS1).

**Result.** The two orders do not agree: real text, mean Kendall tau −0.06 (p 0.65), 0 exact matches in 9 quires (0.4 expected by chance); skribe, −0.54 to +0.15, 0 to 3 exact matches. With these reconstructions the two methods behave as independent, so the reported match cannot be explained by a shared signal, and it cannot be reproduced either: npcompl33t's exact procedure and the Layfield–Davis sequences are needed.

## 13 · Can the sheets be put in a chain? (pre-registered, 27/10/2026)

`sheet_chain/` (`SHEET_CHAIN_PREREG.md`, `sheet_chain.py`). Sheets grouped by hand × section; three affinities between sheets (vocabulary, glyph transitions, the five free habits); pairwise residuals after removing what is typical of each sheet. **All three primary tests met**: vocabulary and glyphs agree on which sheets resemble each other (r 0.78, p 0.0002), far more than in the skribe (0.27–0.36), and sheets that are neighbours in the current nesting are a little closer (p 0.024). **But it is not a chain** (exploratory): almost all of it is herbal hand 1, it is one scale, the word family (share of words with *e*, rho −0.78), on which the real herbal sheets spread much more than the skribe's (SD 0.109 against 0.055–0.083), and that scale does not follow the order of the quires. Each herbal sheet takes a clear side, with or without *e*, more decidedly than the skribe's sheet habit makes it; a scale sorts the sheets but does not order them. The neighbouring-sheet effect is a small lead (9 neighbour pairs).

---

## 14 · Does the gradient run inside a hand? (28/10/2026)

npcompl33t's answer to §10 and §12: the skribe makes the horseshoe only because it is given the hands, and the hands sit at fixed points of his gradient, so the skribe "is receiving time". That assumes what is to be shown (that the hands are ordered in time). The part that can be tested: if the gradient is time, it should also run inside one hand and section, and follow the order of the folios there. Inside a hand × section the skribe has no order by construction. `npcompl33t/within_hand.py`, real text against five seeds of the skribe with R14.8.

| | real | skribe (5 seeds) |
|---|---|---|
| share of the gradient explained by the hand × section means | 0.94 | 0.97 [0.97, 0.98] |

Inside the cells (≥ 12 pages):

| hand, section | pages | horseshoe inside (R²) real / skribe | own axis vs gradient \|r\| real / skribe | Spearman gradient–folio real (p) / skribe |
|---|---|---|---|---|
| 1, herbal | 62 | 0.06 / 0.02 [0.00, 0.03] | 0.62 / 0.65 | +0.39 (0.002) / −0.06 [−0.21, 0.06] |
| 3, stars (Q20) | 24 | **0.45** / 0.04 [0.00, 0.14] | **0.95** / 0.80 | +0.23 (0.29) / −0.15 |
| 2, herbal | 20 | 0.12 / 0.09 | 0.52 / 0.44 | −0.29 (0.21) / 0.00 |
| 2, biological (Q13) | 19 | 0.21 / 0.07 | 0.04 / 0.52 | −0.39 (0.10) / +0.07 |
| 1, pharmaceutical | 16 | 0.01 / 0.01 | 0.18 / 0.35 | +0.11 (0.70) / −0.17 |

- The global gradient is the hands and sections: 94% of it in the real text, 97% in the skribe. With that much carried by the hands, the gradient alone cannot tell hands from time.
- Hand 1 herbal drifts with the folio number (+0.39), but mostly because its herbal pages in the late quires O and Q sit nearer the B side; in quires A–G alone the drift is +0.23 (p 0.10).
- Q13 (all hand 2): its pages' main axis has nothing to do with the gradient (|r| 0.04). Whatever orders Q13, it is not the gradient.
- Q20 (hand 3 stars) is the one place with structure the skribe lacks: a horseshoe inside the hand, on the same axis as the manuscript's gradient. It does not follow the folio order (p 0.29). Something varies continuously inside hand 3; the skribe does not do it.

---

## 15 · Q13's low MATTR when the skribe has not seen Q13 (28/10/2026)

npcompl33t (thread 6244): the skribe makes Q13 the poorest quire in MATTR (0.74 in both texts, thread 6244 post #15) only because it was trained on the pages it writes. `npcompl33t/q13_mattr_holdout.py`, five seeds:

| | Q13 | other quires | Q13's place (1 = poorest) |
|---|---|---|---|
| **learned from the odd folios, even folios written** | | | |
| real even folios | 0.736 | 0.831 | 1 of 5 |
| skribe | 0.734 | 0.811 | 1 of 5 |
| skribe, no copying | 0.751 | 0.851 | 1 of 5 |
| **learned without Q13** | | | |
| real | 0.736 | 0.828 | 1 of 11 |
| skribe | 0.805 | 0.808 | 4 of 11 |
| skribe, no copying | 0.840 | 0.841 | 6 of 11 |

- On pages it has not seen, the skribe still makes Q13 the poorest: the low MATTR is not memorised from those pages.
- Without any Q13 in the learning, hand 2's habits from its other sections do not make Q13 poor. The low MATTR comes from how the words are built in the biological section itself; it needs neither copying nor an order. So MATTR is not independent of section, but the skribe cannot predict it without having seen that section.
- Not reproduced: the page-to-page decline inside Bio that Koen and npcompl33t describe; in the real text the folio MATTR goes by sheet (the two halves of a bifolio are alike), which the skribe does not do.

## 16 · "kch/tch drop while pch does not" (28/10/2026)

npcompl33t (thread 6231), against §11: P/F words change differently from K/T even without *e*, e.g. kch and tch drop while pch does not. `npcompl33t/pf_next_glyph.py`: share of plain k/t and plain p/f followed by each glyph.

| | kch/tch | pch/fch | ke/te | ch + e after k/t |
|---|---|---|---|---|
| Herbal A | 33% | 56% | 14% | 48% |
| Pharma A | 6% | 33% | 56% | 62% |
| Herbal B | 11% | 51% | 34% | 45% |
| Bio B | 5% | 55% | 43% | 48% |
| Stars B | 10% | 59% | 43% | 53% |
| skribe (3 seeds), range over the groups | 5–13% (33% in Herbal A) | 44–65% | | |

kch/tch do fall, but ch + e after k/t stays roughly flat and near pch/fch: the *e* takes the place of *ch* after k/t, and p/f, which cannot take *e*, keep the *ch*. The skribe, with no chronology and only rule R1.3, gives the same picture. This example is the *e* rule, not P/F lagging. What §11 found the skribe does not reproduce remains: the PF–KT distance growing along the gradient (real r +0.51, skribe negative).

## 17 · npcompl33t's own chronology ensemble, run on the skribe (28/10/2026)

Rather than rebuilding his method from his posts (§10–§14), we ran his code: `eo777/voynich-clusters`, `chronology-stability/replication` (16/10/2026), the way his own RF1b study swaps the transcription. Same 207 paragraph pages, same 50 bifolio pools, same Golf 2.1 labels, masks, penalties and the eight anchor orders through the group centres; his counting (Zattera units, word and joined-line transitions), his weighted Jensen-Shannon, MDS, ElPiGraph growth and refinement, imported unchanged. Only the text changes. Consensus as his path-v2 default (1a before 1b, best fit per replicate, pairwise frequencies). 50 resampling replicates per text instead of his 100 (2,400 fits each). `npcompl33t/golf_ensemble/`.

Checks: his first saved fit replays to 2·10⁻¹⁶; our real text (ZL3b, as the skribe learns it) gives his published bifolio order exactly (Spearman 1.00; Q13 and Q20 identical).

| | real | skribe s1 | s2 | s3 |
|---|---|---|---|---|
| agreement of the 50 bifolio scores with his published order (Spearman) | 1.00 | 0.96 | 0.97 | 0.97 |
| Q13: order against his published one (Kendall tau) | +1.00 | +0.20 | +0.40 | +0.80 |
| Q13: decisiveness (1 = every fit gives the same order, 0 = coin flips) | **0.08** | 0.39 | 0.34 | 0.36 |
| Q20: order against his published one (Kendall tau) | +1.00 | +0.07 | +0.20 | −0.20 |
| Q20: decisiveness | **0.89** | 0.27 | 0.08 | 0.25 |
| fits with 3a before 3b / 4a before 4c | 0.55 / 0.47 | 0.57 / 0.46 | 0.46 / 0.42 | 0.57 / 0.37 |

- **The order of the manuscript as a whole** comes out almost the same from a text with no order between sheets (0.96–0.97). It is the hands and sections, plus the anchor order of the Golf groups the curve is started through.
- **Q13**: his own ensemble barely decides the order of its five bifolia (0.08: near coin flips for every pair); the skribe's Q13, whose sheets differ at random, is more decided than the real one. A match of Q13 with another reconstruction rests on an order his method does not establish.
- **Q20** is the exception, as in §14: the real text gives one order almost every time (0.89: 105, 104, 106, 107, 108, 103, the two last labelled 4c), the skribe gives weak orders that change with the seed. Something in the real Q20 varies from sheet to sheet in a consistent direction, and a text written the same way on every sheet does not do it. Whether it is time is not shown by this, but it is real.
- The B-group contrasts (3a/3b, 4a/4c) are near 50/50 in the real text too, which is why his page offers four paths.

## 18 · What the Q20 order follows (29/10/2026)

§17 left one real result: npcompl33t's ensemble orders the six Q20 bifolia the same way almost every time (105, 104, 106, 107, 108, 103), and the skribe's Q20 does not. Layfield and Davis's best LSA order for Q20 is the same sequence (their "Bifolia reordering experiments"), so two methods agree on it. What do they follow? `npcompl33t/q20/`, real text, page scores from the §17 fits.

- **It is a property of the sheet, not of the page.** Both halves of each bifolium get almost the same score (f103/f116 0.89, f105/f114 0.81). Against the physical nesting (outer 103-116 to inner 108-111) the sheet scores go down and up again (0.89, 0.84, 0.81, 0.84, 0.86, 0.88), so it is not a simple writing sequence through the quire.
- **The sheets choose between two word families.** 105-114 has daiin, aiin, otaiin, qotaiin, dair, ar, al in excess; the two last sheets (103-116 and 108-111, the two labelled 4c) share qokeey, qokeedy, okeey, chey, shedy, qokain, okain, otedy… and repeat themselves more (MATTR 0.89 → 0.78, top-20 coverage 18 → 30%, hapax 45 → 32%). These features vary between sheets 3 to 6 times more than in the skribe (`sheet_features.txt`, `excess_words.txt`).
- **The two families are the two registers of language B.** Scored with word models trained without any Q20 line, the page scores follow the likeness to Q13 (biological) against the rest of B, Spearman +0.93 on 23 pages (+0.94 on the 6 sheets), and the likeness to herbal B, −0.91 (−1.00). The Q20 sheets go from herbal-B vocabulary to biological vocabulary (`hidden_variable.txt`).
- **Not position, not copying drift.** The axis is the same with line-medial words only, with the first line of the paragraphs or the others, in the first half of the page or the second: each page is in one register from top to bottom. Hand and transcription marks that are not vocabulary (uncertain spaces 0.00, alternative readings +0.20) and the physical position (nesting +0.16) do not follow it.
- **Not page length.** The late pages are longer (351–568 words, +0.62), but with every page cut to 351 consecutive words the vocabulary axis stays (+0.93 likeness to Q13, +0.94 Q20 axis) and the repetition measures stay (MATTR −0.81) (`equal_length.txt`).
- **The same sheets are written more tightly** (Beinecke scans, `facsimile.txt`). Same page size and same glyph width, but the lines are closer (pitch 34.6 px on 108-111 and 36 on 103-116 against 37.5–38.5 on the 3c sheets; page rho −0.55) and the text starts higher on the page (sheet rho −0.83), hence 50–52 lines instead of 40–48. This is a second variable, not taken from the words, that moves with the first. It looks like two groups (the two 4c sheets against the four 3c) more than a line: 107-112, in the middle of the order, has the spacing of the 3c sheets.
- **Layfield and Davis's orders in our LSA rebuild** (`lisa_orders.txt`): their best Q20 order ranks 17th of 720 on the real text and 102nd–295th on the five skribe seeds; their best Q13 order ranks 21st of 120 (their second best, 2nd). The top of the list is flat (9 Q20 orders within 5% of the best), so the winner depends on transcription and preprocessing. npcompl33t's Q13 order ranks 118th of 120.

Reading: the Q20 order is the passage from one register of language B to the other, sheet by sheet, and both methods see it because both measure the composition of the text. The tighter writing on the same sheets points to two working batches. It does not show which batch came first (the direction of npcompl33t's axis comes from his anchor order), whether there is any order inside a batch, or why the register changes (time, subject or exemplar).

Decisiveness of the order in every quire (`decisiveness.txt`): Q20 0.89 against 0.08–0.27 in the skribe is the clearest case; herbal quires B (0.75 against 0.40–0.67) and D (0.90 against 0.55–0.61) are also more decided than the skribe; Q13 (0.08) is not.

---

## How to repeat it

```bash
cd scribe
PYTHONIOENCODING=utf-8 py -3 manuscript.py 1 2 3 4 5        # manuscript_out/real.txt and scribe_seed1..5.txt (8 s per seed)
cd ..
git clone https://github.com/labyrinthinesecurity/currier-signatures.git <outside the repository>
sed -i 's/signatures_v26/signatures_v27/g' <clone>/verifier.py <clone>/grille.py
PYTHONIOENCODING=utf-8 py -3 external_tests/parisel/run_parisel.py <clone>            # parisel/summary.txt (~20 s)
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/lsa_singulion.py [--k 75] [--stop 0]   # results_k75_stop0.txt
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/bifolium_asymmetry.py       # results_asymmetry_k75.txt (reordering their way)
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/bifolium_asymmetry2.py      # asymmetry2.txt (six measures, 30 s)
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/singulion_vs_nesting.py    # singulion_vs_nesting.txt (best singulion vs best nesting, 3 measures, ~2 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/lsa_anatomy.py [--images <Beinecke scans>]   # lsa_anatomy.txt (~5 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/fold_position.py          # fold_position.txt (pre-registered fold test + positive control, ~5 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/fold_position_lsa_link.py # fold_position_lsa_link.txt (injected copies and the LSA, ~15 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/sheet_order.py           # sheet_order.txt (pre-registered writing order in the sheet, ~15 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/lda_pairs.py             # lda_pairs.txt (the same pairs with LDA, ~30 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/lsa_whitening.py         # lsa_whitening.txt (pre-registered: what the LSA measures, ~20 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/shared_excess.py > external_tests/davis_layfield/shared_excess.txt   # exploratory follow-up
PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/figures.py              # seriation.txt, fig_horseshoe.png, fig_herbalA.png (~5 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/pf_vectors.py           # pf_vectors.txt (p/f arrows, real and 3 skribes x 3 seeds, ~8 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/within_hand.py          # within_hand.txt (the gradient inside each hand x section, ~1 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/q13_mattr_holdout.py    # q13_mattr_holdout.txt (Q13 MATTR, skribe not shown Q13, ~5 min)
PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/pf_next_glyph.py        # pf_next_glyph.txt (glyph after k/t and p/f, ~1 min)
# §17, his own code: clone eo777/voynich-clusters, copy chronology-stability/replication to NPC_WORK, make a Python venv with his
# requirements.txt plus pandas, and install elpigraph-python==0.3.4 with --no-deps --target into golf_stability_20261016/_deps and
# golf_published_stability_20261016/_deps of that copy. Then, in external_tests/npcompl33t/golf_ensemble:
PYTHONIOENCODING=utf-8 py -3 export_texts.py                       # texts.json (real text and skribe seeds 1-3)
<venv>/python run_golf.py replay                                   # his first saved fit, replayed (checks the environment)
<venv>/python run_golf.py run real 50 7                            # and skribe_s1, skribe_s2, skribe_s3 (~10 min each, 7 workers)
<venv>/python analyse_golf.py                                      # golf_results.txt (NPC_CLONE = his clone, for path-v2/bifolia.csv)
# §18, in external_tests/npcompl33t/q20 (page_scores.json is committed: only page_scores.py and decisiveness.py need the §17 fits)
PYTHONIOENCODING=utf-8 py -3 page_scores.py > page_scores.txt      # page scores of the §17 consensus -> page_scores.json
PYTHONIOENCODING=utf-8 py -3 decisiveness.py > decisiveness.txt    # how decided the order is in every quire
PYTHONIOENCODING=utf-8 py -3 sheet_features.py > sheet_features.txt   # features along the Q20 axis, real and skribe (~1 min)
PYTHONIOENCODING=utf-8 py -3 excess_words.py > excess_words.txt
PYTHONIOENCODING=utf-8 py -3 hidden_variable.py > hidden_variable.txt
PYTHONIOENCODING=utf-8 py -3 equal_length.py > equal_length.txt
PYTHONIOENCODING=utf-8 py -3 facsimile.py > facsimile.txt          # downloads 23 Beinecke scans into VMS_IMG once (~21 MB)
PYTHONIOENCODING=utf-8 py -3 lisa_orders.py > lisa_orders.txt      # needs scribe/manuscript_out (manuscript.py 1 2 3 4 5)
```

Known differences from the originals: Parisel calibrates on RF1b-e and we score normalised text from ZL3b (the real text passes all the same, 4/4). Layfield and Davis use ZL 2a with uncertain readings removed and separate the radial and circular text; here only paragraph text, which is the only text the skribe writes. Their stop-word heuristic is not described in enough detail to repeat it; without removing any, or removing the 20 most frequent, the result does not change.
