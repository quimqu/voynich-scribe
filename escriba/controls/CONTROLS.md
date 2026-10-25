# Control amb significat conegut — 19/10/2026

*Pregunta de voynich.ninja: «Do you have any controls with known semantic meaning? What would happen if you applied your model to half of the pages of Moby-Dick? Wouldn't it also produce English-like text that passes many of the same checks?»*

## Disseny

- **Text de control**: llatí, *De docta ignorantia* de Nicolau de Cusa (`../de_docta_ignorantia_punts.txt`, el mateix control de les fases de juliol). Té 37.138 mots. Com que no té línies, `control.py prepara` li dona una maqueta: línies d'uns 45 caràcters (6,3 mots de mitjana), paràgrafs de 10 línies, pàgines de 26 línies i fulls de 4 pàgines. En surten 226 pàgines.
- **El mateix escriba en versió genèrica**, igual per als dos textos. Inclou:
  - còpia del que hi ha a la pàgina, amb edicions escrivibles;
  - memòria de dos glifs;
  - acord de frontera;
  - contextos d'inici de línia;
  - to de llargada;
  - dissimilació.

  En queden fora les regles pròpies del Voynich (`q-`, gallows, tancaments, `p/f`, hàbits de full). Es proven dues variants: còpia del 35% (la del Voynich) i del 10%.
- **Prova**: l'escriba aprèn dels folis senars i escriu la maqueta dels parells; es compara amb els parells reals. El sostre és la comparació dels senars reals amb els parells reals. 3 llavors.
- **16 mesures genèriques**. Entre elles n'hi ha una de nova: **la informació que porta l'ordre dels mots**. És la informació mútua entre mots seguits de la mateixa línia (els 200 mots més freqüents; la resta, en una sola classe), menys la del mateix text amb els mots barrejats dins de cada línia.

Scripts: `control.py` (`prepara`, `corre`, `informe`). Sortides: `res_voynich.json`, `res_llati.json`, `informe_voynich_llati.txt`.

## Resultat

| | Voynich | Llatí |
|---|---|---|
| Mesures reproduïdes: senars reals contra parells reals (sostre) | 16/16 | 13/16 |
| Mesures reproduïdes: escriba genèric, còpia 35% | **12/16** | **7/16** |
| Mesures reproduïdes: escriba genèric, còpia 10% | 10/16 | 7/16 |
| Mot repetit just després / atzar: real → escriba | 3,15 → 4,61 | 0,04 → 4,63 |
| Veïns a un glif de distància / barreja: real → escriba | 2,26 → 1,81 | 0,59 → 1,91 |
| Tipus de mot: real → escriba | 4.850 → 4.412 | 3.897 → 8.451 |
| Mots estranys: real → escriba | 4,5% → 3,2% | 1,6% → 3,7% |
| Ordre dels mots (bits): real → escriba | 0,082 → 0,021 | 0,274 → 0,000 |

En els dos textos l'escriba encerta les entropies de caràcter (h1, h2), el pendent de Zipf i la llargada mitjana. **Aquestes mesures no distingeixen res**: les passa qualsevol model de lletres. Les que separen el Voynich d'una llengua són les de repetició, varietat de vocabulari i ordre dels mots. Aplicat al llatí, l'escriba les falla totes, i la bateria ho detecta (7/16 contra un sostre de 13/16).

Mostra (parells, primeres línies):

```
llatí real:     praevenire ut intellectus cuius intelligere
                est esse studio veritatis perficiatur rara
escriba:        st sa se it mum
                mine ie ine st num ine
```

## On és la informació entre mots seguits

Informació mútua (sobre la barreja dins de línia) entre una propietat del mot anterior i el mot següent:

| | mot anterior sencer | només el seu últim glif |
|---|---|---|
| llatí real | **0,274** | 0,134 |
| Voynich real | 0,082 | **0,106** |
| escriba sobre el llatí | 0,007 | 0,026 |
| escriba complet sobre el Voynich | 0,031 | 0,093 |

- **En llatí**, el mot sencer diu el doble sobre el següent que la seva última lletra: la informació viu en el mot (sintaxi, combinacions).
- **Al Voynich**, l'última lletra sola en diu *més* que el mot sencer. Tota la dependència entre mots seguits és al glif de contacte (R3.3, R3.5): conèixer el mot no hi afegeix res, i agrupar els mots rars fins i tot la dilueix.
- L'escriba complet arriba al 88% de la informació del glif de contacte (0,093 contra 0,106). En canvi, en la mesura «per mot» queda curt (0,031 contra 0,082): els seus mots freqüents no concentren l'enllaç com els reals. Sense la regla de frontera cau a 0,004.

## Lectura

- **Resposta a la pregunta**: no. Aplicat a un text amb significat, l'escriba escriu cadenes amb aspecte de llatí que fallen justament les mesures que separen una llengua del Voynich. Hi sobren repeticions, el vocabulari es dispara, l'ordre dels mots no porta informació i la longitud dels mots veïns queda correlacionada. Les mesures que el Voynich i l'escriba comparteixen són precisament les que el llatí no té: la repetició (3,15 contra 0,04), els quasi bessons (2,26 contra 0,59) i l'enllaç entre mots concentrat al glif de contacte.
- **Límit**: el control no té línies reals (la maqueta és artificial), de manera que les mesures de línia no diuen res per al llatí. Moby-Dick hauria de donar el mateix patró; no s'ha provat, perquè caldria baixar el text.
- **Esmena a la bateria**: la mesura «ordre dels mots» (per mot, 200 més freqüents) **falla a l'escriba sobre el Voynich** (0,031 contra 0,082), però el seu equivalent per glif de contacte quadra (0,093 contra 0,106). No s'ha afegit a les 64 mesures; queda com a pendent.
