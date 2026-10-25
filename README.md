# The scribe: a meaningless procedure that writes a Voynich-like text

This repository contains "the scribe", a small program that writes a complete fake Voynich manuscript on the real manuscript's layout: same pages, same sheets, same paragraphs, same number of lines and words per line, same gaps for the drawings, Currier A and B, the five Davis hands. There is no meaning anywhere in it. It only follows writing rules that were first measured on the real text, and it is scored against the real text with a battery of 76 statistics.

It also contains the battery, the rulebook the scribe implements, the generated text, and two tests designed by other people (Parisel 2026; Layfield and Davis 2026) run on the scribe's output.

Author: Quim Quadrada (quimqu on voynich.ninja). The work was presented in two forum posts, on 18 October 2026 ([the generator](writeup/post_escriba_generador.txt)) and 25 October 2026 ([the external tests](writeup/post_proves_externes.txt)), in thread 6219 of voynich.ninja. A preprint is in preparation.

## What it does

For each word the scribe either copies a word already written nearby on the page (often changing one glyph, with the same two-glyph rule used for new words) or writes a new word glyph by glyph, with a memory of the two previous glyphs. On top of that it follows the rules of place: how a word starts depends on how the previous one ended; the first word of a line prefers d, s or y and avoids the first glyph of the line above; the last word of a line is "closed" (aiin becomes am, ol becomes oly); a paragraph starts with a gallows and its first line uses p and f; a drawing is treated as a margin; each sheet (the folded piece of vellum, four pages) has its own taste for the free choices (k or t, ch or sh, q or not, dy or y, words with e or without); each hand and each section has its own vocabulary of glyph habits. Everything is described in plain words in [writeup/THE_SCRIBE.md](writeup/THE_SCRIBE.md) and, rule by rule with its strength and source, in [REGLES_DEL_SISTEMA.md](REGLES_DEL_SISTEMA.md) (in Catalan).

## Results

The fake text is compared with the real one on 76 measures (repetition at several distances, twins on the same page, line start and end forms, paragraph forms, page and sheet habits, entropies, Zipf, word lengths, long-range similarity between pages, bursts). A measure counts as reproduced when the scribe's value is within 25% of the real one, averaged over five runs.

| comparison | reproduced | median error |
|---|---|---|
| a simple three-rule generator (baseline) vs the real text | 39 / 76 | 0.26 |
| **the scribe vs the real text** | **69 / 76** | **0.067** |
| the scribe learned from the odd folios only, writing the even folios, vs the real even folios | 61 / 76 | 0.080 |
| the real odd folios vs the real even folios (the ceiling) | 67 / 76 | 0.049 |

Removing any single rule costs measures (`escriba/resultats_ablacions_19_10_taula.txt`). What it still gets wrong: a few exact-repeat and distance-5 repeat rates, which words avoid repeating, the m at the end of long lines, and a third too many words of eight or more glyphs. Details in `escriba/ESCRIBA.md` (Catalan) and `writeup/THE_SCRIBE.md` (English).

**External tests** (25 October 2026, [proves_externes/PROVES_EXTERNES.md](proves_externes/PROVES_EXTERNES.md)):

- **Parisel (arXiv 2604.19762)** defines four signatures of the boundary between words, calibrated per Currier dialect, that no slot-based generator or Cardan grille passes at once. Run with his own verifier, the scribe passes all four in Currier A and in Currier B, in all five runs, with values close to his references (end-to-start rate 68 to 70% in A against 71, 63 to 66% in B against 64; boundary mutual information 0.53 to 0.54 in A against 0.59, 0.45 to 0.47 in B against 0.50).
- **Layfield and Davis (Digital Medievalist 19, 2026)** read the LSA similarity between pages (pages of the same bifolium more similar than pages that face each other in the current binding) as evidence that the bifolia were loose sheets bound in the wrong order. The same LSA on the real text reproduces their pattern and their p values; on the scribe, which has sheet habits and no notion of reading order, it gives the same pattern. Their reordering by maximum similarity gains more on the scribe (61% and 78%) than on the real text (33% and 50%). The text similarity measures the writing session, not the reading order.

## What it does not show

It does not prove the Voynich has no meaning. It shows that a procedure with no meaning is enough for most of what we can measure. The tables behind the rules are learned from the text, so the scribe says how the pieces combine, not where the glyph grammar comes from. The idea is very close to Torsten Timm's self-citation hypothesis (Timm and Schinner), reached by another road: measurement first, generator after.

## How to reproduce

You need Python 3.11 or later with numpy, pandas and scipy (`pip install -r requirements.txt`). On Windows the author runs everything with `py -3`; replace by `python3` elsewhere. Every script is run from the folder stated here, with relative paths.

```bash
cd escriba
python3 mesures.py        # the 76 measures of the real text -> mesures_real.json (about 1 min)
python3 compara.py        # real text, three-rule baseline and the scribe, five seeds -> resultats.json and a table (about 10 min)
python3 holdout.py        # learn from the odd folios, write the even ones (about 10 min)
python3 manuscrit.py 1 2 3 4 5   # write the whole manuscript five times -> manuscrit_out/ (8 s per seed)
python3 compara.py ablacions     # the scribe with each rule removed (about an hour)
```

The external tests, from the repository root:

```bash
python3 proves_externes/davis_layfield/lsa_singulion.py       # Layfield and Davis's LSA on the real text and the five seeds
python3 proves_externes/davis_layfield/asimetria_bifoli2.py   # within-bifolium pair types with six similarity measures
git clone https://github.com/labyrinthinesecurity/currier-signatures.git ../currier-signatures   # Parisel's verifier
sed -i 's/signatures_v26/signatures_v27/g' ../currier-signatures/verifier.py ../currier-signatures/grille.py
python3 proves_externes/parisel/run_parisel.py ../currier-signatures
```

The dataset `df_lines_ZL3b_strokes.csv` is built from the ZL3b transliteration by `python3 build_df.py` (run from the root; it reproduces the file byte for byte). All result files are included, so you can compare your run with the author's before changing anything.

## Layout

| path | content |
|---|---|
| `escriba/escriba.py` | the scribe |
| `escriba/mesures.py` | the battery of 76 measures and the loader of the real text |
| `escriba/compara.py`, `holdout.py` | comparison with the real text, ablations, odd/even hold-out |
| `escriba/manuscrit.py`, `quadern.py` | write the whole manuscript, or one quire, in an IVTFF-like format with the ZL3b line identifiers |
| `escriba/estandard.py`, `frontera_per_ma.py`, `controls/` | standard entropy and Zipf measures; the boundary coupling per hand; the control with a real language (Latin, Cusanus) |
| `escriba/*.json`, `escriba/*_taula.txt` | learned tables and all results |
| `escriba/manuscrit_out/`, `escriba/quadern_M/` | the generated text (five seeds of the whole manuscript; quire 13 real, generated, and generated blind) |
| `night_generator/` | the three-rule generator used as baseline, and the slot grammar used by one measure |
| `proves_externes/` | the two external tests: scripts, outputs and write-up |
| `writeup/` | the English write-up and the forum posts |
| `REGLES_DEL_SISTEMA.md` | the rulebook, rule by rule, with strength, system/habit and source (Catalan) |
| `ZL3b-n.txt`, `build_df.py`, `df_lines_ZL3b_strokes.csv`, `README_df_ZL3b_strokes.md` | the transliteration, the script that turns it into the line dataset, the dataset, and its documentation (Catalan) |

The documents in Catalan are the lab notebook of the project; the English write-up covers the same ground.

## Data and credits

- Transliteration: Zandbergen-Landini ZL, version 3b (13 May 2025), IVTFF 2.0, from [voynich.nu](https://www.voynich.nu/transcr.html), where it is made available under CC0. Please acknowledge voynich.nu.
- Scribal hands: Lisa Fagin Davis (2020). Currier languages: Prescott Currier (1976).
- Self-citation: Torsten Timm and Andreas Schinner (2014, 2020); the convergence with their picture is discussed in the write-up.
- External tests: Christophe Parisel, *Evidence of Layered Positional and Directional Constraints in the Voynich Manuscript* (arXiv 2604.19762, 2026) and his [verifier](https://github.com/labyrinthinesecurity/currier-signatures); Colin Layfield and Lisa Fagin Davis, *Singulion Structure and the Voynich Manuscript* (Digital Medievalist 19, 2026, doi 10.4000/16k0a).
- The Latin control text is Nicholas of Cusa's *De docta ignorantia* (15th century).

The code was written with Claude Code (Anthropic) as a coding assistant. The questions, the decisions and the checking of every figure are the author's.

## Licence and citation

Code: MIT. Documents and write-ups: CC BY 4.0. Generated texts: CC0. See [LICENSE](LICENSE). To cite, see [CITATION.cff](CITATION.cff); a DOI will be added with the first release.
