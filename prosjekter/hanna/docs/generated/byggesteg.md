<!-- GENERERT AV generate_loftbed.py / tools/gen_doc_tables.py.
     IKKE REDIGER FOR HÅND - kjør `mise run build`. -->

# Steg for steg

Rekkefølgen er ikke fri. Sengen står inntil bakveggen og inntil begge sidevegger, og den bygges på plass. Alt som skal skrus eller boltes fra en flate som ender mot vegg, må gjøres før den flaten kommer inntil veggen. Derfor bygges den bakfra og utover.

Bildeversjonen av de samme stegene, med samme nummer, ligger i [MONTERING.md](../MONTERING.md). Mål slår du opp i [nøkkelmål](nokkelmal.md) og [kappliste](kappliste.md); leddene står i J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene), med antall og forboring i [beslaglista](beslagliste.md).

**Hvert steg har en «festeplassering»-tabell**, og den er svaret på hvor langt inn og hvor langt opp på materialet et feste skal stå. Hullet er oppgitt i DELENS egne mål — så mange mm inn fra en navngitt ende, så mange mm inn fra en navngitt kant, og senteravstand mellom hullene i samme rad. Ta tabellene med til steg 0: det er der du merker opp og borer, mens delene ennå ligger løse på bukken.

* **Ytterenden** er den enden av delen som peker mot nærmeste endevegg, **innerenden** den som peker inn mot sengas midte. Derfor gjelder ett mål begge sider av senga — og modellen måler at de to halvdelene faktisk projiserer til samme tall før det skrives.
* **Stående deler måles ovenfra.** Foten kappes i vater etter at rammen står, så den enden finnes ikke ennå når du borer.
* **«midt på» er senterlinjen.** Riss den opp med senterlinjal eller med to diagonaler — ikke mål fra den ene siden.
* Målene er senter av hullet. Retningen skruen drives, og hvorfor akkurat den veien, står i [skrueretninger](skrueretninger.md).

## Før steg 0 — mål rommet

Nisja er hverken i vinkel eller i vater, og senga skal stå i begge deler. **Senga er referansen, ikke rommet — bygg i vater og lodd, og ta skjevheten i delene som møter vegg og gulv.**

**Slik gjør du:**

1. Vent til vegger og gulv er ferdige. **Mens veggen er åpen: legg spikerslag i sonene under.** Etterpå kommer du ikke til.
1. **Riv fotlist og alt annet listverk langs bakveggen i hele nisjas bredde — alle 1990 mm — før rammen reises.** 4 deler står både PÅ gulvet og I veggplanet Y -48: de to bakre hjørnestolpene og de to bakre benkeføttene, og en list under dem skyver hele bakkanten ut fra veggen.
1. Slå et vannrett høyderiss rundt hele nisja med linjelaser, 1000 mm over ferdig gulv. Alt måles fra risset, aldri fra gulvet — spikerslagsonene under står i begge notasjoner, og det er riss-kolonnen du setter dem etter.
1. Sett laseren som loddlinje midt i nisja. Mål ut til hver endevegg i rutenett: 5 høyder × 3 dybder på hver vegg. Legg sammen paret i hvert punkt. **Minste sum er nisjas minste bredde.**
1. Er minste bredde et annet tall enn 1990: sett den inn som `WALL_SPAN` i `generate_loftbed.py` og kjør `mise run build`. Kapplista regner seg om.
1. Gulv: mål ned fra risset i sengas fire hjørner og på midten. Merk det høyeste punktet på gulvet. Senga bygges ned fra det.
1. Kapp verksteddelene nå. Romdelene tilpasses på stedet: stolper og føtter kappes 15 mm for lange og trimmes i bunn til rammen står i vater — strek opp med avstandskloss, meddrag. Sidevangene kappes 10 mm for lange i hver veggende og finkappes etter målt bredde. Ytterste endespile strekes opp etter veggen med fast avstand, så fugen blir jevn.
1. **De fire hjørnestolpene står helt inntil endeveggen — null klaring.** Derfor strekes veggsiden på hver av dem, hver gang: sett stolpen på plass, hold den i lodd, og strek opp veggsiden med avstandskloss der veggen buler. Høvle av til stolpen står i lodd inntil veggen. Ingen monn i bredden — det er tre som skal bort, ikke legges til. Buler veggen og du lar det stå, skyver bulen hele rammen ut av lodd.
1. Kapp kanter som møter vegg eller gulv med lite bakfall. Da er det bare den synlige kanten som bestemmer fugen.

**Spikerslag i veggen:**

| Sone | Fra ferdig gulv | Fra høyderisset (1000) | Vegg | Del som skal ha feste |
|---:|---|---|---|---|
| 1 | **0–1402** | **-1000..+402 krysser risset** | Hjørnene, mot endeveggene | Hjørnestolpe, bak (veggside) (2 stk.) |
| 2 | **229–297** | **-771..-703 under risset** | Bakveggen | Benkevange, bak (gjennomgående) |
| 3 | **614–682** | **-386..-318 under risset** | Bakveggen | Bordbærelekt, bak |
| 4 | **1402–1500** | **+402..+500 over risset** | Bakveggen | Sidevange, øvre |

To notasjoner, samme sone. **Målt fra ferdig gulv** er modellens egen Z. **Målt fra høyderisset** er den samme høyden minus 1000 — minus er *under* laserlinja, pluss er *over* den. Gulvet er skjevt og risset er ikke: står du ved den åpne veggen med målebåndet på laserlinja, er det den andre kolonnen du setter sonene etter.

Gulv-kolonnen er fra **ferdig gulv**. Legges gulvet etterpå, må påforingshøyden legges til — i begge kolonner, for risset slås fra ferdig gulv det også.

Hva som kappes nå og hva som kappes på stedet: [kapplista](kappliste.md).

**Sjekk før du går videre:**

* Høyderisset skal gå hele veien rundt nisja og møte seg selv. Gjør det ikke det, står laseren feil.
* Er forskjellen mellom minste og største bredde større enn 10 mm, mål om. Kapp uansett etter den minste.
* Sjekk at spikerslagene ligger i sonene før veggen lukkes — målt ned eller opp fra høyderisset, ikke opp fra gulvet.
* Bakveggen skal være bar helt ned til gulvet i alle 1990 mm, ikke bare der de 4 delene i veggplanet lander. Hold en rett list mot veggen nederst: den skal ligge an hele veien.
* Hver hjørnestolpe skal stå i lodd begge veier. Vipper den fordi veggen buler, høvles bulen av — lys i fugen der veggen viker er greit og skal stå.

## Steg 0 — Kapping, forboring og forsenking

Gjør alt sagarbeid og all boring på bukk, før noe reises. Etterpå kommer du ikke til med drillen på de flatene som vender mot vegg.

**Festemidler:** 8× Filtknott / møbeltapp ⌀40

**Ledd:** J15 — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Slik gjør du:**

1. Kapp etter kapplista. **Verksteddelene kappes ferdig; romdelene kappes med overmål** — kapplista sier hvilke og hvor mye, og de finkappes i rommet. Alle kutt er 90°, ingen gjæring — med to navngitte unntak, og begge står i kapplista: de to kilelektene under platens forkant, og de to vinkelklossene.
1. Skråkapp de to kilelektene. De er 48×68 × 77 mm og skal sages ned i ett rett snitt fra full høyde i den ene enden til 27 mm i den andre (28,0°). Håndsag eller båndsag; overkanten — den som skal limes mot plata — skal stå urørt og plan.
1. Lag de to vinkelklossene, borjiggene til skråskruene — én til J8-B og én til J10. Hver kloss er 2 biter 48×68 × 200 mm av restene, skrudd FLATE MOT FLATE. Bor ⌀18 VINKELRETT gjennom begge mens klossen ennå er firkantet — det er hullet som styrer boret siden, ikke en rampe. Kapp så sålen av under hullet på kappsag med bladet vippet 25° (J8-B) hhv. 30° (J10).
1. **Vippen og flaten er komplementvinkler.** 25° vipp gir en såle som står 65° på den borede flaten — og dermed 25° på hullaksen, som er det leddet er regnet på. Kontroller med tommestokken før klossen får røre sengen: hullets munning i sålen skal måle 42,6 × 18 mm på 25°-klossen og 36 × 18 mm på 30°-klossen. Er ellipsen for kort, ble vippen satt på feil vinkel. Klossene bygges ikke inn i sengen — de er verktøy.
1. Merk hver del med blyant på en flate som blir skjult.
1. **Bryt alle kanter et barn kan nå, nå — mens delene er løse.** Kravet er brutt kant, ikke en bestemt metode: 45° fas eller avrunding, du velger. Fres med V-spor eller avrundingsfres om du har fres; ellers gjør en blokkhøvel eller en pussekloss med 120-korn nøyaktig samme nytte. Viktigst: plateenhetens underside — begge styrelektenes nedre kanter og begge kilene — for det er der et kne møter treet når noen sitter ved bordet. Deretter platens fire egne kanter, og så stolper, rekkverksbord, trinn og stigevangenes kanter. Modellen tegner alle deler skarpe; kantbrytningen er en instruks og flytter ingen mål.
1. Bor alle gjennomgående hull i stolper, vanger, endebjelker og benkevanger — diameter etter forboringskolonnen i beslaglista. Bor gjennom begge deler samtidig, med delene tvunget sammen.
1. Forsenk hodene på alle festemidler som ender i en veggvendt flate. Beslaglista sier hvilke ledd det gjelder.
1. Forbor alle treskruer etter beslaglista. I bordene og i all endeved er forboring et krav, ikke et råd.
1. **Bor setene til de åtte skråskruene nå** — mens delene er løse og ligger flatt på benken. Fire i den bakre benkevangens forside (J8-B) og fire i stubbeføttenes innersider (J10). Reist seng kommer du ikke til med hverken kloss eller tvinger. Alt om setene og klossene er tegnet opp på [setedetalj.svg](../schematics/setedetalj.svg).
1. Slik bores et sete: klem vinkelklossen mot flaten med TO tvinger, hullet rett over merket, og legg en offerkloss mot endeveden. Drillen i **gir 1 og slag AV** — et forstnerbor i slagmodus brenner og vandrer. Trekk boret helt ut 2–3 ganger per lomme og børst sponet ut; et fullt forstnerbor skjærer ikke, det gnisser. Dybden er merket du satte på boret da du lagde klossen: 20 mm langs aksen på J8-B, 18 mm på J10.
1. På den bakre benkevangen står to lommer ved siden av hverandre i hver ende, 24 mm fra senter til senter. **Bor den som ligger nærmest kanten først** — da har klossen hel flate å stå på. Når den andre skal bores, hviler klossen delvis over den ferdige lomma; legg en tynn list under den enden så den ikke vipper.
1. Forbor for skruen med det samme, mens delen ligger som den ligger: **lommebunnen er forborets egen jigg.** Bunnen står vinkelrett på skrueaksen, så et brad-point-bor satt i senter av den flate bunnen (⌀6 på J8-B, ⌀3,5 på J10) retter seg selv inn i riktig vinkel. Ikke prøv å sikte den på frihånd.
1. Slå filtknotter under alle fire hjørnestolper og alle fire stubbeføtter.

**Sjekk før du går videre:**

* Romdelene skal IKKE kappes ferdig nå. Kapplista sier hvilke — de kappes med overmål og finkappes i rommet.
* Legg de to lengste delene — sidevangene — inn i rommet nå og sjekk at de går fritt forbi begge vegger. De er kappet kortere enn veggavstanden nettopp for dette.
* Legg delene i fire hauger på gulvet, én per steg. Du kommer til å lete mindre.

## Steg 1 — Bakrammen — bygg den flatt på gulvet

Hele baksiden av sengen er ett eneste flatt lag: to korte stolper og tre vannrette deler i samme plan. Det laget er monteringsflaten mot veggen. Og det MÅ bygges som én ramme: den bakre benkevangen og bordbærelekta er kappet til å fylle nøyaktig mellom de to stolpene, så de lar seg ikke tre inn etterpå.

**Deler:** 1× Benkevange, bak (gjennomgående) 48×68 × 1794 · 1× Bordbærelekt, bak 48×68 × 1794 · 2× Hjørnestolpe, bak (veggside) 36×98 × 1402 · 1× Sidevange, øvre 48×98 × 1984

**Festemidler:** 4× Treskrue 5×40 forsenket Torx · 4× Treskrue 6×120 forsenket Torx · 4× Treskrue 6×80 forsenket Torx · 2× Vinkelbeslag 40×40×20

**Ledd:** J2-B, J8-B, J12 — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Festeplassering — mål på delen:**

| Ledd | Merkes opp på | Fra enden | Fra kanten | c/c |
|---|---|---|---|---:|
| **J2-B** 2× Treskrue 6×120 | bakre sidevange 48×98 × 1984, oversiden | 36 / 77 mm fra ytterenden | 18 mm fra bakkanten | 41 |
| **J8-B** 2× Treskrue 6×80 | bakre benkevange 48×68 × 1794, forsiden (mot rommet) | 34 mm fra ytterenden | 20 / 44 mm fra overkanten | 24 |
| **J12** 1× Treskrue 5×40 | bakre hjørnestolpe 36×98 × 1402, innersiden (mot sengas midte) | 808 mm fra toppen | midt på (18 mm fra hver side) | — |
| **J12** 1× Treskrue 5×40 | bordbærelekt 48×68 × 1794, undersiden | 20 mm fra ytterenden | 18 mm fra bakkanten | — |
| **J12** 1× Vinkelbeslag 40×40×20 | bakre hjørnestolpe 36×98 × 1402, innersiden (mot sengas midte) | 788 mm fra toppen | midt på (18 mm fra hver side) | — |

**Slik gjør du:**

1. Legg de to bakre stolpene ut i riktig avstand. De er de korte — de stopper under sidevangen.
1. Legg den bakre sidevangen oppå stolpetoppene. Den skal hvile på endeveden, ikke henge på siden av stolpen. Fest etter J2-B.
1. Legg den bakre benkevangen ned mellom stolpene og fest den etter J8-B. Det står ingen kloss under vangeenden — **hullene du boret i steg 0 er jiggen**: vangen har nøyaktig én høyde der hullene i vangen og hullene i stolpen står over hverandre. Legg en list eller en tvinge under vangen mens du skrur hvis du er alene. Vangen er kappet nøyaktig så den fyller mellom de to stolpene — den kan ikke tres inn senere.
1. J8-B er skråskruer, og setene deres er boret i steg 0 — ⌀18 flatbunnet lomme 20 mm ned langs skruens egen akse, 25° på flaten. Her skal du bare skru. Skruen finner lomma selv gjennom forboret; kjenn etter at hodet lander flatt på bunnen og ikke stopper høyt. Stopper det høyt, står konusen på kanten av forboret — skru ut, rens lomma for spon og ta den om igjen.
1. Sett vinkelbeslagene til bordbærelekta på stolpenes innsider, legg lekta på høykant mellom stolpene og fest etter J12.

**Sjekk før du går videre:**

* Mål diagonalene i rammen — de skal være like.
* Kjenn etter med håndflaten over hele baksiden: ingen skruehoder, ingenting som stikker ut. Denne flaten skal ligge helt flatt mot veggen.
* Legg vinkelhaken på begge hjørner.

## Steg 2 — Reis bakrammen og skru den fast i veggen

Sengen festes til veggen gjennom den bakre sidevangen. Vangen ligger flatt mot veggen i hele sin lengde, så skruene går rett gjennom den og inn i stenderne. De skruene holder ikke bare sengen på plass — de støtter også vangen på midten.

**Festemidler:** 6× Veggfeste etter veggtype (treskrue 8×100 i stender, eller plugg + skrue i mur)

**Ledd:** J14 — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Slik gjør du:**

1. Reis bakrammen og skyv den inntil bakveggen og inntil begge sidevegger.
1. Finn stenderne i veggen. Merk av senterlinjene på sidevangen.
1. Loddsjekk begge stolper, og vater langs sidevangen.
1. Skru rammen fast i veggen gjennom sidevangen (J14). Ta et feste i hver stender du treffer — minst i endene og på midten.
1. Skru en midlertidig skråstiver fra rammen ned til gulvet hvis rammen står alene en stund. Den er flat og velter lett framover.

**Sjekk før du går videre:**

* Vater langs sidevangen, og lodd på begge stolper.
* Ta tak i vangen og dra. Rammen skal ikke bevege seg fra veggen i det hele tatt.
* Er veggen mur eller betong, bruk plugg eller betongskrue. Er den bindingsverk, må du treffe stender. En plateplugg i gips er ikke et veggfeste.

## Steg 3 — Endebjelkene og de fremre stolpene

Nå bygges de to endene ut fra bakrammen. Endebjelken går fra den bakre stolpen til den fremre og bærer begge sidevanger.

**Deler:** 2× Endebjelke 36×98 × 836 · 2× Hjørnestolpe, front 36×98 × 2037

**Festemidler:** 8× Treskrue 6×80 forsenket Torx

**Ledd:** J1 — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Festeplassering — mål på delen:**

| Ledd | Merkes opp på | Fra enden | Fra kanten | c/c |
|---|---|---|---|---:|
| **J1** 2× Treskrue 6×80 | endebjelke 36×98 × 836, innersiden (mot sengas midte) | 18 mm fra vegg- og romenden | 19 / 63 mm fra underkanten | 44 |

**Slik gjør du:**

1. Reis den fremre stolpen på plass mot sideveggen.
1. Legg endebjelken opp mellom de to stolpene og fest den til begge etter J1. **Det er ingen bærekloss under bjelkeenden, og hullene fra steg 0 er jiggen:** bjelken har nøyaktig én høyde der hullene i bjelken og hullene i stolpen møtes, så du kan ikke sette den skjevt. Klem en list på stolpens innside i høyde med bjelkens underkant hvis du bygger alene — den listen tas av igjen.
1. Gjenta i den andre enden.

**Sjekk før du går videre:**

* Vater på begge endebjelker, og kontroller at de ligger i nøyaktig samme høyde.
* Lodd på begge fremre stolper, i begge retninger.
* Endebjelkens overkant skal ligge i flukt med den bakre sidevangens underkant. Gjør den ikke det, får ikke den fremre vangen samme høyde som den bakre.
* Kjenn etter at ingenting stikker ut mot sideveggene.

## Steg 4 — Fremre sidevange

Den fremre vangen lukker rammen i overetasjen. Den hviler på begge endebjelker og festes til de fremre stolpene.

**Deler:** 1× Sidevange, øvre 48×98 × 1984

**Festemidler:** 4× Treskrue 6×80 forsenket Torx

**Ledd:** J2 — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Festeplassering — mål på delen:**

| Ledd | Merkes opp på | Fra enden | Fra kanten | c/c |
|---|---|---|---|---:|
| **J2** 2× Treskrue 6×80 | fremre sidevange 48×98 × 1984, baksiden (mot veggen) | 47,5 mm fra ytterenden | 27 mm fra under- og overkanten | 44 |

**Slik gjør du:**

1. Løft vangen opp på endebjelkene, på utsiden av dem.
1. Fest den til begge fremre stolper etter J2. **Skruene drives innenfra:** du står inne i sengerammen — den er tom, spilene kommer først i steg 8 — og skrur gjennom vangens innside og inn i stolpen. Da blir stolpens forside, som er den flaten rommet ser, helt uten skruehoder.

**Sjekk før du går videre:**

* Mål avstanden mellom de to sidevangene i begge ender og på midten. Den skal være lik overalt — det er madrassbredden, og madrassen er kappet nøyaktig etter den.
* Vater langs vangen, og kontroller at den ligger i samme høyde som den bakre.
* Mål diagonalene i sengeflaten sett ovenfra.

## Steg 5 — Fremre benkevanger, stubbeføtter og endelister

Den fremre benkevangen er delt i to. Midtpartiet er med vilje åpent, slik at gulvet foran stigen er helt fritt. Endelisten hører hjemme i dette steget og ikke blant spilene: den er bæreverk som vangene, den står i samme høyde som dem, og den skal stå ferdig før noe legges oppå.

**Deler:** 2× Benkevange, front (bit) 48×68 × 642 · 2× Endelist 36×48 × 98 · 4× Stubbefot 48×68 × 229

**Festemidler:** 16× Treskrue 5×40 forsenket Torx · 8× Treskrue 5×60 forsenket Torx · 4× Treskrue 6×80 forsenket Torx · 4× Vinkelbeslag 90×90×40×2,5 varmforsinket

**Ledd:** J8, J10, J17 — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Festeplassering — mål på delen:**

| Ledd | Merkes opp på | Fra enden | Fra kanten | c/c |
|---|---|---|---|---:|
| **J8** 2× Treskrue 6×80 | fremre benkevange 48×68 × 642, baksiden (mot veggen) | 47,5 mm fra ytterenden | 22 mm fra under- og overkanten | 24 |
| **J10** 2× Treskrue 5×40 | stubbefot 48×68 × 229, yttersiden (mot sideveggen) | 22,5 / 67,5 mm fra toppen | midt på (24 mm fra hver side) | 45 |
| **J10** 2× Treskrue 5×40 | benkevange 48×68 × 1794, undersiden | 411,5 / 456,5 mm fra ytterenden | midt på (24 mm fra hver side) | 45 |
| **J10** 2× Treskrue 5×40 | benkevange 48×68 × 642, undersiden | 90,5 / 135,5 mm fra innerenden | midt på (24 mm fra hver side) | 45 |
| **J10** 1× Treskrue 5×60 | stubbefot 48×68 × 229, innersiden (mot sengas midte) | 35 mm fra toppen | midt på (24 mm fra hver side) | — |
| **J10** 1× Vinkelbeslag 90×90×40×2,5 | stubbefot 48×68 × 229, yttersiden (mot sideveggen) | i flukt med toppen | midt på (24 mm fra hver side) | — |
| **J17** 2× Treskrue 5×60 | endelist 36×48 × 98, forsiden (mot rommet) | 22,5 mm fra begge ender | 16 mm fra underkanten | 53 |

**Slik gjør du:**

1. Fest hver vangebit til sin fremre hjørnestolpe etter J8. **Skruene drives innenfra**, fra vangens innside og inn i stolpen, så stolpens forside blir stående uten skruehoder. Du kommer til ovenfra: benken er åpen til spilene går på i steg 7. Ingen kloss under enden — hullene fra steg 0 holder vangen i riktig høyde.
1. Sett en stubbefot under den innerste enden av hver vangebit. Vangebiten skal slutte akkurat der foten står — ingen utstikk forbi foten.
1. Sett de to bakre stubbeføttene under den bakre benkevangen, rett under de samme punktene.
1. Fest alle fire føtter etter J10. Den ene 5×60 per fot er en skråskrue nedenfra og opp i vangen, og setet er boret i steg 0 — ⌀18 flatbunnet lomme 18 mm ned langs aksen, 30° på fotens innerside. Skru beslaget først, skråskruen sist.
1. ENDELISTEN, én i hver ende: skru den flatt på FORSIDEN av den bakre hjørnestolpen, med overkanten i flukt med benkevangens overkant (297 mm over gulvet). To 5×60 ved siden av hverandre (J17) — 36 mm gjennom listen og 24 mm inn i stolpen, så det står 12 mm igjen til veggflaten bak. Ikke bruk lengre skrue.

**Sjekk før du går videre:**

* Ingenting skal krysse gulvet mellom de to benkene.
* Vater langs begge vangebiter, og samme høyde som den bakre benkevangen.
* Alle fire føtter skal stå med hele endeflaten mot gulvet og hele toppflaten mot vangen. Er det luft under en fot, kil den ikke opp — juster den.
* Legg en rett list fra endelisten og bort på begge benkevanger. Alle tre overkanter skal ta borti listen — det er flaten spilene legges på i steg 7.
* Ingen skruespiss skal være synlig eller følbar på baksiden av den bakre stolpen. Det er veggflaten.

## Steg 6 — Stigen

Bygg hele stigen ferdig liggende på gulvet, og skru den så på den fremre sidevangen.

**Deler:** 2× Bordkloss 48×68 × 91 · 5× Rungetrinn 48×68 × 320 · 10× Stigekloss 36×48 × 36 · 2× Stigevange 36×48 × 2037

**Festemidler:** 10× Treskrue 5×60 forsenket Torx · 10× Treskrue 6×120 forsenket Torx · 10× Treskrue 6×80 forsenket Torx

**Ledd:** J3, J4, J5, J5-B — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Festeplassering — mål på delen:**

| Ledd | Merkes opp på | Fra enden | Fra kanten | c/c |
|---|---|---|---|---:|
| **J3** 3× Treskrue 6×80 | fremre sidevange 48×98 × 1984, baksiden (mot veggen) | 808 mm fra ytterenden | 25 / 49 / 73 mm fra underkanten | 24 |
| **J4** 1× Treskrue 6×120 | stigevange 36×48 × 2037, yttersiden (mot sideveggen) | 763 / 988 / 1213 / 1489 / 1764 mm fra toppen | midt på (18 mm fra hver side) | — |
| **J5** 1× Treskrue 5×60 | stigekloss 36×48 × 36, innersiden (mot sengas midte) | midt på (24 mm fra hver ende) | midt på (18 mm fra hver side) | — |
| **J5-B** 2× Treskrue 6×80 | stigevange 36×48 × 2037, yttersiden (mot sideveggen) | 1377 / 1401 mm fra toppen | midt på (18 mm fra hver side) | 24 |

**Slik gjør du:**

1. Skru stigeklossene på innsiden av hver stigevange (J5). Klossen er 36 mm lang — nøyaktig så dyp som stigevangen — og skal ligge i flukt med vangens for- og bakkant, ikke stikke bakover slik trinnet gjør. Klosshøyden er trinnhøyden — mål to ganger.
1. Legg trinnene på klossene og fest dem (J4).
1. Skru de to BORDKLOSSENE på (J5-B) mens stigen ennå ligger flatt. De er 91 mm lange, står i samme X som stigeklossene og har overkanten på 682 — det er bordplatens underside. De skrus fra stigevangens UTSIDE, én 6x80 hver, og de stikker 53 mm BAKOVER forbi vangen: det er hylla bordplaten hviler på i bordstilling. Forkanten flukter med vangens forkant, som trinnene.
1. Reis stigen mot den fremre sidevangen. Trinnenes forkant skal ligge i flukt med stigevangenes forkant — trinnene stikker BAKOVER, ikke framover. Det som stikker bakover er hylla den løse platen skal hvile på.
1. Skru stigen fast til vangen etter J3 — **innenfra**, gjennom sidevangen og inn i stigevangen, så stigevangens forside blir uten skruehoder. Klem stigen fast mot vangen først; du står på den andre siden når du skrur. Gjennomgangshullene er boret i steg 0.

**Sjekk før du går videre:**

* Mål lysåpningen mellom stigevangene øverst og nederst — den skal være lik.
* Alle 5 trinn i vater.
* Mål høyden på bordklossenes overkant fra stigefoten: 682 mm, begge to, og i vater med hverandre. Bordplaten hviler på dem og på bordbærelekta samtidig — står de skjevt, vipper platen.
* Stå på nederste trinn og kjenn etter. Sitter noe løst nå, sitter det løst for alltid.

## Steg 7 — Benkespiler og endespiler

Fem spiler per benk, lagt oppå benkevangene — og helt ute ved hver vegg en 764 mm ENDESPILE på endelisten fra steg 5. De to endespilene er det som gjør underetasjen til en seng i full lengde: uten dem stopper spilefeltet 98 mm fra veggen i hver ende, og putekanten har ingenting under seg.

**Deler:** 10× Benkespile 23×98 × 800 · 2× Endespile 23×98 × 764

**Festemidler:** 24× Treskrue 5×60 forsenket Torx

**Ledd:** J11, J11-E, J16 — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Festeplassering — mål på delen:**

| Ledd | Merkes opp på | Fra enden | Fra kanten | c/c |
|---|---|---|---|---:|
| **J11** 1× Treskrue 5×60 | benkespile 23×98 × 800, oversiden | 24 mm fra vegg- og romenden | midt på (49 mm fra hver side) | — |
| **J11-E** 1× Treskrue 5×60 | endespile 23×98 × 764, oversiden | 24 mm fra romenden | 23 mm fra innerkanten | — |
| **J16** 1× Treskrue 5×60 | endespile 23×98 × 764, oversiden | 18 mm fra veggenden | midt på (49 mm fra hver side) | — |

**Slik gjør du:**

1. Legg ut alle fem spilene på én benk før du skrur, og sjekk delingen mot kapplista.
1. Skru hver spile ned i den bakre og den fremre benkevangen, én skrue per ende (J11). Forsenk hodene — dette er en sitteflate.
1. Gjenta speilvendt på den andre benken.
1. ENDESPILEN er kortere enn de andre, 764 mm: den starter på stolpens forside, ikke på veggen — stolpen står i soveflaten her. Endelisten den skal hvile på sitter ferdig på stolpen fra steg 5; her legges bare spilen. Legg den mot veggen, tett inntil naboen, og skru én skrue ned i endelisten (J16) og én ned i den fremre benkevangen (J11-E).

**Sjekk før du går videre:**

* Kjenn over hele benken med håndflaten: ingen skruehoder skal stikke opp.
* Sett deg på begge benker.
* Endespilen skal ligge i nøyaktig samme plan som de andre — legg en rett list på tvers over hele benken og se etter lys under.

## Steg 8 — Køyespiler

Spilene ligger OPPÅ begge sidevanger — ikke i et spor og ikke på en lekt. Alle er like lange.

**Deler:** 14× Køyespile 23×98 × 800

**Festemidler:** 28× Treskrue 5×60 forsenket Torx

**Ledd:** J6 — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Festeplassering — mål på delen:**

| Ledd | Merkes opp på | Fra enden | Fra kanten | c/c |
|---|---|---|---|---:|
| **J6** 1× Treskrue 5×60 | køyespile 23×98 × 800, oversiden | 24 mm fra vegg- og romenden | midt på (49 mm fra hver side) | — |

**Slik gjør du:**

1. Legg ut alle spilene løst først og fordel dem etter kapplista, før du skrur noe.
1. Skyv hver spile helt inn til veggen. Bakkanten på spilene er det madrassen støter mot.
1. Skru hver spile ned i begge vanger, én skrue per ende (J6).

**Sjekk før du går videre:**

* Alle spiler skal dekke hele bredden av begge vanger. Ligger en spile bare halvveis på vangen, flytt den.
* Ingen skruehoder over flaten — de ligger under madrassen.
* Gå over hele bunnen med håndflaten før madrassen legges på.

## Steg 9 — Rekkverk foran

To bånd, hvert delt i to bord, med klatreåpningen i midten. Man klatrer GJENNOM rekkverket, ikke over. Det er ikke rekkverk på baksiden — der er veggen sperren. Bordene ligger på INNSIDEN av stolpene, mot sengen, ikke utenpå.

**Deler:** 4× Rekkverksbord, front 36×98 × 832

**Festemidler:** 16× Treskrue 5×60 forsenket Torx

**Ledd:** J7 — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Festeplassering — mål på delen:**

| Ledd | Merkes opp på | Fra enden | Fra kanten | c/c |
|---|---|---|---|---:|
| **J7** 2× Treskrue 5×60 | rekkverksbord 36×98 × 832, baksiden (mot veggen) | 47,5 mm fra ytterenden · 24 mm fra innerenden | 22,5 mm fra under- og overkanten | 53 |

**Slik gjør du:**

1. Legg det nederste båndet an mot innsiden av hjørnestolpen og stigevangen, i flukt med stolpenes innerplan.
1. Skru fra sengesiden inn i stolpen og i stigevangen (J7). Forbor — bordet sprekker lett nær enden.
1. Gjenta for det øverste båndet.

**Sjekk før du går videre:**

* Mål åpningene over madrassoverflaten mot tallene i nøkkelmålene. De er sikkerhetskravet i denne sengen.
* Ta tak i toppbordet og dra. Det skal ikke gi seg.

## Steg 10 — Løs plate med fire lekter — og ingen beslag

Platen er ikke et løst bord. Den er en liten enhet som løftes ut i ett stykke og senkes rett ned igjen — i begge stillinger. Lektene under den gjør to jobber: de gjør platen stiv, OG de er styringen. De to lange går ned på hver side av trinnenden med 2 mm klaring, så de finner plassen selv. Det er ikke ett beslag i denne mekanismen, og det skal ikke være én skrue synlig oppå platen.

**Deler:** 2× Avstivningslekt under plate 48×68 × 750 · 2× Kilelekt under platens forkant (skråkappet) 48×68 × 77 · 1× Løs plate 18 mm plate, 574 bred × 798

**Festemidler:** 16× Treskrue 5×40 forsenket Torx

**Ledd:** J13a, J13b — se J-oversikten i [ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og [beslagliste](beslagliste.md)

**Festeplassering — mål på delen:**

| Ledd | Merkes opp på | Fra enden | Fra kanten | c/c |
|---|---|---|---|---:|
| **J13a** 6× Treskrue 5×40 | avstivningslekt 48×68 × 750, undersiden | 22,5 / 163,5 / 304,5 mm fra vegg- og romenden | midt på (24 mm fra hver side) | 141 |
| **J13b** 2× Treskrue 5×40 | fremre kilelekt 48×68 × 77, undersiden | 22,5 mm fra begge ender | midt på (24 mm fra hver side) | 32 |

**Slik gjør du:**

1. Bor hullene i lektene FØR noe limes. Regelen er den samme for alle fire delene, og den er lettest å huske slik: bor ⌀12 opp i undersiden TIL DET STÅR 27 mm igjen opp til plata, og ⌀3,5 videre gjennom de siste 27 mm. På de to lange styrelektene, som er 68 mm hele veien, blir det 41 mm kontrabor. På de to skråkappede kilene blir det dypest ved roten og null ved tuppen — tuppen ER 27 mm, så der ligger hodet i flukt med kilens egen underside. Skruen tar 13 mm i den 18 mm tykke platen uansett, med 5 mm plate igjen over spissen.
1. Legg platen med undersiden opp. Merk av de to lange avstivningslektene 77 mm inn fra hver sidekant — det er målet som gjør at de treffer utsiden av trinnenden.
1. Lim (D3) hele lektas overkant, legg den på plass og skru opp fra undersiden (J13a). Skruene er tvinger: de trekker limfugen sammen og blir sittende.
1. Samme sak for de to kilelektene, i flukt med platens forkant og med den HØYE enden mot den lange lekta (J13b) — den skråkappede tuppen peker ut mot platekanten. De bærer hjørnet trinnet ikke rekker fram til.
1. Ingenting går gjennom platens overside. Har du et hull der, har du boret feil vei.
1. Legg platen i sengestilling: senk den rett ned mellom benkene, bakkanten på den bakre benkevangen, forkanten på trinn 1. De to lange lektene skal gli ned på hver side av trinnenden uten å tvinges.
1. Prøv bordstilling: samme plate, samme lekter, rett ned på bordbærelekta og de to BORDKLOSSENE. Klossene har endeflaten i nøyaktig samme lengderetning som trinnendene, så de to lektene finner dem på samme måte — bare 70 mm dypere inn.

**Sjekk før du går videre:**

* Skyv platen sidelengs. Den skal bevege seg et par millimeter og så stoppe mot trinnenden — begge veier, i begge stillinger.
* Vri på platen. Den skal kile seg med én gang: en vridning drar begge lektene samme vei, og den ene tar imot.
* Platen skal ligge stødig på begge opplegg i begge stillinger, uten å vippe. Den ligger på tre i hele bredden bak og på trinnet foran.
* Se over platens overside i motlys. Ingen skruehoder, ingen propper, ingen hull.
* Platen kan løftes rett opp. Det skal den kunne — låsen i sengestilling er en egen avgjørelse, ikke en del av dette steget.

## Steg 11 — Madrass og puter

Sengen er dimensjonert rundt en STANDARD madrass på 80 × 200 cm — den er ikke spesialmål og skal ikke spesialbestilles. Det eneste målet du må velge selv er TYKKELSEN, og der er det bare ett riktig svar: 120 mm. Vinduet er 110–125 mm, og en helt vanlig 160 mm madrass er ULOVLIG i denne sengen — den legger spalten opp til rekkverket midt i klemvinduet.

**Deler:** 2× Benkepute, skum **100 mm** (663 × 800 mm, hakk 98 × 36 i veggkanten) · 1× Madrass 80 × 200 cm, **120 mm tykk** (vindu 110–125 mm) · 2× Ryggpute, skum **100 mm** (332 × 800 mm)

**Slik gjør du:**

1. Legg madrassen på plass. En 80 × 200 presses de siste millimeterne inn mellom veggene, og den skal fylle hele dybden fra veggen til de fremre stolpene.
1. UNDERETASJEN: fire puter, alle 100 mm tykke og 800 mm dype. To benkeputer på 663 mm og to ryggputer på 332 mm — lagt etter hverandre dekker de nedre soveflate nøyaktig, 663 + 332 + 332 + 663 = 1990 mm.
1. Skjær et 98 × 36 mm hakk i veggkanten på hver av de to benkeputene, der den bakre hjørnestolpen står. Brødkniv.
1. SOFASTILLING: benkeputene ligger der de ligger — de flyttes aldri. Ryggputene reises på høykant ytterst på hver benk, med ryggen mot bordbærelekta.
1. MERK MAKSMÅLET PERMANENT. EN 747 krever det, og det er ikke en tusjstrek som skal kunne tørkes bort: skriv «MAKS MADRASS 125 MM» på innsiden av en fremre stolpe, i høyden 1648 mm over gulvet. Den som bytter madrass om ti år skal kunne lese grensen av sengen selv.
1. Skriv nedre grense, 110 mm, ved siden av. For tynn madrass åpner spalten under nederste rekkverksbord; for tykk lukker den seg ned i klemvinduet.

**Sjekk før du går videre:**

* Ettertrekk alle festemidler som kan ettertrekkes.
* Madrassen skal ligge stramt mot veggen og mot de fremre stolpene, uten spalte langs noen av de to lange kantene.
* Rist i sengen i begge retninger. Ingen bevegelse mot bakveggen.
* Mål spalten fra madrassens overside opp til undersiden av det nederste rekkverksbordet. Den skal være 60–75 mm. Er den mindre, er madrassen for tykk.
* Sett datoen for første ettertrekk i kalenderen: om fire uker, og deretter en gang i året.

