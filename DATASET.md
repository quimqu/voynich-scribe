# The dataset: ZL3b lines with stroke transliteration

Built on 25 July 2026 from the **ZL version 3b (13 May 2025)** transliteration by
Zandbergen–Landini, format **IVTFF 2.0**, alphabet **Eva- (basic)**.

## Sources
- File: `ZL3b-n.txt` (included), obtained from the GitHub mirror `jere-mie/ivtt-wasm`
  (`static/transliterations/`), which replicates the official set from voynich.nu.
- Format: R. Zandbergen, *IVTFF – Intermediate Voynich MS Transliteration File Format*,
  issue 2.0.1 (25 June 2025): https://voynich.nu/software/ivtt/IVTFF_format.pdf
- Reference tool: IVTT v2.4 (7 September 2025): https://voynich.nu/software/ivtt/IVTT_manual.pdf
- Table of files and explanation: https://voynich.nu/transcr.html

## Control figures
- **5,385 loci** (rows), exactly matching the earlier CUVA dataframe, over **227 pages**.
- **36,272 tokens** (32,606 in P paragraphs, 1,149 L labels, 2,517 circular/radial C·R),
  **174,913 glyphs**.
- **Stroke coverage 99.82%** (glyphs without a map, W or GAP: 0.18%).
- **Round trip seg→EVA: 0 errors over 36,272 words** (invertibility guaranteed by assert).
- 2,748 commas joined · 817 alternative readings (first one taken, IVTT option `-u1`) ·
  431 ligature groups · 758 drawing intrusions `<->`.
- Difference from the CUVA dataframe (38,496 tokens): almost all of it is explained by the **comma
  policy** (here 2,748 uncertain spaces are joined: 36,272+2,748 ≈ 39,020) and by the handling of
  alternative readings.

## Processing decisions (pre-registered)
1. **Commas (uncertain space) → glyphs joined** (decision by quimqu). The position of each join is
   kept in `comma_join_positions` (format `word:offset`), so that the information is not lost (test X5).
2. Alternative readings `[a:b]` → **first reading**; all the alternatives kept in
   `alt_readings`.
3. Ligatures `{...}` (glyphs written fused, IVTFF §p.27): content kept as text,
   groups recorded in `ligature_groups`, the raw material of the stroke phase.
4. `<->` (drawing intrusion) → safe space; count in `n_drawing_gaps`.
5. `<%>` and `<$>` → columns `paragraph_start`/`paragraph_end` + paragraph indices.
6. Extended EVA `@nnn;` → one glyph; provisional decomposition if it is in the map (status `review`),
   otherwise `W<nnn>`. Review by actual frequency in `extended_review.csv`.
7. `?` (illegible character) → GAP glyph, excluded from coverage; count in `n_gap`.
8. Capitalised EVA (1 occurrence) → lower case + allograph mark ` (backtick).
9. Comments `<!...>` kept in `inline_comments`; other short tags in `inline_other_tags`.
10. The **locator character** of the locus (`@ + = * & ~ /`) is kept raw in `locus_locator`
    (full semantics: Table 7 of the format PDF).

## Stroke transliteration (Table A, validated by quimqu on 25 July 2026)
Primitives (upper case, an alphabet disjoint from EVA): C curve · I minim · L leg · O loop ·
B bar/bench · U tail up · J tail down · Q tail-loop · F tall flourish · P plume · X cross ·
V vertex · G foot hook · T platform · M high bar · R mirror curve · D small ring ·
` allograph · W+id weirdo · ? GAP. Full map with status (`ok`/`review`) in `stroke_map.json`.
Two columns:
- `text_strokes_seg`: glyphs separated by `|`, words by `.`; **invertible** (assert).
- `text_strokes_flat`: continuous stream of strokes per word; faithful to the ink, **not** uniquely
  decodable (e.g. `a`=CI ≡ `e`+`i`; `sh`=CBCP ≡ `ch`+plume): the ambiguity is real and is an
  object of study (X2), not a defect.
Rows pending visual review: l, g, q, u, v, j, z and all the extended ones (see status).

## Column dictionary
Identification: `page_tag`, `page_seq`, `locus_num`, `locus_full`, `locus_locator`,
`locus_type` (P0…Lz…Cc…Ro, IVTFF Table 9), `locus_generic`, `is_label`, `transcriber`.
Production (IVTFF page header): `quire` ($Q, A=1…T=20), `page_in_quire` ($P),
`folio_in_quire` ($F), `bifolio_num` ($B, from the outside in), `sheet_id` (=$Q+$B, sheet ID,
ReneZ convention), `illustration` ($I), `section` (name), `currier_language` ($L),
`davis_hand` ($H, Lisa Fagin Davis hands 1–5), `currier_hand` ($C), `extraneous` ($X).
Structure: `paragraph_start/end`, `par_index_in_page`, `line_in_par`.
Text: `text_eva_raw` (as in the file), `text_eva` (clean, with commas), `text` (comma policy
applied: the main column, analogous to the one in the CUVA dataframe), `n_words`, `n_glyphs`.
Annotations: `comma_join_positions`, `n_comma_joins`, `alt_readings`, `n_alt`,
`ligature_groups`, `n_ligatures`, `n_drawing_gaps`, `inline_comments`, `inline_other_tags`,
`extended_used`, `n_weirdo`, `n_gap`.
Strokes: `text_strokes_seg`, `text_strokes_flat`.

## Files
- `df_lines_ZL3b_strokes.csv`: the dataframe (5,385 rows × 43 columns)
- `stroke_map.json`: Table A, machine-readable, with statuses
- `extended_review.csv`: extended EVA by actual frequency, for review by quimqu
- `build_df.py`: full, reproducible pipeline (asserts included)
- `ZL3b-n.txt`: source

## Pending (phase X)
- Review by quimqu of the `review` rows (rare glyphs + extended) and of `extended_review.csv`.
- An independent **Table B** (from the Curve-Line System of Cham/pfeaster) to comply with R6.
- Once validated: prompt for battery X (X1–X6) on this dataframe.
