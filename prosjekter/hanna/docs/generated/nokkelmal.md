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
| **191** | benkevangens underkant / stubbefotens topp |
| **259** | benkevangens overkant = trinn 1 = platens underside i sengestilling |
| **277** | platens overside i sengestilling |
| **282** | benkeoverflate (sittehøyde uten pute) |
| **382** | **puteoverflate — nedre soveflate og sittehøyde med pute** (V13) |
| **414** | bordbærelektas underkant |
| **482** | bordbærelektas overkant = trinn 2 = platens underside i bordstilling |
| **500** | bordplate |
| **714** | ryggputens topp i sofastilling (V13) |
| **720** | trinn 3 |
| **958** | trinn 4 |
| **967** | endebjelkens underkant |
| **1065** | endebjelkens overkant = sidevangens underkant (fri høyde under sengen) |
| **1163** | sidevangens overkant |
| **1186** | spilebunn / madrassens underside / bakre stolpetopp |
| **1336** | madrassens overside (ved 150 mm madrass; lovlig band 140–155) |
| **1401** | rekkverk, nedre bånd underkant |
| **1499** | rekkverk, nedre bånd overkant |
| **1574** | rekkverk, øvre bånd underkant |
| **1672** | rekkverk, øvre bånd overkant |
| **1700** | fremre stolpetopp |

Stigningen fra gulv til spilebunn: 259 + 223 + 238 + 238 + 228 mm. Første stigning er benkevangens høyde — det er en avsats du trår opp på, ikke et klatretrinn. De fire klatretrinnene er 223–238 mm.

## Dybdeplan (Y)

| Y | Hva |
|---:|---|
| **-48** | BAKVEGGEN — monteringsflaten. Bakre stolper, endebjelkeender og bakre stubbeføtter ligger i dette planet. Ingenting får stikke bak det.; bakre sidevange, benkevange, bordbærelekt og spilebunn — bakkant; bakre stolpes forside |
| **-27** | bordbærelektas forside |
| **0** | bakre sidevanges og benkevanges forside; avstivningslektenes bakkant |
| **704** | fremre sidevange og benkevange — bakkant |
| **716** | rekkverksbordenes bakkant |
| **720** | trinnenes bakkant (hylla platen hviler på) |
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
| Stubbeføtter | 577..645 og 1345..1413 |
| Løs plate | 708..1282 (574 mm bred) |
| Avstivningslekter (styrer platen) | 785..833 og 1157..1205 |
| Kilelekter under forkanten | 708..785 og 1205..1282 |
| Klaring lekt → trinnende | 2 mm hver vei (trinnendene står på X 835 og 1155 i begge stillinger) |

### Platebredden er kvantisert — lovlige vinduer

Åpningen mellom benkene er fast, **700 mm**, så sideklaringen er `(700 − bredde) / 2` på hver side. EN 747 gjør bare tre klaringsbånd lovlige — under 5 mm kommer ikke fingeren inn, 12–25 mm går den fritt gjennom, 60–75 mm går hele lemmet fritt og åpningen er fortsatt under EN 747s egen 75 mm-grense — og mellom båndene kiler fingeren seg. Bredden er derfor ikke en skrue man vrir på: den lander i ett av tre vinduer, eller så er den ulovlig.

| Klaringsbånd | Lovlig platebredde | |
|---|---|---|
| 60–75 mm | 550–580 mm | **valgt — 574 mm, 63 mm klaring** |
| 12–25 mm | 650–676 mm | tidligere vindu (652 mm) |
| 0–5 mm | 690–700 mm | upraktisk — spiser opp de 2 mm innsettingsklaring |
| — | **581–649 mm** | **forbudt** — klaringer 25,5–59,5 mm, midt i klembåndet |
| — | **677–689 mm** | **forbudt** — klaringer 5,5–11,5 mm, midt i klembåndet |

Bredden deltar **ikke** i begrensningene på stillingsbyttet — det er høyden og dybden på plateenheten som møter overføringssjakten (132 mm fri høyde mot en 86 mm høy enhet). Å smalne platen gir mer slingring ved innsettingen og mindre bordflate, ingenting annet. Modellen asserter vinduene: en «bare litt smalere»-endring stopper byggeporten med akkurat denne tabellen.

**Køyespiler:** 14 stk., første spile starter på X 20, deling 142,46 mm, siste spile slutter på X 1970. Åpning mellom spilene 44,46 mm.

**Benkespiler:** 5 per benk, deling 112,25 mm, felt X 98..645 (speilvendt på den andre benken).

**Endespiler (V13):** 1 per benk, 764 mm lang, X 0..98 og 1892..1990, Y -12..752. Den er kortere fordi den starter på den bakre hjørnestolpens forside, og den lukker feltet helt ut til veggen — spalten inn til første benkespile er 0 mm. Uten den stopper soveflaten nede 98 mm fra veggen i hver ende. Endelisten under den er 36×48 × 98 mm, skrudd på stolpens forside (J17).

## Skruerader i rammeleddene

Ingen bolt går inn i en stolpe. Stolpen er 36 mm tykk, og på den tykkelsen har en M8 ikke nok kantavstand; en 6 mm treskrue har akkurat nok. To skruer i et ledd står alltid symmetrisk om delens midtlinje. Skruetyper og antall står i [beslaglista](beslagliste.md).

| Ledd | Skruer | Z | Kantavstand | Avstand mellom | I planet |
|---|---:|---|---|---:|---|
| J1 — endebjelke 48×98 | 2 per ledd | **994** og **1038** | 27 / 27 | 44 | Y -30 og 770 (midt i stolpedybden) |
| J2 — sidevange 48×98 | 2 per ledd | **1092** og **1136** | 27 / 27 | 44 | X 50,5 fra hver vegg |
| J8 — benkevange 48×68 | 2 per ledd | **213** og **237** | 22 / 22 | 24 | X 50,5 fra hver vegg |

Minstekrav for en forboret 6 mm treskrue: kantavstand 18 mm (3d), avstand mellom to skruer langs fiberretningen 30 mm (5d). Alle radene over holder kravet.

Endeavstanden fra vangens ende inn til J2- og J8-skruen er 47,5 mm, godt over minstekravet 18 mm — den brede stolpen ga denne avstanden gratis.

**Ingen forsenkte boltehoder.** Ingen del av rammen festes lenger fra en flate som ender mot vegg, så det finnes ikke et eneste hode som må senkes ned under en monteringsflate. Skruehoder forsenkes som vanlig der de er i veien for hånda.

## Madrass og puter

| | Mål |
|---|---|
| Madrass, overkøye | **standard 80 × 200 cm.** Sengen er dimensjonert rundt den; liggeflaten er 1990 × 800 mm, så madrassen presses de siste 10 mm inn mellom veggene og fyller bredden nøyaktig |
| **Madrasstykkelse** | **140–155 mm — kjøp 150 mm.** Åpningen fra madrassens overside opp til nedre rekkverksbånd skal ligge i EN 747-båndet 60–75 mm. Tynnere enn 140 og åpningen blir større enn 75; **tykkere enn 155 og den faller ned i klemvinduet under 60 mm**. En vanlig 160 mm madrass er altså ULOVLIG her. Modellen tegner 150 mm, som gir 65 mm — midt i båndet |
| **Maks madrasstykkelse merkes på sengen** | 155 mm. EN 747 krever at maksmålet står permanent på sengen. Merk linja 1341 mm over gulvet — 155 mm over spilene — på innsiden av en fremre stolpe (steg 11) |
| Madrassens sideveis vandring | ingen — madrassen fyller hele bredden mellom veggen og de fremre stolpene |
| **Soveflate, underetasjen** | **1990 × 800 mm** — samme lengde som overkøyen. De to bakre hjørnestolpene står i flaten og tar et 98 × 36 mm hjørne i hver ende; ellers er den hel |
| **Puter, tykkelse** | **100 mm, alle fire.** Lik tykkelse er hele poenget: fire like tykke puter er én seng. Sittehøyden blir 282 + 100 = **382 mm** |
| Puter, dybde | 800 mm — hele flatens dybde, vegg til fremre stolpeplan |
| **Benkepute (2 stk.)** | **663 × 800 × 100 mm** — 1/3 av lengden. Skjær et 98 × 36 mm hakk i veggkanten, der stolpen står |
| **Ryggpute (2 stk.)** | **332 × 800 × 100 mm** — 1/6 av lengden. Rene rektangler |
| Regnestykket | 663 + 332 + 332 + 663 = **1990 mm**. 1990 deler seg ikke på 6, så tredelen er rundet ned og sjettedelen opp — summen er eksakt, og det er summen som må stemme |
| Alle fire av én skumplate | 80 × 200 cm dekker dem: 800 mm er nøyaktig dybden og 2000 mm er 10 mm mer enn lengden. Fire tverrkapp |
| Midtsonen ligger | 5 mm lavere enn benkene (377 mot 382 mm). Putene er like tykke likevel — skummet tar de 5 millimeterne, og ingen puteskjøt ligger på en sonegrense |
| Hodehøyde over nedre soveflate | 781 mm til køyespilene (683 mm under sidevangene) |
| Ryggpute i sofastilling | står på høykant ytterst på hver benk: 100 mm tykk, 800 mm dyp, 332 mm høy, topp 714 mm. Ryggen mot bordbærelekta |


## Referansekroppen — hva sengen er til for

Modellen har fire *referansekropper*: et barn på **1200 mm** (EN 747 åpner overkøya fra 6 år), bygget som én solid av 14 kuler, sylindre og bokser med segmentene som brøkdeler av ståhøyden etter **AnthroKids** (de digitaliserte Snyder-studiene 1975/1977, math.nist.gov/~SRessler/anthrokids/, fri bruk). To ligger i sengestilling, to sitter i bordstilling. En kropp er ikke en del: den kappes ikke, bærer ingenting, står i ingen liste og er tatt ut av alle kontaktsjekker — men den er i parts.tsv og i eksportene, og målene under er målt på den.

| | Mål |
|---|---:|
| **Fri høyde over hodet, sittende** | **127 mm** — kronen står i Z 1036 og «Bed Slat_11» er det første over. Man sitter helt rett opp i sofaen |
| Sittehøyde | 654 mm (0,545 × H) over seteflaten på 382 mm |
| **Bordplaten over setet** | **118 mm**, og bare 100 mm under seg — ett lår er 115 mm. **Ingen knær går under denne platen.** Den er en lekeflate i fanghøyde mellom to sofahalvdeler, og man sitter i skredderstilling ved den |
| Foldet kne til platekant | 130 mm |
| Håndleddet over platen | 5 mm — armen rekker fram når overkroppen lener seg |
| **Fri høyde over ansiktet, nede** | **603 mm** til køyespilene |
| Over den som ligger i køya | ingenting — køya er åpen oppover. Rekkverket står 93 mm over kroppens høyeste punkt og 158 mm over ansiktet |
| Madrass igjen bak føttene | 588 mm av 1990 — plassen å vokse i |

## Sikkerhetsmål (EN 747)

| | Mål | Krav |
|---|---:|---:|
| Madrassoverside → nedre rekkverksbånd | 65 | ≤ 5 eller 60–75 |
| Mellom de to rekkverksbåndene | 75 | ≤ 5 eller 60–75 |
| Klatreåpningens bredde | 320 | 300–400 |
| Rekkverkets høyde over madrassen | 336 | ≥ 160 |
| Åpning mellom madrass og vegg (verste stilling) | 0 | ≤ 75 |
| Fri klatreåpning i stigen | 320 | ≥ 300 |
| Største klatretrinn | 238 | ≤ 250 |
