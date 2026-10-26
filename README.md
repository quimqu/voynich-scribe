# The skribe (name as Stolfi suggested): a meaningless procedure that writes a Voynich-like text

This repository contains "the skribe", a small program that writes a complete fake Voynich manuscript on the real manuscript's layout: same pages, same sheets, same paragraphs, same number of lines and words per line, same gaps for the drawings, Currier A and B, the five Davis hands. There is no meaning anywhere in it. It only follows writing rules that were first measured on the real text, and it is scored against the real text with a battery of 82 statistics.

It also contains the battery, the rulebook the skribe implements, the generated text, and two tests designed by other people (Parisel 2026; Layfield and Davis 2026) run on the skribe's output.

It was called "the scribe" until 26 October 2026; Jorge Stolfi suggested "skribe" so that the program is not confused with the human scribes of the manuscript. The file and folder names keep the old spelling (`scribe/`, `scribe.py`, `voynich-scribe`) so that links and commands do not break.

Author: Quim Quadrada (quimqu on voynich.ninja). The work was presented in two forum posts, on 18 October 2026 ([the generator](writeup/post_generator.txt)) and 25 October 2026 ([the external tests](writeup/post_external_tests.txt)), in thread 6219 of voynich.ninja. A preprint is in preparation.

## What it does

For each word the skribe either copies a word already written nearby on the page (often changing one glyph, with the same two-glyph rule used for new words) or writes a new word glyph by glyph, with a memory of the two previous glyphs. On top of that it follows the rules of place: how a word starts depends on how the previous one ended; the first word of a line prefers d, s or y and avoids the first glyph of the line above; the last word of a line is "closed" (aiin becomes am, ol becomes oly); a paragraph starts with a gallows and its first line is written in a register of its own (p and f, sh rather than ch, t rather than k, rarer words); a drawing is treated as a margin; each sheet (the folded piece of vellum, four pages) has its own taste for the free choices (k or t, ch or sh, q or not, dy or y, words with e or without); each hand and each section has its own vocabulary of glyph habits; and each line is more or less inclined to start its words with a gallows. Everything is described in plain words in [writeup/THE_SCRIBE.md](writeup/THE_SCRIBE.md) and, rule by rule with its strength and source, in [RULES.md](RULES.md).

## Results

The fake text is compared with the real one on 82 measures (repetition at several distances, twins on the same page, line start and end forms, paragraph forms, page and sheet habits, entropies, Zipf, word lengths, long-range similarity between pages, bursts, words that start with a gallows, the register of the first line). A measure counts as reproduced when the skribe's value is within 25% of the real one, averaged over five runs.

| comparison | reproduced | median error |
|---|---|---|
| a simple three-rule generator (baseline) vs the real text | 44 / 82 | 0.25 |
| **the skribe vs the real text** | **78 / 82** | **0.060** |
| the skribe learned from the odd folios only, writing the even folios, vs the real even folios | 69 / 82 | 0.068 |
| the real odd folios vs the real even folios (the ceiling) | 73 / 82 | 0.049 |

*26 October 2026, two additions, both calibrated on the odd folios only. (1) A line habit for words that start with a gallows (rule R14.7), after remarks by dashstofsk and nablator on voynich.ninja: it reproduces the clustering of these words by line and changes no other rule, but does not improve the score as a whole (`scribe/SCRIBE.md` §10). (2) The register of the first line of the paragraph (rule R5.2, amended): sh rather than ch, t rather than k, rarer words, fewer ee. This one does improve the skribe, above all where it was not fitted: on the even folios from 65 / 82 (0.089) to 69 / 82 (0.068), and it makes the old rule against repeating on the first line unnecessary (`scribe/SCRIBE.md` §11). Before both, the skribe scored 69 / 76 (0.067) and 61 / 76 on the even folios.*

The three-rule generator is the first generator of the project (`night_generator/generator3.py`): new words glyph by glyph with one two-glyph table for the whole manuscript, copying of nearby words (same line and the two lines above, mostly changed by one glyph), and a memory that is emptied at each page and paragraph, plus a crude line-start avoidance and *-iin* → *-m* at line end. It has no hands, sections, sheet habits or rules of place beyond those; it shows how much of the score the rest of the rulebook earns. Details in [writeup/THE_SCRIBE.md](writeup/THE_SCRIBE.md) §3.

Removing any single rule costs measures, except two switches that are no longer in use (the A/B tables, replaced by the per-hand and per-section ones, and the section dy, off since 19 October) (`scribe/results_ablations_table.txt`; the same ablations without the first-line register in `results_ablations_without_fl_table.txt`, and without the gallows habit, on 78 measures, in `results_ablations_without_g0_table.txt`). What it still gets wrong: which frequent words avoid repeating, the m at the end of long lines, the q- on the first word of a paragraph (at the threshold), the page overdispersion of words with e, and the clustering of words that start with a bench gallows (cth-, ckh-) in herbal A. Some measures (neighbours one glyph apart, H8, a- at line start, the repeats on the first line) pass or fail depending on the seed. Details in `scribe/SCRIBE.md` (the lab notebook of the skribe) and `writeup/THE_SCRIBE.md` (English).

**External tests** (25 October 2026, run on the skribe of 19 October, [external_tests/EXTERNAL_TESTS.md](external_tests/EXTERNAL_TESTS.md)):

- **Parisel (arXiv 2604.19762)** defines four signatures of the boundary between words, calibrated per Currier dialect, that no slot-based generator or Cardan grille passes at once. Run with his own verifier, the skribe passes all four in Currier A and in Currier B, in all five runs, with values close to his references (end-to-start rate 68 to 70% in A against 71, 63 to 66% in B against 64; boundary mutual information 0.53 to 0.54 in A against 0.59, 0.45 to 0.47 in B against 0.50).
- **Layfield and Davis (Digital Medievalist 19, 2026)** read the LSA similarity between pages (pages of the same bifolium more similar than pages that face each other in the current binding) as evidence that the bifolia were loose sheets bound in the wrong order. The same LSA on the real text reproduces their pattern and their p values; on the skribe, which has sheet habits and no notion of reading order, it gives the same pattern. Their reordering by maximum similarity gains more on the skribe (61% and 78%) than on the real text (33% and 50%). The text similarity measures the writing session, not the reading order.
- **Singulion or nesting?** With their LSA the best singulion order beats the best nested order in 8 of 9 quires; with plain shared vocabulary it does not (5 of 9). The whole gain comes from one pair, the inner face of the bifolium. Two pre-registered tests (copies near the fold; writing order within the sheet) and LDA do not see it; once the hand and section styles are removed, it looks like a burst of one word family shared by the two inner pages, a different family in each sheet (a lead, not a result). Sections 4 to 9 of `EXTERNAL_TESTS.md`.

## What it does not show

It does not prove the Voynich has no meaning. It shows that a procedure with no meaning is enough for most of what we can measure. The tables behind the rules are learned from the text, so the skribe says how the pieces combine, not where the glyph grammar comes from. The idea is very close to Torsten Timm's self-citation hypothesis (Timm and Schinner), reached by another road: measurement first, generator after.

## How to reproduce

You need Python 3.11 or later with numpy, pandas and scipy (`pip install -r requirements.txt`). On Windows the author runs everything with `py -3`; replace by `python3` elsewhere. Every script is run from the folder stated here, with relative paths.

```bash
cd scribe
python3 measures.py        # the 82 measures of the real text -> measures_real.json (about 1 min)
python3 compare.py        # real text, three-rule baseline and the skribe, five seeds -> results.json and a table (about 10 min)
python3 holdout.py        # learn from the odd folios, write the even ones (about 10 min)
python3 manuscript.py 1 2 3 4 5   # write the whole manuscript five times -> manuscript_out/ (8 s per seed)
python3 compare.py ablations     # the skribe with each rule removed (about an hour)
```

The external tests, from the repository root:

```bash
python3 external_tests/davis_layfield/lsa_singulion.py       # Layfield and Davis's LSA on the real text and the five seeds
python3 external_tests/davis_layfield/bifolium_asymmetry2.py   # within-bifolium pair types with six similarity measures
git clone https://github.com/labyrinthinesecurity/currier-signatures.git ../currier-signatures   # Parisel's verifier
sed -i 's/signatures_v26/signatures_v27/g' ../currier-signatures/verifier.py ../currier-signatures/grille.py
python3 external_tests/parisel/run_parisel.py ../currier-signatures
```

The dataset `df_lines_ZL3b_strokes.csv` is built from the ZL3b transliteration by `python3 build_df.py` (run from the root; it reproduces the file byte for byte). All result files are included, so you can compare your run with the author's before changing anything.

## Layout

| path | content |
|---|---|
| `scribe/scribe.py` | the skribe |
| `scribe/measures.py` | the battery of 82 measures and the loader of the real text |
| `scribe/compare.py`, `holdout.py` | comparison with the real text, ablations, odd/even hold-out |
| `scribe/manuscript.py`, `quire.py` | write the whole manuscript, or one quire, in an IVTFF-like format with the ZL3b line identifiers |
| `scribe/standard_measures.py`, `boundary_per_hand.py`, `controls/` | standard entropy and Zipf measures; the boundary coupling per hand; the control with a real language (Latin, Cusanus) |
| `scribe/*.json`, `scribe/*_table.txt` | learned tables and all results |
| `scribe/manuscript_out/`, `scribe/quire_M/` | the generated text (five seeds of the whole manuscript; quire 13 real, generated, and generated blind) |
| `night_generator/` | the three-rule generator used as baseline, and the slot grammar used by one measure |
| `external_tests/` | the two external tests: scripts, outputs and write-up |
| `writeup/` | the English write-up and the forum posts |
| `RULES.md` | the rulebook, rule by rule, with strength, system/habit and source |
| `ZL3b-n.txt`, `build_df.py`, `df_lines_ZL3b_strokes.csv`, `DATASET.md` | the transliteration, the script that turns it into the line dataset, the dataset, and its documentation |

`RULES.md`, `scribe/SCRIBE.md` and `DATASET.md` are translated from the lab notebook of the project (originally in Catalan); `writeup/THE_SCRIBE.md` covers the same ground for a general reader.

## Data and credits

- Transliteration: Zandbergen-Landini ZL, version 3b (13 May 2025), IVTFF 2.0, from [voynich.nu](https://www.voynich.nu/transcr.html), where it is made available under CC0. Please acknowledge voynich.nu.
- Scribal hands: Lisa Fagin Davis (2020). Currier languages: Prescott Currier (1976).
- Self-citation: Torsten Timm and Andreas Schinner (2014, 2020); the convergence with their picture is discussed in the write-up.
- External tests: Christophe Parisel, *Evidence of Layered Positional and Directional Constraints in the Voynich Manuscript* (arXiv 2604.19762, 2026) and his [verifier](https://github.com/labyrinthinesecurity/currier-signatures); Colin Layfield and Lisa Fagin Davis, *Singulion Structure and the Voynich Manuscript* (Digital Medievalist 19, 2026, doi 10.4000/16k0a).
- The Latin control text is Nicholas of Cusa's *De docta ignorantia* (15th century).

The code was written with Claude Code (Anthropic) as a coding assistant. The questions, the decisions and the checking of every figure are the author's.

## Licence and citation

Code: MIT. Documents and write-ups: CC BY 4.0. Generated texts: CC0. See [LICENSE](LICENSE). To cite, see [CITATION.cff](CITATION.cff); a DOI will be added with the first release.
