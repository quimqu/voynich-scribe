# df_lines_ZL3b_strokes — Voynich ZL3b amb transliteració de traços (fase X)

Construït el 25/07/2026 a partir de la transliteració **ZL versió 3b (13/05/2025)** de
Zandbergen–Landini, format **IVTFF 2.0**, alfabet **Eva- (bàsic)**.

## Fonts
- Fitxer: `ZL3b-n.txt` (inclòs), obtingut del mirall GitHub `jere-mie/ivtt-wasm`
  (`static/transliterations/`), que replica el joc oficial de voynich.nu.
- Format: R. Zandbergen, *IVTFF – Intermediate Voynich MS Transliteration File Format*,
  issue 2.0.1 (25/06/2025) — https://voynich.nu/software/ivtt/IVTFF_format.pdf
- Eina de referència: IVTT v2.4 (07/09/2025) — https://voynich.nu/software/ivtt/IVTT_manual.pdf
- Taula de fitxers i explicació: https://voynich.nu/transcr.html

## Xifres de control
- **5.385 loci** (files) — coincideix exactament amb el df CUVA anterior — sobre **227 pàgines**.
- **36.272 tokens** (32.606 en paràgrafs P, 1.149 labels L, 2.517 circular/radial C·R),
  **174.913 glyphs**.
- **Cobertura de traç 99,82%** (glyphs sense mapa W o GAP: 0,18%).
- **Roundtrip seg→EVA: 0 errors sobre 36.272 paraules** (invertibilitat garantida per assert).
- 2.748 comes unides · 817 lectures alternatives (presa la primera, opció IVTT `-u1`) ·
  431 grups de lligadura · 758 intrusions de dibuix `<->`.
- Diferència amb el df CUVA (38.496 tokens): quasi tota s'explica per la **política de comes**
  (aquí 2.748 espais incerts s'uneixen: 36.272+2.748 ≈ 39.020) i pel tractament d'alternatives.

## Decisions de processament (pre-registrades)
1. **Comes (espai incert) → unió de glyphs** (decisió quimqu). La posició de cada unió queda a
   `comma_join_positions` (format `paraula:offset`), per no perdre la informació (test X5).
2. Lectures alternatives `[a:b]` → **primera lectura**; totes les alternatives conservades a
   `alt_readings`.
3. Lligadures `{...}` (glyphs escrits fusionats, IVTFF §p.27): contingut conservat com a text,
   grups registrats a `ligature_groups` — matèria primera de la fase de traços.
4. `<->` (intrusió de dibuix) → espai segur; recompte a `n_drawing_gaps`.
5. `<%>` i `<$>` → columnes `paragraph_start`/`paragraph_end` + índexs de paràgraf.
6. Extended EVA `@nnn;` → un glyph; descomposició provisional si és al mapa (status `review`),
   si no `W<nnn>`. Revisió per freqüència real a `extended_review.csv`.
7. `?` (caràcter il·legible) → glyph GAP, exclòs de cobertura; recompte a `n_gap`.
8. EVA capitalitzada (1 ocurrència) → minúscula + marca d'al·lògraf ` (backtick).
9. Comentaris `<!...>` conservats a `inline_comments`; altres tags curts a `inline_other_tags`.
10. El **caràcter localitzador** del locus (`@ + = * & ~ /`) es conserva cru a `locus_locator`
    (semàntica completa: Taula 7 del PDF del format).

## Transliteració de traços (Taula A, validada per quimqu 25/07/2026)
Primitives (majúscules, alfabet disjunt de l'EVA): C corba · I minim · L pota · O llaç ·
B barra/banc · U cua amunt · J cua avall · Q cua-llaç · F floritura alta · P ploma · X aspa ·
V vèrtex · G ganxo de peu · T plataforma · M barra alta · R corba mirall · D anelleta ·
` al·lògraf · W+id weirdo · ? GAP. Mapa complet amb estat (`ok`/`review`) a `stroke_map.json`.
Dues columnes:
- `text_strokes_seg` — glyphs separats per `|`, paraules per `.`; **invertible** (assert).
- `text_strokes_flat` — flux continu de traços per paraula; fidel a la tinta, **no** unívocament
  decodificable (p. ex. `a`=CI ≡ `e`+`i`; `sh`=CBCP ≡ `ch`+ploma): l'ambigüitat és real i és
  objecte d'estudi (X2), no un defecte.
Files pendents de revisió visual: l, g, q, u, v, j, z i tots els extended (vegeu status).

## Diccionari de columnes
Identificació: `page_tag`, `page_seq`, `locus_num`, `locus_full`, `locus_locator`,
`locus_type` (P0…Lz…Cc…Ro, Taula 9 IVTFF), `locus_generic`, `is_label`, `transcriber`.
Producció (capçalera de pàgina IVTFF): `quire` ($Q, A=1…T=20), `page_in_quire` ($P),
`folio_in_quire` ($F), `bifolio_num` ($B, de fora a dins), `sheet_id` (=$Q+$B, ID de full,
conveni ReneZ), `illustration` ($I), `section` (nom), `currier_language` ($L),
`davis_hand` ($H, mans Lisa Fagin Davis 1–5), `currier_hand` ($C), `extraneous` ($X).
Estructura: `paragraph_start/end`, `par_index_in_page`, `line_in_par`.
Text: `text_eva_raw` (tal com al fitxer), `text_eva` (net, amb comes), `text` (política de
comes aplicada — columna principal, anàloga a la del df CUVA), `n_words`, `n_glyphs`.
Anotacions: `comma_join_positions`, `n_comma_joins`, `alt_readings`, `n_alt`,
`ligature_groups`, `n_ligatures`, `n_drawing_gaps`, `inline_comments`, `inline_other_tags`,
`extended_used`, `n_weirdo`, `n_gap`.
Traços: `text_strokes_seg`, `text_strokes_flat`.

## Fitxers
- `df_lines_ZL3b_strokes.csv` — el dataframe (5.385 files × 43 columnes)
- `stroke_map.json` — Taula A llegible per màquina, amb estats
- `extended_review.csv` — extended EVA per freqüència real, per a revisió de quimqu
- `build_df.py` — pipeline complet i reproduïble (asserts inclosos)
- `ZL3b-n.txt` — font

## Pendent (fase X)
- Revisió quimqu de les files `review` (glyphs rars + extended) i de `extended_review.csv`.
- **Taula B** independent (des del Curve-Line System de Cham/pfeaster) per complir R6.
- Un cop validat: prompt de la bateria X (X1–X6) sobre aquest df.
