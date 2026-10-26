# Control with known meaning (19 October 2026)

*Question from voynich.ninja: "Do you have any controls with known semantic meaning? What would happen if you applied your model to half of the pages of Moby-Dick? Wouldn't it also produce English-like text that passes many of the same checks?"*

## Design

- **Control text**: Latin, *De docta ignorantia* by Nicholas of Cusa (the same control as in the July phases; the Latin source text is not included in this repository, only the prepared `latin.json` is). It has 37,138 words. Since it has no lines, `control.py prepare` gives it a layout: lines of about 45 characters (6.3 words on average), paragraphs of 10 lines, pages of 26 lines and sheets of 4 pages. This yields 226 pages.
- **The same skribe in a generic version**, identical for both texts. It includes:
  - copying of what is on the page, with writable edits;
  - two-glyph memory;
  - boundary agreement;
  - line-start contexts;
  - length tone;
  - dissimilation.

  Left out are the rules specific to the Voynich (`q-`, gallows, closures, `p/f`, sheet habits). Three variants are tested: copying at 22% (the Voynich setting since 19 October), 35% (the setting before) and 10%.
- **Test**: the skribe learns from the odd folios and writes the layout of the even ones; it is compared with the real even folios. The ceiling is the comparison of the real odd folios with the real even folios. 3 seeds.
- **16 generic measures**. Among them there is a new one: **the information carried by word order**. It is the mutual information between consecutive words of the same line (the 200 most frequent words; the rest, in a single class), minus that of the same text with the words shuffled within each line.

Scripts: `control.py` (`prepare`, `run`, `report`). Outputs: `res_voynich.json`, `res_latin.json`, `report_voynich_latin.txt`.

## Result

| | Voynich | Latin |
|---|---|---|
| Measures reproduced: real odd against real even (ceiling) | 16/16 | 13/16 |
| Measures reproduced: generic skribe, copy 22% | **13/16** | **7/16** |
| Measures reproduced: generic skribe, copy 35% | 12/16 | 7/16 |
| Measures reproduced: generic skribe, copy 10% | 13/16 | 6/16 |
| Word repeated right after / chance: real → skribe (22%) | 3.15 → 3.76 | 0.04 → 4.62 |
| Neighbours one glyph apart / shuffle: real → skribe (22%) | 2.26 → 1.69 | 0.59 → 1.84 |
| Word types: real → skribe (22%) | 4,850 → 4,330 | 3,897 → 9,448 |
| Strange words: real → skribe (22%) | 4.5% → 3.3% | 1.6% → 3.9% |
| Word order (bits): real → skribe (22%) | 0.082 → 0.036 | 0.274 → 0.016 |

*Rerun on 27 October 2026 with the skribe of 26 October. The run of 19 October gave 12/16 and 10/16 on the Voynich and 7/16 and 7/16 on Latin; its "copy 35%" variant used the default copying rate, which was 35% then. The new habits of 26 October (gallows-initial lines, first-line register) are off in the generic skribe, which has no style habits.*

In both texts the skribe gets the character entropies (h1, h2), the Zipf slope and the mean length right. **These measures distinguish nothing**: any letter model passes them. The ones that separate the Voynich from a language are those of repetition, vocabulary variety and word order. Applied to Latin, the skribe fails all of them, and the battery detects it (7/16 against a ceiling of 13/16).

Sample (even folios, first lines):

```
real Latin:     praevenire ut intellectus cuius intelligere
                est esse studio veritatis perficiatur rara
scribe:         st ita regat nes fut
                fintellarbell ta ita incis quolum maxit
```

## Where the information between consecutive words lies

Mutual information (over the within-line shuffle) between a property of the previous word and the next word:

| | whole previous word | only its last glyph |
|---|---|---|
| real Latin | **0.274** | 0.134 |
| real Voynich | 0.082 | **0.106** |
| skribe on Latin (19 October) | 0.007 | 0.026 |
| full skribe on the Voynich | 0.034 | 0.091 |

- **In Latin**, the whole word says twice as much about the next one as its last letter does: the information lives in the word (syntax, combinations).
- **In the Voynich**, the last letter alone says *more* than the whole word. All the dependence between consecutive words is in the contact glyph (R3.3, R3.5): knowing the word adds nothing, and grouping the rare words even dilutes it.
- The full skribe (of 26 October; even folios, five seeds, `contact_info.py` → `contact_info_out.txt`, which gives 0.083 and 0.109 on the real text with its own reading of the files) reaches 84% of the contact-glyph information (0.091 against 0.109). In the "per word" measure, on the other hand, it falls short (0.034 against 0.083): its frequent words do not concentrate the link as the real ones do. Without the boundary rule it dropped to 0.004 (19 October).

## Reading

- **Answer to the question**: no. Applied to a text with meaning, the skribe writes Latin-looking strings that fail precisely the measures that separate a language from the Voynich. There are too many repetitions, the vocabulary balloons, word order carries no information and the length of neighbouring words ends up correlated. The measures that the Voynich and the skribe share are precisely the ones Latin does not have: repetition (3.15 against 0.04), near-twins (2.26 against 0.59) and the link between words concentrated in the contact glyph.
- **Limit**: the control has no real lines (the layout is artificial), so the line measures say nothing for Latin. Moby-Dick should give the same pattern; it has not been tried, because the text would have to be downloaded.
- **Amendment to the battery**: the "word order" measure (per word, 200 most frequent) **fails on the skribe over the Voynich** (0.034 against 0.083), but its contact-glyph equivalent matches (0.091 against 0.109). It has not been added to the 64 measures; it remains pending.
