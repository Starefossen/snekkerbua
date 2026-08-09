# HANNA — loftseng, byggeveiledning

HANNA er en loftseng med sofa, bord og ekstraseng under. Den er bygget på mål
for en nisje mellom to vegger og står **inntil bakveggen og inntil begge
sideveggene**. Den bygges på plass.

> **Denne sengen er ikke reversibel.** Den lange baksiden skal stå mot vegg og
> skal skrus fast i veggen. Det er ikke rekkverk på baksiden — der er veggen
> sperren. Snur du sengen, mangler den et rekkverk.

---

## Sånn henger papirene sammen

Alle mål er regnet ut fra modellen `generate_loftbed.py` og skrevet ut av
`mise run build`. Ingen mål er skrevet inn for hånd noe sted. Endrer du
modellen, endrer tabellene seg med den.

| Fil | Hva du finner der |
|---|---|
| [generated/kappliste.md](generated/kappliste.md) | Hver del: dimensjon, lengde, antall, hvor den sitter |
| [generated/innkjopsliste.md](generated/innkjopsliste.md) | Hva du skal kjøpe, og hvilke deler som kappes av hvert bord |
| [generated/nokkelmal.md](generated/nokkelmal.md) | Ytre mål, alle høyder, alle dybdeplan, stige- og rekkverksmål, skruerader, madrassmål, sikkerhetsmål |
| [generated/beslagliste.md](generated/beslagliste.md) | Alle beslag og skruer, hvor de går, hva som forbores, hvilken side du driver fra |
| [generated/byggesteg.md](generated/byggesteg.md) | Steg for steg i tekst |
| [MONTERING.md](MONTERING.md) | Steg for steg i bilder, samme nummer |
| [schematics/](schematics/) | Tegninger |

**Denne fila gjentar ingen av de målene.** Står et mål i en tabell der, står
det ikke her. Her står det hvorfor, og hvordan. Der et tall likevel dukker opp i
teksten, er det fordi tallet *selv* er begrunnelsen — og da står det alltid med
en henvisning til fila som eier det. Regnedelen i vedlegg A henter spennene sine
fra kapplista og nøkkelmålene.

---

## 1. Verktøy

| Verktøy | Til hva |
|---|---|
| Batteridrill, 18 V eller mer | Rammen er skrudd, ikke boltet — men det er mange 6 mm skruer i heltre, og de vil ha moment |
| Trebor ⌀6 og ⌀4 | Rammeskruene: gjennomgangshull i den ene delen, styrehull i den andre. Se forboringskolonnen i [beslaglista](generated/beslagliste.md) |
| Trebor i flere små diametre til forboring | Se forboringskolonnen i beslaglista. Forbor **alltid** i den tynne bordbærelekta, i bordene og i all endeved |
| Forsenker (kjeglesenker) | Alle skruehoder i flater man tar på: benkespiler, køyespiler, plate |
| Bits Torx T20 / T25 / T30 | Etter skruestørrelse |
| Fastnøkkel 10 mm | Låsemutrene på M6 (platebeslagene) |
| Sirkelsag eller håndsag + anlegg | Alle kutt er 90°. Ingen gjæring i hele sengen |
| Vinkelhake, minst 300 mm | Endrammene |
| Vater, minst 600 mm | Endebjelker og vanger |
| Tommestokk og målebånd | |
| To skrutvinger, minst 300 mm | Holder deler mens du borer gjennom begge samtidig |
| Skrustikke eller ambolt + hammer | Bøying av U-brakettene og krokplatene |
| Blyant og syl | Merking av borsentre |
| To personer | Endrammene skal reises, og de øvre vangene skal opp i høyden |

---

## 2. Trevirke og beslag

Kjøp: [innkjøpsliste](generated/innkjopsliste.md).
Kapping: [kappliste](generated/kappliste.md).
Beslag og skruer: [beslagliste](generated/beslagliste.md).

Alt trevirke er høvlet konstruksjonsvirke C24. Alle beslag og skruer er
elforsinket eller varmforsinket.

**Det går ikke én bolt inn i en stolpe i denne sengen.** Stolpene er tynne på
tvers av rommet, og på den tykkelsen får en M8 ikke den kantavstanden en bolt
krever — den ville sprenge stolpen på langs. Hvert eneste ledd inn i en stolpe
er derfor **forborede treskruer i 6 mm** — det samme mønsteret som stigevangene
bruker. For en 6 mm skrue er kravet til kantavstand nøyaktig det en
stolpetykkelse gir på midtlinjen.

Det er ikke en nødløsning. **Tre bærer på tre overalt — bortsett fra i
bæreklossene, og der er skruen lasten.** Hver eneste lange del hviler på noe:
sidevangene på endebjelkene, den bakre sidevangen rett på stolpetoppene,
endebjelken på bæreklossene J1-B, benkevangene på klossene J9-B/J9-F og på
stubbeføttene. Ingen av *de* skruene er opplegg.

Men klossen selv står ikke på noe. Den henger på stolpen i skruene sine, og de
skruene står i **skjær** — det er den eneste plassen i rammen der en loddrett
reaksjon går gjennom stål. Det er verdt å si rett ut, for det er også den
plassen hvor antallet skruer betyr noe:

* **J1-B**, under endebjelken: klossflaten mot stolpen er 36 × 36 mm, og der
  er det bare plass til **én** 6 mm skrue med lovlig kantavstand. Én 6 mm
  skrue i skjær ≈ 2,0 kN mot ≤ 1 kN hjørnereaksjon — utnyttelse 0,50.
* **J9-B / J9-F**, under benkevangene: samme flate, samme svar, men lasten er
  halvparten — utnyttelse 0,25.
* **Ingen av dem står alene.** I det samme hjørnet er den bårne delen selv
  skrudd til den samme stolpen — endebjelken med to 6×90 (J1), den bakre
  benkevangen med to skrå 6×90 (J8-B), den fremre med to 6×80 (J8) — og de
  skruene tar skjær i nøyaktig samme snitt. Regnet som den kombinerte
  skjærveien den er, blir hjørnet 3 × 6 mm = 6,0 kN mot 1 kN, altså **0,17**.
  Klossen er der for å ta bruddformen bort fra bjelkeenden, ikke for å være
  det eneste som holder.

Alt dette står i lasttabellen i vedlegg A, rad for rad. Bolten er fortsatt
borte, og det er fortsatt riktig.

**Én konsekvens til, og den er god:** ingenting i rammen festes lenger fra en
flate som ender mot vegg. Da finnes det heller ingen skruehoder som må senkes
ned under en monteringsflate — ingen forsenkte boltehoder, ingen store
forsenkingshull, og ingen deler som må boltes ferdig før de får møte veggen.

Stål brukes bare fire steder: vinkelbeslagene under stubbeføttene,
vinkelbeslagene under bordbærelektas ender, og U-brakettene og krokplatene på
den løse platen. Bare de to siste er konstruksjon — resten er bånd og opplegg.

## 3. Byggerekkefølgen — og hvorfor den er som den er

Sengen står i en nisje. Tre av flatene er vegg. Det bestemmer alt.

**Hele baksiden av sengen er ett flatt lag.** Bakre sidevange, de to bakre
stolpene, bakre benkevange, bakre bordbærelekt, endene av begge endebjelker og
bakkanten på hver eneste spile ligger i ett og samme plan — og det planet er
monteringsflaten mot veggen. Ingenting stikker bak det.

Det gir to konsekvenser som styrer rekkefølgen:

* **Baksiden er en ramme, så bygg den som en ramme.** De bakre delene henger
  sammen i ett plan. Legg dem ut på gulvet, skru dem sammen der, og reis
  bakrammen som ett stykke. Da får du gjort alt som skal gjøres fra flater som
  senere ender mot vegg.
* **Veggfestet er den bakre sidevangen selv.** Vangen ligger flatt mot veggen i
  hele sin lengde, så sengen skrus fast rett gjennom den og inn i stenderne. Det
  trengs ingen brakett og ingen kloss. De samme skruene støtter dessuten vangen
  på midten, så det lange spennet den ser ut til å ha på papiret er ikke det
  spennet den faktisk får.

Og det som *ikke* går an, hvis du bygger i feil rekkefølge:

* **De bakre delene er fanget mellom stolpene.** Den bakre benkevangen og den
  bakre bordbærelekta er kappet til å fylle nøyaktig fra stolpe til stolpe. Står
  begge stolpene først, får du dem aldri inn — de er akkurat for lange til å
  vippes på plass, og det er meningen: det er slik de får endefeste i begge
  ender. De må legges inn mens rammen ligger flat.
* **Fronten stenger.** Alt som skal inn bakfra må være inne før den fremre
  sidevangen går på.

Derfor:

1. **Bakrammen bygges liggende, midt på gulvet** — to korte stolper og de tre
   vannrette bakre delene, som ikke kan settes inn senere.
2. **Bakrammen reises og skrus fast i veggen.** Nå står baksiden, i lodd og i
   vater, og resten bygges framover fra den.
3. **Endene bygges ut:** bæreklosser, fremre stolpe, endebjelke. Én ende av
   gangen.
4. **Fronten lukkes:** fremre sidevange, så de to fremre benkevangene og alle
   fire stubbeføtter.
5. **Resten kommer forfra og ovenfra:** stige, benkespiler, køyespiler,
   rekkverk, plate, madrass.

Den samme rekkefølgen, med sjekkpunkter for hvert steg:
**[byggesteg.md](generated/byggesteg.md)**. Med bilder:
**[MONTERING.md](MONTERING.md)**. Oversiktstegning:
[schematics/byggerekkefolge.svg](schematics/byggerekkefolge.svg).

### Tre ting du skal kontrollere hele veien

* **Vater.** Den bakre sidevangen først — den er referansen for alt annet. Så
  hver del etter hvert som den går inn. En vange som ikke er i vater tar du ikke
  igjen senere.
* **Vinkel og diagonal.** Mål diagonalene i bakrammen før den reises, og i
  sengeflaten når begge sidevanger står.
* **Veggklaringen.** De gjennomgående delene er med vilje kappet kortere enn
  veggavstanden, slik at de kan svinges inn. Klaringen er liten. Sjekk at ingen
  del blir stående i spenn mot en vegg, og at ingen spile eller skruehode
  stikker ut i veggplanet.

### Forboring — kort regel

* **Bor gjennomgående hull gjennom begge deler samtidig**, med delene tvunget
  sammen. Bores de hver for seg, treffer de ikke.
* **Forbor hver eneste treskrue.** Ingen unntak i den tynne bordbærelekta, i
  bordene og i endeved.
* **Ingenting i rammen er boltet.** Hele rammen er skrudd, med forborede
  6 mm treskruer. Se J1, J2, J3 og J8.
* Diameterne står i forboringskolonnen i
  [beslaglista](generated/beslagliste.md).

---

## 4. J — leddene

Antall, skruetype, forboring og hvilken side du driver fra står i
[beslaglista](generated/beslagliste.md). Boltradenes høyder står i
[nøkkelmål](generated/nokkelmal.md). Her står hva leddet er og hva som er
poenget med det.

### J1 — Endebjelke → hjørnestolpe

Endebjelken støter mot stolpens innside og skrus gjennom bjelken og inn i
stolpen. Skruene går på tvers av fiberretningen i begge deler, ikke inn i
endeved.

**Bjelken henger ikke i skruene.** Den står på en kloss — se J1-B. Skruene er
bånd som holder rammen sammen.

Skruene drives inne fra sengen. Du kommer til dem når som helst, både under
byggingen og når du skal ettertrekke.

### J1-B — Bærekloss under endebjelken

En kort kloss skrudd på stolpens innside, rett under bjelkeenden. Bjelken hviler
på klossen. Uten den ville hele lasten hengt i to skruer nær enden av bjelken —
og bruddformen der er sprø oppflising av veden.

Skruen drives fra klossens frie ende og inn i stolpen — inne fra sengen. Det er
**én** skrue, ikke to: klossens flate mot stolpen er 36 × 36 mm, og to 6 mm
skruer trenger 60 mm av den flaten (4d mellom dem og 3d til hver kant). Klossen
er liten, så forbor gjennom den; en kloss som sprekker under skruen bærer ikke.

Den ene skruen står i skjær og bærer hjørnereaksjonen sammen med endebjelkens
egne to — se lasttabellen og avsnitt 2.

### J2 — Fremre sidevange → fremre hjørnestolpe

Vangen ligger flatt mot stolpen. Skruene drives fra stolpens forside, gjennom
stolpen og inn i vangen, og du kommer til dem når som helst.

Vangen bærer ikke i skruene — den ligger på begge endebjelker.

Merk skruelengden: her går skruen gjennom en tynn stolpe og inn i en tykk vange,
og den skal **ikke** komme ut på baksiden av vangen. Bruk lengden som står i
beslaglista, ikke den lengste du har i esken.

### J2-B — Bakre sidevange → bakre hjørnestolpe

Dette leddet er annerledes, og det er meningen. Den bakre stolpen står **i
vangens eget plan** og er kappet slik at den slutter akkurat under vangen.
Vangen **hviler rett på stolpens endeved**. Hjørnereaksjonen går vange → stolpe
→ gulv som ren trelagring, uten et eneste festemiddel i lastens vei.

Festet er derfor bare et bånd som holder de to sammen mot vridning og løft. To
kraftige skruer settes rett ned gjennom vangen i stolpens endeved, mens
bakrammen ennå ligger flatt på gulvet. Forsenk hodene godt — køyespilene skal
ligge flatt over dem.

Et rett beslag over skjøten ville vært det opplagte, og det går ikke: vangen er
dypere enn stolpen, så den står et lite stykke proud av stolpens romside, og en
rett plate ville bare ligget an mot den ene av dem. Skruer ned i endeveden er
svakere i uttrekk enn et beslag, men her holder de bare igjen — lasten står på
tre, og veggfestet sitter i den samme vangen noen centimeter unna.

**Ikke sett noe på veggsiden.** Den flaten skal være helt plan.

### J3 — Stigevange → fremre sidevange

Tre kraftige treskruer gjennom stigevangen og inn i sidevangen. Leddet er
skrudd, ikke boltet — samme mønster som resten av rammen bruker, se J1, J2
og J8. Tre og ikke fire: omlegget er 48 × 98 mm, og fire 6 mm skruer i én rad
ville krevd 108 mm der det er 98. Fire i to par ville krevd 60 mm på tvers der
det er 48.

Stigevangen står med den tynne siden mot rommet, så skruene treffer vangen på
midtlinjen med akkurat den kantavstanden en 6 mm skrue skal ha.

Forbor gjennomgående i stigevangen, og forbor i sidevangen også. Skruene sitter
i én loddrett rad, én over og én under vangens midtlinje med den tredje midt
imellom, slik at leddet tar moment.

### J4 — Rungetrinn → stigekloss og stigevange

Trinnet ligger på klossen og er skrudd ned i den ovenfra. I tillegg går én
kraftig skrue fra utsiden av stigevangen inn i trinnenden.

Skruen i trinnenden bærer **ingen** vertikal last — den holder bare trinnet på
plass sideveis. Vekten din går rett ned i klossen og videre inn i vangen. Det er
riktig utformet, og det er grunnen til at trinnet ikke kan glippe selv om skruen
i endeveden skulle løsne.

Trinnene stikker **bakover**, ikke framover: forkanten ligger i flukt med
stigevangens forkant, og det som blir liggende bak vangeplanet er hylla den løse
platen hviler på.

### J5 — Stigekloss → stigevange

Én skrue per kloss, inn i vangens innside. Klossen dekker bare 36 × 48 mm av
stigevangen, og to 5 mm skruer trenger 50 mm av de 48. Klosshøyden er
trinnhøyden. Mål to ganger.

Klossen er ikke overlatt til den ene skruen: trinnet ligger på klossen og er
skrudd ned i den ovenfra (J4), og trinnenden er i tillegg skrudd til
stigevangen med en 6×120 gjennom vangen. De tre festene deler samme hjørne, og
klossen kan ikke rotere om skruen sin så lenge trinnet står.

### J6 — Køyespile → sidevange

Spilene ligger **oppå** begge vanger, ikke i et spor og ikke på en lekt. Én skrue
ned i hver vange per spile. Forsenk hodet under flaten — det ligger madrass over.

De to ytterste spilene er kortere enn resten fordi de støter mot de bakre
stolpene. Legg dem først.

### J7 — Rekkverksbord → hjørnestolpe og stigevange

Rekkverksbordene ligger på **innsiden** av stolpene og stigevangene, mot sengen.
Hvert bord tar tak i en hjørnestolpe i den ene enden og i en stigevange i den
andre, med full flate mot begge. Skruene drives fra sengesiden.

Bordene stopper i flukt med stigevangenes innside, slik at klatreåpningen
fortsetter rett opp forbi rekkverket. Man klatrer **gjennom**, ikke over.

Det er ikke rekkverk på baksiden. Se sikkerhetsavsnittet.

### J8 og J8-B — Benkevange → hjørnestolpe

To ulike ledd, ett foran og ett bak.

**J8, foran:** vangebiten ligger flatt mot stolpen, og skruene kommer fra
stolpens forside — samme detalj som J2.

**J8-B, bak:** den bakre benkevangen går fra stolpe til stolpe og støter mot
stolpens sideflate med enden. Her går skruene **skrått** fra vangens forside inn
i stolpen. Forbor hele veien — en skråskrue nær en ende er den letteste måten å
sprekke en vange på.

I begge tilfeller hviler vangen på en bærekloss (J9-B / J9-F). Skruene er bånd,
ikke opplegg.

### J9-B og J9-F — Bæreklosser under benkevangene

Samme prinsipp som J1-B: vangeenden står på tre. Uten klossen ville et par
skruer alene være et hengsel, og benkeenden ville vippe.

De to bakre klossene (J9-B) sitter på de bakre stolpenes innsider og monteres
mens bakrammen ligger flat. De to fremre (J9-F) sitter på de fremre stolpenes
baksider. **Én skrue per kloss**, av samme grunn som ved J1-B: flaten mot
stolpen er 36 × 36 / 48 × 48 mm, og det er ikke lovlig plass til to.

**J9-F tar en kortere skrue enn alle de andre klossene.** Det står bare en
stolpetykkelse bak den, og en for lang skrue kommer ut på stolpens forside.
Sjekk lengden i beslaglista før du skrur.

### J10 — Benkevange → stubbefot

Foten står under vangen med hele endeflaten mot gulvet og hele toppflaten mot
vangen.

Vinkelbeslaget sitter i **hjørnet mellom fotens ytterside og vangens
underside**, og det er en ekte vinkel: den ene fliken ligger loddrett på foten
og skrus vannrett inn i den, den andre ligger vannrett under vangen og skrus
rett opp i den. To skruer i hver flik — det er det en 90 mm flik har lovlig
plass til. Beslaget er 40 mm bredt og ikke 65: en 65 mm flik ville stukket
17 mm ut av en 48 mm vange.

I tillegg går **én** skråskrue nedenfra opp gjennom foten og inn i vangen, fra
den fotsiden som vender inn mot benkeåpningen. Én og ikke to: foten er 48 mm
bred, og to 5 mm skråskruer ved siden av hverandre trenger 50.

De **fremre** føttene står akkurat der vangebiten slutter. Vangebiten skal ikke
stikke ut forbi foten i det hele tatt — den ender på den.

### J11 — Benkespile → benkevange

Én skrue i hver ende, ned i vangen. Forsenk. Dette er en sitteflate.

### J12 — Bordbærelekt → bakre hjørnestolpe

Lekta går fra stolpe til stolpe og støter mot stolpenes sideflater med endene,
akkurat som den bakre benkevangen. Den er for tynn til å skrus i enden, så hver
ende får et lite vinkelbeslag å hvile på. Beslaget står med den loddrette
fliken på stolpens innerflate og den vannrette fliken **under lektas ende** —
det er den veien rundt, og bare den veien: snudd andre veien ville den
vannrette fliken pekt ut i lufta over lekta og ikke båret noe som helst. Lekta
henger ikke i skruer — den ligger på beslaget.

Beslaget er 20 mm bredt, ikke 40. Stolpeflaten det ligger på er 36 mm og
lekta er 21 mm tykk; et 40 mm bredt beslag ville stukket ut av begge, og på
stolpen ville det stukket ut i **veggplanet**, som skal være helt flatt. Én
skrue i hver flik — en 40 mm flik har ikke lovlig plass til to 5 mm skruer.

Lekta står **på høykant**. Legger du den flatt, faller bæreevnen med faktor 20
og bordplaten svikter. Forbor — lekta er tynn.

Lekta må inn mens bakrammen ligger flat, av samme grunn som benkevangen: den er
kappet til å fylle nøyaktig mellom stolpene.

Lekta er det bakre opplegget for platen i bordstilling, og overkanten skal ligge
i nøyaktig samme høyde som trinn 2. Da ligger platen rett på begge to, uten
beslag og uten kile.

### J13 — Den løse platen

Platen er ikke et løst bord. Den er en liten enhet som løftes ut i ett stykke, og
beslagene på den er konstruksjon.

**J13a — avstivningslekter.** To lekter på høykant, skrudd under platen fra
oversiden. De går fra det bakre opplegget helt fram til trinnet. Uten dem holder
ikke platen når noen setter seg på den. Med dem er platen to T-bjelker. Se
lasttabellen i vedlegg A.

**J13b — U-brakettene foran.** To braketter som **omslutter trinnet** og klemmer
platen fast til stigen. De gjør to jobber samtidig:

* de er platens vippesikring — du får ikke løftet forkanten av hylla;
* og de er stigens avstivning nedad. Stigefoten er ikke bundet til noe annet i
  dybderetningen, og det er gjennom platen den er bundet tilbake til den bakre
  bærelinjen.

Dette er grunnen til at platen alltid skal ligge i, i en av de to stillingene.

**J13c — krokplatene bak.** To plater som holder bakkanten nede. De henger ned
**foran** den bakre benkevangen og haker seg inn **under** den. Grunnen til at
de griper forfra: baksiden av vangen ligger i veggplanet, **den flaten er
veggen**, og der er det ingen plass til et beslag. Ingenting av krokplatene
kommer på veggsiden.

I bordstilling henger de samme platene fritt like foran bordbærelekta og virker
der som stopp framover. Bakkanten holdes ikke nede i bordstilling — det trengs
ikke, for et bord belastes nedover, og forkanten er uansett låst til trinnet av
U-brakettene.

Sett platene i X der de går klar av avstivningslektene.

### J14 — Veggfeste (obligatorisk)

**Sengen skal skrus fast i veggen. Dette er ikke valgfritt**, av tre grunner:
veggen er rekkverket på baksiden, stigefoten regner med at rammen ikke gynger,
og skruene bærer sin del av den bakre sidevangen.

Festet er så enkelt som det kan bli: **den bakre sidevangen ligger flatt mot
veggen i hele sin lengde**, så du skrur rett gjennom vangen og inn i veggen.
Ingen brakett, ingen kloss, ingen kile.

Finn stenderne og merk av senterlinjene på vangen før du skrur. Ta et feste i
hver stender du treffer, og minst i begge ender og på midten. Er veggen mur
eller betong, bruk plugg eller betongskrue.

**Treff noe som holder.** En plateplugg i gips er ikke et veggfeste for en seng
noen sover i.

### J15 — Filtknotter

Under alle fire hjørnestolper og alle fire stubbeføtter. Slå dem i før du reiser
noe.

---

## 5. Madrass og puter

Mål på madrass og puter: [nøkkelmål](generated/nokkelmal.md#madrass-og-puter).

### Overkøyen

**Sengen er dimensjonert rundt en standard madrass på 80 × 200 cm.** Det er
ikke et spesialmål, og madrassen skal ikke bestilles etter sengen — det er
sengen som er bygd etter madrassen. Rommet er noen millimeter smalere enn
200 cm, så madrassen presses de siste millimeterne inn mellom veggene. Det er
meningen: da ligger den i ro.

**Tykkelsen har BEGGE grenser, og de trekker hver sin vei.** Rekkverksbåndene
sitter i faste høyder, og madrassens overflate er det de måles fra:

* **For tynn** madrass senker liggeflaten, og spalten mellom madrassen og det
  nederste rekkverksbordet blir større enn EN 747 tillater.
* **For tykk** madrass hever liggeflaten, og rekkverket står ikke lenger høyt
  nok over den som ligger der.

Begge tallene regnes ut av modellen av de to faste høydene — spilebunnen og
rekkverket — og står i [nøkkelmålene](generated/nokkelmal.md#madrass-og-puter).
Skriv dem BEGGE med tusj på innsiden av en fremre stolpe. Panelet på siste side
i monteringsanvisningen tegner de to grensene med en pil hver.

### Underetasjen — tre puter

Underetasjen er sofa, bord og ekstraseng i én. Sengeflaten er tre soner: to
benker og platen mellom dem. Derfor tre puter, ikke én madrass.

Platen ligger med vilje litt lavere enn benkeflaten. Midtputen skal være
tilsvarende tykkere, slik at de tre putene ender i samme høyde og
sofaputene har et spor å folde seg ned i.

### Tre måter å skaffe dem på — valget er åpent

| | Hva | Ca. pris | Merknad |
|---|---|---|---|
| **a** | Industrisøm, skumplate 12 cm kvalitet 35P, 120 × 200, kappes til | ≈ 2 590 kr | Én plate dekker alle tre putene. Fastest og mest «møbelaktig». Du kapper selv, eller får det kappet |
| **b** | IKEA ÅGOTNES 80 × 200 × 10, kappes til | ≈ 450 kr | Klart billigst. 10 cm er i tynneste laget som sitteunderlag — legg en fastere topper på de to benkeputene |
| **c** | Kaldskum 39K, eller mål-tilpasset fra maaho.com | ≈ 4 299 kr | Dyrest, men du får riktig mål og riktig fasthet levert, uten å kappe |

**Alle tre trenger trekk.** Skum uten trekk smuldrer og blir skittent. Regn med
trekk som en egen post uansett hvilken vei du går.

**Skjøt putene til hverandre** med borrelås eller trykknapper i trekkene. Ellers
sklir de fra hverandre den første natta noen sover der.

---

## 6. Notater til butikkturen

* **Hovedbordet må bestilles.** Ring før du drar. Det aller meste av sengen er
  det samme bordet, og butikken har sjelden nok av det på lager. Får du bare
  nærmeste nabo-dimensjon, er det mulig — men da er det én konstant i
  `generate_loftbed.py` som endres, og hele modellen må kjøres på nytt og
  kapplista regnes om. Ikke improviser på sagbenken.
* **Platen må kappes av kryssfiner.** Den er bredere enn limtreplatene i
  furuhylla rekker. Kjøp 18 mm kryssfiner og kapp.
* **Vil du kunne bygge om til frittstående seng senere?** Da trenger du to
  rekkverksbord til på baksiden og to bakre stolper i full høyde. Kjøp dem gjerne
  nå, og — viktigst — **forbor de bakre stolpene for rekkverket mens de ligger på
  bukken**. Resten av sengen er uendret; det er bare de fire delene.
* Kjøp litt ekstra av alle skruestørrelsene. De koster ingenting, og en tur
  tilbake koster en kveld.

---

## 7. Sikkerhet

Kravene er fra **EN 747** (køyesenger og loftsenger). Tallene sengen faktisk
har, og kravet ved siden av, står i
[nøkkelmål](generated/nokkelmal.md#sikkerhetsmål-en-747). Alle er innenfor.

**7.1 Baksiden har ikke rekkverk — veggen er sperren.** Det er derfor sengen må
skrus fast i veggen (J14), og det er derfor den ikke kan snus. Madrassen er
**klemt fast** mellom veggen og de fremre stolpene: den fyller hele dybden, den
kan ikke skyve seg, og det står ingen spalte igjen langs noen av de to lange
kantene. Klemspalte-spørsmålet på den siden er dermed ikke i spill i det hele
tatt.

**7.2 Rekkverket foran har en klatreåpning.** Man klatrer gjennom, ikke over
toppbordet. Åpningen er like bred som stigen og ligger rett over den.

**7.3 Madrasstykkelsen skal ligge innenfor BEGGE grensene.** For tynn åpner
spalten under nederste rekkverksbord; for tykk senker rekkverket over den som
ligger der. Se avsnitt 5 og nøkkelmålene.

**7.4 Ikke hopp på bar spilebunn.** Med madrass fordeles lasten over flere
spiler og alt er greit. Uten madrass, med full dynamisk last rett på én spile,
er spilen overbelastet. Legg madrassen på før noen går opp.

**7.5 Den løse platen skal alltid ligge i.** Den er stigens avstivning nedad
(J13b). Skal du ha den ut, ta stigen med i vurderingen — og ikke la noen klatre
mens platen er ute.

**7.6 Ikke sett deg på platens kant, og ikke bruk den som trinn.** Den er
sikret mot å vippe, men den er ikke en avsats.

**7.7 Ettertrekk.** Alle låsemuttere ettertrekkes etter fire uker og deretter en
gang i året. Sengen vibrerer hver gang noen snur seg.

**7.8 Aldersgrense.** Loftsenger og overkøyer anbefales ikke til barn under
**6 år**.

**7.9 Sjekk sengen når du flytter noe.** Blir sengen dratt ut fra veggen, mister
den både rekkverket sitt og stivheten sin.

---

## Vedlegg A — lastbane

Regnedelen. Du trenger ikke lese dette for å bygge sengen.

Spennene i tabellene er delenes frie spenn, som følger av kapplista og
nøkkelmålene.

**Materiale:** C24 gran. f<sub>m,k</sub> = 24, f<sub>c,0,k</sub> = 21,
f<sub>c,90,k</sub> = 2,5, f<sub>v,k</sub> = 4,0 MPa, E<sub>mean</sub> = 11 000
MPa. γ<sub>M</sub> = 1,3. Med k<sub>mod</sub> = 0,9 (korttids- og dynamisk last)
blir f<sub>m,d</sub> = **16,6 MPa**. Trykk på tvers av fiberretningen med
k<sub>c,90</sub> = 1,5 gir **2,31 MPa**.

**Festemidler**, konservative erfaringstall: treskrue 5 mm i skjær ≈ **1,5 kN**,
6 mm ≈ **2,0 kN**. Det går ingen bolt inn i en stolpe i denne sengen; M6-bolten
i platebeslagene er det eneste gjengede festet igjen.

**Designlaster:** overkøye 100 kg + madrass, dynamisk faktor 2 → **2 kN**
punktlast. Trinn **1 kN**. Benk **1 kN**. Plate **2 kN** dynamisk (noen setter
seg eller kneler på den). Rekkverk **0,5 kN** vannrett.

### A.1 Overkøyen

| Ledd | Bæremåte | Spenn / flate | Last | Utn. | Dom |
|---|---|---|---|---:|---|
| Køyespile 36×98 | Bøyning | 800 mm | 1 kN på én spile | **0,57** | ✓ σ ≈ 9,5 MPa |
| Køyespile, **bar bunn** | Bøyning | 800 mm | 2 kN dynamisk på én spile | **1,14** | ✗ Se 7.4 — madrassen fordeler lasten |
| Spile → sidevange | Trelagring, full vangebredde under hver spile | 48 mm opplegg | 0,7 kN | 0,05 | ✓ |
| Bakre sidevange, regnet som fritt spenn mellom hjørnestolpene | Bøyning | 1894 mm | 2 kN | **0,73** | ✓ Konservativt — se raden under |
| Bakre sidevange **som bygget** | Bøyning, men vangen er skrudd til veggen i hver stender den treffer, så den er understøttet flere ganger på veien | ≈ 600 mm mellom veggfestene | 2 kN | ≈ **0,08** | ✓ Dette er grunnen til at veggfestet ikke er valgfritt |
| Fremre sidevange 48×98 | Bøyning, avstivet av de to stigevangene | 1894 mm | 2 kN | < 0,73 | ✓ |
| Vange → endebjelke | **Trelagring** | ≈ 5,3 kN | ≤ 1 kN | 0,19 | ✓ Vangen hviler, den henger ikke |
| Bakre vange → bakre stolpetopp | **Trelagring** på stolpens endeved, 95 × 36 mm | ≈ 7,9 kN | < 1 kN | 0,13 | ✓ Ingen festemidler i lastens vei. Hele stolpetoppens endeved er opplegg |
| Endebjelke 48×98 | Bøyning | 836 mm | 2 kN | **0,26** | ✓ |
| Endebjelke → bærekloss J1-B | **Trelagring** 48 × 36 | 1728 mm² → 4,0 kN | ≤ 1 kN | 0,25 | ✓ |
| Bærekloss → stolpe (J1-B), klossen alene | Skruskjær, 1 × 6 mm — klossflaten 36 × 36 mm tar ikke to | 2,0 kN | 1 kN | **0,50** | ✓ Dette er den eneste loddrette lasten i rammen som går gjennom stål |
| Samme hjørne, **kombinert skjærvei** | Klossens skrue + endebjelkens egne to 6×90 inn i den samme stolpen, i samme snitt | 6,0 kN | 1 kN | 0,17 | ✓ Klossen tar bruddformen bort fra bjelkeenden; den er ikke alene om lasten |
| *Uten bærekloss — ikke en tillatt byggemåte* | Kun skruer nær bjelkeenden | — | 2 kN | — | ✗ Sprø oppflising av veden. **Derfor er klossen der** |
| Fremre hjørnestolpe 36×98 | Knekking om svak akse, verste frie lengde 708 mm | N<sub>c,Rd</sub> ≈ **26,4 kN** | ≈ 1 kN | **0,05** | ✓ Svak akse er dimensjonerende, og margin er likevel svært god |
| Bakre hjørnestolpe 36×98 | Knekking, kortere stolpe, avstivet av benkevange og bordbærelekt | ≫ 26 kN | ≈ 1 kN | < 0,05 | ✓ |
| Stolpe → gulv | Endeved mot gulv | 45 kN i treet | 1 kN | 0,02 | ✓ |

### A.2 Stigen

| Ledd | Bæremåte | Spenn / flate | Last | Utn. | Dom |
|---|---|---|---|---:|---|
| Rungetrinn 48×73 | Bøyning | 320 mm | 1 kN | **0,17** | ✓ σ ≈ 2,9 MPa. Trinnet kjennes helt stivt |
| Trinn → stigekloss | **Trelagring** 36 × 73 | 2628 mm² → 6,1 kN | 0,5 kN | 0,08 | ✓ |
| Stigekloss → stigevange | Skruskjær, 1 × 5 mm — klossflaten 36 × 48 mm tar ikke to | 1,5 kN | 0,5 kN | **0,33** | ✓ |
| Samme hjørne, **kombinert skjærvei** | Klossens skrue + trinnendens 6×120 gjennom stigevangen | 3,5 kN | 0,5 kN | 0,14 | ✓ Trinnet låser også klossen mot å rotere om sin ene skrue |
| Skrue i trinnenden | Bærer ingen vertikal last | — | ≈ 0 | — | ✓ Riktig utformet |
| Stigevange → gulv | Ren søyle helt ned til gulvet | — | 1 kN | — | ✓ Ingen festemiddel i klatrelastens vei nedover |
| Stigevange, knekking **ut av planet** | Fri lengde gulv → fremre sidevange | λ ≈ 103, k<sub>c</sub> ≈ 0,29 → 7,3 kN | 1 kN | **0,14** | ✓ men se vedlegg B, avvik 2. Vangen står med den tynne siden ut av planet |
| Stigevange → fremre sidevange (J3) | Skruskjær, 3 × 6 mm — 98 mm omlegg tar ikke fire i rad | 6,0 kN | < 1 kN | 0,17 | ✓ Samme detalj som hele rammen bruker |
| Stigens stivhet i eget plan | Rammevirkning: to vanger + fire trinn | — | — | — | ✓ |

### A.3 Underetasjen

| Ledd | Bæremåte | Spenn / flate | Last | Utn. | Dom |
|---|---|---|---|---:|---|
| Benkespile 36×98 | Bøyning — samme stykke som køyespilen | 800 mm | 1 kN på én spile | **0,57** | ✓ Ved vanlig sitting, 0,5 kN, er utnyttelsen 0,29 |
| Spile → benkevange | Trelagring 48 × 98 | 4704 mm² → 10,9 kN | 0,5 kN | 0,05 | ✓ |
| Bakre benkevange 48×73 | Bøyning over åpningen mellom stubbeføttene | 700 mm | 0,5 kN | **0,14** | ✓ Ved 1 kN: 0,28 |
| Fremre benkevangebit 48×73 | Bøyning, to opplegg, ingen utkraging | 597 mm | 0,5 kN | < 0,14 | ✓ Innerenden står midt på stubbefoten |
| Benkevange → stubbefot | **Trelagring** 48 × 48 | 2304 mm² → 5,3 kN | 0,5 kN | 0,09 | ✓ |
| Benkevange → bærekloss J9-B | **Trelagring** 48 × 48 | 2304 mm² → 5,3 kN | 0,5 kN | 0,09 | ✓ |
| Bærekloss → stolpe (J9-B / J9-F) | Skruskjær, 1 × 6 mm | 2,0 kN | 0,5 kN | 0,25 | ✓ Samme sak som J1-B, halv last |
| Stubbefot 48×48 | Knekking over 186 mm | λ ≈ 13 | 0,5 kN | ≈ 0 | ✓ Ikke en søyle, et opplegg |

### A.4 Plate og rekkverk

| Ledd | Bæremåte | Spenn / flate | Last | Utn. | Dom |
|---|---|---|---|---:|---|
| Plate 18 mm, **bar** | Bøyning over to opplegg | 715 mm | 2 kN dynamisk | **1,40** | ✗ Holder ikke alene |
| Plate 18 mm **med to avstivningslekter 48×73 på høykant** | To T-bjelker med platen som flens | 715 mm | 2 kN dynamisk | **0,26** | ✓ Dette er hele grunnen til at lektene finnes |
| Plate → U-brakett | M6 i skjær | ≈ 3 kN per bolt | 0,13 kN | 0,04 | ✓ |
| Bordbærelekt 21×95 **på høykant** | Bøyning om sterk akse | 1794 mm | 0,55 kN bordlast | **0,15** | ✓ Flatt lagt faller kapasiteten med faktor 20 |
| Bordbærelekt → stolpe | Skruskjær, 1 × 5 mm per beslagflik — 40 mm flik tar ikke to | 1,5 kN | 0,13 kN | 0,09 | ✓ Lekta ligger dessuten PÅ den vannrette fliken; skruen holder den bare nede |
| Rekkverksbord 36×98 | Bøyning om svak akse, vannrett last | ≈ 760 mm | 0,5 kN | **0,13** | ✓ |
| Rekkverksbord → stolpe | Skruskjær, 2 × 5 mm per omlegg | 3,0 kN | 0,25 kN | 0,08 | ✓ |

### A.5 Global stabilitet

| Retning | Hva som holder igjen | Dom |
|---|---|---|
| Langs rommet | De to sideveggene, og de fire hjørnestolpene som står inntil dem | ✓ |
| I dybden, øvre nivå | Portalramme i hver ende — to stolper og en endebjelke, festet i begge hjørner — pluss veggfestet J14, som binder hele den bakre sidevangen til veggen | ✓ Veggfestet fjerner all gynging |
| I dybden, nedre nivå | Den gjennomgående bakre benkevangen, de ti benkespilene og platen danner en vannrett skive som binder alle stolper og føtter sammen | ✓ |
| Vipping forover | Fotavtrykket er grunnere enn sengen er høy, men tyngdepunktet ligger godt innenfor det. Veggfestet er uansett det som avgjør | ✓ |

### A.6 De høyeste utnyttelsene

| Ledd | Utn. |
|---|---:|
| Bakre sidevange regnet uten veggfestet | 0,73 |
| Køyespile og benkespile, 1 kN på én spile | **0,57** |
| Bærekloss J1-B → stolpe, klossens ene skrue regnet alene | **0,50** |
| Stigekloss → stigevange, klossens ene skrue regnet alene | 0,33 |
| Endebjelke | 0,26 |
| Plate med avstivningslekter | 0,26 |
| Endebjelke → bærekloss (trelagring), bærekloss J9 → stolpe | 0,25 |
| Stigevange → fremre sidevange (J3) | 0,17 |
| Stigevange, knekking ut av planet | 0,14 |
| Alle andre ledd | ≤ 0,13 |

De to øverste skrueradene er de eneste stedene i sengen der en loddrett
reaksjon går gjennom stål i det hele tatt, og begge er regnet **uten** hjelp
fra nabofestene i det samme hjørnet. Med den kombinerte skjærveien er de 0,17
og 0,14 — se avsnitt 2.

Ingen ledd i den ferdige sengen har utnyttelse over 1,0. De to tilfellene som
gjør det, er begge dekket av bruksreglene: bar spilebunn under hopping (7.4) og
platen uten avstivningslekter — som ikke er en tillatt byggemåte, lektene skal
monteres.

---

## Vedlegg B — aksepterte avvik

Her står de bevisste valgene som ikke er det lærebokrene, med begrunnelsen,
slik at den som bygger vet hva han går med på.

**Avvik 1 — veggen erstatter det bakre rekkverket.**
Sengen har rekkverk bare på framsiden. På baksiden er veggen sperren. Madrassen
ligger klemt mellom veggen og de fremre stolpene, uten spalte langs noen av de
lange kantene, så den klassiske seng/vegg-klemspalten finnes ikke her.
*Betingelser:* sengen **skal** stå inntil vegg og **skal** være skrudd fast i
den (J14). Sengen kan ikke snus og kan ikke stå fritt i rommet. Vil du gjøre den
frittstående, må to rekkverksbord og to fulle bakre stolper på plass — se
butikknotatene, og regn med at hele lastbanen på baksiden må sjekkes på nytt:
det er den bakre sidevangen som deler lasten med veggskruene.

**Avvik 2 — stigefoten er ikke bundet i dybderetningen.**
Gulvet foran stigen er med vilje helt fritt, og den fremre benkevangen krysser
det ikke. Prisen er at stigevangene ikke har noe hold i dybderetningen nede ved
gulvet. *Det som erstatter det:* den løse platen. U-brakettene (J13b) omslutter
trinnet og klemmer platen til stigen, og platen binder stigen tilbake til den
bakre bærelinjen. Veggfestet (J14) holder resten av rammen i ro.
*Betingelse:* platen **skal** alltid ligge i, i en av de to stillingene. Se 7.5.

**Avvik 3 — bar spilebunn tåler ikke dynamisk last.**
Én spile alene under full hoppelast er overbelastet. Med madrass på fordeles
lasten over flere spiler og utnyttelsen halveres. *Betingelse:* madrassen legges
på før noen går opp. Se 7.4.

---

## Tegninger

| Tegning | Innhold |
|---|---|
| [byggerekkefolge.svg](schematics/byggerekkefolge.svg) | Oversikt over byggerekkefølgen, med samme nummer som byggesteg og MONTERING |
| [side-elevation.svg](schematics/side-elevation.svg) | Langsiden sett forfra: stolper, stigevanger og trinn, sidevange, begge rekkverksbånd med klatreåpningen, benkevanger, stubbeføtter og benkespiler, med alle skrueposisjoner |
| [end-elevation.svg](schematics/end-elevation.svg) | Kortsiden, med veggen inntegnet. Her ser du at sengen er usymmetrisk: bakre stolpe stopper i sengeflaten, fremre går helt opp til rekkverket |
| [ladder-detail.svg](schematics/ladder-detail.svg) | Stigen: vanger, klosser, trinn, J3-skruene, og hylla bak trinnet som platen hviler på |
| [bench-detail.svg](schematics/bench-detail.svg) | Benken: bærekloss mot hjørnestolpen, vangebiten som ender på stubbefoten, benkespilene og platekanten |
| [panel-detail.svg](schematics/panel-detail.svg) | Den løse platen i begge stillinger, med avstivningslekter, U-braketter og krokplater |
