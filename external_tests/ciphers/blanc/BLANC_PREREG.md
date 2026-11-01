# Preregistre: un missatge «blanquejat» dins de l'skribe (31/10/2026)

*Escrit abans de córrer res. És la porta que deixen oberta §7, §9 i §10 de XIFRATS.md: una llengua escrita en ordre, unitat a unitat (lletra, síl·laba o mot), deixa la seva estructura a l'ordre dels mots, i el Voynich no en té. Queda un missatge que, abans de fer-se mots, ha passat per un pas que n'esborra l'ordre: una taula que canvia amb una clau (tipus Vigenère de clau llarga, o una roda o graella que avança), o un text comprimit. Estadísticament, totes aquestes vies donen el mateix: una seqüència de símbols gairebé independents i uniformes.*

## Què es fa

- **Text pla**: el llatí de §7 (*De docta ignorantia*), lletres i espai, 27 símbols.
- **Blanqueig**: cada símbol `u_i` es xifra com `(u_i + k_i) mod 27`, amb `k_i` d'un generador amb llavor (una clau tan llarga com el text). Qui té la clau desfà el pas exactament. El resultat representa també un missatge comprimit o una taula que gira, que tenen la mateixa estadística.
- **Escrivà**: el xifrat de dues capes de §7 tal qual (`xifrat_escriba.py`, l'skribe 98ecf31, 400 intents per mot, taula repartida per massa amb `ciphers.allocate`). Es comprova que el desxifrat torna els símbols blanquejats exactes.
- **Variants**:
  - **B1**: el missatge blanquejat sol, un símbol per mot.
  - **B2**: el missatge blanquejat més l'hàbit de parelles de §8 (taula «estreta», 162 parelles apreses dels senars, λ = 0,13). Perquè es pugui desxifrar sense ambigüitat, **un mot que fa parella apresa amb l'anterior és nul** (el lector se'l salta). Quan l'escrivà segueix l'hàbit, escriu una nul·la; quan no, el mot de missatge ha de caure a la classe del símbol que toca **i no** pot fer parella apresa amb l'anterior.
- **Llavors**: 3 per variant al text sencer i 3 a pàgines no vistes (après dels senars, escriu els parells).

## Mesures i criteris (els mateixos de `sil/SILLABES_PREREG.md`)

| | criteri | real |
|---|---|---|
| **C1** bateria | ≥ 74/88 al text sencer i ≥ 70/88 a pàgines no vistes (mitjana de 3) | — |
| **C2** forma de l'ordre | K=2 ≤ 0,025 **i** K=32 entre 0,03 i 0,08 | 0,012 · 0,054 |
| **C3** ordre total | entre 0,06 i 0,12 bits | 0,088 |
| **C4** frases | trios diferents repetits ≤ 190 **i** seqüències de 5 mots repetides ≤ 2 | 94 · 0 |

**Què espero (escrit abans de veure res):** B1 s'ha de comportar com l'skribe sol (ordre ~0,03), perquè el missatge ja no té ordre; per tant, B1 hauria de fallar C3 i passar C2 i C4. B2 és la que decideix.

**Lectura acordada:**
- **B2 passa C1–C4**: un missatge blanquejat (amb clau o comprimit) amagat a les tries de l'skribe, amb l'hàbit de parelles, és **indistingible** de l'hàbit sol amb totes les mesures que tenim. La porta del xifrat **no es pot tancar amb estadística**: només queden la capacitat i la plausibilitat històrica (un procediment així al segle XV), i una clau.
- **B2 falla C2 o C4**: fins i tot un missatge blanquejat deixa un rastre que el Voynich no té, i la porta es tanca molt més.
- **B2 falla només C1**: el missatge, amb aquesta implementació, costa massa mesures. Es diu quines, i no és decisiu.
- **B1 passa C1–C4** (no ho espero): l'ordre dels mots del real no necessita ni l'hàbit, i caldria revisar §8.

Secundari (no decideix): capacitat (bits i mots llatins), intents i reserva, fracció de nul·les a B2, repetició immediata.
