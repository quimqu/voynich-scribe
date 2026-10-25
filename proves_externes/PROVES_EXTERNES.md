# Proves externes: l'escriba davant de dos articles del 2026 (25/10/2026)

*Dues proves que no hem dissenyat nosaltres, aplicades tal com les publiquen els seus autors al text real (ZL3b, text de paràgraf, normalitzat com a `escriba/manuscrit.py`) i al text de l'escriba (`escriba/escriba.py`, 5 llavors, tot el manuscrit, mateixa maqueta). Cap paràmetre de l'escriba s'ha tocat per a aquestes proves: és l'escriba del 19/10 (registre L5). Scripts i sortides en aquesta carpeta; l'entrada és `escriba/manuscrit_out/` (`real.txt`, `scribe_seed1..5.txt`).*

---

## 1 · Parisel (2026): les quatre signatures de frontera

**L'article.** C. Parisel, *Evidence of Layered Positional and Directional Constraints in the Voynich Manuscript: Implications for Cipher-Like Structure*, arXiv 2604.19762 (v2, juny 2026). Mesura què passa a la frontera entre dos mots seguits i en treu quatre signatures, calibrades per separat per a Currier A i B sobre la seva transliteració (RF1b-e), que qualsevol generador del Voynich hauria de reproduir alhora:

| signatura | què és | referència A | referència B |
|---|---|---|---|
| Sig1 E→S | fronteres que van d'un glif «de final» a un glif «d'inici» (classes per ràtio 2:1 de posició) | 71,0 % [56, 86] | 64,3 % [50, 79] |
| Sig2 bilateral | glifs amb ràtio de posició > 100:1 a totes dues bandes (inici i final) | sí | sí |
| Sig3 MI | informació mútua entre l'últim glif d'un mot i el primer del següent | 0,586 (≥ 0,29) | 0,498 (≥ 0,25) |
| Sig4 forma | distribució de freqüència dels glifs de frontera: llei de potència, no altiplà | zipfiana | intermèdia |

Prova dos generadors (un de slots paramètric, > 2.000 execucions, i una graella de Cardan a la manera de Rugg, 15 configuracions): **cap passa les quatre alhora** per a cap dels dos dialectes, perquè la taxa E→S i la MI (o la forma) demanen condicions oposades d'una mateixa palanca. Demana generadors on aquests trets surtin de mecanismes independents.

**Què hem fet.** El verificador de l'autor (`github.com/labyrinthinesecurity/currier-signatures`, commit 5d50101; cal corregir l'import `signatures_v26` → `signatures_v27`) calibra la referència sobre RF1b-e i puntua un fitxer de mots, una línia del manuscrit per línia, contra la referència del dialecte. Li donem el text real i el de cada llavor de l'escriba, separats per dialecte amb **la mateixa assignació de folis que fa servir ell** (`run_parisel.py`). El text real serveix de control: amb la nostra normalització ha de passar.

**Resultat (`parisel/resum.txt`, informes complets a `parisel/out_*.txt`).**

| text | dialecte | mots | E→S | MI | bilateral | forma | atestació | veredicte |
|---|---|---|---|---|---|---|---|---|
| real (ZL3b) | A | 10.378 | 66,4 % | 0,584 | sí (3, 3) | zipfiana 0,857 | 91 % | **4/4** |
| real (ZL3b) | B | 21.380 | 65,8 % | 0,499 | sí (5, 8) | intermèdia 0,815 | 93 % | **4/4** |
| escriba, 5 llavors | A | 10.378 | 68,1–70,5 % | 0,526–0,541 | sí (3–5, 4–5) | zipfiana 0,866–0,879 | 72 % | **4/4 × 5** |
| escriba, 5 llavors | B | 21.380 | 63,3–65,6 % | 0,454–0,470 | sí (4–5, 5–9) | intermèdia 0,818–0,826 | 79 % | **4/4 × 5** |

(*atestació*: fracció de mots del text que existeixen al dialecte de RF1b-e; en el real no és el 100 % perquè les transliteracions difereixen.)

**Lectura.** L'escriba passa les quatre signatures per als dos dialectes, a les cinc llavors, i no només per dins dels marges: els valors són a prop de la referència (MI 0,92× a A i 0,93× a B; E→S a ±3 punts; la forma és la del dialecte). No està afinat per a cap d'aquestes mesures. Els mecanismes que Parisel demana que siguin independents ho són a l'escriba per construcció: E→S i MI surten de l'acord de frontera (R3.3) i de les terminacions com a tancament (R2.7); la forma, de la plantilla de mot (R2.1) i de la memòria de dos glifs (R13); i la bilateralitat, dels glifs que només obren o només tanquen (R1.5). És la primera vegada que un generador publicat passa aquest benchmark. **Confirma per un camí extern** que l'acoblament de frontera és un fenomen de glif de contacte (H14, K2), no de gramàtica de mots.

Reserves: les taules de l'escriba s'aprenen del text (com totes les de l'escriba); un 21–28 % dels mots de l'escriba no són al dialecte de RF1b-e (són mots nous, A12/R16), cosa que el verificador informa però no penalitza.

---

## 2 · Davis i Layfield (2026): la similitud entre pàgines i l'estructura de «singulions»

**L'article.** L. Fagin Davis i C. Layfield, *Singulion Structure and the Voynich Manuscript*, Digital Medievalist 19 (19/10/2026, doi 10.4000/16k0a). Sostenen que el manuscrit es va fer amb bifolis solts («singulions») que mai no havien d'anar niats en quaderns, i que l'enquadernació actual és equivocada. La prova textual: anàlisi semàntica latent (LSA: documents de 40 mots per pàgina, TF-IDF, SVD amb k = 75, cosinus entre pàgines plegades a l'espai) i la similitud mitjana entre pàgines segons la relació física:

- **confoliate**: recto i verso del mateix foli;
- **conjoint**: les dues pàgines de la cara interior del bifoli (a-v | b-r), físicament contínues per la plegadura;
- **facing**: pàgines consecutives en l'ordre actual (v | r).

En dos manuscrits llatins de control (Bestiari d'Aberdeen, *Speculum*) facing ≈ confoliate > conjoint, com toca en un text que es llegeix seguit. Al Voynich (quaderns 1–7, 13 i 20) troben conjoint 0,433 > confoliate 0,383 > facing 0,298 (p conf/fac 0,005; fac/conj 0,000; conf/conj 0,168): les pàgines veïnes en l'ordre actual s'assemblen menys que les del mateix bifoli. En dedueixen que l'ordre actual és erroni, i reordenen els bifolis dels quaderns 13 i 20 buscant el facing màxim (guanys del 12 % i del 20 %). No controlen mà, llengua ni secció: ho diuen, i ho tracten qualitativament.

**Què s'havia dit abans (voynich.ninja).** La idea que la similitud dins del bifoli és producció i no lectura no és nova: Wladimir D (2018–2019, «volum d'informació solapada» per bifoli: el text es va escriure abans de cosir), pfeaster (2022, «bifolio as a functional unit», alineacions estranyes per bifoli), oshfdk (12/2025: «l'estadística apunta a l'ordre d'escriptura, bifoli a bifoli, no al de lectura»), dashstofsk (02/2026: correlacions de pàgina a Q13 i Q20, «escrit full a full, primer una cara i després l'altra») i, sobretot, la revisió de Torsten Timm (*The Singulion and the Sequence*, 07/2026): la similitud dins del bifoli és real, la lectura com a ordre de lectura està infradeterminada, i a la reordenació li falten un nul de permutacions i un calibratge amb text conegut barrejat. Timm també proposa (13 i 15/07/2026) que les pàgines de la cara interior són les més semblants «perquè es veien juntes». El que faltava era un text de control sense significat amb hàbits de full, que és el que l'escriba dona.

**La nostra lectura prèvia.** El programa ja havia mesurat que **el full és la sessió d'escriptura**: recto, verso i foli conjugat comparteixen vocabulari, hàbits i mida de lletra, i el foli veí d'un altre full no (G6, H11, R7.4). L'escriba té hàbits de full i vocabulari de mà i secció, i cap noció d'ordre de lectura.

**Què hem fet (`davis_layfield/lsa_singulion.py`).** El mateix LSA (documents de 40 mots, resta ≥ 20, TF-IDF, df ≥ 2, k = 75, pàgines plegades, cosinus) sobre el text real i el de l'escriba, als mateixos quaderns (A–G, M, T). A més dels tres tipus de parell seus, n'afegim dos: la **cara exterior** del bifoli (b-v | a-r) i les **diagonals** (a-r | b-r, a-v | b-v). Prova de Mann-Whitney entre tipus, com ells.

| text | confoliate | conjoint | outer | diag | facing | p conf/fac | p conf/conj | p fac/conj | p conj/outer |
|---|---|---|---|---|---|---|---|---|---|
| Davis-Layfield (real, ZL 2a) | 0,383 | 0,433 | — | — | 0,298 | 0,005 | 0,168 | 0,000 | — |
| **real (ZL3b, aquí)** | 0,225 | 0,284 | 0,183 | 0,208 | 0,154 | 0,008 | 0,100 | 0,000 | 0,015 |
| **escriba (5 llavors)** | 0,147 ± 0,009 | 0,145 ± 0,012 | 0,143 ± 0,018 | 0,152 ± 0,011 | 0,091 ± 0,017 | 0,001–0,43 (4/5 < 0,07) | 0,48–0,97 | 0,03–0,18 | 0,60–0,95 |

(n: confoliate 76, conjoint 38, outer 37, diag 75, facing 68. Els valors absoluts no són comparables amb els seus perquè l'espai és un altre; l'ordre i les p sí. Amb k = 50 o traient els 20 mots més freqüents, el mateix.)

1. **La rèplica surt.** Sobre el text real reproduïm el seu patró i les seves p: conjoint > confoliate > facing, amb facing significativament per sota de tots dos i conjoint no distingible de confoliate.
2. **L'escriba reprodueix la seva prova contra l'estructura de quaderns.** En un text sense significat, les pàgines del mateix bifoli (0,145) també s'assemblen molt més que les pàgines veïnes de bifolis diferents (0,091; p < 0,07 a 4 de 5 llavors). La similitud entre pàgines mesura la sessió d'escriptura, no l'ordre de lectura: **el senyal que fan servir no pot decidir si l'ordre és bo o dolent.** És el nul que la revisió de Timm demanava.
3. **La reordenació no és informativa.** Fent com ells (facing mitjà de l'ordre niat contra el màxim sobre totes les permutacions dels bifolis a les juntures), el text real guanya un 33 % a M i un 50 % a T; l'escriba, que no té cap ordre bo a recuperar, guanya 61 ± 26 % i 78 ± 19 % (`asimetria_bifoli.py`). El màxim de 120 o 720 permutacions d'una mesura sorollosa sempre puja.
4. **Una asimetria dins del bifoli que no es confirma** (§3): amb el LSA, la cara interior del real (0,284) s'assembla més que l'exterior (0,183), i l'escriba no ho fa; però cap altra mesura ho reprodueix.

**Lectura.** Davis i Layfield poden tenir raó en l'enquadernació per motius codicològics (taques, dibuixos que salten de pàgina, mans que alternen), però la part textual del seu argument és un efecte de producció que el programa ja tenia mesurat, que altres havien assenyalat, i que un text sense significat reprodueix.

---

## 3 · L'asimetria dins del bifoli: examinada i no confirmada

**D'on surt.** En veure la taula de §2 (post hoc, no pre-registrat): amb el LSA, la cara interior del bifoli (a-v | b-r) s'assembla més que l'exterior (b-v | a-r), +0,096 aparellat per bifoli, Wilcoxon p = 0,019, 68 % dels 37 bifolis; i si el plec s'escriu en l'ordre a-r, a-v, b-r, b-v, la similitud baixa amb la distància d'escriptura (1: 0,246; 2: 0,208; 3: 0,183; pendent per bifoli p = 0,048). L'escriba no ho fa (+0,001), perquè l'hàbit de full tracta les quatre pàgines igual. Dues lectures eren possibles: deriva de vocabulari en el temps d'escriptura del plec, o còpia del camp visible a través de la plegadura amb el full obert (la proposta de Timm del 07/2026).

**La prova crítica (`asimetria_bifoli2.py`, `asimetria2.txt`).** Les mateixes pàgines i els mateixos 37 bifolis, amb sis mesures de semblança en lloc d'una. El contrast és aparellat per bifoli (interior − exterior), així que mà, llengua, secció i quadern són idèntics a les dues bandes; només canvia l'aparellament de les quatre pàgines.

| mesura | interior | exterior | interior − exterior (real) | p signe | % bifolis > 0 | escriba |
|---|---|---|---|---|---|---|
| LSA k = 75 (cosinus) | 0,284 | 0,183 | **+0,096** | 0,024 | 68 % | +0,001 |
| TF-IDF sense SVD (cosinus) | 0,221 | 0,188 | +0,026 | 0,073 | 59 % | +0,003 |
| Jaccard de tipus | 0,108 | 0,103 | +0,002 | 0,61 | 49 % | 0,000 |
| Jaccard a llargada igual (les 4 pàgines retallades a la mínima, 20 sortejos) | 0,103 | 0,099 | +0,002 | 0,61 | 49 % | 0,000 |
| bessones exactes (fracció de mots amb el mateix tipus a l'altra pàgina) | 0,307 | 0,296 | +0,004 | 0,74 | 46 % | 0,000 |
| quasi-bessones a distància 1 (A1) | 0,658 | 0,648 | +0,005 | 0,72 | 54 % | −0,005 |
| les cinc tries lliures (distància L1 de taxes, signe invertit) | | | +0,020 | 0,70 | 43 % | +0,004 |

El pendent per distància d'escriptura només és negatiu amb el LSA (p 0,048) i el TF-IDF (p 0,031); amb les altres quatre mesures, no (p 0,15–0,80). Dins del LSA, l'efecte és de la mà 2 (10 bifolis, +0,186, p 0,004) i de la mà 3 (5 bifolis, +0,174); a la mà 1 (21 bifolis) és +0,026, p 0,65. La correlació de (interior − exterior) amb la diferència de mots entre els dos parells és +0,52 per al TF-IDF, +0,45 per a les bessones i +0,18 per al LSA: part del que es mesura és quina pàgina té més text. L'alineació vertical de les bessones exactes entre pàgines (|Δ fracció de línia| contra línies barrejades) és 0,96–1,01 a tots els tipus de parell: els bessons d'una pàgina a l'altra no són a la mateixa alçada.

**Veredicte.** L'asimetria és un efecte d'una sola representació (els 75 eixos del LSA, que pesen un grapat de mots freqüents), concentrat en 15 bifolis de les mans 2 i 3, que no apareix en cap de les cinc mesures directes del vocabulari compartit, ni en la còpia a distància 1 que és la via per on la «còpia del camp visible» hauria d'actuar, ni en les tries lliures que és per on hi hauria d'actuar la «deriva de la mà». Amb una mesura post hoc i cinc rèpliques negatives sobre les mateixes dades, no es pot dir que la cara interior s'assembli més. **NO CONFIRMAT.** La proposta de Timm (les pàgines interiors més semblants perquè es veien juntes) no troba suport en la xarxa de quasi-bessones, que és on l'hauria de tenir. Si algun dia es vol reprendre: caldria una mesura pre-registrada, i probablement les coordenades (si hi ha còpia a través de la plegadura, els models haurien de ser a prop de la plegadura).

---

## Com repetir-ho

```bash
cd Voynich/novetats/escriba
PYTHONIOENCODING=utf-8 py -3 manuscrit.py 1 2 3 4 5        # manuscrit_out/real.txt i scribe_seed1..5.txt (8 s per llavor)
cd ..
git clone https://github.com/labyrinthinesecurity/currier-signatures.git <fora del repositori>
sed -i 's/signatures_v26/signatures_v27/g' <clon>/verifier.py <clon>/grille.py
PYTHONIOENCODING=utf-8 py -3 proves_externes/parisel/run_parisel.py <clon>            # parisel/resum.txt (~20 s)
PYTHONIOENCODING=utf-8 py -3 proves_externes/davis_layfield/lsa_singulion.py [--k 75] [--stop 0]   # resultats_k75_stop0.txt
PYTHONIOENCODING=utf-8 py -3 proves_externes/davis_layfield/asimetria_bifoli.py       # resultats_asimetria_k75.txt (reordenació a la seva manera)
PYTHONIOENCODING=utf-8 py -3 proves_externes/davis_layfield/asimetria_bifoli2.py      # asimetria2.txt (sis mesures, 30 s)
```

Diferències conegudes amb els originals: Parisel calibra sobre RF1b-e i nosaltres puntuem text normalitzat del ZL3b (el real passa igualment, 4/4). Davis i Layfield fan servir ZL 2a amb lectures incertes eliminades i separen el text radial i circular; aquí només text de paràgraf, que és l'únic que l'escriba escriu. El seu heurístic de mots buits no està descrit prou per repetir-lo; sense treure'n cap, o traient els 20 més freqüents, el resultat no canvia.
