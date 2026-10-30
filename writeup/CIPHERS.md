# Could a cipher turn Latin into Voynichese? Ciphers tested against the skribe

*What a cipher would have to do to produce the Voynich text from a natural language, what it would cost, and where the real text differs from a meaningless procedure. Written on 30 October 2026. Code, data and results: `external_tests/ciphers/` (comments in Catalan; the long Catalan notes are `external_tests/ciphers/XIFRATS.md`).*

---

## Summary

- **The entropy "bump" is the shape of the words, not a cipher.** Inside a word, the Voynich has a two-glyph memory: conditional entropy stays almost flat from n = 2 to n = 5 (2.08, 1.86, 1.74, 1.46), while Latin keeps falling (3.09, 2.25, 1.34, 0.82). Any scheme whose output words are Voynich-shaped reproduces the curve for free. My own Positional Mimic Cipher of 2025 (thread 4921) matches H2 only because it moves about **10 bits per word** into the side note ("residuals"); the glyph plus residual stream has the Latin curve.
- **A cipher that writes the plain text word by word fails where a language fails.** Nomenclators, homophones and Naibbe-type schemes reach 27–36 of 76 measures. They miss repetition, the line and paragraph rules, and the order of words. A nomenclator also carries the syntax of the plain text: 0.31–0.34 bits of word-order information, against 0.09 in the Voynich.
- **A cipher can be hidden inside the skribe.** Let the skribe write as usual, and accept each word only if its form (with the scribal layer undone: line-end closure, *p*/*f*, *q-*) falls in the class of the next plain-text letter. It decodes exactly (checked on the whole manuscript), and with one letter per word it reproduces **74/88** (the skribe alone 81/88; on unseen pages 70 against 75). With repetitions as nulls, 78/88. The price is space: **2,700 to 7,200 Latin words** in the whole manuscript, depending on the variant. So the statistics we have cannot exclude a small hidden text.
- **The real text costs a little more than the skribe's**: 0.3–0.45 bits per word (3%). The excess is lexical: mid-frequency words the skribe does not choose often enough. It follows the hand, not the subject: two pages of the same hand and different section share twice as many keywords as two pages of the same section and different hand. Labels do not occur in the text of their own page more than in any other page of the section.
- **The biggest gap of the skribe was the order of words** (real 0.088 bits, skribe 0.03). A Latin message one letter per word fills it exactly (0.085), but with the wrong shape: in the cipher, two word classes already recover it (0.07, it is the vowel and consonant rhythm of Latin); in the real text two classes recover almost nothing (0.012), and it only appears from 16 classes on. **A small habit fills it with the right shape and no message**: chaining a few dozen learnt word pairs in about 4% of the words (0.08; 0.001–0.010 with two classes; battery 74–79/88).
- **The Voynich repeats nothing longer than two words.** In 32,284 words: 94 three-word sequences seen twice or more, one four-word sequence, no five-word sequence. Herbals, recipe books, novels and word-by-word ciphers of the same size repeat hundreds of trigrams and dozens of five-word sequences, even in languages without articles (Finnish: 309, 88, 30). The skribe with the pair habit makes 100, 4 and 0.

**Reading.** A concrete writing procedure, with one more small habit (word pairs), accounts for everything measured here. If there is a message, it has to sit in the free choices of the scribe, written with many symbols (syllables or letter pairs, not one letter per word, not whole words), and it is short. This does not prove that there is no message; it says what kind, and how big, a message could still be.

---

## 1. Data

- **Voynich**: ZL3b (Zandbergen and Landini, IVTFF 2.0), paragraph text only, uncertain spaces joined, drawing gaps as spaces: 32,284 words. The same text the skribe learns from.
- **Plain text**: *De docta ignorantia* (Nicholas of Cusa), cut to the same number of words and poured into the real layout (same lines, pages, paragraphs and gaps). For the language test also Vietnamese (VIQR) and Mandarin (pinyin); for the phrase test several Project Gutenberg texts.
- **Measures**: the battery of the skribe (76 measures in §3, run with the skribe of 19 October; 88 from §5 on, with the skribe of 28 October, 98ecf31), entropy curves, held-out bits per word, and the word-order information used in the Latin control (mutual information between consecutive words of a line, top 200 words, minus the same text shuffled within each line).
- **Unseen pages**: learn from odd folios, write the even folios, compare with the real even folios. The two real halves agree on 78/88.

A note on the old notebook: the parser I used in 2025 turned comments such as `<!@254;>` into glyphs (33 "glyphs" in the biological section instead of 21), glued the two words on each side of a drawing gap, split uncertain spaces and mixed labels into the text. With clean data the Voynich H2 is 2.08, not 1.75.

## 2. The bump

Conditional entropy of the n-th glyph given the n−1 before, inside the word (the estimator of the notebook):

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Voynich | 3.86 | **2.08** | **1.86** | **1.74** | 1.46 | 1.12 | 0.65 | 0.29 |
| Latin | 3.94 | 3.09 | 2.25 | 1.34 | 0.82 | 0.60 | 0.54 | 0.50 |

Held out (Witten-Bell, spaces as symbols) the Voynich bottoms out at order 3 (1.93 bits per glyph) and Latin at order 5 (1.92). Both Currier languages have the plateau. In Latin, the beginning of a word tells you the rest (a lexical memory); in the Voynich, after the previous glyph, more context hardly helps.

## 3. Ciphers that write the plain text word by word

Battery of 76 measures (skribe of 19 October era):

| scheme | H2 | battery | word order (bits) | side note (bits/word) |
|---|---|---|---|---|
| Voynich | 2.08 | 76 | 0.088 | |
| Latin, plain | 3.09 | 18 | 0.305 | |
| **PM-Cipher (2025 notebook, rerun on clean data)** | 2.18 | 20 | 0.270 | **10.2** |
| letter + random digit (my "homophonic" test of June 2025) | 2.61 | 11 | | 0 |
| Naibbe-type: 1–2 letters to one real Voynich word | 2.08 | 28 | 0.062 | 0 |
| nomenclator: Latin word to Voynich word by rank | 1.96 | 27 | 0.305 | 0 |
| nomenclator + homophones + boundary rule | 2.07 | 36 | 0.337 | 0 |
| model cipher: Huffman over a simple Voynich model | | 44 | 0.058 | 0 |

- The PM-Cipher lowers H2 by mapping several letters to one glyph at each position; the information goes to the residual note (1.79 bits per glyph). A one-to-one substitution leaves the curve exactly as in Latin.
- The letter + digit scheme does not make the bump on clean EVA data.
- Every scheme that outputs Voynich words gets the curve right without trying. The curve does not discriminate.
- All the word-by-word schemes miss the same things: the real text repeats the previous word 3.1 times more than chance (ciphers 0.1–0.3), its line starts with *d/s/y-* 48% of the time (ciphers 11–18%), 93% of paragraphs start with a gallows (32–60%), 27% of line-final words are closed (1–5%).
- **Any generator can be turned into a cipher**: build a Huffman tree over the model's probabilities for the next word and let the bits of the plain text choose the path. Whoever has the model rebuilds the tree and reads the bits back (checked). The output is as good as the model. With this simple model each word carries 8.2–8.5 bits, so the whole manuscript holds about 10,000 Latin words written letter by letter.

## 4. Where the real text exceeds the skribe

Same estimator for every text: learn from odd folios, measure the cost of the even folios in bits per word.

| text | characters | words | context model |
|---|---|---|---|
| Voynich | **12.35** | **12.76** | **13.36** |
| skribe, 3 seeds | 11.96–12.06 | 12.42–12.58 | 12.74–12.96 |

A model learnt from the skribe loses 1.0 bit per word more on the real text than on another skribe text. A model learnt from the real text predicts the skribe better than the real text itself: the skribe is a more "typical" version of the real text.

Where the excess lives: half of it in mid-frequency words (3–20 occurrences: `cheeky`, `sheeky`, `orain`, `olkeedy`, `qotol`, `opchey`), a quarter in rare words, almost none in the most frequent ones. By position, the paragraph-initial word (0.92 bits), the line-final word (0.67) and the first line (0.64), the registers the skribe only half does. Flat across sections.

Is it subject matter? Three tests, real against skribe:

- **Concentration on the page** (index of dispersion of mid-frequency words within hand × section): real 1.27, skribe 1.24–1.28, shuffled 1.01. Latin, which has subjects, 1.53.
- **Who shares keywords** (TF-IDF cosine, pages of different sheets): same hand and different section 0.055, same section and different hand 0.027. The skribe gives the same table to the third decimal.
- **Labels in the text of their own page**: 9.3% exact (41% within one glyph) against 8.2% (39%) on other pages of the same section, inside the noise; the skribe, which knows nothing about labels, gives differences of the same size.

The excess is a vocabulary of the hand, not of the subject.

## 5. A cipher inside the skribe

**How it works.** The plain text is cut into units of one letter (or one to two letters). Each unit is a class of word forms. The class of a word is read from its form with the scribal layer undone (line-end closure *-m*, *-ly*, *-ry*, *-sy*, *-g* undone; *p/f* to *k/t*; no *q-*), using a table that shares out the real word forms among the units by mass, and a fixed rule for new forms. The skribe writes as usual (copying, boundary contact, hands, sheets, line registers, closure), and each word is accepted only if it falls in the class of the next unit; otherwise it chooses again. Decoding is a table look-up, word by word.

| | full text | unseen pages | bits/word | Latin words in the manuscript | word order |
|---|---|---|---|---|---|
| skribe alone | **81/88** | **75/88** | 0 | 0 | 0.032 |
| cipher, 1 letter per word | **74/88** | **70/88** | 3.96 | 4,800 | 0.085 |
| cipher, 1–2 letters per word | 65/88 | 62/88 | 6.59 | 7,200 | 0.100 |
| cipher, 1 letter, repetitions as nulls (rationed) | **78/88** | 69/88 | 2.2 | 2,700 | 0.037 |

- Both variants decode exactly over the whole manuscript (32,284 units).
- With one letter per word the message costs 7 measures, mostly immediate repetition (0.15% against 0.90%): repeating a word means repeating a plain-text letter.
- Repetitions as nulls bring it back, but if every repetition is accepted the text fills up with them (80% nulls against 34% repeated forms in the real text). Accepted with the same probability as a meaningful word, 45% nulls and 78/88.
- The plain language does not show in the battery: Latin 75, Vietnamese 77, pinyin 74, random letters 74–77. **It shows in the word order**: Latin 0.089, Vietnamese 0.167, pinyin 0.312, random letters 0.02.

## 6. The order of words

| | full | without identical pairs | without pairs at edit distance 1 |
|---|---|---|---|
| Voynich (odd · even folios: 0.081 · 0.082) | **0.088** | 0.085 | 0.081 |
| skribe, 3 seeds | 0.028–0.034 | 0.029–0.034 | 0.030–0.034 |
| cipher with Latin, 3 seeds | **0.082–0.088** | 0.081–0.087 | 0.077–0.083 |
| cipher with random letters | 0.022–0.027 | | |

It is not repetition, and it is stable between halves. A Latin message fills the gap exactly, so I checked its **shape**: exchange clustering of words into K classes that maximise the information between a word's class and the next word's, learnt on odd folios, measured on even folios:

| K classes | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|
| Voynich | **0.012** | 0.014 | 0.027 | **0.052** | 0.054 |
| skribe | 0.002–0.003 | 0.004–0.007 | 0.002–0.009 | 0.006–0.012 | 0.007–0.028 |
| cipher with Latin | **0.072–0.075** | 0.11–0.12 | 0.10–0.15 | 0.11–0.12 | 0.13 |
| Naibbe-type (1–2 letters) | 0.027 | 0.048 | 0.053 | 0.060 | 0.050 |
| nomenclator + homophones | 0.025 | 0.065 | 0.147 | 0.179 | 0.247 |
| **skribe + word-pair habit, no message** | **0.001–0.010** | 0.004–0.013 | 0.012–0.025 | 0.025–0.035 | **0.041–0.055** |

The pair habit: from the lines of the **odd** folios, take the pairs of consecutive words seen 3 times or more with a PMI of at least 1 bit (not identical, not one glyph apart): 162 pairs of 60 words. When the previous word has learnt partners, with probability 0.13 the skribe chooses again until the word makes a pair. In the end the habit acts on 3.5–5% of the words. It fills the word order (0.078–0.087; 0.071–0.075 on even folios, where the pairs were not learnt), with the real shape, and keeps the battery (74–79/88).

So the simplest account of the word order is a habit of a few dozen word pairs per hand and section, not a message written letter by letter.

## 7. Phrases

Distinct sequences of consecutive words (same line) that occur twice or more, every text cut to 32,284 words and poured into Voynich line lengths:

| text | word types | 3 words | 4 words | 5 words |
|---|---|---|---|---|
| **Voynich** | 7,915 | **94** | **1** | **0** |
| Apicius, Latin recipes | 4,943 | 1,162 | 509 | 204 |
| *Forme of Cury*, English recipes, c. 1390 | 4,795 | 1,800 | 712 | 215 |
| Culpeper, English herbal, 1652 | 3,248 | 1,806 | 647 | 221 |
| *De docta ignorantia* | 5,972 | 745 | 131 | 20 |
| *Divina Commedia* | 6,329 | 541 | 56 | 7 |
| *I promessi sposi* | 7,790 | 424 | 58 | 15 |
| *Seitsemän veljestä* (Finnish) | 11,036 | 309 | 88 | 30 |
| *Pan Tadeusz* (Polish) | | 192 | 73 | 37 |
| nomenclator + homophones (§3) | 5,591 | 556 | 80 | 15 |
| Naibbe-type (§3) | 5,809 | 35 | 1 | 0 |
| skribe alone | 7,525 | 21–51 | 0–1 | 0 |
| skribe + pair habit (§6) | | 100 | 4 | 0 |

The only repeated four-word sequence is `ol shedy qokedy qokeedy` (twice, both biological). Confirmed pairs (found on odd folios, confirmed on even folios): 15. Three of them (`s aiin`, `or aiin`, `r aiin`) are almost certainly one word split by a doubtful space; the rest are Currier B, mostly hand 2 in the biological section and hand 3 in the stars (`qol chedy`, `shedy qokaiin`, `chedy qokeey`, `otar ar`).

Formulas are exactly what a recipe book or herbal has and the Voynich has not: *ut ferveat cum ferbuerit* (18 times in Apicius), *and serue it forth* (29 in the *Forme of Cury*). A word-by-word cipher repeats them too, even with homophones. Only schemes that do not write plain-text words one by one, such as Naibbe-type schemes or the skribe, repeat as little as the Voynich. A code with dozens of homophones per word, or a spelling that never repeats a phrase the same way, would also break exact repetition; this test does not exclude them.

## 8. What it adds up to

1. **The entropy bump, the line rules, the repetition and the absence of phrases are properties of how the text is written**, and a meaningless procedure reproduces them.
2. **A cipher could still hide inside that procedure**: it decodes exactly and costs only a few measures. It cannot be ruled out with these statistics; it can only be found with its key.
3. **But it would have to be of a particular kind**: many symbols per unit (syllables or letter pairs, not single letters and not whole words), written into the free choices of the scribe, and short (a few thousand Latin words in the whole book). An alphabet written one letter per word leaves a few-class rhythm in the word order that the Voynich does not have; a word-by-word code leaves the syntax and the phrases.
4. **Nothing measured here needs a message.** The only part of the real text the skribe did not explain, the order of words, is explained by a small habit of word pairs.

**Still running** (preregistered on 30 October before any result, `XIFRATS.md` and `sil/SILLABES_PREREG.md` in the private notes): a code of about 330 Latin and Italian syllables hidden in the skribe, with four criteria fixed in advance (battery, the shape of the word order, the total word order, and the phrase counts). If it passes all four, a syllable code is as compatible with the Voynich as the pair habit without a message, and only capacity separates them.

## How to reproduce

From `external_tests/ciphers/` (Python 3.12, numpy, scipy, pandas, matplotlib; the skribe is read from `scribe/`; small auxiliary data in `_data/`):

```
py -3 diag_parser.py                                       # §1: the old notebook parser against the clean data
py -3 corre.py ; py -3 corre2.py ; py -3 grafica.py        # §2-3: word-by-word ciphers, model cipher (76 measures)
py -3 sobrant.py ; py -3 sobrant_on.py ; py -3 pagines.py  # §4
py -3 xifrat_escriba.py prova                              # §5: short round trip
py -3 xifrat_escriba.py corre <tots|senars> <skribe|1|12> <seed> ; py -3 agrega.py
py -3 xifrat_extra.py <nulles|nulles2|llengua|sobrant|desxifrat> [senars]
py -3 ordre.py ; py -3 classes.py ; py -3 memoria_mots.py  # §6
py -3 ngrames.py ; py -3 frases_controls.py ; py -3 frases_quasi.py ; py -3 frases_sense_articles.py   # §7
```

`tots` = full text, `senars` = learnt from odd folios. The Vietnamese and pinyin texts of the language test are not included (they came from Jorge Stolfi's samples); the Gutenberg texts are downloaded by `frases_controls.py`.
