# L'escriba: com està escrit el Voynich, com a procediment

> **19/10/2026:** bateria de 76 mesures (12 de noves: entropies, Zipf, llargades, abast llarg entre pàgines, ràfegues). L'escriba té ara taules de glifs per mà i per mà × secció i pesos de llargada per posició, i copia el 22% dels mots (abans el 35%): **69/76, error medià 0,05–0,07** (l'escriba del 14/10: 69/76, 0,098). Vegeu §9.
>
> **14/10/2026:** la bateria tenia un error de càrrega (els mots amb lligadura es perdien); l'escriba té ara memòria de formes a les còpies modificades (§6) i un hàbit de família de mot per full i secció (§7). Xifres actuals: **58/64 mesures, 4,1% de mots estranys (real 4,6%)**. Les xifres de §1–§5 són les del 28/09.

*28/09/2026. Prova de foc del reglament (`../REGLES_DEL_SISTEMA.md`): si les regles són bones, un escriba que les segueixi ha d'escriure un text que no es distingeixi del Voynich en tot el que sabem mesurar. L'escriba escriu un manuscrit sencer amb la mateixa maqueta que el real (pàgines, fulls, paràgrafs, línies, mots per línia, forats de dibuix, llengua A/B, mans) i es compara amb el real en 57 mesures.*

Fitxers: `escriba.py` (l'escriba), `mesures.py` (la bateria), `compara.py` (comparació i ablacions), `holdout.py` (generalització), `ajusta_copia.py` i `calibra_families.py` (calibratge), `resultats_holdout_taula.txt`, `resultats_taula.txt`, `resultats_ablacions_taula.txt`, `resultats*.json`, `mostra_pagines.txt` (pàgines escrites per l'escriba al costat de les reals).

```bash
cd smileitems/Voynich/novetats/escriba
PYTHONIOENCODING=utf-8 py -3 mesures.py          # mesures del text real → mesures_real.json
PYTHONIOENCODING=utf-8 py -3 compara.py          # real, generador de la nit i escriba (5 llavors)
PYTHONIOENCODING=utf-8 py -3 compara.py ablacions
PYTHONIOENCODING=utf-8 py -3 holdout.py         # après dels senars, escriu els parells
```

---

## 1 · El procediment (el que fa l'escriba, en l'ordre en què ho fa)

Per a cada full, i dins del full per a cada pàgina, cada paràgraf i cada línia:

1. **Tria l'hàbit del full.** Cada full té una taxa pròpia per a quatre tries lliures: `t` o `k`, `sh` o `ch`, posar `q-` o no, `-dy` o `-y`. Cada pàgina del full s'hi assembla, amb una petita variació pròpia. Dins del paràgraf, la taxa deriva una mica de línia a línia (R7.2, H2, H4, H11).
2. **Tria la llengua.** A i B fan servir la mateixa taula de contacte de glifs amb pesos diferents (R7.3).
3. **Tria el to de la línia**: aquesta línia tindrà mots una mica més llargs o una mica més curts que la mitjana (R14.5).
4. **Per a cada mot**, decideix si **copia** o **escriu de nou**:
   - **Copia** un 35% de les vegades (només un 3,5% a la primera línia del paràgraf). Tria el model entre tots els mots ja escrits a la pàgina, amb preferència pels propers (el pes baixa a la meitat cada tres línies i escaig), un bonus per al mot que queda just a sobre, i preferència pels mots que encaixen amb la frontera. El mot immediatament anterior es repeteix segons la seva família: molt els de banc + `o` + `l`/`r` (`chol`), bastant els de gallows + `e` + `(d)y` (`qokedy`), poc els de `-aiin` i els de banc + `e` + `y` (A1, R2.8, R7.1, R9.2).
     - Un 45% de les còpies (sempre, a la primera línia) **canvia un glif**: substitució, inserció o supressió, amb les freqüències de les parelles de mots veïns reals.
     - Si la còpia ha canviat, **torna a triar el prefix** segons la frontera (R3.3).
     - Si el model era tancat i va a l'interior de la línia, l'obre en la meitat dels casos (R4.3). Si té `p`/`f` i no és a la primera línia, les torna `k`/`t` (R1.3). Si va just després d'un forat, li treu la `q-` (R6.1).
   - **Escriu de nou**, glif a glif, amb la taula de contacte: cada glif depèn dels dos anteriors, i els dos primers del mot depenen també de l'últim glif del mot anterior (R13, R3.3). La taula té quatre contextos d'inici: inici de línia, inici de paràgraf, després d'un forat, i després d'un altre mot (R4.2, R5.1, R6.1). L'hàbit del full desplaça les quatre tries lliures. El mot s'accepta només si:
     - cap a la plantilla de slots (R2.1);
     - no té dues gallows (se'n rebutgen el 55%, R2.2);
     - no té `e` i `i` alhora (se'n rebutgen el 45%, R13.7).
     
     Es fan cinc candidats i se'n tria un segons el to de llargada de la línia. **L'últim mot de la línia** s'escriu amb una taula pròpia, apresa dels últims mots reals amb el tancament desfet (A4).
5. **Primer mot de cada línia interior**: si comença pel mateix glif que la línia de sobre, el torna a escriure amb una probabilitat que depèn del glif. Ho fa sempre amb `ch`, dues de cada tres vegades amb `o` o `q`, la meitat amb una gallows, gairebé mai amb `s` (R4.5, H8).
6. **Primera línia de paràgraf**: gairebé no copia, evita repetir el mot anterior, i canvia `k`/`t` per `p`/`f` en un 30% dels mots (R1.3, R5.2).
7. **Tanca l'últim mot** de la línia amb la força de la seva mà i segons quants mots porta la línia: `-iin` → `-m`, `-in` → `-m`, `-l` → `-ly`, `-r` → `-ry`, `-s` → `-sy`, `-y` → `-g`. L'últim mot de paràgraf es tanca menys. **El mot d'abans d'un forat de dibuix** es tanca amb una força més baixa (R4.3, R14.2, R6.1).

### Les forces, estimades del text real

| regla | valors |
|---|---|
| tancament, línia no final | `iin`→`m` 0,60 · `in`→`m` 0,52 · `l`→`ly` 0,21 · `r`→`ry` 0,26 · `s`→`sy` 0,14 · `y`→`g` 0,06 |
| tancament, final de paràgraf | `iin`→`m` 0,32 · `l`→`ly` 0,25 · `r`→`ry` 0,22 · `s`→`sy` 0,18 |
| tancament, abans del forat | `iin`→`m` 0,15 · `l`→`ly` 0,16 · `r`→`ry` 0,17 · `s`→`sy` 0,20 |
| tancament per mà (`iin`→`m`) | mà 1 0,29 · mà 2 0,64 · mà 3 0,88 |
| evitació del primer glif de sobre | `ch` 1,0 · `o` 0,67 · `q` 0,65 · gallows 0,52 · `l` 0,40 · `sh` 0,38 · `d` 0,37 · `y` 0,28 · `s` 0 |
| repetició del mot anterior per família | banc+`o`+`l`/`r` ×3,2 · gallows+`e`+`(d)y` ×1,5 · altres ×0,8 · `-aiin` ×0,8 · banc+`e`+`y` ×0,55 |
| còpia | 35% dels mots; 45% amb un glif canviat; abast ~4 línies; 3,5% a la primera línia |
| hàbit del full i la pàgina | desviació 0,45 en log-odds per full i 0,45 per pàgina; deriva de línia 0,25 amb memòria 0,6 |

Tot el que no és a la taula (la taula de contacte, la taula de final de línia, les edicions, la frontera) s'aprèn del text real. Són taules grans. **No és un reglament de deu línies**: és un procediment de set passos amb una gramàtica local apresa.

## 2 · Què reprodueix

57 mesures: les 27 de la bateria de la nit (`../nit_2026-09-27_outputs/generator.py`) i 30 de noves, una per regla del reglament. Una mesura es considera reproduïda si queda a menys del 25% del valor real (mitjana de 5 llavors).

| | generador de la nit | **escriba** |
|---|---|---|
| mesures reproduïdes | 32 / 57 | **53 / 57** |
| de la bateria de la nit | 18 / 27 | **25 / 27** |
| error medià \|log(gen/real)\| | 0,193 (≈ 21%) | **0,074 (≈ 8%)** |

Mesures clau (real / nit / escriba): repetició adjacent sobre l'atzar 3,09 / 2,91 / 3,33 · repetició a distància 2 3,66 / 2,52 / 3,07 · mots freqüents que es repeteixen més de ×3: 52% / 32% / 41% · `-m` a l'últim mot 15,9% / 9,1% / 16,9% · formes tancades a l'últim mot 27,1% / 11,5% / 27,7% · gallows al primer mot de paràgraf 93% / 54% / 92% · `p`/`f` a la primera línia 30,7% / 9,5% / 31,9% · `d/s/y-` després del forat 42% / 13% / 38% · sobredispersió de `q-` per pàgina 6,3 / 1,3 / 5,6 · tipus de mot 7.697 / 10.284 / 7.784 · mots amb bessó a la pàgina 65% / 61% / 67%.

`mostra_pagines.txt` té tres pàgines escrites per l'escriba al costat de les reals.

## 3 · Quines regles calen (ablacions)

Traient cada regla d'una en una (5 llavors; les mesures de `q-` després del forat i al primer mot de paràgraf estan al llindar i canvien per atzar, i no es tenen en compte):

| regla treta | reproduïdes | què es perd |
|---|---|---|
| — | 53 | |
| còpia del camp visible | 43 | totes les mesures de repetició |
| acord de frontera | 47 | informació mútua a la frontera i els quatre *lifts*; l'error medià passa de 0,074 a 0,110 |
| contextos d'inici | 47 | formes d'inici de línia i de paràgraf, `a-` a l'inici, forma després del forat |
| primera línia | 48 | `p`/`f`, menys repeticions a la primera línia |
| to de llargada de línia | 49 | correlació de llargada entre veïns |
| regles de mot / plantilla de slots | 49 | dues gallows, `e`/`i`, dispersió de llargades |
| dissimilació | 49 | primer glif de la línia de sobre |
| hàbit del full / pesos A/B | 50 | sobredispersió per pàgina |
| repertori de final de línia / tancament | 50–52 | `-m` i formes tancades a l'últim mot |
| repetició per família | 52 | repetició adjacent |

## 4 · Què no reprodueix, i les regles que hi deuen faltar

1. **La meitat dels mots freqüents es repeteix molt, i un 16% ho evita**: l'escriba fa 41% i 23%. La propensió per família ho explica en part (G7). La resta és de mot concret: al real, `dal`, `shey`, `saiin`, `cheey` o `qokar` no es repeteixen mai de manera adjacent, i `okaiin` s'hi repeteix ×5. **Regla que falta**: una propensió a la repetició per mot, més fina que la família.
2. **La `-m` segons la llargada de la línia**: al real, les línies de deu mots o més acaben en `-m` 3,5 vegades més que les d'un a quatre; a l'escriba, 2,0. La força del tancament ja depèn del nombre de mots, però no n'hi ha prou. A més, **a algunes pàgines la `-m` és un hàbit de pàgina, també a l'interior de la línia**: f3r real porta `cham`, `chom`, `cthom`, `shom` a mig text. **Regla que falta**: el tancament com a cinquè hàbit de pàgina.
3. **Final de paràgraf i mot d'abans del forat** es tanquen un 25–30% massa. Són ajustos de força, no regles noves.

## 5 · Què vol dir

- **El Voynich es deixa escriure amb un procediment de set passos**, sense cap nivell de significat: glifs amb memòria de dos i una frontera entre mots, còpia del que ja hi ha a la pàgina, formes de posició (inici, final, primera línia, forat), i un hàbit de full que va canviant. Amb això es reprodueixen 53 de les 57 mesures, gairebé totes les que el programa havia fet servir per dir que el text *no* és llengua ni xifra.
- **Totes les regles hi fan falta**: traient-ne qualsevol, se'n perden entre 1 i 10 mesures.
- **Generalitza (`holdout.py`)**: après només dels folis senars, l'escriba escriu la maqueta dels folis parells i es compara amb els parells reals. Surten 48 de 56 mesures reproduïdes, amb un error medià del 7,7%. Com a referència, les dues meitats reals s'assemblen entre elles en 51 de 56 mesures, amb un 6,6% (la mesura del full no s'hi compta, perquè amb mig manuscrit el foli conjugat sovint cau a l'altra meitat). Quatre de les vuit fallades de l'escriba també surten entre les dues meitats reals: són mesures inestables. Les pròpies de l'escriba són la repetició adjacent, la repetició a distància 3, la `-m` segons la llargada de la línia i el tancament abans del forat. **Les regles no memoritzen el text: descriuen com està fet.**
- **Límit honest**: l'escriba fa servir taules apreses del text: la de contacte de glifs, la de final de línia, la de frontera i les edicions. El procediment diu com es combinen les peces, no d'on surt la taula de contacte. Aquesta taula és la «gramàtica de glifs» del manuscrit (R13), i reduir-la a poques regles és la feina del reglament (§13), no de l'escriba.

---

## 6 · Memòria de formes (14/10/2026)

*Punt 2 de `ESTAT_DEL_PROGRAMA.md` §6. Scripts: `memoria_formes.py` (exploració), `diagnosi_estranys.py` (d'on surten els mots estranys). Sortides: `resultats_memoria_formes.json`, `diagnosi_estranys_out.txt`, i les taules `resultats_taula.txt`, `resultats_ablacions_taula.txt` i `resultats_holdout_taula.txt` refetes amb el valor nou per defecte.*

### 6.1 · Abans de res: un error a la càrrega del text real

`mesures.clean()` havia de conservar el contingut de les lligadures `{…}`, però la substitució tenia un byte `\x01` en lloc de `\1`. Els mots amb lligadura es perdien sencers: 394 grups en 359 línies. Corregit. `mesures_real.json` és ara de 59 mesures (les 57 i les dues `[ull]`). Canvien sobretot les mesures sorolloses de repetició a distància (k=2: 3,66 → 3,27; k=3: 2,80 → 3,45). **Les xifres d'ull que es donaven abans (7,9% real, 11,2% escriba) eren d'una altra càrrega i no es poden comparar.** Amb la càrrega corregida: **real 4,6%, escriba d'abans 8,7%**. L'escriba d'abans, mesurat de nou, reprodueix 51 de 59.

### 6.2 · D'on surten els mots estranys

Un mot és estrany si té algun trigrama de glifs (amb inici i fi de mot) que al real surt 3 vegades o menys. Escriba d'abans, llavor 1:

| origen | mots produïts | estranys |
|---|---|---|
| mot nou, glif a glif (cada candidat) | 107.038 | 2,4% |
| mot nou de final de línia (cada candidat) | 14.755 | 4,9% |
| **còpia amb un glif canviat** | 3.642 | **36%** |
| tancament de final de línia (nous estranys que crea) | 1.078 | 8,6% |

La font principal és l'edició de la còpia: canvia, insereix o treu un glif **sense mirar els veïns** (`daiin→daain`, `chedy→chddy`, `ol→oo`). Els mots nous, que l'escriba ja escriu amb memòria de dos glifs (R17.3), gairebé no en fan. Amb la memòria de formes, les còpies modificades estranyes passen del 36% a l'1,7%.

### 6.3 · Què s'ha provat (2–3 llavors per a l'exploració, 5 per al resultat)

| variant | reproduïdes | mots estranys | tipus |
|---|---|---|---|
| escriba d'abans | 53/59 | 8,5% | 7.775 |
| la còpia modificada va a un veí del repertori (mot conegut, a un glif) | 50–52/59 | 4,2–4,3% | 6.350–6.490 |
| + refer els mots nous desconeguts (50% / 80%) | 45 / 43 | 2,9 / 2,2% | 4.710 / 3.350 |
| **l'edició ha de ser escrivible: cada glif, possible (≥3 vegades) després dels dos anteriors** | **54–55/59** | **4,0–4,1%** | 7.120–7.190 |
| escrivible amb ≥1 vegada | 48/59 | 5,9% | 7.380 |
| escrivible + propensió a la repetició per mot | 50–52/59 | 3,9–4,1% | 7.000–7.130 |
| escrivible + repertori a la meitat de les còpies | 49–51/59 | 4,0% | 6.860 |

- **El repertori de mots sencers no és la resposta.** Arregla l'ull, però l'escriba perd varietat (tipus −18%) i mesures de repetició. Al real, una variant a un glif d'un mot de la pàgina sovint és un mot nou (hàpax), no un de conegut. Refer els mots nous que no són coneguts encara és pitjor (43–45/59).
- **La resposta és que l'edició també l'escriu la mà.** L'escriba copia el mot i en canvia un glif, però el canvi ha de ser escrivible amb la mateixa memòria de dos glifs amb què escriu els mots nous. És la regla R17.3 aplicada també a les còpies; no cal cap regla nova. Si en 30 intents no surt cap edició escrivible, la còpia queda intacta.
- **La propensió a la repetició per mot** (observada sobre esperada a la pàgina, encongida cap a la de la família) no millora `mots freq. amb rep <0,3x`: 22–30% amb aquesta peça, contra 16% real i 22–25% sense. Resultat negatiu. Queda apagada (`use_wordrep`).
- **Tancament de final de paràgraf per mà** (`par_by_hand`, per J1): sense efecte mesurable. Apagat.

### 6.4 · Resultat (5 llavors, valor nou per defecte: `mod_contact=3`, `mod_tries=30`)

| | abans (càrrega corregida) | **amb memòria de formes** | real |
|---|---|---|---|
| mesures reproduïdes | 51/59 | **54/59** | |
| de les 57 originals | 51/57 | **52/57** | |
| error medià | 0,061 | 0,064 | |
| mots estranys | 8,7% | **4,1%** | 4,6% |
| mots estranys per línia | 0,68 | **0,32** | 0,36 |
| tipus | 7.859 | 7.150 | 7.915 |

- **Ablació** (`compara.py ablacions`): sense la memòria de formes, 51/59 i 8,7% d'estranys. Totes les peces continuen fent falta: treure'n qualsevol costa d'1 a 9 mesures.
- **Generalització** (`holdout.py`): la taula de contacte que decideix què és escrivible s'aprèn només dels folis senars, i als parells el resultat és 0,31 mots estranys per línia contra 0,35 real. La memòria de formes no és memòria del text de prova. En total, 47/59 (error medià 0,101) contra 50/59 (0,066) entre les dues meitats reals.
- **El que encara no reprodueix**: `quasi(ed=1) / base` (1,59 contra 2,21: els veïns a un glif de distància), `mots freq. amb rep <0,3x` (24% contra 16%), `-m final: línies 10+ / 1–4` (1,94 contra 3,41) i `q-` al primer mot de paràgraf i tancament de l'últim mot de paràgraf (al llindar). Per a la `-m`, la causa és ara localitzada: a les línies curtes **no finals**, l'escriba tanca en `-m` un 11% i el real un 6%. Segons J1 (la força del tancament és de mà i de secció), hi falta la secció.

**Lectura.** L'ull no demanava un diccionari. Demanava que la mà fos la mateixa quan copia i quan escriu de nou: tot el que surt de la ploma, també la variant d'un mot copiat, passa per la memòria de dos glifs. Amb això, l'escriba fa tants mots estranys com el real o menys. La «memòria de formes» de R16.3 (quins mots existeixen com a unitats per a la mà) **no cal per a l'ull**. Si existeix, s'ha de buscar en el que encara falla: la repetició per mot i els veïns a un glif.

---

## 7 · Vocabulari de pàgina: l'hàbit «e» i el «dy» de secció (14/10/2026, tarda)

*Scripts: `vocabulari_pagina.py` (exploració), `calibra_seccio_e.py` (desplaçaments per secció → `sec_e.json`, `sec_dy.json`, i `*_senars.json` per a `holdout.py`), `mostra_memoria_formes.py` (mostres de quatre versions → `mostra_memoria_formes.txt`).*

### 7.1 · Què es veia a ull i la bateria no mesurava

A les mostres, f78r real és monòtona en `-edy` (`qokedy` ×15) i la de l'escriba ho era en `qokaiin` (×15). La bateria té ara cinc mesures noves (64 en total):

| mesura | real | escriba §6 | **actual** |
|---|---|---|---|
| sobredispersió per pàgina dels mots amb `e` | 24,6 | 9,0 | **20,3** |
| mots amb `e`, biològic / herbari | 2,04 | 1,51 | **1,84** |
| mots en `-edy` al biològic | 27,5% | 17,9% | **22,7%** |
| quota del mot més freqüent de la pàgina (mediana) | 4,7% | 4,7% | 4,9% |
| mots de 8 glifs o més | 5,3% | 7,3% | 7,4% |

- **La monotonia de pàgina ja era bona** (la quota del mot més freqüent quadra): el que fallava era *quina* família de mot domina cada pàgina i cada secció.
- **Els mots llargs tenen la mateixa estructura que els reals** (gallows 0/1/2+: 20/69/12% contra 20/62/18%; `qokeeedy`, `cheodaiin`, `qokeeody`), però n'hi ha un terç de més. Ve de la tria del «to de llargada» (el millor de 5 candidats), que infla les cues: els candidats en tenen un 5%. Les edicions no hi tenen res a veure (295 de 2.295).

### 7.2 · Què s'ha afegit

1. **Hàbit `e`** (`use_ehabit`): una cinquena tria lliure, la `e` després del nucli (banc o gallows), és a dir, el bloc de mot amb `e` (`-y/-dy`) o sense (`-aiin/-ar/-ol`) de R2.4. Varia per full, pàgina i línia com les altres quatre (σ 0,45; generador aleatori propi, perquè la resta de l'escriba no canviï).
2. **Desplaçament per secció** de l'hàbit `e` i de l'hàbit `dy` (`-dy` o `-y`), calibrat perquè la proporció de cada secció quadri amb el real. Valors (text sencer / només senars): `e` herbari −0,41/−0,40, biològic +0,36/+0,44, estrelles +0,37/+0,37, farmacèutic +1,55/+1,23; `dy` farmacèutic +2,3/+2,1, biològic +0,47/+0,45, estrelles −0,38/−0,46. **Són estables entre meitats**: és un hàbit de secció, no soroll. On l'escriba anava més errat era el farmacèutic: 26% de mots amb `e` contra 47%.

Són paràmetres ajustats al text (11 en total), com les forces de §1. El que diuen és que **les seccions es distingeixen per la família de mot que hi domina**, a més de per la llengua i la mà (H2, H4).

### 7.3 · Resultat (5 llavors)

| | escriba §6 | **actual** |
|---|---|---|
| mesures reproduïdes | 55/64 | **58/64** |
| generalització (après dels senars, als parells; meitats reals 55/64) | 47/59 (amb 59 mesures) | **51/64** |
| mots estranys | 4,1% | 4,1% |

- **Ablació**: sense l'hàbit `e`, 52/64 i sobredispersió 8,9. Sense el `dy` de secció, també 58/64: es perd el `-edy` del biològic i el tancament davant de dibuix, i es guanyen dues mesures que ja eren inestables (`repetició k=5`, `q-` al primer mot de paràgraf). Es manté.
- **Generalització**: les cinc mesures noves de pàgina i secció es reprodueixen als folis parells amb paràmetres apresos dels senars. Només hi falla la dels mots llargs.
- L'error medià (0,07–0,09 segons el calibratge) no és una xifra estable: una vintena de mesures tenen errors entre 0,07 i 0,10 i la mediana hi salta.

### 7.4 · El que queda

- **Mots llargs** (7,4% contra 5,3%). Suavitzar el to de llargada (4 candidats, σ 0,45) els baixa al 6,3%, però l'escriba perd varietat (−13% de tipus) i la correlació de llargada entre veïns. No s'ha aplicat. Cal un to de llargada que no infli les cues.
- **Mots que fan lleig a ull** i que cap mesura caça: `shedytedy`, `qokaiinsh`, `doraiiny`, `keeyl`. Són concatenacions de dos blocs de mot, cadascun normal. Una mesura possible: «mots que contenen dues terminacions».
- Les fallades d'abans: `quasi(ed=1)`, `rep <0,3x`, la `-m` de les línies curtes no finals.

---

## 8 · Preguntes del fòrum (19/10/2026)

### 8.1 · Un quadern sencer (`quadern.py`)

```bash
PYTHONIOENCODING=utf-8 py -3 quadern.py M 1                         # après de tot el manuscrit
ESCRIBA_TRAIN=sense_M PYTHONIOENCODING=utf-8 py -3 quadern.py M 1   # sense haver vist el quadern M (abans: calibra_seccio_e.py amb la mateixa variable)
```

Escriu tot el manuscrit i n'extreu el quadern, de manera que els hàbits de full i la còpia funcionen com sempre. Format semblant a l'IVTFF, amb els identificadors de línia del ZL3b, `<->` als forats de dibuix (copiats de la maqueta real; l'escriba no mira les imatges) i `<%>`/`<$>` als paràgrafs. També desa el real normalitzat igual. Fet per al quadern 13 (`quadern_M/`, amb `README.txt` en anglès); registre L1.

`ESCRIBA_TRAIN=sense_<Q>` (per exemple `sense_M`, o `sense_M+N`) treu els quaderns de l'aprenentatge. `mesures.load_real()` porta ara `quire` i `locus` a cada línia.

### 8.2 · Mesures estàndard (`estandard.py`, `estandard_out.txt`)

| | real | escriba |
|---|---|---|
| h1 / h2 / h3 (bits per caràcter, espai inclòs) | 3,88 / 2,12 / 1,85 | 3,86 / 2,09 / 1,84 |
| pendent de Zipf (rangs 1–1000) | 1,00 | 1,00 |
| MATTR (finestra de 500 mots) | 0,64 | 0,60 |
| ràfegues dels 50 mots més freqüents (coeficient de variació dels intervals) | 1,76 | 1,51 |
| semblança de vocabulari entre pàgines a distància 1 / 10 / 100 | 0,35 / 0,26 / 0,17 | 0,29 / 0,24 / 0,19 |

Les entropies i Zipf quadren. La llarga distància no: al manuscrit hi ha una deriva de vocabulari entre pàgines veïnes que l'escriba no fa (registre L2).

### 8.3 · Control amb significat conegut (`controls/`)

Vegeu `controls/CONTROLS.md`. L'escriba genèric aplicat al llatí de Cusanus falla on falla una llengua (7/16 contra un sostre de 13/16), i la bateria ho detecta. Per fer-lo amb un altre text:

```bash
PYTHONIOENCODING=utf-8 py -3 controls/control.py prepara <text.txt> <nom>
PYTHONIOENCODING=utf-8 py -3 controls/control.py corre <nom>
PYTHONIOENCODING=utf-8 py -3 controls/control.py informe voynich <nom>
```

`ESCRIBA_CORPUS=<fitxer.json>` fa que l'escriba aprengui d'aquell text en lloc del Voynich. Amb `mesures.set_reference(L)`, les mesures que miren el text real sencer (els trigrames rars) passen a mirar el del control.


---

## 9 · Abast llarg, llargades i el vocabulari de cada mà (19/10/2026)

*Continuació de §8.2 (registre L2 → L5): la deriva de vocabulari entre pàgines que l'escriba no feia. Les 12 mesures noves s'han posat dins de la bateria (`mesures.py`), amb definicions pròpies; els valors difereixen una mica dels d'`estandard.py`. Scripts: `mesures.py` (part 5, 12 mesures noves), `escriba.py` (taules per mà i per mà × secció, pesos de llargada), `calibra_llargada.py` (→ `len_w.json`, `len_w_senars.json`), `holdout.py` (ara accepta `clau=valor`). Taules: `resultats_taula.txt`, `resultats_holdout_taula.txt`, `resultats_ablacions_19_10_taula.txt`.*

### 9.1 · Les mesures noves (bateria de 76)

| mesura | real | escriba 14/10 |
|---|---|---|
| entropia de caràcter h1 / h2 / h3 (text de línia, amb espais) | 3,91 / 2,14 / 1,86 | 3,89 / 2,11 / 1,84 |
| pendent de Zipf (1.000 primers) | 1,00 | 1,00 |
| mots de 2–3 glifs / de 5–6 glifs | 21,6% / 41,0% | 28,8% / 33,2% |
| vocabulari compartit (cosinus): pàgines veïnes, a 10, a 100 | 0,33 / 0,25 / 0,155 | 0,27 / 0,22 / 0,163 |
| veïnes / a 100 pàgines | 2,13 | 1,65 |
| ràfegues dels 50 mots més freqüents (CV dels intervals) | 1,76 | 1,51 |
| sobredispersió per pàgina dels 50 mots més freqüents | 2,06 | 1,87 |

Les entropies i Zipf ja quadraven. Fallaven les llargades (massa mots curts: la memòria de dos glifs fa llargades massa disperses; `ol` 2,4 vegades massa) i l'abast llarg: les pàgines veïnes es semblen menys que al real i les llunyanes més.

### 9.2 · D'on surt la semblança entre pàgines

Descomposició (cosinus de vocabulari, real / escriba 14/10): mateixa mà i secció a 2–10 pàgines 0,336 / 0,293; mans diferents a 50–150 pàgines 0,159 / 0,187; mateixa mà a 50–150 pàgines 0,231 / 0,221. **No és la continuïtat entre pàgines: és el vocabulari propi de cada mà** (i de cada secció dins de la mà), que l'escriba no tenia perquè aprenia la taula de glifs per llengua A/B. Coincideix amb Schwartz 2026 (els nuclis dels mots gairebé no es comparteixen entre mans).

Mecanismes provats i descartats (2–3 llavors): copiar de les pàgines anteriors del llibre (aplana tota la corba, també a 100 pàgines, i baixa les ràfegues; 51–53/64); copiar de les pàgines ja escrites del mateix full (igual); reutilitzar mots del repertori de les últimes pàgines en lloc d'inventar-los (millora poc la pàgina veïna i fa perdre mesures). Queden al codi, apagats (`r_prev`, `r_sheet`, `r_stock`).

### 9.3 · Què s'ha canviat

1. **Taules de glifs per mà i per mà × secció** (`use_hand_tab`, `use_sec_tab`): comptes de la mà (o de la mà dins de la secció, si hi ha ≥40 línies) més 3 pseudocomptes repartits segons la taula de la llengua (o de la mà). Amb això, el to de secció ja hi és, i els desplaçaments de secció del 14/10 (`use_sec_e`, `use_sec_dy`) es comptaven dues vegades (`-edy` al biològic 34,7% contra 27,5%): queden apagats.
2. **Llargada del mot nou per posició a la línia** (`use_len_w`): la tria entre els cinc candidats es pondera per la llargada, amb pesos per al primer mot, l'interior i l'últim, calibrats en tres passades perquè la distribució de tot el text (còpies incloses) quadri amb la real.
3. **Forces reajustades**: còpia 35% → **22%**, repetició del mot anterior per família 0,8 → 0,5, hàbit de full σ 0,45 → 0,3, rebuig de dues gallows 0,55 → 0,35 i de `e`+`i` 0,45 → 0,25, tancament davant del forat ×0,75 i a final de paràgraf ×0,75 (`par_scale`, nou).

**Lectura del 22%.** Amb un vocabulari propi de cada mà, els mots ja es repeteixen més per si sols (repetició a 2 i a 5 mots: 4,6 i 5,0 vegades l'atzar amb la còpia al 35%, contra 3,3 i 2,9 al real). Part del que semblava còpia era el vocabulari de la mà. És el mateix que troba Schwartz: molta reutilització del repertori propi i poca còpia recent.

### 9.4 · Resultat (5 llavors, 76 mesures)

| versió | reproduïdes | error medià | après dels senars, als parells (meitats reals 67/76) |
|---|---|---|---|
| escriba del 14/10 | 69/76 | 0,098 | 62/76 (0,080) |
| **escriba del 19/10** | **69/76** | **0,049–0,067** (dues tandes) | 61/76 (0,080) |
| sense taules per mà i secció | 68/76 | 0,062 | |
| sense pesos de llargada | 67/76 | 0,068 | |

*Les dues ablacions, i la primera fila del fitxer `resultats_ablacions_19_10_taula.txt`, es van fer amb els desplaçaments de secció del 14/10 encara activats; la fila «sense desplaçaments de secció» d'aquell fitxer és la configuració final.*

- **El recompte no millora** (el criteri del ±25% ja és saturat i té soroll entre llavors), però **l'error medià baixa a la meitat** i les mesures noves passen: mots de 2–3 glifs 23,3% (real 21,6%), veïnes / a 100 pàgines 1,84 (2,13), ràfegues 1,58 (1,76). L'escriba del 14/10 fallava els mots de 2–3 glifs i la repetició a 5 mots.
- **Generalització**: igual que abans (61–62/76). Les 8 mesures noves de llargada i d'abast llarg es reprodueixen totes als parells amb taules apreses dels senars.
- **Encara falla**: `quasi(ed=1)` (els veïns a un glif: amb menys còpia n'hi ha menys), la repetició a 3 mots (2,5 contra 3,4), els mots freqüents que es repeteixen molt o gens (de mot concret, no de família), la `-m` de les línies llargues, la `q-` al primer mot de paràgraf (al llindar) i, sense el desplaçament de secció, la sobredispersió per pàgina dels mots amb `e` (18,4 contra 24,6).
- **Límit honest**: les taules per mà i secció són més paràmetres apresos del text (una taula de contacte per a cada combinació amb prou línies). El que diuen és que **cada mà, i cada mà a cada secció, té la seva gramàtica de glifs**, no només el seu to; no diuen per què.
