# Can the sheets be put in a chain? Pre-registration (27/10/2026, written before running `sheet_chain.py`)

**Question.** Each bifolio (sheet) was written in one sitting: its four pages share habits, vocabulary and hand, and a neighbouring page from another sheet does not (G6, H11; `writeup/THE_SCRIBE.md` §5). Ordering the bifolia of a quire by text similarity has so far given nothing reliable: the skribe, whose sheets have no order, "gains" more than the real text, and two text methods (LSA and npcompl33t's glyph transitions) give unrelated orders (`external_tests/npcompl33t/order_agreement.txt`). One residual remains: neighbouring pages share a little more vocabulary in the real text than in the skribe (0.35 against 0.31). If the sheets were written one after another with habits that drift, sheets written in succession should resemble each other more than other sheets of the same hand and section, and that order of writing could be rebuilt. The skribe is the null: it draws the tastes of every sheet independently.

**Units.** Sheets (`$F` in `scribe/manuscript_out/*.txt`) with at least two pages of paragraph text and at least 250 words, grouped by hand × section (the majority over the sheet's pages). Only groups with at least 4 sheets. Every comparison is between sheets of the same group, so hand and section are held fixed.

**Three affinities between two sheets** (each on the pooled text of the sheet):
- **VOC**: cosine of TF-IDF word vectors (words in at least 2 sheets).
- **GLY**: minus the square root of npcompl33t's weighted Jensen-Shannon dissimilarity of glyph transitions (`npcompl33t/seriation.py`).
- **HAB**: minus the Euclidean distance between the sheets' rates of the five free habits (`k` among `k`+`t`, `sh` among `ch`+`sh`, `q-` before `o-`, `-dy` among `-dy`+`-y`, words with `e`), each standardised within the group. Secondary: it is built from the same words as VOC.

In each group, every affinity matrix is reduced to its **pairwise residual**: the additive sheet effects (a sheet that is typical resembles every other) are removed, A_ij = μ + a_i + a_j + r_ij. Only r_ij, how much two particular sheets resemble each other beyond that, is used below.

**Primary tests** (alpha 0.05, Holm over the three):
- **P1 · Coherence.** Pearson r between the VOC and GLY residuals, pooled over the groups; p by permuting the sheets within each group (5,000 permutations). Real p < 0.05.
- **P2 · Beyond independent sheet tastes.** The real P1 r is larger than the P1 r of each of the five skribe seeds (a one-sided sign over 5 seeds; met only if all five are below the real one, p = 1/32 under exchangeability).
- **P3 · The current binding as a chain.** Pairs of sheets that are neighbours in the current nesting (same quire, consecutive positions, same group) have a higher combined residual (mean of the VOC and GLY residuals, each z-scored within the group) than the other pairs of the same group and quire; one-sided Mann-Whitney, real p < 0.05; and the real difference larger than in each of the five skribe seeds.

**Predictions.** Writing order with drifting habits: P1 and P2 hold; P3 holds if the binding keeps the writing order. Independent sheet tastes (the skribe's model): P1 may hold (a sheet's tastes show in both vocabulary and glyphs), P2 does not. No shared structure at all: P1 fails.

**Secondary (reported, not decisive).** HAB against VOC and GLY; the share of the combined residual explained by one dimension (a chain is one-dimensional, independent tastes are not), real against the skribe; herbal hand 1 alone. Only if P1 and P2 hold: a chain of the sheets in each group (spectral order of the combined affinity) and its agreement across the three measures.

Any other cut is exploratory and will be labelled as such.

---

## Outcome (added after running, 27/10/2026)

**All three primary tests met** (`sheet_chain.txt`; Holm P1 0.001, P2 0.049, P3 0.049). P1: the pairwise residuals of vocabulary and glyph transitions agree, r 0.778 (p 0.0002). P2: the five skribe seeds give 0.27–0.36. P3: sheets that are neighbours in the current nesting are closer than the other sheets of the same quire and group, +0.59 (p 0.024; skribe −0.23 to +0.27). Groups: herbal hand 1 (20 sheets), herbal hand 2 (5), stars hand 3 (7), biological hand 2 (5).

**What lies behind it (exploratory, not pre-registered).**
- Almost all of it is herbal hand 1 (r 0.76; skribe 0.17–0.33). The small groups give high r in the skribe too (few pairs). Without the two sheets from the pharmaceutical quires (O1, Q1) it stays at 0.757.
- It holds between sheets of different quires (r 0.76 over 174 pairs; same quire 0.83 over 16), and vocabulary and glyphs point to the same leading axis (|rho| 0.83; skribe 0.06–0.76).
- That axis is the word family: share of words with `e` rho −0.78, `-dy` among `-y` −0.56, `k` among `k`+`t` −0.47. The real herbal-A sheets spread much more along it than the skribe's: SD of the share of `e`-words between sheets 0.109 against 0.055–0.083, `-dy` 0.079 against 0.031–0.053. This is the same shortfall as the page overdispersion of `e`-words that the skribe misses (24.6 against 16.6): the skribe's sheet habit for the word family is too weak.
- The axis does not follow the order of the quires (|rho| with the quire letter 0.39; skribe 0.13–0.51). Order of the sheets along it: Q1 O1 G3 G4 C1 A3 A1 D3 F2 A2 G1 C2 C4 F4 E3 D4 B1 E4 B2 C3.

**Reading.** P1 and P2 do not show a chain: they show that each herbal sheet sits somewhere on one scale (more or fewer words with `e`) much more decidedly than the skribe's sheets do, and that vocabulary and glyphs both follow it, which is what a stronger sheet habit predicts. A single scale sorts the sheets but does not order them: sheets with the same value can come from any time. P3 (neighbouring sheets in a quire are alike, mostly herbal hand 1, 9 neighbour pairs against 7) is a lead that the quires group sheets of similar taste, whether because they were written in that order or because they were gathered by look; it is small. Next step for the skribe: a stronger sheet habit for the word family, then this test again.
