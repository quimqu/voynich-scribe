# external_tests/ciphers/

Code, results and notes for `writeup/CIPHERS.md` (29–31 October 2026): could a cipher turn Latin into Voynichese? The code comments and the long notes (`XIFRATS.md`) are in Catalan; the English write-up is `writeup/CIPHERS.md`.

| file | what it does | CIPHERS.md |
|---|---|---|
| `diag_parser.py`, `notebook_parser_vell.py` | the parser of my 2025 PM-Cipher notebook, run on `ZL3b-n.txt` and compared with the clean data | §1 |
| `lab.py` | data, entropy curves (word reset and held out), bits per word, the 76-measure battery (`_data/escriba/mesures.py`) | §2–3 |
| `pm_cipher_nb.py` | the functions of the 2025 notebook, copied as they were | §3 |
| `ciphers.py`, `corre.py`, `corre2.py`, `stego.py`, `grafica.py` | word-by-word ciphers, the model (Huffman) cipher, `xifrats.png` | §2–3 |
| `sobrant.py`, `sobrant_on.py`, `pagines.py` | real text against the skribe: bits per word, where the excess lives, subject or hand, labels | §4 |
| `xifrat_escriba.py`, `agrega.py`, `xifrat_extra.py` | the cipher hidden inside the skribe (rewrites `Escriba.write` in memory with a retry loop), seeds in `xe/`, nulls, plain language, decoding check | §5 |
| `ordre.py`, `classes.py`, `memoria_mots.py` (`mm/`) | word order, its shape (exchange clustering), the skribe with a word-pair habit | §6 |
| `ngrames.py`, `frases_controls.py`, `frases_quasi.py`, `frases_sense_articles.py` | repeated pairs, trigrams and longer sequences, against Gutenberg texts | §7 |
| `sil/` (`sillabes.py`, `SILLABES_PREREG.md`, `sillabes.txt`, `out/`) | the preregistered syllable code: criteria written before running, Latin and Italian (*Pinocchio*, Gutenberg 52484, included), 3 seeds full text and 3 on unseen pages; `py -3 sil/sillabes.py corre <tots\|senars> <la\|it> <seed>`, then `py -3 sil/sillabes.py agrega` | §8 |
| `XIFRATS.md` | the notes in Catalan, section by section, with every number | all |

The skribe is imported from `../../scribe/` (set `SCRIBE` to override). `_data/` holds small auxiliary files from my private notes: the 76-measure battery in Catalan and its slot table, the Latin control layout and *De docta ignorantia*. The Vietnamese and pinyin texts of the language test (`xifrat_extra.py llengua`) are not included. `frases_controls.py` downloads its Gutenberg texts to `_corpus/`.

Run everything from this folder with `py -3` (Python 3.12, numpy, scipy, pandas, matplotlib). Some runs take a long time: the cipher with 1–2 letters per word needs about an hour per seed.
