<!-- GENERERT AV generate_loftbed.py / tools/gen_doc_tables.py.
     IKKE REDIGER FOR HÅND - kjør `mise run build`. -->

# Nøkkelmål

Alle mål i mm. X går langs rommet mellom de to veggene, Y i dybden med bakveggen på -48, Z opp fra gulvet.

## Ytre mål

| | Mål |
|---|---:|
| Bredde, vegg til vegg | 1990 |
| Dybde over alt | 836 |
| Høyde foran (stolpetopp) | 1700 |
| Høyde ved veggen (bakre stolpe) | 1065 |
| Gjennomgående deler kappes til | 1984 (X 3..1987) |
| Klaring til hver vegg for disse | 3 |

En 1990 mm lang del lar seg ikke svinge inn i en 1990 mm åpning. Derfor er hver gjennomgående del 1984 mm.

## Høyder (Z)

| Z | Hva |
|---:|---|
| **0** | gulv |
| **186** | benkevangens underkant / stubbefotens topp |
| **259** | benkevangens overkant = trinn 1 = platens underside i sengestilling |
| **277** | platens overside i sengestilling |
| **295** | benkeoverflate (sittehøyde) |
| **409** | bordbærelektas underkant |
| **482** | bordbærelektas overkant = trinn 2 = platens underside i bordstilling |
| **500** | bordplate |
| **720** | trinn 3 |
| **958** | trinn 4 |
| **967** | endebjelkens underkant |
| **1065** | endebjelkens overkant = sidevangens underkant (fri høyde under sengen) |
| **1163** | sidevangens overkant |
| **1199** | spilebunn / madrassens underside / bakre stolpetopp |
| **1339** | madrassens overside (ved 140 mm madrass; lovlig band 140–326) |
| **1414** | rekkverk, nedre bånd underkant |
| **1512** | rekkverk, nedre bånd overkant |
| **1587** | rekkverk, øvre bånd underkant |
| **1685** | rekkverk, øvre bånd overkant |
| **1700** | fremre stolpetopp |

Stigningen fra gulv til spilebunn: 259 + 223 + 238 + 238 + 241 mm. Første stigning er benkevangens høyde — det er en avsats du trår opp på, ikke et klatretrinn. De fire klatretrinnene er 223–241 mm.

## Dybdeplan (Y)

| Y | Hva |
|---:|---|
| **-48** | BAKVEGGEN — monteringsflaten. Bakre stolper, endebjelkeender og bakre stubbeføtter ligger i dette planet. Ingenting får stikke bak det.; bakre sidevange, benkevange, bordbærelekt og spilebunn — bakkant; bakre stolpes forside |
| **-27** | bordbærelektas forside |
| **0** | bakre sidevanges og benkevanges forside; avstivningslektenes bakkant |
| **704** | fremre sidevange og benkevange — bakkant |
| **715** | trinnenes bakkant (hylla platen hviler på) |
| **716** | rekkverksbordenes bakkant |
| **750** | platens forkant; avstivningslektenes og kilelektenes forkant |
| **752** | fremre sidevanges forside = fremre stolpers og stigevangers bakside = spilebunnens forkant; rekkverksbordenes forkant |
| **788** | fremre stolpers og stigevangers forside = trinnenes forkant; sengens forkant — det ytterste planet |

Fri bredde mellom de to sidevangene: **704**. Spilebunnen fra vange til vange: **800** — nøyaktig madrassbredden.

## Stige, trinn og rekkverk (X)

| | X |
|---|---|
| Stigens senterlinje | 995 |
| Stigevanger | 787..835 og 1155..1203 |
| Fri åpning mellom stigevangene | **320** |
| Trinn (4 stk.) | 835..1155, 320 mm lange |
| Stigeklosser | 835..871 og 1119..1155 |
| Rekkverksbord | 3..835 og 1155..1987 |
| Klatreåpning i begge rekkverksbånd | **320** |
| Benkene | 0..645 og 1345..1990 |
| Åpent gulv mellom benkene | 645..1345 (700 mm) |
| Gangpassasje ved siden av stigen | 142 mm på hver side |
| Stubbeføtter | 572..645 og 1345..1418 |
| Løs plate | 708..1282 (574 mm bred) |
| Avstivningslekter (styrer platen) | 785..833 og 1157..1205 |
| Kilelekter under forkanten | 708..785 og 1205..1282 |
| Klaring lekt → trinnende | 2 mm hver vei (trinnendene står på X 835 og 1155 i begge stillinger) |

**Køyespiler:** 14 stk., første spile starter på X 20, deling 142,46 mm, siste spile slutter på X 1970. Åpning mellom spilene 44,46 mm.

**Benkespiler:** 5 per benk, deling 112,25 mm fra ytterveggen og innover.

## Skruerader i rammeleddene

Ingen bolt går inn i en stolpe. Stolpen er 36 mm tykk, og på den tykkelsen har en M8 ikke nok kantavstand; en 6 mm treskrue har akkurat nok. To skruer i et ledd står alltid symmetrisk om delens midtlinje. Skruetyper og antall står i [beslaglista](beslagliste.md).

| Ledd | Skruer | Z | Kantavstand | Avstand mellom | I planet |
|---|---:|---|---|---:|---|
| J1 — endebjelke 48×98 | 2 per ledd | **994** og **1038** | 27 / 27 | 44 | Y -30 og 770 (midt i stolpedybden) |
| J2 — sidevange 48×98 | 2 per ledd | **1092** og **1136** | 27 / 27 | 44 | X 50,5 fra hver vegg |
| J8 — benkevange 48×73 | 2 per ledd | **210,5** og **234,5** | 24,5 / 24,5 | 24 | X 50,5 fra hver vegg |

Minstekrav for en forboret 6 mm treskrue: kantavstand 18 mm (3d), avstand mellom to skruer langs fiberretningen 30 mm (5d). Alle radene over holder kravet.

Endeavstanden fra vangens ende inn til J2- og J8-skruen er 47,5 mm, godt over minstekravet 18 mm — den brede stolpen ga denne avstanden gratis.

**Ingen forsenkte boltehoder.** Ingen del av rammen festes lenger fra en flate som ender mot vegg, så det finnes ikke et eneste hode som må senkes ned under en monteringsflate. Skruehoder forsenkes som vanlig der de er i veien for hånda.

## Madrass og puter

| | Mål |
|---|---|
| Madrass, overkøye | **standard 80 × 200 cm.** Sengen er dimensjonert rundt den; liggeflaten er 1990 × 800 mm, så madrassen presses de siste 10 mm inn mellom veggene og fyller bredden nøyaktig |
| Madrasstykkelse | **140–326 mm.** Tynnere enn 140 og åpningen opp til nedre rekkverksbånd blir større enn 75 mm; tykkere enn 326 og rekkverket står mindre enn 160 mm over madrassen. Modellen tegner 140 mm |
| Madrassens sideveis vandring | ingen — madrassen fyller hele bredden mellom veggen og de fremre stolpene |
| Puter i underetasjen, dybde | 798 mm |
| Pute over venstre benk | 645 mm bred |
| Pute over platen (midten) | 700 mm bred |
| Pute over høyre benk | 645 mm bred |
| Midtputen er tykkere enn benkeputene med | 18 mm — platen ligger så mye lavere enn benkeflaten, og det er nettopp plassen putene skal folde seg ned i |

## Sikkerhetsmål (EN 747)

| | Mål | Krav |
|---|---:|---:|
| Madrassoverside → nedre rekkverksbånd | 75 | ≤ 75 |
| Mellom de to rekkverksbåndene | 75 | ≤ 75 |
| Øvre bånd → stolpetopp | 15 | ≤ 75 |
| Rekkverkets høyde over madrassen | 346 | ≥ 160 |
| Åpning mellom madrass og vegg (verste stilling) | 0 | ≤ 75 |
| Fri klatreåpning i stigen | 320 | ≥ 300 |
| Største klatretrinn | 241 | ≤ 250 |
