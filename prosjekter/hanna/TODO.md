# TODO — HANNA

Restanse etter helhetsrevisjonen (tre uavhengige revisorer, 2026-08-20/21).
Retterunde 1 er landet (`77a3657`). Stryk punkter etterhvert som de landes.

## Pågår

- [ ] **Retterunde 2** (agent i arbeid): byggesteg-logikk (bakramme-reisning som
      tipp, steg 0 delt i verksted-/romdelhull, trimpunkter, steg 2-festetabell),
      sone 3-beslutning (veggfester i bordbærelekta eller omdøpt kolonne),
      steg-06/steg-02-figurfiks + tegnet-festemiddel-assert, spikerslag-arkets
      tekstkollisjoner, ASSEMBLY/PRAKSIS/UTSTYR-etterslep, håndark mot ny
      bordkloss 48×68×91. Reviewes, portes, committes.

## Neste: portrunde — automatiser klassene revisorene fant manuelt

- [ ] **C9 per byggesteg**: manøvrerbarhets-regelen (i dag bare enkeltdeler)
      kjørt på hvert stegs sammenstilling — ville felt «1990-ramme inn i
      1990-nisje» maskinelt.
- [ ] **Referanse-ende mot overmål**: assert som feller festeplasseringer som
      refererer en ende med overmål på boretidspunktet (kappliste × X6 er
      begge datasett porten alt har).
- [ ] **README-tall målt av porten**: talte tall (asserter, deler, sider,
      festemidler, løpemeter) sammenlignes maskinelt mot README i check,
      i stedet for å gjenfortelles.
- [ ] **ASSEMBLY-tallsveip i porten**: hvert «NNN mm/MPa/kg» i håndprosaen mot
      modellens oppnåelige verdier, med hviteliste (konsistensrevisoren gjorde
      dette manuelt — femlinjers skript).
- [ ] Falsifisering som port, ikke vane: systematisk feilinjisering av nye
      asserter (tally-rundens 7/7-mønster).

## Mindre restanse fra revisjonen

- [ ] ~28 halvtautologiske asserter utenfor de to klyngene (de 23 hele er tatt).
- [ ] `render_endelevation`: «14 like»/puteantall er verifisert riktige, men
      hardkodet — krever refaktor av modulnivå-dict for å utledes.
- [ ] `schematic.Sheet.dim`: samme ordmellomrom-under-halo-problem som
      `render_lineart` fikk brudd-i-streken for.

## Åpne beslutninger (Hans)

- [ ] **Linjelaser-kjøp**: anbefaling Bosch UniversalLevel 360 Premium Set
      (~1 732 kr); budsjett: Jula Meec 360° 999 kr / Bosch PLL 360 1 095 kr
      (PLL 360-1 mangler vertikal linje — unngå). Avstandsmåler bevisst
      avmeldt (laserplan + tommestokk er mer presist). Føres i UTSTYR.md når
      valgt.
- [ ] **Release**: kutte release på alt dette (v2.0 — geometrien er ny), eller
      la main stå til rommet er målt og WALL_SPAN satt?
- [ ] **Fotstøtte ved pulten**: åpent punkt fra bordrunden (sålene henger
      134 mm for referansebarnet). Kan ses sammen med krok-oppgaven (v2).

## Fysisk huskeliste (byggeplass)

- Madrass oppe: **120 mm** (110–125). 140/150/160 er ulovlige — gammel plan sa 150.
- 48×68: **3 bord**; 36×48: **1 bord** (bordklossene flyttet til 48×68 i X10).
- Fjern fotlist/listverk i hele nisjas bredde før reisning.
- Kryssfinerplaten kappes med dekkfiber **langs** 574-retningen (bæreevne).
- Nisjedybde ≥ 1402 mm må bekreftes ved rommåling (bakrammen tippes opp inne).
