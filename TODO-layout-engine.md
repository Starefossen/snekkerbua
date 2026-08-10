# TODO — regel-/beslutningsmotor for annotasjonene

Arbeidsnotat for den som tar opp tråden. Slettes når oppdraget er ferdig; den
står ikke i `REF_DOCS` og havner ikke i `docs/hanna.pdf`.

Oppdraget: erstatte heuristisk, spesialtilpasset plassering av annotasjoner med
en REGEL-/CONSTRAINT-MOTOR + skalautledet Theme, slik at riktig layout er en
KONSEKVENS av regler og ingen side trenger egen kode.

---

## Status per del

| Del | Status |
|---|---|
| **A** — annotasjonsmotor (`tools/layout.py`) | **ikke påbegynt** |
| **B** — Theme utledet av skala | **ikke påbegynt** (forarbeid gjort, se under) |
| **C** — spesialtilfeller → data i `byggesteg.json` | **ikke påbegynt** |
| **D** — opprydding + determinismesele | **ferdig** (2 commits) |

Ingenting er halvbygd. Treet er grønt, `mise run check` er grønn, ingen
genererte artefakter endret seg av D-runden.

---

## Det som ER gjort (del D)

* `BADGE_ALPHABET` bor nå ett sted: `tools/gen_glyphs.py`. `gen_doc_tables.py`
  slår den opp via `_badge_alphabet()` (sen import — gen_glyphs drar inn
  SVG-maskineriet).
* Døde konstanter ute av `render_lineart.py`: `HEAD_FRAC`, `TOL`,
  `MIN_CONTACT`.
* Tre foreldede referanser rettet: `JOINT_CONTACTS` → `JOINTS i
  generate_loftbed.py` (assertmeldingen i `check_coverage`),
  `tools/gen_montering.py` → `render_lineart`/`render_steps` (docstring i
  `gen_doc_tables.py`), og `render_steps.py` sin feilaktige påstand om at
  per-steg-STL-ene skrives av `generate_loftbed.py` (de skrives av
  `gen_doc_tables.emit_step_meshes()`).
* Fem ubrukte vendorede Lucide-ikoner slettet (`baby`, `hammer`, `pencil`,
  `person-standing`, `phone`) + regelen skrevet ned i PRAKSIS §4.
* `mise run check` lagt til: kjører `gen_doc_tables` + `render_lineart` to
  fulle ganger og krever byte-identiske `shasum` over alt `git ls-files`
  finner i `docs/generated docs/MONTERING.md docs/img parts.tsv`.
  **Målt: 99 artefakter, byte-identiske. Kjeden er allerede deterministisk.**
  PRAKSIS §5 er skrevet om deretter.

---

## Miljø og målte fakta (ikke gjett på nytt)

* `python3` = mise-shim, build123d 0.11.1, `rsvg-convert` finnes. Alt virker.
* **Kjøretid er ikke et problem**: `gen_doc_tables.py` ≈ 9 s,
  `render_lineart.py` ≈ 11 s, `mise run check` ≈ 42 s. Iterer fritt.
* Utgangspunktet (HEAD før D) er byte-rent: full kjede gir null `git diff`.
* Modellens bbox-diagonal (sengens egen, `full_bed(G).bounding_box()`):
  **2747.54 mm**.

### Steg 1 — de fire feilene, verifisert i tegningen

Bekreftet ved å lese `docs/img/steg-01.svg` og zoome PNG-en. Sidens rektangel
er `[-1351, -958, -233, 554]` (halvsnitt), `gap = 38.0`.
`choose_marks` beholder 6 merker:

| jid | bokstav | per | p2 | kind |
|---|---|---|---|---|
| J2-B | C | 2 | (-1036, 121) | screw |
| J8-B | A | 2 | (-1022, -633) | screw |
| J12  | B | 1 | (-1015, -488) | screw |
| J12  | D | 1 | (-981, -480)  | **plate** |
| J12  | B | 1 | (-963, -421)  | screw |
| J9-B | A | 1 | (-1013, -673) | screw |

1. **Beslaget flyter feil vei.** J12-vinkelbeslaget flyter OPP-og-venstre, dvs.
   inn i bordbærelekta det sitter under. `clear_diagonal()` velger retning
   etter hvor det er mest hvitt papir — ren heuristikk, ingen semantikk.
   **R1-fasit for J12:** anker `(98, -37.5, 387)`, `direction (-1,0,0)`,
   `run (0,0,-1)`, `reach 40`. De to skruene gjennom det har drivakser
   `(-1,0,0)` (inn i stolpen) og `(0,0,+1)` (opp i lekta). Resultant
   `(-1,0,1)/√2`; motsatt resultant = **`(+1,0,-1)/√2`** → beslaget skal flyte
   i +X og NED. Projiser med `view.dir_xy()`.
2. **A-paret.** To A-kropper tegnet: J8-B (per=2, allerede slått sammen) og
   J9-B (per=1). **De OVERLAPPER IKKE** — målt på de faktiske polygonene i
   SVG-en er bbox-ene `(-763..-672, 608..633)` og `(-894..-813, 615..649)`,
   ca. **50 mm fra hverandre**. R2 slik den er formulert (overlapp ≥ N %)
   utløses altså ikke av dette paret. Se «Uavklart» under.
3. **Legendens lederlinjer.** `render_step()` tegner opptil 4 lange grå
   stiplede linjer fra innsettpanelet til de nærmeste merkene
   (`_edge_of_box(...)`-løkka). De skal bort: badge-nøkkelen bærer allerede
   koblingen. Lupene/miniatyrene beholder sin korte leder.
4. **To A-merker.** Årsaken er funnet, og den er ikke duplisering:
   `mark_label` parkerer teksten «bak hodet» langs `label_dir = (ux, uy)`.
   J9-B peker mot venstre, så «bak hodet» er mot HØYRE — rett mot J8-B-skruen.
   Ⓐ havner MELLOM de to kroppene og leses som en merking av naboen.
   Leserekkefølgen blir «[skrue] Ⓐ [skrue] Ⓐ2x».
   **Dette er en ren R5-konsekvens**: et merke skal aldri lande nærmere en
   fremmed kropp enn sin egen. Skjerp scoringen, så flytter Ⓐ seg selv.

### Uavklart — TA STILLING FØR DU KODER R2/R4

Oppdragsteksten sier «A-pair merged '2x' per R2» og «single A badge per R4».
Men J8-B (2 stk) + J9-B (1 stk) summerer til **3**, ikke 2, og de to kroppene
overlapper ikke. Verre: **PRAKSIS §4 forbyr eksplisitt sammenslåing på tvers av
ledd**, og eksempelet den bruker er nøyaktig dette paret — «endebjelkens to
6×90 og bæreklossens ene i det samme hjørnet, og «3×» der ville sendt byggeren
til feil hull».

Anbefalt linje (spør brukeren hvis du er i tvil):

* **R2 slår sammen kropper som faktisk overlapper**, uansett ledd — to kropper
  tegnet oppå hverandre er en løgn uansett hva tabellen sier. Ikke-overlappende
  kropper separeres i stedet (skruen hopper lenger ut langs SIN EGEN akse —
  aldri sidelengs, jf. `assert_on_axis` og PRAKSIS §4).
* **R4 = ett merke per tegnet element**, og merket må ligge nærmere sitt eget
  element enn noe annet. Da forsvinner steg 1s doble Ⓐ uten at tellingen på
  tvers av ledd slås sammen.
* Legg sammenslåing på tvers av ledd bak ett navngitt flagg i regelsettet, så
  det er en linje å snu hvis brukeren vil ha «Ⓐ 3x» likevel.

Rapporter uansett ærlig hva som faktisk falt ut av reglene.

---

## Del B — Theme: tallene er regnet ut, bare å skrive inn

Rot: **`pen = subject_diag / 400`** = 2747.54/400 = **6.8689 mm**.
`subject_diag` = diagonalen i tegningsobjektets egen bbox (sengen), altså et
tall modellen eier — ikke en side. Sidenære størrelser (`INSET_W_FRAC`,
`EXPLODE_FRAC`, `EXPLODE_PLATE_FRAC`, margene) fortsetter å måles mot sidens
egen korte side / bredde, som i dag.

| dagens | verdi | i pen | foreslått ratio | blir |
|---|---|---|---|---|
| `W_PRIOR` | 2.2 | 0.320 | 0.32 | 2.20 |
| `W_NEW` | 7.0 | 1.019 | 1.00 | 6.87 |
| `W_HERO` | 5.6 | 0.815 | 0.80 | 5.50 |
| `W_RULE` | 2.6 | 0.379 | 0.38 | 2.61 |
| `W_LEAD` | 2.4 | 0.349 | 0.35 | 2.40 |
| `W_MARK` | 5.2 | 0.757 | 0.75 | 5.15 |
| `W_HATCH` | 1.5 | 0.218 | 0.22 | 1.51 |
| `W_SCREW` | 4.2 | 0.611 | 0.60 | 4.12 |
| `W_PHANTOM` | 3.0 | 0.437 | 0.44 | 3.02 |
| `BADGE_R` | 25.0 | 3.640 | 3.60 | 24.7 |
| `PAD` | 70 | 10.191 | 10.0 | 68.7 |
| `INSET_PAD` | 16.0 | 2.329 | 2.30 | 15.8 |

Alt innenfor ~2 % av dagens, altså «identically-or-better» i praksis, men
**ikke** byte-identisk: hver eneste SVG endrer seg. Regn med at
regresjonstesten er visuell (se alle 12 sidene), ikke en `git diff`.
`info_panel()` sine harde punktstørrelser (46, 44, 40, 32, 26, 24) og
`joint_section()`/`mirror_note()` sine inline-tall må inn i samme tabell.

**Gotcha:** `BADGE_R` styrer også LAYOUTBESLUTNINGER (`mark_label`s kandidater
og kostfunksjon, `half_crop`s margin `BADGE_R * 5.0`, `render_panel`s
sidereknskap). 25.0 → 24.7 kan vippe et badge til en annen kandidat. Det er
lov, men se etter det.

---

## Del C — spesialtilfellene som skal bli data

Talt i `render_lineart.py` (+ kallstedene). Skal bli deklarative felt i
`byggesteg.json`, emittert av `gen_doc_tables.emit_json()` (rundt linje 1626,
dict-comprehension over `steps`), og lest som oppslag i stedet for grener:

* `HALF_VIEW_STEPS = {1, 3, 5}` → `half_view: true` per steg.
* `if n == 0` i `render_all()` → `page_type: "cutpage"`.
* `if n == 10` i `render_all()` → `page_type: "panel"`.
* `if n == 2` (`st["thumbnails"]`) → `thumbnails: true` (før/etter-reisning).
* `is_mattress` (`any(p.label.startswith("Mattress"))`) styrer SEKS oppførsler
  i `render_step()`: ingen merker, egen panelstørrelse `0.32/0.36`,
  `avoid_top_left`, `info_panel` i stedet for `draw_inset`, hopp over
  `check_coverage`, hopp over luper/ledere. → egne felt (`info_panel: true`,
  `no_fasteners: true`, …), ikke ett labelmatch.
* `crop_to_subject()` sin `0.34`-terskel → `crop_to_subject: true/false`.

`render_panel.py` og `render_cutpage.py` blir stående som sidetyper, men skal
konsumere samme Theme + elementmotor for sine annotasjoner.
`render_panel.py` kaller i dag `RL.mark_label`, `RL.badge`, `RL.draw_inset`,
`RL.BADGE_R`, `RL.INSET_W_FRAC` direkte — de er integrasjonspunktene.

---

## Del A — skisse som allerede er tenkt igjennom

Ny fil `tools/layout.py`, importert av `render_lineart.py`.

**Elementmodell.** Hvert element: `anchor` (modellpunkt via `view.xy`),
`kind`, `footprint`, `rule`, `tether`, `tag`/`owner`.
Typer: eksplodert festemiddel, flytende beslag/del, badge, tellemerke, leder,
innsettpanel, lupe, bildetekst, speilminiatyr.

**Ett scoringsløp.** I dag finnes FIRE separate scorere som skal bli én
`place(candidates, footprint, occupancy, tether)`:
`emptiest_corner()`, `mark_label()`s `cost()`, `clear_diagonal()`,
`clear_back()`. Legg en `Occupancy` under dem: svart strek, grå strek,
plasserte bokser, plasserte punkter — med `cost(rect)` og `clearance(p, cap)`.

**Rekkefølge i løseren:** (1) paneler (størst fotavtrykk først, hjørnekandidater),
(2) kropper etter retningsreglene R1/R2 (retning er GITT, bare avstand er fri),
(3) merker/tekster mot ferdig okkupasjonsfelt.

**Asserter må måle BLEKKET**, slik `assert_on_axis()` gjør i dag. Legg derfor
en `Page.record`-liste: hver `body`/`badge`/`leader`/`panel`/`label` som
faktisk emitteres registreres med geometri + eier, og assertene itererer over
den. `assert_on_axis()` er mønsteret å kopiere — den henter aksen ut av det
tegnede polygonet, ikke ut av tallene som gikk inn.

---

## De neste tre handlingene

1. **Skriv `tools/layout.py` med `Theme` + `Occupancy` + `place()` alene**, og
   bytt `render_lineart.py` over til `Theme` (del B) uten å røre plasseringen
   ennå. Kjør hele kjeden, se alle 12 sidene, commit. Dette er den eneste
   endringen som rører hver eneste SVG, så den skal stå for seg selv.
2. **Legg R1 inn** (`disassembly_dir()`) + `assert_float_direction`, og fjern
   `clear_diagonal()`. Verifiser at J12 på steg 1 flyter +X/ned. Commit.
3. **Legg R3 + R5 inn**: drep lederlinjene fra innsettpanelet, og flytt
   `mark_label` over på `place()` med kravet «nærmere sitt eget element enn noe
   fremmed». Da faller steg 1s feil 3 og 4 ut. Commit.

Deretter R2/R4 (se «Uavklart»), så del C, så full regenerering + PDF.

**Husk til slutt:** `mise run check` skal være grønn, `mise run pdf` kjøres på
nytt, og `docs/img/*.png` + `docs/hanna.pdf` committes med.
