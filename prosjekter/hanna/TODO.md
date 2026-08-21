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

- [x] ~28 halvtautologiske asserter utenfor de to klyngene (de 23 hele er tatt).
      Gjort: klassen er jaget med en AST-detektor (venstre og høyre side
      utfoldes gjennom definisjonskjeden og sammenlignes) — 42 `==`-ledd
      funnet, 29 av dem døde. 31 asserter skrevet om til å måle solider
      (`.extents` på de bygde kroppene, via to nye hjelpere `built`/`built_z`),
      2 strøket åpent med begrunnelse i stedet. De 13 som står igjen er enten
      merket som navneidentiteter fra før, eller ledd i en kjede der det andre
      leddet ER en måling.
- [x] `render_endelevation`: «14 like»/puteantall er verifisert riktige, men
      hardkodet — krever refaktor av modulnivå-dict for å utledes.
      Gjort: `NAMES` er blitt `names(M)`, antallene telles i modellen, og
      `assert_counts_ink` leser dem tilbake ut av den ferdige SVG-en.
- [x] `schematic.Sheet.dim`: samme ordmellomrom-under-halo-problem som
      `render_lineart` fikk brudd-i-streken for.
      Gjort: `render_lineart.Page.dimension`-idiomet er flyttet over —
      `text_box`, `_clip_box` og `line_cut` bryter streken der figuren står i
      stedet for å male halo bak den, med samme stubbe-regel (kortere stubbe
      enn et pilhode → hel strek). Alle tre genererte ark regenerert og lest
      som PNG: streken krysser ikke lenger ordmellomrommet i «1990 mm».
- [x] Lastveis-tillegget i ASSEMBLY håndregner spenninger og kapasiteter
      (σ i MPa, lagerkapasitet i kN). 22 av dem står i tallsveipets hviteliste
      fordi modellen ikke regner dem. Skal den?
      Gjort — ja. Hele C24-arket er navngitt ett sted (ved `K_CR`), og
      `X13`-blokka regner 22 lastrader + k_h-tabellen + uttrekket etter EC5
      8.7.2 og printer dem som X7 printer sine. Hvitelista gikk fra 44 til 21
      oppføringer (20 ASSEMBLY-linjer og 3 PRAKSIS-linjer ut, sistnevnte
      dekket av urelaterte modelltall og notert i fila). Tre tall i ASSEMBLY
      var feil og er rettet mot modellen: lagerkapasiteten under trinnet
      (3,2 → 3,0 kN, delte på karakteristisk 2,5 i stedet for design 2,31),
      endespilen (0,46 → 0,48, skalert med spennforholdet i annen),
      spile-mot-vange (0,05 → 0,06) og stolpe-mot-gulv (45 → 45,6 kN);
      A.6 sa dessuten 0,15 om trinnet der A.2 for lengst hadde
      1,2 kN-lasten (0,18). To nye feilinjiseringer i
      `tools/falsifiser.py` beviser at klassen nå felles.
      ÅPENT, IKKE TATT: de to Johansen-tallene (1,15 / 1,56 kN uten
      taueffekt) står som SITERTE konstanter, ikke utledet — en ærlig
      utledning trenger skruens f_u, som fila ikke har. Regnet med EC5s
      vanlige f_u = 600 N/mm² blir de 1,43 og 1,97, altså +24 % og +26 %:
      godt over 10 %-grensen, så det er rapportert og ikke overkjørt.

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
- [x] **Fotstøtte ved pulten** (X14): bygget som en LØS fotkrakk — 2 gavler
      36×98 × 272 på høykant + 4 dekkbord 48×68 × 416 flatt, 8 × 6×80 (J18),
      og ikke én skrue inn i sengen. Dekket topper på **146 mm**, og høyden er
      utledet og ikke valgt: setet bærer låret bare mellom 134,8 og 153,9 mm
      (for lavt = putekanten skjærer inn i låret dypere enn rumpa selv ligger;
      for høyt = låret slipper puta), og av de ni kurvene sengens fem
      dimensjoner lager treffer nøyaktig én det båndet (98 på høykant + 48
      flatt). Bredden er bukta D13 lar stå mellom gangpassasjene, dybden er de
      to sålenes egen avstand rundet opp til hele bord. Begge figurene er
      re-posert: legg i lodd, fot flatt, lårvinkelen SOLVED slik at sålen
      lander på dekket — sålegapet er assertert til 0. Ingen nye bord kjøpt
      (svinn 36×98 17 → 13 %, 48×68 30 → 18 %), nytt byggesteg 12, og to nye
      feilinjiseringer i `tools/falsifiser.py` vokter kapplistas «(løs del)».
      ÅPENT, SAGT HØYT: fila slutter å sitere popliteal 0,28 H som noe den
      bygde kroppen gir — kneledd til såle måler 313,2 mot 336, og de 22,8
      dekomponeres (16,8 boksfoten + 6,0 tabellen) og assertes.

## Fysisk huskeliste (byggeplass)

- Madrass oppe: **120 mm** (110–125). 140/150/160 er ulovlige — gammel plan sa 150.
- 48×68: **3 bord**; 36×48: **1 bord** (bordklossene flyttet til 48×68 i X10).
- Fjern fotlist/listverk i hele nisjas bredde før reisning.
- Kryssfinerplaten kappes med dekkfiber **langs** 574-retningen (bæreevne).
- Nisjedybde ≥ **1500 mm** må bekreftes ved rommåling — det er bakrammen
  liggende som setter kravet, ikke senga (836 mm dyp). Rammen tippes opp inne.
