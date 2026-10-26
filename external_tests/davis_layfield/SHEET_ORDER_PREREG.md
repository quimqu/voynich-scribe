# Writing order within the sheet: pre-registration (25/10/2026, written before running `sheet_order.py`)

**Already seen (not evidence here).** With LSA, the six page pairs of a bifolium order themselves as if the folded sheet had been written as a booklet a-r, a-v, b-r, b-v: inner face a-v|b-r 0.284 > the two leaves a-r|a-v 0.234, b-r|b-v 0.221 > the diagonals 0.207–0.208 > outer face b-v|a-r 0.183; flat in the skribe (`results_asymmetry_k75.txt`). Two readings: **time** (the hand's habits drift while writing; pages written one after the other are closer) and **time + sight** (Q. Quadrada: a-v and b-r are also visible together on the open sheet, so they should beat the two leaves, which are written one after the other but never seen together).

**New measures (none of them looked at before).** Per page pair, on the same 37 complete bifolia of quires 1–7, 13, 20 (ZL3b paragraph text):
- **G3**: cosine of glyph-trigram TF-IDF vectors (trigrams inside words with word-boundary marks; no SVD).
- **XE**: cross-entropy gain: a glyph-bigram model of page x (add-0.5 smoothing towards the whole-manuscript model) scores page y; similarity = bits per glyph saved against the whole-manuscript model, averaged over both directions.
- **NMF**: cosine of word-topic weights from a 20-topic non-negative matrix factorisation of the same 40-word TF-IDF documents (a latent model that is not the SVD).
- LSA is reported for reference only.

**Primary tests (one-sided Wilcoxon, paired per bifolium, all 37 bifolia, each on G3 and XE; alpha 0.05 with Holm correction over the six):**
- **P1 · time:** mean of the three pairs written one after the other (a-r|a-v, a-v|b-r, b-r|b-v) > outer face (b-v|a-r).
- **P2 · sight:** inner face (a-v|b-r) > mean of the two leaves (a-r|a-v, b-r|b-v).
- **P3 · continuity across the page turn:** each page split into a top and a bottom half by lines; for the three consecutive transitions X → Y (a-r → a-v, a-v → b-r, b-r → b-v), C = sim(bottom of X, top of Y) − ½[sim(top X, top Y) + sim(bottom X, bottom Y)]; the mean C of the bifolium > 0. Control: the non-consecutive transition b-v → a-r, same C, expected ≈ 0.

**Predictions.** Time: P1 and P3 hold. Time + sight: P1, P2 and P3 hold. Neither: nothing holds on G3 or XE, and the LSA ordering is a property of the LSA.
**Secondary (reported, not decisive):** NMF; hand 1 and hand 2 separately; the five skribe seeds as null (their sheet habit is constant over the four pages, but they have line-to-line drift within a page, which may give some P3).

Any other cut is exploratory and will be labelled as such.


---

## Outcome (added after running, 25/10/2026)

**All six primary tests: not met** (Holm 0.58–1.00). G3: P1 +0.015 (p 0.15), P2 −0.004 (p 0.75), P3 +0.009 (p 0.10). XE: P1 +0.005 (p 0.29), P2 +0.005 (p 0.37), P3 +0.002 (p 0.31). Neither "time" nor "time + sight" holds on the two measures that are not latent models.

**Secondary.** NMF: P1 +0.061 (p 0.036), P2 p 0.26, P3 −0.033 (p 0.97). LSA (reference): P1 p 0.012, P2 p 0.050, P3 −0.005 (p 0.65); hand 2: P1 p 0.003, P3 −0.040. The skribe: P1, P2, P3 near zero with single seeds reaching p 0.00–0.04 on XE and G3.

**Validation (added afterwards, not pre-registered).** Within a page, split into thirds, all four measures see the adjacent thirds as closer than the top and bottom thirds (real: G3 p 0.0005, XE p 0.0002, NMF and LSA p < 0.0001; the skribe too). The measures can see drift at the scale of half a page, so the absence of continuity across the page turn (P3) is informative: what draws neighbouring lines together inside a page does not carry over to the next page, even with the LSA.
