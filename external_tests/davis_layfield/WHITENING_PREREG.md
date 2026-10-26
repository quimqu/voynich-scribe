# What the Davis-Layfield LSA measures: pre-registration (25/10/2026, written before running `lsa_whitening.py`)

**Hypothesis.** Folding a page as v = q U_k / S_k and taking the cosine is, up to the truncation at k, a *whitened* similarity: q_x (A^T A)^+ q_y, where A^T A is the word co-occurrence matrix of the 40-word documents. Whitening divides out the directions of large variation (the styles of hand and section, which the four pages of a sheet share) and compares pages on what is left: how each page **deviates from its hand's usual vocabulary**. The inner-face asymmetry (inner face a-v|b-r more similar than outer face b-v|a-r; §3, §5) would then mean that the two inner pages deviate from their hand's norm in the same direction more than the two outer pages do. Evidence so far: the effect grows with the whitening (q U S a quarter, q U two thirds, q U / S all of it; §5) and LDA, which is dominated by the large styles, does not see it (§8).

**Primary measure (transparent, no SVD): DEV.** For each page, the relative frequency of each word. For each bifolium, the norm of its hand = mean and standard deviation of each word's relative frequency over all other pages of the same hand (the four pages of the bifolium left out). Words used on at least 5 pages of that hand. A page's deviation vector = z-scores (frequency − mean) / sd. Similarity of two pages = cosine of their deviation vectors.

**Primary test.** Inner face minus outer face, paired per bifolium, one-sided Wilcoxon (inner greater), on (a) all 37 bifolia and (b) hand 2 (10 bifolia); Holm over the two; alpha 0.05.
**Prediction if the hypothesis is right:** DEV shows inner > outer (at least in hand 2), and the real text exceeds the five skribe seeds. **If not:** DEV is flat, and what the LSA picks up is not "shared deviation from the hand's norm".

**Secondary (reported, not decisive):** the same deviation measure with the norm of hand × section; full-rank whitened similarity q (A^T A + λI)^-1 q' for three ridges λ (the 25th, 75th and 150th eigenvalue), to separate whitening from truncation; plain cosine after removing the top r principal directions (r = 5, 10, 25); the six-pair ordering (P1) for DEV.

Any other cut is exploratory and will be labelled as such.


---

## Outcome (added after running, 25/10/2026)

**Primary (DEV against the hand norm): not met.** All bifolia +0.025, one-sided p 0.15; hand 2 +0.047, p 0.080 (Holm 0.16 both). Same direction, not significant.

**Secondary.** DEV against the **hand × section** norm: +0.064, p 0.018 (34 bifolia); hand 2 +0.105, p 0.037; the skribe +0.005 (p 0.24–0.88). Full-rank ridge-whitened similarity (no truncation): p 0.017–0.019 at all three ridges, hand 2 p 0.014. Plain cosine after removing the top 5 or 10 directions: p 0.007 and 0.005 (hand 2 p 0.002, 0.005); after removing 25, p 0.066. Plain TF-IDF cosine: p 0.043 (hand 2 p 0.007). The skribe is flat in every one.

**Exploratory follow-up (`shared_excess.py`).** Splitting DEV (hand × section) into shared excess and shared deficit: the effect is all excess (+0.075, p 0.007; deficit −0.003, p 0.55); not related to page length (Spearman +0.19, p 0.29). It is carried by a different word family in each bifolium, used above the norm on both inner pages: f108|f111 `lkeedy qokeedy qoteedy keedy`; f33|f40 `oky okar dal chdy`; f50|f55 `chody otar ykar okal`; f4|f5 `shody sho shodaiin`; f104|f115 `qokchedy cheos cheedy cheey`.
