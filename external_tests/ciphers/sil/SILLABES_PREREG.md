# Preregistre: una llengua amagada síl·laba a síl·laba (30/10/2026)

*Escrit abans de córrer res. És la prova que queda oberta a XIFRATS.md §7 (punt 3) i §8: si el Voynich porta un missatge, ha de ser un codi de **molts símbols**, perquè un alfabet escrit lletra a lletra deixa a l'ordre dels mots una estructura de poques classes que el Voynich no té (K=2: 0,072 contra 0,012). La candidata natural és la síl·laba.*

## Què es fa

- **Text pla**: llatí (*De docta ignorantia*, el mateix de §7) i, com a segona llengua, italià (*Pinocchio*, Gutenberg 52484, sense accents).
- **Unitats**: síl·labes, amb la síl·laba final de cada mot marcada (`ta` ≠ `ta#`), de manera que el lector recupera també els límits de mot. Síl·labes per una regla fixa (V-CV, VC-CV, muta cum liquida junta, `qu` consonant, diftongs `ae au oe` un sol nucli). Les 300 síl·labes més freqüents són unitats pròpies (~94% del text llatí); les altres s'escriuen lletra a lletra, i la marca de final de mot `#` va com a unitat a part. Unes 330 classes.
- **Escrivà**: el xifrat de dues capes de §7 (`xifrat_escriba.py`) tal qual: l'skribe sencer (98ecf31), i cada mot només s'accepta si la seva forma normalitzada cau a la classe de la unitat que toca (3.000 intents; si no, un mot real de la classe). Taula repartida per massa amb `ciphers.allocate`. Es comprova que el desxifrat torna les unitats exactes.
- **Llavors**: 3 per variant al text sencer i 3 a «pàgines no vistes» (après dels senars, escriu els parells).

## Mesures i criteris (fixats ara)

Comparació: Voynich real; skribe sol; skribe + hàbit de parelles (§8, sense missatge); xifrat d'1 lletra per mot (§7).

| | criteri perquè el codi de síl·labes sigui compatible amb el Voynich | real | per què |
|---|---|---|---|
| **C1** bateria | ≥ 74/88 al text sencer i ≥ 70/88 a pàgines no vistes (mitjana de 3) | — | el nivell del xifrat d'1 lletra; l'skribe fa 81 i 75 |
| **C2** forma de l'ordre | K=2 ≤ 0,025 **i** K=32 entre 0,03 i 0,08 (classes de `classes.py`, après als senars, mesurat als parells) | 0,012 · 0,054 | la prova que va tombar l'alfabet (0,072 a K=2) |
| **C3** ordre total | entre 0,06 i 0,12 bits | 0,088 | |
| **C4** frases | trios diferents repetits (≥ 2 cops) ≤ 190 **i** seqüències de 5 mots repetides ≤ 2 | 94 · 0 | un xifrat mot a mot en fa 556; un text normal, centenars |

**Lectura acordada abans de veure res:**
- **C1–C4 es compleixen amb el llatí**: un codi de síl·labes és tan compatible amb el Voynich com l'hàbit de parelles sense missatge. Les estadístiques que tenim no poden distingir una llengua amagada síl·laba a síl·laba d'un text sense missatge; queda la capacitat (quants mots llatins hi caben) com a únic argument.
- **Falla C2 o C4**: el codi de síl·labes deixa un rastre que el Voynich no té, i perd. Si falla amb el llatí i passa amb l'italià (o al revés), es diu així, sense triar.
- **Falla només C1**: el missatge costa massa amb aquesta implementació; no és decisiu sobre el tipus de codi.

Secundari (no decideix): capacitat (bits per mot, mots del text pla al manuscrit), intents i mots de reserva, tipus de mot, repetició immediata.
