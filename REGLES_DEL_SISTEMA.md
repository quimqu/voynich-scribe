# Les regles del sistema d'escriptura del Voynich

*Reglament, no informe. Recull com a regles explícites tot el que el programa (fases 1–4w, juliol 2026; sessions 27–28/09/2026) ha mesurat amb controls. Cada regla porta: la seva **força** (percentatge de compliment o ràtio contra l'atzar), si és de **sistema** (igual a les cinc mans) o d'**hàbit** (varia per mà o per pàgina), i la **font** (script o entrada del registre). Dades: ZL3b, 32.284 mots de paràgraf, 7.915 tipus. Números del 28/09/2026 (`sessio_2026-09-28/regles_compliment_out.txt`) llevat que es digui.*

*Seccions 13 i 14: afegides el 28/09 a la tarda (segona passada de mineria). Com llegir-ho: "sempre" vol dir ≥ 98%; "gairebé sempre" 90–98%; "de preferència" un biaix fort però amb excepcions normals. No hi ha cap regla de significat: totes són de forma, de lloc i de procés.*

---

## 0 · Les tres regles de fons

**R0.1 · És un sistema d'escriptura, no una llengua escrita.** Els mots porten 12,5 bits contra 19,5 del llatí; l'ordre dels mots no porta res (0,018 bits per bigrama); no hi ha cap classe de mots «de ciment» (articles, preposicions); cap xifra de llengua provada reprodueix les seves estadístiques. [A9, A11, B1, B2]

**R0.2 · Les regles són de tres nivells: glif, mot i lloc.** Tot el que és regular es decideix mirant, com a màxim, tres glifs a banda i banda d'un espai, i on és el mot dins de la línia, la pàgina i el full. Cap regla mira més enllà del mot veí. [G2, H1, §3]

**R0.3 · Sistema contra hàbit.** Unes regles són idèntiques a les cinc mans (sistema); d'altres tenen la mateixa direcció però força diferent (hàbit). El reglament ho marca a cada regla. [G10, night1]

---

## 1 · L'alfabet

**R1.1 · Famílies de glifs.** Les gallows formen una graella de 2 potes × 2 llaços (`k t p f`) més la variant amb banc (`ckh cth cph cfh`); els bancs són `ch sh`; els minims `i n m` i les corbes `e a o y`; les cues `l r s d`; el connector `q`. Sistema. [A12]

**R1.2 · Al·lògrafs: parelles que són el mateix signe en llocs diferents.** `ch~sh`, `k~t`, `p~f` (i `ckh~cth`) es fusionen sense pèrdua (percentil ~0 del nul). La tria entre ells la mana el lloc, amb només 0,009 bits de context. Sistema. [A7, V3, U1]

**R1.3 · `p` i `f` són les gallows de primera línia.** A la primera línia d'un paràgraf, el 35% de les gallows són `p`/`f`; a les línies interiors, el 3%. Sistema (30–54% a totes les mans). **I depenen de l'espai lliure a sobre**: a la resta de la primera línia (sense el primer mot), 42% si és la primera de la pàgina, 34% si el paràgraf té espai a sobre, 22% si està enganxat a l'anterior (diferència +12 punts, IC +7 a +17, a totes les seccions i mans). El primer mot les porta igual (51–56%), la quantitat de gallows no canvia, i les línies interiors amb espai no en fan. [V5, G4, night1, H9]

**R1.4 · `q` sempre va seguit de `o` i sempre és inicial.** 97,8% i 98,5%. Sistema. [regles_compliment]

**R1.5 · Glifs que no comencen ni acaben mot.** `e`, `i`, `n`, `m` no comencen mai un mot (< 0,5%); `e`, `a`, `i`, `ch`, `q`, `ckh` no l'acaben mai. Sistema. [regles_compliment]

**R1.6 · Lligadures per comoditat de ploma**, sense relació amb l'ordre (gallows + banc, sobretot a l'herbari). [A12, Y5]

---

## 2 · El mot

**R2.1 · Plantilla.** Un mot és `[prefix] [nucli] [e…] [sufix]`, on el nucli és una gallows o un banc (o cap), les `e` són d'una a tres, i el sufix és una de les terminacions de R2.4. La plantilla més senzilla cobreix el 74% dels tokens; el slot grammar de 23 posicions apreses de les dades en cobreix el 98,8% (`slots.json`). Sistema (A i B tenen el mateix esquelet, cobertura mútua 98%). [G1, night1]

**R2.2 · Una gallows per mot.** 0 gallows 46%, 1 gallows 52%, 2 gallows 1,8%, 3 mai. Sistema. [regles_compliment]

**R2.3 · Els prefixos.** `qo-` (4.176 dels 16.000 mots amb gallows), `o-` (3.946), cap (3.135), `y-` (967), `ch-` (577), `l-` (447), `cho-`, `ol-`. Davant de banc no hi ha prefix (5.705 de 5.705). Sistema. [night1]

**R2.4 · Els sufixos i els dos blocs.** Sufixos principals: `-y`, `-dy`, `-aiin`, `-ol`, `-ar`, `-ain`, `-al`, `-or`. El mot tria entre **dos blocs**: el bloc `e/d/y` (nucli amb `e` → `-y`, `-dy`: `kee`→`y`/`dy` en el 75%; `ke`, `te`→`dy`) i el bloc `a/ii/n` (nucli nu `k`/`t` → `-aiin`, `-ain`, `-ar`, `-al`). No són paradigmes de flexió: són dues vies. MI nucli~sufix 0,83 bits (nul 0,28). Sistema, però B fa més mots «tancats» (`qokeedy`) que A (excés 0,69 contra 0,25). [G9, night1]

**R2.5 · Ordre dins del mot.** Hi ha un ordre posicional dirigit (56 precedències consistents, totes ja implicades pels slots o pel terminador; cap de nova) i no té sentit de lectura propi (deu ordres ortogonals igual de bons). Sistema. [A6, Y2]

**R2.6 · Longitud.** Campana estreta: 3 glifs 15%, 4 el 21%, 5 el 24%, 6 el 18%, 7 el 9%; mitjana 4,8; 8 o més, 5%. No és lognormal com les notacions additives. Sistema. [A12, S1]

**R2.7 · Les terminacions són puntuació de tancament, no lletres.** L'únic tret del cos que prediu el glif final és el recompte de minims (z +229); treure les terminacions contreu el vocabulari un 32% (llatí 12%). Sistema. [A5]

**R2.8 · Quasi tot mot té un bessó a prop.** El 95,6% dels tokens tenen un mot a distància d'edició ≤ 1 ja escrit a la mateixa pàgina, mediana 3 línies més amunt, amb biaix cap a la mateixa alçada horitzontal. Sistema (procés). [A1, W1]

---

## 3 · L'espai i la frontera entre mots

**R3.1 · L'espai és una regla de glifs.** Un bigrama de lletres amb l'espai com a símbol reprodueix tots els parells de frontera; l'espai s'endevina el 87% amb dues lletres a cada banda. Sistema. [G2]

**R3.2 · Fronteres fortes i febles.** Després de `-y` davant de `q-`, o de `-n` davant de `o-`/`ch-`, l'espai és segur (1% de dubte del transcriptor). Entre `o|l`, `l|k`, `s|a`, `r|a` és feble (28–45% de dubte). Els mots `a-` porten espai dubtós al davant el 27%; els `q-`, l'1%. Sistema. [G2, prefix2]

**R3.3 · L'acord de frontera (la regla del prefix).** El prefix d'un mot de nucli `a-`/`o-` depèn del glif final del mot anterior i dels dos primers glifs del nucli, i de res més:

| el mot anterior acaba en | nucli `a-` pren | nucli `o-` pren |
|---|---|---|
| `-y` | `d-` 73%, `s-` 15%, cap 10% | `q-` 56%, cap 39% |
| `-n` | `d-` 51%, cap 44% | cap 77%, `q-` 20% |
| `-r` | cap 79%, `d-` 18% | cap 81%, `q-` 16% |
| `-l` | `d-` 70%, cap 20% | cap 63%, `q-` 28% |
| `-s` | cap 89% | cap 84% |

I dins del nucli `o-` després de `-y`: `ok-` pren `q-` el 72%, `ot-` el 48%, `ol-` el 26%, `or-` el 7%. Explica el 35% de la tria; el mot anterior sencer, el mot següent, la posició i la tria anterior no hi afegeixen res. La resta és taxa de pàgina i moneda (R7.2). **Hàbit en la força** (mà 1: `q` després de `-y` 0,14; mans 2–3: 0,33), **sistema en la forma**. [G3, H1, H2]

**R3.4 · `q-` és la forma de continuació.** 1% a etiquetes, 4% a primer mot de paràgraf, 13% a primer mot de línia, 18% interior, 8,5% a últim mot de línia. Sistema. [G3, allography A2]

**R3.5 · No hi ha sintaxi de mots.** Cap mot es prediu del mot anterior més enllà del glif de contacte (0,16 bits a distància 1, 0,009 a distància 2, 0 al salt de línia). Cap resegmentació ho canvia. Sistema. [A4, G2]

---

## 4 · La línia

**R4.1 · La línia és la unitat.** Tota l'estructura seqüencial viu al primer i a l'últim mot de la línia i a les repeticions; fixant-los, el guany d'un HMM mor (replicat tres vegades). Sistema. [A4, R3]

**R4.2 · Inici de línia: formes d'inici.** El primer mot comença per `d-`, `s-` o `y-` el 40% (interior 13%), i per `a-` el 0,3% (interior 4,3%: **prohibit**). Sistema (les cinc mans: `a-` 0,000–0,003 tret de la mà 5, 0,033). [G10, night1]

**R4.3 · Final de línia: formes tancades.** A l'últim mot de la línia, `-iin` es tanca en `-m` (60%, contra 7% interior), `-l` en `-ly` (25% contra 4%), `-r` en `-ry` (25% contra 2%), `-s` en `-sy`, `-y` en `-g` (5% contra 0,2%). Formes tancades en conjunt: 25% a l'últim mot, 2,3% a l'interior. No passa davant de `q-` dins de la línia: és el final físic. **No** depèn de la proximitat física al marge: amb coordenades, l'últim mot tanca igual arribi o no al marge (29% contra 25–28%), també on no hi ha dibuixos. És una forma de posició, no abreviatura per manca d'espai (corregit el 28/09, `coordenades/REGLES_DE_LLOC.md` §A). **Tampoc depèn del nombre de mots de la línia** (corregit el 14/10): la pujada de la `-m` del 7% al 32% amb la longitud de la línia en mots és composició de mans (la mà 1 escriu línies curtes i tanca poc, la mà 3 llargues i tanca molt). Dins de cada mà i secció, observat menys esperat per trams de mots: −0,03 a +0,05, tots compatibles amb zero; coeficient dels mots amb efecte fix de mà, +0,03 [−0,07, +0,27] (`proves_seccio5/PROVES_SECCIO5.md` §5.2). Sistema en la forma, **hàbit en la força** (`m/iin` final: mà 1 0,37, mà 5 0,85). [G4, allography A1, night1, J1]

**R4.4 · L'últim mot és més curt i anòmal.** z −8,9 en longitud a línies intermèdies; +0,14 bits de sorpresa en caràcters. Sistema. [LAAFU, B, U5]

**R4.5 · Dissimilació vertical.** Dues línies consecutives del mateix paràgraf eviten començar pel mateix glif: 8,8% contra 14,7% (ràtio 0,60, z −10). Només el primer glif; no es copia res més de la línia de sobre (ràtio 1,0 a tots els altres índexs). Després de `ch` inicial, la línia següent comença per `ch` el 0,8% (esperat 13,7%); després d'una gallows inicial, ràtio 0,21. **No depèn de la geometria**: igual amb interlineat estret o ample i amb l'inici alineat o desplaçat respecte de la línia de sobre. **Tampoc decau amb el temps** (14/10): la ràtio és la mateixa si la línia de sobre té 29, 41 o 50 glifs (0,65 / 0,63 / 0,66; ×0,90 [0,70–1,13] per cada doble). El primer glif de sobre es va escriure fa 20–60 glifs, molt més enllà de la memòria de dos glifs del mot (R17.3). Per tant no és memòria curta de traç: és un **registre de l'últim inici de línia** que no s'esvaeix (la línia de dues amunt ja no s'evita, R4.6). La vista no queda exclosa, però no explica per què la línia de dues amunt, que també és a la vista, no s'evita (`proves_seccio5/PROVES_SECCIO5.md` §5.3). **Hàbit** (mà 1 0,41, mà 5 0,84). [G5, H8, J2]

**R4.6 · La línia de dues amunt no s'evita; s'atrau una mica.** Cru, el primer glif coincideix amb el de dues línies amunt 1,33 vegades l'esperat. La major part és mecànica: si s'evita la del mig, amb pocs inicials possibles es repeteix la de dalt (A-B-A). Amb un nul que conserva la composició del paràgraf i imposa la dissimilació adjacent, queda 1,11 (z +2,9) a distància 2 i res a distància 3 (1,02) ni 4 (1,00). Corregit el 14/10: la versió anterior (0,19 contra 0,13 a distàncies 2 i 3) comparava amb una cadena de Markov que no conservava la composició del paràgraf. Hàbit. [G5, J2]

---

## 5 · El paràgraf

**R5.1 · El paràgraf comença amb gallows.** El primer mot del paràgraf porta gallows el 93% (primer mot de línia interior: 44%). I no comença per `q-` (4%). Sistema. [V5, G3]

**R5.2 · La primera línia és un registre propi.** A més de `p`/`f` (R1.3): la meitat de repeticions donat el seu vocabulari (0,58), més hàpax (18,8% contra 13,2%), mots més llargs (5,38 contra 5,16), i la segona línia no en reutilitza els mots (4,7% contra 7,1%). Sistema. [G8]

**R5.3 · El primer mot de paràgraf no es dissimila** amb el del paràgraf anterior (ràtio 1,00): la regla R4.5 és de línia dins de paràgraf. [G5]

---

## 6 · Els dibuixos

**R6.1 · El forat de dibuix és un marge.** El mot d'abans del forat tanca com un final de línia a mitges (formes tancades 10% contra 2% interior i 25% al marge; `r→ry` 19% contra 2%; mots més curts). El mot de després obre com un inici de línia sencer (`d-/s-/y-` 41% = inici de línia 40%; `q-` 4%). L'acord de frontera (R3.3) es trenca al forat: després de `-y`, `q-` passa del 49% al 12%. **Conseqüència: el text es va escriure després del dibuix.** Sistema (mateix patró a herbari, biològic i farmacèutic). **El forat gairebé mai parteix un mot** (14/10): la concatenació dels mots de banda i banda és un mot atestat tan sovint com a l'espai normal (excés +0,018 contra +0,016), lluny de l'espai dubtós (+0,10). Com a molt un 4% dels forats (~30 de 745). L'excés de `-d/-s` abans del forat no ve de mots partits: és sobretot la `s` solta (31 casos abans i 13 després del forat), que no es comporta com un prefix separat (`proves_seccio5/PROVES_SECCIO5.md` §5.5). [H5, J3]

**R6.2 · Però `a-` sí que pot començar després d'un forat** (1,9%, igual que l'interior). La prohibició d'`a-` (R4.2) és del marge esquerre físic; les formes d'inici `d-/s-/y-` són d'inici d'unitat. [H5]

**R6.3 · Els mots d'etiqueta no són al text de la seva pàgina** més que al d'altres pàgines de la secció (z +1,0). No hi ha lligam etiqueta → text de la pàgina. [G7]

---

## 7 · La pàgina i el full

**R7.1 · El vocabulari és de pàgina.** Barrejant els mots dins de cada pàgina, l'excés de repeticions adjacents passa de ×3,1 a ×1,23: la major part de la repetició és vocabulari local. Sistema (procés). [G7, A1]

**R7.2 · Cada pàgina té la seva taxa per a cada tria lliure.** La proporció de `q-` (donats R3.3), de `k` contra `t`, de `ch` contra `sh`, de `-dy` contra `-y` varia per pàgina molt més que una binomial (z +10 a +58), més enllà de llengua, secció i mà. Dins de la pàgina, les tries són monedes sense memòria (prefix) o amb contagi de veí immediat i deriva de poques línies (`k/t`, `-y/-dy`). **Hàbit.** [H2, H4]

**R7.3 · A i B són el mateix sistema amb pesos diferents.** Mateix esquelet de slots (cobertura mútua 98%); B omple més `e`, `d`, `y` (`qokeedy`), A omple la segona `o` i deixa oberts el 44–49% dels mots (`-l/-r/-o/-s`) contra el 30–36% de B. `q` davant d'`o-` després de `-y`: A 0,46, B 0,59. Hàbit (de mà i de secció). [G1, G4, H2]

**R7.4 · El full és la sessió.** Recto, verso i foli conjugat del mateix bifoli comparteixen vocabulari i hàbits gràfics (z +2 a +6 a totes les seccions); el foli adjacent d'un altre full, no. També comparteixen **la mida de la lletra** i, amb ella, l'interlineat i el nombre de línies (interlineat: z −6,4 dins del full, z +0,1 amb el foli veí d'un altre full); la proporció interlineat/lletra és constant a tot el manuscrit. El vocabulari deriva contínuament al llarg del còdex amb salts a les fronteres de mà i quadern. Sistema (procés). [G6, A2, W3, H11]

**R7.5 · El text no té fletxa de temps.** Cap còpia en cadena: asimetria 0,496 amb potència demostrada. La còpia és radial (de qualsevol cosa visible), no lineal. [A3, Q2]

**R7.6 · Les quatre pàgines d'un full es van escriure amb regles idèntiques i taxes semblants** (R7.2 feblement compartida dins del full, z +2,3). [H2]

---

## 8 · Les etiquetes

**R8.1 · Les etiquetes són formes de citació.** Comencen per `o-` el 56% (text 21%), per `q-` l'1% (text 16%); tanquen amb `-y`/`-ly`/`-ry` (10,9% contra 1,6%): el mot `otal` del text és `otaly` a l'etiqueta. Els mots `o-` d'etiqueta són els que al text van amb `qo-`. Sistema. [G4]

**R8.2 · Repertori tancat.** 45 etiquetes es repeteixen com a etiqueta en tres pàgines o més (`otaly`, `otedy`, `okol` en 7). [G7]

**R8.3 · Les etiquetes del zodíac no són comptadors.** Cap alineament posició a posició entre signes, cap període dins d'anell, i les etiquetes idèntiques no comparteixen posició; el test veuria un codi compartit seguit per la meitat de les etiquetes. Les veïnes s'assemblen per còpia, no per numeració. [H6, W8, V2]

---

## 9 · Les repeticions

**R9.1 · Un mot es repeteix a continuació el 0,94% de les vegades** (×3,1 l'atzar), amb 11 triples; cauen al mig de la línia, no al principi ni al final; no són ditografia ni farciment. Hàbit en la força (×1,7 a ×2,3 per mà). [G7, night1]

**R9.2 · Qui es repeteix i qui s'evita.** Sota nul de pàgina: banc+`o`+`l/r` (`chol`) ×2,6; gallows+`e`+`dy/y` (`qokedy`) ×2,3; `-aiin/-ain` (`daiin`) ×0,7. Gran part surt de R3.3: `-y` admet `q-` darrere (un mot en `-y` pot seguir-se a si mateix), `-n` no admet `d-`. [G3, G7]

**R9.3 · Res es copia glif a glif de la línia de sobre** (ràtio 1,0 a tots els índexs excepte el primer, 0,52 per R4.5). La reutilització de mots és de memòria i pàgina, no d'alineació. [G5, night2]

---

## 10 · Sistema contra hàbit (les cinc mans de Davis)

| regla | mà 1 | mà 2 | mà 3 | mà 4 | mà 5 | veredicte |
|---|---|---|---|---|---|---|
| `a-` a inici de línia | 0,001 | 0,003 | 0,003 | 0,000 | 0,033 | sistema |
| `d/s/y-` a inici de línia | 0,37 | 0,41 | 0,44 | 0,50 | 0,39 | sistema |
| `p/f` a la primera línia (entre gallows) | 0,41 | 0,38 | 0,30 | 0,23 | 0,54 | sistema |
| `q-` a primer mot de paràgraf | 0,05 | 0,06 | 0,03 | 0,00 | 0,00 | sistema |
| `m/iin` a final de línia | 0,37 | 0,66 | 0,78 | 0,60 | 0,85 | sistema en la forma, hàbit en la força |
| `q` després de `-y` | 0,14 | 0,33 | 0,32 | 0,13 | 0,17 | hàbit |
| dissimilació vertical (ràtio) | 0,41 | 0,60 | 0,78 | 0,64 | 0,84 | hàbit |
| repetició `AA` / atzar | 1,8 | 1,7 | 2,3 | 1,9 | 2,1 | hàbit |

(mà 1: herbari A i farmacèutic; mà 2: herbari B i biològic; mà 3: estrelles; mà 4: astronòmic i zodíac; mà 5: text sol i herbari B.) [night1, G10]

---

## 11 · Com s'escriu una pàgina seguint el reglament (la recepta)

1. Comença el paràgraf amb un mot amb gallows, de preferència `p` o `f`, mai amb `q-`; si hi ha espai lliure a sobre, fes servir `p`/`f` també a la resta de la primera línia (R5.1, R1.3).
2. A la primera línia, tria mots més llargs i més nous, i no els repeteixis a la segona (R5.2).
3. Cada mot: prefix + nucli + `e` + sufix, una gallows com a màxim, 4–6 glifs, i decideix el bloc: amb `e` → `-y`/`-dy`; sense → `-aiin`/`-ar`/`-ol` (R2.1–R2.6).
4. Si el mot anterior acaba en `-y` i el següent comença per `o`, posa-hi `q-` (amb la taxa d'aquesta pàgina); si acaba en `-r` o `-s`, no hi posis res; si el següent comença per `a`, posa-hi `d-` (R3.3).
5. Per triar `k` o `t`, `ch` o `sh`: la taxa de la pàgina i el mot del costat; res més (R7.2, R1.2).
6. Comença cada línia per `d-`, `s-` o `y-` de preferència, mai per `a-`, i no repeteixis el primer glif de la línia de sobre (R4.2, R4.5).
7. A l'últim mot de cada línia que no sigui l'última del paràgraf, tanca: `-iin` → `-m`, `-l` → `-ly`, `-r` → `-ry`, i fes el mot curt, hi hagi o no espai al marge. No estrenyis la lletra per fer-hi cabre res (R4.3, R4.4, R14.2, R15.1).
8. Si topes amb un dibuix, tanca una mica abans i torna a començar després com si fos una línia nova, però aquí pots començar per `a-` (R6.1, R6.2).
9. Agafa els mots dels que tens a la vista a la pàgina, canviant-ne un glif (R2.8, R7.1); de tant en tant repeteix-ne un al mig de la línia (R9.1).
10. Escriu les quatre pàgines del full a la mateixa sessió, amb el mateix vocabulari i la mateixa mida de lletra (R7.4). A les etiquetes, treu el `q-` i tanca amb `-y` (R8.1).

Un generador que segueix les regles 3, 4, 5 i 9 reprodueix 16 de 27 mesures del manuscrit; el que li falta és sobretot la capa de producció (deriva, full, primera línia) i el contagi entre veïns. [G11]

---

## 13 · Regles de contacte entre glifs (segona passada, 28/09; `sessio_2026-09-28/mineria_regles*.py`)

*Què pot seguir què dins del mot. "Mai" vol dir menys d'un cas per mil. Totes són de sistema.*

**R13.1 · `q` només va davant de `o`** (98%; l'1% restant, `qe`). No es dobla, no és mai final, no és mai interior.

**R13.2 · `n` i `m` són terminals.** `n` acaba el mot el 95% (99% amb `no`, `na`); `m`, el 95%. Cap dels dos va mai davant d'`e`, `i`, gallows, `q`, `s`. `m` i `n` no conviuen en un mateix mot (ràtio 0,14).

**R13.3 · El grup de minims és `a` + `i`(1–3) + `n`/`r`/`m`.** Les 6.609 tirades d'`i` van precedides d'`a` (95%) o `o` (4%) el 99,1%, i seguides de `n` (86%), `r` (10%), `m` (1%) el 97%. `i` no va mai davant d'`o`, `e`, `y`, `a`, banc, `q`, gallows. Les tirades són d'1 (2.389), 2 (4.048) o 3 (171); de 4, una vegada.

**R13.4 · `a` només va davant de minims i cues.** Després d'`a`: `i` 49%, `r` 22%, `l` 21%, `m` 5,5%, `n`, `s`. Mai `o`, `e`, `y`, `a`, banc, gallows.

**R13.5 · Les `e` viuen entre el nucli i la terminació.** Les 13.382 tirades d'`e` van precedides d'un banc (53%) o d'una gallows (41%) el 95%, i seguides de `d` (36%), `y` (28%), `o` (22%) el 85%. `e` no va mai davant d'`i`, `l`, `r`, `n`, `q`, `m`. Tirades d'1 (9.103), 2 (3.927), 3 (345); de 4, set vegades.

**R13.6 · Només `e` i `i` es doblen.** `ee` 26% de les `e`, `ii` 40% de les `i`; `oo`, `ll`, `dd` per sota del 0,4%; `k`, `t`, `p`, `f`, `n`, `q`, `m`, `cth`, `ckh` no es doblen mai.

**R13.7 · `e` i `i` no conviuen** (ràtio 0,15): és el nivell de glif dels dos blocs de R2.4 (`e`→`-y/-dy` contra `i`→`-aiin/-ain`).

**R13.8 · `y` és final o prefix.** Després de `y`: fi de mot (95% amb `yk`, `yt`), i si no, gallows o banc (`y-` inicial, R13.12). Mai `e`, `y`, `i`, `n`, `m`.

**R13.9 · Les gallows van precedides de `o`, d'inici de mot, de `y`, `l`, `e` o banc** (55% / 17% / 8% / 8% / 5% / 4%); mai d'una altra gallows, `n`, `m`. Van seguides d'`e` (31%), `a` (26%), banc (16%), `y` (12%), `o` (11%); mai d'`i`, `r`, `n`, `q`, `m`, una altra gallows. Dues gallows diferents no conviuen (`k`+`t` 0,12; `ckh`+`t` 0,07).

**R13.10 · `p` i `f` prefereixen el banc després** (`pch`, `fsh`: atracció 2,5); `ckh` prefereix `y` (2,75).

**R13.11 · `l` és el connector.** Després d'`l`: fi de mot, `k`, banc, `o`, `d`, `y`, `sh`, `a`. És l'únic glif de cua que pot anar davant de gallows (`lk`, `lt`) i de banc (`lch`, `lsh`). `r` i `s`, en canvi, són gairebé sempre finals (`ra`, `ro`, `sa`, `so` a part).

**R13.12 · `y-` inicial és un prefix.** 1.544 tokens; el mot sense la `y` és atestat el 68%; va seguit de gallows (64%) o banc (22%).

**R13.13 · Els mots `a-` són terminacions soltes.** 1.321 tokens, 287 tipus (`aiin`, `ar`, `al`, `ain`, `am`, `air`); sense gallows (91%) ni banc (95%), 3,8 glifs. Són el sufix sense nucli, i per això prenen `d-`/`s-` (R3.3): `daiin` = `d` + `aiin`.

**R13.14 · Els bancs no van mai davant d'`i`, `n`, `q`, ni d'un altre banc** (`chsh` mai), i sí d'`e`, `o`, `y`, `d`, `a`, `ckh`.

## 14 · Més regles de línia i de paràgraf

**R14.1 · La gallows nua és forma d'inici de línia.** Un mot que comença directament per gallows (sense `o-`, `qo-`, `y-`, `l-`) és el primer de la línia el 22,6% contra 7,8% a l'interior i 7,6% a l'últim: s'afegeix a `d-/s-/y-` (R4.2) com a forma d'inici. Sistema.

**R14.2 · El tancament és de posició, no de marge (corregit el 28/09 amb coordenades).** L'últim mot de l'última línia del paràgraf tanca menys (17% contra 27%; `-m` 9% contra 17%) i és més llarg (5,16 contra 4,75). La primera versió d'aquesta regla ho atribuïa a no arribar al marge, amb un indicador indirecte (mots de la línia respecte de la mediana). **Mesurat físicament, no és així**: l'última línia tanca menys encara que arribi al marge (13%, n = 69), i les línies no finals tanquen igual arribin o no al marge. L'última línia del paràgraf és una posició pròpia amb menys tancament. Sistema. [H10; `coordenades/REGLES_DE_LLOC.md` §A]

**R14.3 · El segon mot és el més curt i el menys prefixat.** Longitud 4,61 (primer 5,26, resta 4,7–4,8); `d/s/y-` 9% (primer 40%, interior 13%); `-y` 45,5% (primer 35%). No depèn de si el primer porta prefix (10% contra 9%). `q-` fa el màxim al tercer mot (21,5%). Sistema.

**R14.4 · La dissimilació és només vertical.** Dos mots consecutius de la mateixa línia comparteixen el glif inicial una mica **més** que a l'atzar (ràtio 1,04, z +3), el final (1,03, z +4,5) i els dos primers glifs (1,08, z +4,5): en horitzontal els veïns s'atreuen (R2.8, contagi), en vertical el primer glif s'evita (R4.5, ràtio 0,60).

**R14.5 · La longitud és de línia.** Si el primer mot és llarg (≥ 6), el segon fa 4,88; si és curt (≤ 4), 4,26. Hàbit.

**R14.6 · Mots per línia per secció** (línies intermèdies): herbari 6,9, biològic 8,1, estrelles 10,3, farmacèutic 10,1, text sol 10,0. És l'amplada que deixen els dibuixos, no una regla d'escriptura.

---

## 15 · Regles de lloc amb coordenades (28/09; `coordenades/REGLES_DE_LLOC.md`)

**R15.1 · L'escriba no estreny la lletra per arribar al marge.** Les línies que arriben al marge dret no són més denses que les que queden curtes (1,66 contra 1,66–1,75 glifs per interlineat). Amb R4.3 corregida: cap senyal de planificació del final de línia per l'espai.

**R15.2 · La mida de la lletra és del full** (vegeu R7.4). L'interlineat la segueix.

## 16 · El reglament com a procediment: l'escriba (28/09; `escriba/ESCRIBA.md`)

Un escriba sintètic que segueix aquest reglament, amb les forces estimades del text, escriu un manuscrit amb la mateixa maqueta que reprodueix **53 de 57 mesures** (error medià 7,4%; el generador de la nit, 32 de 57 i 21%). Après només dels folis senars, reprodueix els parells en 48 de 56 (7,7%), gairebé com una meitat real reprodueix l'altra (51 de 56, 6,6%). Traient qualsevol regla se'n perden mesures (fins a 10 sense la còpia i 6 sense l'acord de frontera). Regles que hi ha calgut afegir o precisar respecte d'aquest reglament:

**R16.1 · La força del tancament depèn de la mà i del nombre de mots de la línia** (mà 1: de 0,14 amb 2–5 mots a 0,35 amb 12 o més; mà 3: de 0,31 a 0,40), no de l'espai físic (R14.2). No n'hi ha prou per reproduir del tot la relació amb la llargada de línia. **Corregit el 14/10 (J1):** dins de cada mà i secció, el nombre de mots no hi afegeix res; la diferència entre trams de mots d'una mateixa mà és composició de seccions. A l'escriba, el que no quadra és la `-m` a les línies curtes no finals (11% contra 6% real).
**R16.2 · L'últim mot de la línia té repertori propi**, a més del tancament (A4): escrit amb la taula de l'interior, surt amb massa poca `-m`.
**R16.3 · La repetició del mot anterior depèn de la família** (banc+`o`+`l`/`r` ×3,2; gallows+`e`+`(d)y` ×1,5; `-aiin` i banc+`e`+`y` ≤ ×0,8), i també del mot concret (`dal`, `shey`, `saiin` no es repeteixen mai; `okaiin` ×5), que l'escriba encara no fa: una propensió per mot estimada del text i encongida cap a la de la família no millora la mesura (14/10, `escriba/ESCRIBA.md` §6.3).
**R16.4 · El tancament també és hàbit de pàgina**: algunes pàgines (f3r) porten `-m` fins i tot a l'interior de la línia. L'escriba no ho fa.
**R16.5 · La còpia ve de tota la pàgina, amb preferència pel que és a prop**, no de les dues línies anteriors: un 35% dels mots, amb abast d'unes quatre línies i un glif canviat en un 45%. És la forma quantitativa de A1 i R7.1.
**R16.7 · La família de mot també és hàbit** (14/10, J7). Com les quatre tries lliures de R7.2, la tria entre el bloc amb `e` (`-y/-dy`) i el bloc sense (`-aiin/-ar/-ol`) té taxa de full i de pàgina, i un desplaçament de secció estable (herbari cap a `-aiin`, biològic i farmacèutic cap a `e`; el farmacèutic, a més, cap a `-y` més que `-dy`). Hàbit.
**R16.6 · La còpia modificada també l'escriu la mà** (14/10, J4). El glif que canvia, s'afegeix o es treu en copiar un mot ha de ser escrivible després dels dos anteriors (≥3 vegades al text en aquell context), com qualsevol mot nou (R17.3). Sense aquesta condició, el 36% de les còpies modificades surten amb una seqüència de glifs que el manuscrit no té, i la pàgina sembla falsa (8,7% de mots estranys contra 4,6% real); amb ella, 4,1%. No cal cap repertori de mots sencers: un repertori arregla l'ull però treu varietat i mesures.

## 17 · El ductus: de què està feta la gramàtica de glifs (28/09; `ductus/DUCTUS.md`)

**R17.1 · Vuit lletres funcionals.** Per al contacte entre glifs, el Voynich té 8 classes: `o`, `a`, `i`, `d`, `q` (soles), E (`e` i els bancs, amb i sense gallows), K (les gallows) i T (les terminals `y n m g l r s`). Amb 8 classes l'entropia del glif següent és 2,33 bits contra 2,24 amb els 22 glifs; amb 12 (separant `l`, `r`/`s`, `p`/`f`, `ch`/`sh` de l'`e`), 2,25. Quin glif es tria dins de la classe no afecta el que ve després: és l'al·lografia (R1.2) i l'hàbit del full (R7.2).
**R17.2 · Trenta-cinc transicions.** Amb memòria d'un glif, 35 transicions entre classes tenen ≥ 1% de massa (23 cobreixen el 95%): T → fi; E → E, `o`, T, `d`; `o` → K, T, `d`; K → E, `a`, `o`; `a` → `i`, T; `i` → T, `i`; `d` → T, `a`; `q` → `o`.
**R17.3 · La memòria de dos és la casella.** El que la memòria de dues classes afegeix (0,65 bits per glif) és quasi tot a cinc llocs: el primer glif del mot és prefix (T inicial vol K o E), `qo-` vol gallows, dues `e` tanquen, dues `i` tanquen, i `o` després del nucli és terminal. És la plantilla prefix · nucli · tirada · terminació de R2.1.
**R17.4 · L'acord de frontera és el traç final.** El traç amb què acaba el mot anterior (cua avall, cua amunt, floritura, llaç) explica el 91% del que explica el glif sencer sobre el prefix del mot següent; classes aleatòries de glifs no expliquen res. Precisa R3.3: el que compta és el gest amb què acaba la ploma.
**R17.5 · El contacte dins del mot no és cinemàtic.** El traç final només explica el 45% de les 93 prohibicions entre glifs (`ki` prohibit, `or` permès, mateixa junció): el que mana és la classe (gallows i banc volen `e`/`a`/`o`/`y`). Plantilla sil·làbica, no ergonomia.
**R17.6 · L'escriba escriu amb el ductus.** Amb 8 classes i memòria de dos (90 transicions), l'escriba reprodueix 49 de 57 mesures (error medià 0,081) contra 53 (0,074) amb la taula sencera de 22 glifs. Perd només mesures de repetició de mot concret. Amb memòria d'un, 35 de 57: sense casella els mots surten mal formats.

---

## 12 · El que les regles no diuen

- Cap regla decideix el mot següent més enllà del glif de contacte: no hi ha frase. [R3.5]
- Cap regla porta contingut mesurable: el residu de les tries lliures és moneda amb taxa de pàgina; un missatge que imités les monedes hi cabria (≤ 6,6 KB de capacitat cega) i no es podria veure. No n'hi ha cap indici. [H3, H4, D1]
- Cap regla diu la intenció. [D6]
