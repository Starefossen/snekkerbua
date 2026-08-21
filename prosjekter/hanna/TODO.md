# TODO — HANNA

Restanse etter helhetsrevisjonen (tre uavhengige revisorer, 2026-08-20/21).
Stryk punkter etterhvert som de landes.

## Landet

- [x] **Retterunde 1** (`77a3657`) — de tjue kryssende skruene, klossen, fiberen.
- [x] **Retterunde 2** (`f7e2781`) — sone 3 fikk 3 veggfester (J12-V),
      nisjedybdekrav 1500, steg 0 delt, trimpunkter inne, alle ark/prosafunn
      rettet.

## Portrunde (X12) — landet

- [x] **C9 per byggesteg**: `check_step_units` i `tools/gen_doc_tables.py`.
      Enhetene UTLEDES (sammenhengende komponenter av «deler steget legger
      til, bundet av ledd steget driver»), måles som kropper og holdes til tre
      regler: plass mellom veggene, tippdiagonal under taket, og — er den
      bredere enn 1984 — bygges på plass med et senere steg som reiser den.
      Bakrammen er utfallet av regel 3, ikke et tilfelle: 42 enheter i 10 steg.
- [x] **Referanse-ende mot overmål**: `assert_datum_ink`, lest av det
      EMITTERTE blekket (27 plasseringsrader × kapplistas overmål × steg 0s
      utsettelsesliste). Ingen linje måler fra en fot; de 6 leddene som måler
      fra en veggende med overmål er nøyaktig de steg 0 utsetter.
- [x] **README-tall målt av porten**: `tools/check_tall.py`, 24 talte
      påstander (asserter/artefakter/sider/deler/løpemeter/festemidler, norsk
      og engelsk) pluss 3 sitater av modellens egen utskrift. Sidetallet måles
      der PDF-en finnes og sier tydelig fra der den ikke gjør det.
- [x] **ASSEMBLY-tallsveip i porten**: samme fil. 663 tall med enhet i
      ASSEMBLY + PRAKSIS, 44 i hviteliste med grunn, potten dekker 17 % av
      heltallene opp til 2500 (parvise differanser ble prøvd og forkastet —
      de tar potten til 93 %).
- [x] **Falsifisering som port**: `tools/falsifiser.py`. 5 vokterasserter
      kjøres rene som kontroll, og 11 navngitte feilinjiseringer må felle hver
      sin. Ingenting skrives til disk.
- [x] **Veggfestenes ærlighet**: `STUD_LAYOUT_UNKNOWN` i modellen, c/c-tallet
      merket veiledende i fragmentet, og en assert på blekket som nekter
      veggfesterader å oppgi X som fasit.

## Mindre restanse fra revisjonen

- [ ] ~28 halvtautologiske asserter utenfor de to klyngene (de 23 hele er tatt).
- [ ] `render_endelevation`: «14 like»/puteantall er verifisert riktige, men
      hardkodet — krever refaktor av modulnivå-dict for å utledes.
- [ ] `schematic.Sheet.dim`: samme ordmellomrom-under-halo-problem som
      `render_lineart` fikk brudd-i-streken for.
- [ ] Lastveis-tillegget i ASSEMBLY håndregner spenninger og kapasiteter
      (σ i MPa, lagerkapasitet i kN). 22 av dem står i tallsveipets hviteliste
      fordi modellen ikke regner dem. Skal den? Da blir hvitelista kortere og
      sveipet skarpere — men det er en modellutvidelse, ikke en portsak.

## Åpne beslutninger (Hans)

- [x] **Linjelaser**: byggherren har LÅNT en 360°-linjelaser, og den dekker
      behovet inntil videre — ingenting er kjøpt. Anbefalingen er ført i
      UTSTYR.md som anbefaling: Bosch UniversalLevel 360 Premium Set
      (~1 730 kr, ±0,4 mm/m, 360° horisontal + vertikal, stativ inkludert),
      budsjett Jula Meec 360° 999 kr, og unngå Bosch PLL 360-1 (ingen vertikal
      linje). Avstandsmåler er bevisst avmeldt — laserplan + tommestokk måler
      denne jobben bedre.
- [x] **Release**: v2.0 kuttes etter denne runden. Geometrien er ny siden
      v1.0, og porten er en annen port. `WALL_SPAN` settes når rommet er målt;
      det blir en egen runde og en egen release.
- [ ] **Fotstøtte ved pulten**: åpent punkt fra bordrunden (sålene henger
      134 mm for referansebarnet). Kan ses sammen med krok-oppgaven (v2).

## Fysisk huskeliste (byggeplass)

- Madrass oppe: **120 mm** (110–125). 140/150/160 er ulovlige — gammel plan sa 150.
- 48×68: **3 bord**; 36×48: **1 bord** (bordklossene flyttet til 48×68 i X10).
- Fjern fotlist/listverk i hele nisjas bredde før reisning.
- Kryssfinerplaten kappes med dekkfiber **langs** 574-retningen (bæreevne).
- Nisjedybde ≥ **1500 mm** må bekreftes ved rommåling — det er bakrammen
  liggende som setter kravet, ikke senga (836 mm dyp). Rammen tippes opp inne.
