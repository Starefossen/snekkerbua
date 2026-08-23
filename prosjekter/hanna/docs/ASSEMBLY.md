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
| [generated/kappliste.md](generated/kappliste.md) | Hver del: dimensjon, lengde, antall, hvor den sitter — og om den kappes ferdig nå eller med overmål og tilpasses i rommet |
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
| Trebor i flere små diametre til forboring | Se forboringskolonnen i beslaglista. Forbor **alltid** i bordbærelekta, i bordene og i all endeved |
| Forsenker (kjeglesenker) | Alle skruehoder i flater man tar på: benkespiler, køyespiler, trinn |
| Forstnerbor ⌀18 og ⌀12 | ⌀18: setet under hvert skråskruehode (J8-B og J10) — boret går ned i hullet i vinkelklossen, som er det som holder vinkelen; se J8-B og [setedetalj.svg](schematics/setedetalj.svg). ⌀12: kontraborene i lektene og kilene under platen (J13a/J13b) |
| Fres med V-spor eller avrundingsfres — eller høvel, blokkhøvel, pussekloss | Kantbrytningen, avsnitt 3. Ingenting her krever fres |
| Bits Torx T20 / T25 / T30 | Etter skruestørrelse |
| Sirkelsag eller håndsag + anlegg | Alle kutt er 90°, med ett unntak: de to kilelektene sages på skrå i ett langsgående snitt (J13b). Ingen gjæring i hele sengen |
| Vinkelhake, minst 300 mm | Rett vinkel i bakrammen og i sengeflaten — mål diagonalene |
| Vater, minst 600 mm | Endebjelker og vanger |
| Linjelaser, selvnivellerende kryss | Høyderisset rundt nisja og loddlinja midt i den. All oppmåling av rommet skjer fra risset — se avsnitt 3 |
| Tommestokk og målebånd | |
| To skrutvinger, minst 300 mm | Holder deler mens du borer gjennom begge samtidig |
| Blyant og syl | Merking av borsentre |
| Én person — to ved reisningen | Steg 2 (bakrammen tippes opp) og steg 4 (den fremre sidevangen løftes opp på begge endebjelker samtidig). Resten er skrevet for én mann med tvinger og hjelpelister |

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

Det er ikke en nødløsning. **Tre bærer på tre der tre kan bære på tre.** Hver
eneste lange del hviler på noe: sidevangene på endebjelkene, den bakre
sidevangen rett på stolpetoppene, benkevangene på stubbeføttene. Ingen av *de*
skruene er opplegg.

Tre hjørner har ikke noe å hvile på, og der går den loddrette reaksjonen
gjennom stål. Det står her, rett ut, fordi det er der antallet skruer betyr
noe:

* **J1**, endebjelken mot stolpen: to 6×80 i skjær ≈ 4,0 kN mot ≤ 1 kN
  hjørnereaksjon — utnyttelse **0,25**.
* **J8**, den fremre benkevangebiten mot stolpen: to 6×80 ≈ 4,0 kN mot
  0,5 kN — **0,13**. Etter X18 er de to skrå, akkurat som J8-Bs, fordi enden
  er buttet og ikke lappet — og skråstillingen koster ingenting her heller.
* **J8-B**, den bakre benkevangen mot stolpen: to skrå 6×80 ≈ 4,0 kN mot
  0,5 kN — **0,13**. Skruene står skrått i planet, men lasten står loddrett
  på dem uansett, så skråstillingen koster ingenting.

**Her sto det åtte bæreklosser før, og de er tatt bort.** Argumentet for dem
var at delen skulle *bære på tre* i stedet for å henge i skruer. Følg det ett
skritt til, og det spiser seg selv: klossen står ikke på noe heller. Den
henger på stolpen i **én** 6 mm skrue — 2,0 kN mot inntil 1 kN, utnyttelse
0,50, den høyeste skrueraden i hele sengen. Klossen tok ikke lasten ut av
stålet; den halverte stålet leddet ellers hadde hatt.

Sprekkfaren klossen ble kjøpt mot er også målt nå. Skruene i bjelkeenden står
18 mm (3 × skruediameteren) fra bjelkens ende langs fiberretningen og 19 mm
(3,2 ×) fra kanten i den retningen lasten virker, i 36 × 98 mm C24. Det er et
helt vanlig omlegg, med bedre kantavstand enn regelen krever — ikke en sprø
endeskjøt.

**Det klossen egentlig var, var en jigg:** en hylle å legge delen på mens du
skrudde den fast. Den jobben gjør nå hullene. Alle gjennomgangshull bores i
steg 0, gjennom begge deler samtidig med delene tvunget sammen, og et
hullmønster har nøyaktig én stilling der det står over seg selv. Delen kan
ikke settes i feil høyde.

Alt dette står i lasttabellen i vedlegg A, rad for rad. Bolten er fortsatt
borte, og det er fortsatt riktig.

**Og én ting til, som ikke er statikk:** ingen skruehoder står på sengens
front. Alt fra vangenes ytterflate og fram til stolpeplanet er den eneste
flaten noen ser på, og J2, J3 og J8 skrus derfor **innenfra og ut** — gjennom
den 48 mm tykke vangen og inn i den 36 mm tykke stolpen eller stigevangen, i
stedet for omvendt. Begge veier holder målene like godt (36 + 48 er det samme
som 48 + 36, og spissdekningen er 4 mm uansett vei), så det er utseendet som
avgjør, og modellen har en assert som sier det: ingen festemiddelhoder på en
romvendt flate. Rekkverksbordene har vært skrudd slik hele tiden.

**Og du kommer til.** Bak hvert eneste av de hodene står det over 700 mm åpen
luft — inn i den tomme sengerammen for J2 og J3, inn i det åpne benkerommet
for J8 — på det tidspunktet i rekkefølgen leddet skrus, og faktisk også i den
ferdige sengen. Alle tre skrus før spilene går på. En drill med bits er en
kvart meter.

**Én konsekvens til, og den er god:** ingenting i rammen festes lenger fra en
flate som ender mot vegg. Da finnes det heller ingen skruehoder som må senkes
ned under en monteringsflate — ingen forsenkte boltehoder, ingen store
forsenkingshull, og ingen deler som må boltes ferdig før de får møte veggen.

**Det er ikke ett vinkelbeslag i denne sengen lenger.** Tegningen hadde seks —
fire under stubbeføttene og to under bordbærelektas ender — og byggherren
bygget uten alle seks (X18). Det som gjør jobben i stedet er skruer, og det er
skruer huset allerede eide: en 6×120 rett ned gjennom benkevangen i fotens
endeved og en 5×60 skråskrue opp i vangen fra fotens side (J10), og to 6×80
skråskruer ut av flatbunnede seter i bordbærelektas forside (J12) — nøyaktig
det leddet den bakre benkevangen har hatt siden K4. Beslagets vannrette flik
var hylla lekta hvilte på mens den ble skrudd; hullparet er den hylla nå, for
et hullbilde passer i én eneste stilling. Alt stål i sengen er dermed skruer,
og platemekanismen er fortsatt ren tre — lektene gjør hele jobben, se J13.

**Det står ingen lås i beslaglista, og det er ikke en glipp.** Låsen i
sengestilling var det siste åpne valget i platemekanismen. Valget er tatt: det
blir ingen lås. Begrunnelsen står i vedlegg B, avvik 4, og treverket den ville
tatt tak i står der det sto — se J13.

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
3. **Endene bygges ut:** fremre stolpe, så endebjelke. Én ende av gangen.
   Det står ingen kloss under bjelkeenden — de forborede hullene er jiggen.
4. **Fronten lukkes:** fremre sidevange, så de to fremre benkevangene, alle
   fire stubbeføtter, de to benkespileleddene og alle fire endelister — hele
   benkens bæreverk i samme kotehøyde. Etter X18 er de fremre benkevangene
   buttet mellom stolpe og stubbefot i stolpenes eget plan, og de festes med
   lommeskruer; leddet og de fremre endelistene er det som gir spileendene
   flaten de mistet da vangen flyttet seg fram.
5. **Resten kommer forfra og ovenfra:** stige, benkespiler, køyespiler,
   rekkverk, plate, madrass.

Den samme rekkefølgen, med sjekkpunkter for hvert steg:
**[byggesteg.md](generated/byggesteg.md)**. Med bilder:
**[MONTERING.md](MONTERING.md)**. Oversiktstegning:
[schematics/byggerekkefolge.svg](schematics/byggerekkefolge.svg).

**Og før steg 1: bryt kantene.** Det gjøres i steg 0, mens delene ennå er løse
på bukken. Kravet står under.

### Rommet først — før noe kappes

Nisja er ikke et rektangel. Vegger heller, gulv faller, og hjørner er sjelden
90°. Senga skal stå i vater og lodd likevel. Regelen er derfor:

**Senga er referansen, ikke rommet — bygg i vater og lodd, og ta skjevheten i
delene som møter vegg og gulv.**

Det deler kapplista i to, og delingen er en regel i modellen, ikke en
håndskrevet liste: en del som kommer inntil en endevegg, eller som står på
gulvet, får sluttmålet sitt av rommet. De delene står for seg selv i
[kapplista](generated/kappliste.md), med overmålet sitt i egen kolonne. Resten
kappes ferdig på bukken.

To ting må være på plass før kappingen:

* **Spikerslag i veggen.** Senga ligger flatt mot veggen i noen få
  høydebånd, ikke overalt. Sonene er regnet ut av modellen og står i
  [byggesteg](generated/byggesteg.md#før-steg-0--mål-rommet) — i **to
  notasjoner**: over ferdig gulv, og som fortegnstall fra høyderisset (minus
  er under laserlinja, pluss er over). Gulvet er skjevt og risset er ikke, så
  det er den andre kolonnen du setter sonene etter. Legg dem mens
  veggen er åpen — etterpå kommer du ikke til.
* **Et vannrett høyderiss rundt hele nisja.** Alt måles fra risset, aldri fra
  gulvet. Framgangsmåten — loddlinje midt i nisja, rutenett mot hver
  endevegg, minste sum er minste bredde — står samme sted.

Blir minste bredde et annet tall enn det modellen står på, er det ett tall som
skal endres: `WALL_SPAN` i `generate_loftbed.py`. Kjør `mise run build`, og
kapplista, innkjøpslista og nøkkelmålene følger etter.

**De fire hjørnestolpene har null klaring mot endeveggen.** Modellen setter dem
i selve veggplanet, så en bul i veggen har ingen luft å forsvinne i: enten går
den av treet, eller så skyver den hele rammen ut av lodd. Derfor er dette fast
framgangsmåte for hver av de fire, ikke et unntak ved store avvik: sett
stolpen på plass, hold den i lodd, strek opp veggsiden med avstandskloss —
meddrag — og høvle av til stolpen står i lodd inntil veggen. Det er materiale
som fjernes; det legges ingenting på i bredden, og den nominelle dimensjonen i
kapplista står. Stolpene bærer begge behandlingene i
[kapplista](generated/kappliste.md): overmål i bunn og oppstreking av siden.

Kanter som møter vegg eller gulv kappes med lite bakfall. Da er det bare den
synlige kanten som bestemmer fugen.

### Kantbrytning — alle kanter et barn kan nå

**Alle kanter et barn kan nå skal brytes.** Kravet er *brutt kant*, ikke én
bestemt metode: 45° fas eller avrunding (R6,35 eller R9,5), byggerens valg
kant for kant. Skarpkantet høvlet C24 er skarpt nok til å skjære, og det blir
ikke rundere av at noen maler det.

Tre steder er verdt å nevne ved navn:

* **Plateenhetens underside** — styrelektenes nedre kanter og kilelektenes kanter.
  Dette er kanten ingen ser: den sitter under bordplaten, i knehøyde for den
  som sitter ved bordet. Etter X9 er den knehøyden ikke lenger et bilde: platen
  er en pult med 262 mm under seg, og knærne står faktisk der inne. 68 mm
  skarpkantet lekt mot et kne er det eneste stedet i denne sengen der en kant
  treffer noen som ikke ser den komme.
* **Platens egne kanter, alle fire.** Den håndteres hver gang stillingen
  skiftes, og et kappet finérdekke gir flis.
* **Alt man allerede tar på:** stolper, rekkverksbord, trinn og
  stigevangenes kanter.

Verktøy: fres med V-spor eller avrundingsfres for den som har fres. Har du det
ikke, gjør en håndhøvel, en blokkhøvel eller en pussekloss nøyaktig samme
jobb. Det er noen millimeter tre som skal bort, ikke en profil som skal
lages — ingenting her krever fres.

Det er lettest mens delene er løse, altså i steg 0. En kant som bare er
tilgjengelig fra én side etter at delen står i rammen, tar dobbelt så lang tid
og blir halvparten så pen.

**Modellen tegner fortsatt hver del firkantet.** Kantbrytningen er en instruks,
ikke geometri, og den flytter ingen mål: ingen lengde, ingen klaring og ingen
skruerad endrer seg av at en kant er brutt.

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
* **Forbor hver eneste treskrue.** Ingen unntak i bordbærelekta, i
  bordene og i endeved.
* **Ingenting i rammen er boltet.** Hele rammen er skrudd, med forborede
  6 mm treskruer. Se J1, J2, J3 og J8.
* Diameterne står i forboringskolonnen i
  [beslaglista](generated/beslagliste.md).

---

## 4. J — leddene

Antall, skruetype, forboring og hvilken side du driver fra står i
[beslaglista](generated/beslagliste.md). Skrueradenes høyder står i
[nøkkelmål](generated/nokkelmal.md). Her står hva leddet er og hva som er
poenget med det.

### J1 — Endebjelke → hjørnestolpe

Endebjelken støter mot stolpens innside og skrus gjennom bjelken og inn i
stolpen. Skruene går på tvers av fiberretningen i begge deler, ikke inn i
endeved.

**De to skruene er hele festet.** Det står ingen kloss under bjelkeenden — den
sto der til denne runden, og den er tatt bort, fordi en kloss som selv henger i
én skrue gir leddet halvparten så mye stål som bjelkens egne to. Se avsnitt 2
og lasttabellen: 4,0 kN mot en hjørnereaksjon på høyst 1 kN, utnyttelse 0,25.

Skruene står 18 mm fra bjelkens ende og 27 mm fra over- og underkant. Begge er
over minstekravet for en 6 mm skrue, og den som betyr mest her — kantavstanden
i lastretningen — har halvannen gang så mye.

**Hullene er jiggen.** Gjennomgangshullene i bjelken og styrehullene i stolpen
bores i steg 0, gjennom begge deler samtidig. Da har bjelken nøyaktig én høyde
der hullene står over hverandre, og du kan ikke montere den skjevt. Bygger du
alene: klem en list på stolpens innside i høyde med bjelkens underkant, legg
bjelken på den, skru, og ta listen av igjen.

Skruene drives inne fra sengen. Du kommer til dem når som helst, både under
byggingen og når du skal ettertrekke.

### J2 — Fremre sidevange → fremre hjørnestolpe

Vangen ligger flatt mot stolpen. **Skruene drives innenfra og ut:** du står
inne i sengerammen — den er tom, spilene kommer flere steg senere — og skrur
gjennom vangens innside, gjennom vangen og inn i stolpen.

Det er en utseendebeslutning, og den er tatt bevisst. Stolpens forside er en
av de flatene rommet faktisk ser, og der skal det ikke stå skruehoder. Begge
retninger holder målene like godt: 48 mm vange pluss 36 mm stolpe er det
samme stykket tre som 36 pluss 48, og spissen har 4 mm tre bak seg uansett vei
— så det er ikke statikken som velger. Se avsnitt 2.

Vangen bærer ikke i skruene — den ligger på begge endebjelker.

Merk skruelengden: skruen skal **ikke** komme ut på stolpens forside. Bruk
lengden som står i beslaglista, ikke den lengste du har i esken.

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

Tre kraftige treskruer gjennom sidevangen og inn i stigevangen. Leddet er
skrudd, ikke boltet — samme mønster som resten av rammen bruker, se J1, J2
og J8. Tre og ikke fire: omlegget er 48 × 98 mm, og fire 6 mm skruer i én rad
ville krevd 108 mm der det er 98. Fire i to par ville krevd 60 mm på tvers der
det er 48.

**Retningen er innenfra og ut**, som J2 og av samme grunn: stigevangens
forside står i sengens front, og der skal det ikke stå skruehoder. Klem stigen
fast mot sidevangen først — du står på den andre siden når du skrur.

Stigevangen står med den tynne siden mot rommet, så skruene treffer den på
midtlinjen med akkurat den kantavstanden en 6 mm skrue skal ha.

Forbor gjennomgående i sidevangen, og forbor i stigevangen også. Skruene sitter
i én loddrett rad, én over og én under vangens midtlinje med den tredje midt
imellom, slik at leddet tar moment.

### J4 — Rungetrinn → stigekloss og stigevange

Trinnet ligger på klossen. Det er **ett** festemiddel i dette leddet, og det er
den kraftige skruen fra utsiden av stigevangen inn i trinnenden. Gjennom
trinnets overside går det ingenting.

Skruen i trinnenden bærer **ingen** vertikal last — den holder bare trinnet på
plass sideveis. Vekten din går rett ned i klossen og videre inn i vangen. Det er
riktig utformet, og det er grunnen til at trinnet ikke kan glippe selv om skruen
i endeveden skulle løsne.

**Her sto det en 5×60 ned gjennom trinnet og inn i klossen, og X10 strøk den —
fordi den ikke kunne eksistere.** Den hadde ingen lovlig plass å stå på: vangens
36 mm dybde låser hvor gjennomgangsskruen i trinnenden kan stå i dybden,
trinnets 48 mm låser hvor den kan stå i høyden, og en skrue som slippes ned fra
trinnets overside må krysse hele trinnet for å nå klossen — altså rett gjennom
6×120-ens egen kanal. Snus den, og drives opp nedenfra, klarerer den 6×120-en
med 12 mm og lander i stedet på J5, som sitter midt i klossens egen høyde og
heller ikke kan flytte seg. Klossen kan ikke ta en loddrett skrue så lenge
trinnet har en vannrett.

**Så jobben er lagt på treet i stedet, og det er en bedre begrunnelse enn den
strøkne skruen var.** Klossen er fanget mellom tre ting: vangeflaten den er
skrudd til, trinnet som ligger på 1296 mm² av oversiden hennes, og at det
trinnet selv er naglet til vangen 48 mm lenger opp av 6×120-en. Skal klossen
rotere om sin ene skrue (J5), må den løfte et trinn som er skrudd fast. Det er
lås av tre, ikke av stål — og det er grunnen til at **hver eneste kloss i denne
stigen har et trinn oppå seg**. X9 hang to klosser på vangene som ikke hadde
det, og måtte kjøpe en skrue nummer to til hver av dem for å erstatte trinnet;
X16 strøk klossene, og med dem den ene delen i sengen som trengte stål fordi
den manglet tre.

Trinnene stikker **bakover**, ikke framover: forkanten ligger i flukt med
stigevangens forkant, og det som blir liggende bak vangeplanet er hylla den løse
platen hviler på. **Den setningen gjelder begge stillinger igjen.** Fra X9 til
X15 gjaldt den bare trinn 1, fordi bordstillingen da hvilte på to påskrudde
bordklosser og ikke på et trinn i det hele tatt; etter X16 lander platens
forkant på **trinn 1** i sengestilling og på **støttetrinnet** i bordstilling —
samme profil, samme hylle, samme ledd, samme 320 mm trinn. På den stigen som
faktisk står, er støttetrinnet **trinn 2** og ikke trinn 3: se X18 nedenfor.

**Klossen følger ikke trinnet bakover.** Den er 36 mm dyp — nøyaktig så dyp som
stigevangen — og står i vangens eget dybdebånd, ikke i trinnets. Klossen har
aldri rørt mer av vangen enn de 36 millimeterne, så de 37 som er kappet vekk
(K1) bar ingenting; de sto derimot rett i veien for den løse platen når den
skal bæres fra det ene setet til det andre. Se J13. Det betyr også at trinnets
bakre 32 mm står **fritt** ved endene: trinnet er 68 mm dypt og vangeplanet tar
de fremste 36, så det er en 48 mm tykk kloss tre som stikker 32 mm ut, ikke et
spenn.

**X18 — STIGEN SOM STÅR HAR FIRE TRINN, OG DET SKAL LESES FØR RESTEN AV DETTE
AVSNITTET.** Byggherren kappet fire: **297, 682, 962 og 1242**. De to nederste
er med vilje platens to stillinger — «trinnene er laget for den opprinnelige
høyden av benk og bord» — og de to øverste er den samme utledningen X2 skrev.
Trinnet på 489 ble tegnet og aldri kappet, og uten det er steget fra trinn 1 opp
på støttetrinnet **385 mm**. Grensen i denne fila er 281 og er ikke rørt; det
bygde steget er 104 mm for langt. **Men veien barna faktisk går, er ikke den:**
de setter foten på **benkekanten** underveis — 297 → benkesetet 420 → 682 — og
da er største virkelige steg **262 mm**, innenfor grensen. Avviket er derfor
**akseptert**, ikke «bør rettes», og hele dommen — begge stillinger målt, EN
747-vurderingen og det femte trinnet som **opsjon** — står i **vedlegg B,
avvik 5**. Alt som følger i dette avsnittet er utledningen slik den var tegnet,
og den er beholdt fordi det er den opsjonen peker tilbake på.

**Stigen er to løp, og X16 flyttet skillet mellom dem opp i et trinn.**
Trinnoverkantene ble tegnet på 297, 489, 682, 962 og 1242, og stigningskjeden fra
gulv til spilebunn er 297 + 192 + 193 + 280 + 280 + 281. Fem trinn som før; det
er ikke antallet som er endret, det er fordelingen. Grunnen står i J13 og i
8.2, og den er snudd på hodet siden X9: **682 er ikke lenger en høyde et trinn
har forbud mot å stå på — det er høyden et trinn skal stå på.** Bordplatens
underside er 682, støttetrinnet er lagt nøyaktig der, og de to løpene **møtes** på
det trinnet. X9 leste den samme høyden som et bånd som måtte holdes tomt og
skjøv trinnene til 297 / 572 / 848 / 1073 / 1298 for å få det til; til og med
v15 sto de på 297 / 542 / 787 / 1032 / 1277, jevnt fordelt.

**Antallet trinn var fortsatt FEM da det ble tegnet, og det skal stå her og
ikke i en fotnote.** Bestillingen var «ta bort et trinn og juster avstanden», og
et trinn ble ikke borte på tegningen — det ble borte i verkstedet, se X18 over. Trinn 1 er naglet til benkevangen på 297, spilebunnen ligger på 1523, og
297 → 682 lar seg ikke gå i ett steg. Det som forsvant, er de **to
bordklossene**. Ved platens forkant sto det tre trebiter i to omfar — et trinn
oppe og et klossepar under — og der står det nå én. Det var de klossene
byggherren så fra gulvet, og det er dem runden tok; trinnet overtok jobben
deres.

Det er verdt å si nøyaktig hva som ble gitt opp og hva som ikke ble det.
**Stigningsgrensen ble hevet med én millimeter, og den ble hevet i åpent
lende.** Det øvre løpet er 841 mm i tre steg, og 841 = 3 × 280 + 1, så største
klatretrinn er 281 mm der fila før sa 280. De fem klatretrinnene ligger på 192,
193, 280, 280 og 281 — det er **det** tallet EN 131s bånd 250–300 gjelder for i
denne fila, og 281 ligger godt inne i båndet; 280 var husets egen avrunding av
det, ikke normens tall. Det fantes nøyaktig ett alternativ: legge støttetrinnet
på 683 i stedet for 682. Da går det øvre løpet opp i tre like steg og grensen
står — men bordplaten går til 701, bordbærelekta til 615–683 og
**spikerslagsone 3 én millimeter oppover en vegg byggherren spikrer denne
uka**. Veggen er ikke forhandlingsbar, og en fot finner ikke én millimeter på
et 280 mm steg. Det ble sagt nei til dette i åpent lende, med tallet skrevet
ned ved siden av.

Å ta et kortere steg enn normen legger opp til er ikke en fare, det er bare
tettere trinn; det er den *lange* stigningen grensen vokter. Det som ble gitt
opp er *jevnheten*, som X1/X2 selv skrev ned som en utseendebeslutning — og den
er ikke slakket, den er **delt**: inne i hvert av de to løpene er stigen jevn
til 1 mm, og den grensen (2) er urørt. Forskjellen **mellom** løpene er derimot
89 mm mot en egen grense på 90, der X9 sto på 51 mot 60. Spriket er ingen
overraskelse, det er regnestykket: det nedre løpet har 385 mm å klatre i stedet
for 551, i de samme to stegene. Nede er det to grunne steg opp til pulten, oppe
er det en ordentlig stige — og det er nettopp det denne sengen er.

Det som skiller de to løpene er ikke lenger et forbudt bånd, det er et påbudt
punkt. Løftesjakten står igjen som betingelse **over** støttetrinnet — ingen
*annen* trinnoverkant får ligge i båndet 614..848 — men trinnet platen hviler
på er selve gulvet i det løftet og er unntatt fra sitt eget forbud. Ut over det
er stigen den samme utledningen X2 skrev, bare gjort to ganger: færrest trinn,
så jevnest, i hvert løp for seg. Flytter platen seg igjen, følger støttetrinnet
den og hele stigen regnes om; ingen setter et trinn for hånd.

**Og prisen ble betalt et annet sted, av trinn 2 — på tegningen.** Det nedre
løpet falt med støttetrinnet, så trinn 2 gikk fra 572 til 489, og underkanten
sto 21 mm over den nedre soveflaten der den før sto 104. Det var ikke takhøyde
lenger, det var en **spalte** — og 21 mm ligger inne i EN 747-båndet 12–25 mm,
der et lem passerer fritt og ingenting kiler seg.

**X18 gjorde den prisen om intet, for trinnet finnes ikke.** Det laveste som
står over den nedre soveflaten er bordbærelekta på 194 mm, og transportsjakten
over benken — den platen bæres gjennom når den bytter stilling — gikk fra
121 til **294 mm**. Plateenheten er 86 mm høy, så den passerer med 208 mm i
stedet for 35. Det er den ene tingen i hele X18 som ble bedre uten at noen
betalte for den. Se 5 og 7.

Første steget, de 297 fra gulvet opp på benkevangen, er fortsatt en avsats du
trår opp på og ikke et klatretrinn — og trinn 1 står fortsatt på 297 og bærer
fortsatt sengemodus-platen. Både X9 og X16 rørte stigen **over** trinn 1 og
ingenting annet.

**Hullene i vangen, målt fra vangetoppen — les dette før du borer.** Stigevangen
kappes med overmål og finkappes i **bunnen**, så toppen er den enden som ligger
fast, og det er den alle hull måles fra. Hullsenteret ligger midt i trinnets
høyde, altså 24 mm under trinnets overkant.

| Trinn | Overkant over gulv | J4 ⌀6 fra vangetoppen |
|---:|---:|---:|
| 1 | 297 mm | **1598 mm** |
| 2 (støttetrinnet) | 682 mm | **1213 mm** |
| 3 | 962 mm | **933 mm** |
| 4 | 1242 mm | **653 mm** |

**Begge kolonnene flyttet seg i X18, og av to uavhengige grunner.** Trinnet på
489 ble aldri kappet, så raden er borte; og stigevangen er kappet ved 1871 og
ikke ved 2037, så *alle* de gjenværende målene fra vangetoppen er 166 mm
kortere enn på det forrige arket. Gammel → ny, rad for rad:

| Overkant | X16-ark (vangetopp 2037) | X18-ark (vangetopp 1871) |
|---:|---:|---:|
| 297 mm (før) | 1764 mm | **1598 mm** |
| 489 mm (før) | 1572 mm | *trinnet finnes ikke* |
| 682 mm (før) | 1379 mm | **1213 mm** |
| 962 mm (før) | 1099 mm | **933 mm** |
| 1242 mm (før) | 819 mm | **653 mm** |

Stigeklossens hull (J5, ⌀3 i vangen) trenger ikke sin egen kolonne: klossen står
rett under trinnet sitt og er like høy, så J5-hullet ligger **48 mm lenger ned
fra vangetoppen** enn J4-hullet i samme rad — klosshøyden, hver gang.

**Bare trinn 1 står der det sto.** Etter X9-arket lå de fire andre J4-hullene på
[var 1489, 1213, 988 og 763 mm fra vangetoppen], og de to bordklossene hadde
hvert sitt hullpar [var 1377 og 1401]. Har du boret etter det arket, står fire
hull tomme og ett av bordklosshullene 2 mm fra det nye støttetrinnets — se det
strøkne J5-B-avsnittet under for hvordan det plugges.

### J5 — Stigekloss → stigevange

Én skrue per kloss, inn i vangens innside. Klossen dekker bare 36 × 48 mm av
stigevangen, og to 5 mm skruer trenger 50 mm av de 48. Klosshøyden er
trinnhøyden. Mål to ganger.

**K1 endret ingenting i dette leddet.** Klossen ble kappet 73 → 36 mm, men de
36 × 48 millimeterne mot vangen er de samme — det var alt klossen noen gang
rørte, siden vangen bare er 36 mm dyp. Det ene som ble bedre er hvor skruen
lander: før satt den på Y 751,5, altså en halv millimeter **utenfor** vangens
bakplan, fordi den ble sentrert i en 73 mm lang kloss. Nå sitter den på Y 770,
midt i vangen.

Klossen er ikke overlatt til den ene skruen — men det som holder den er
**tre**, ikke en skrue til. Trinnet ligger på 1296 mm² av klossens overside, og
trinnenden er skrudd til stigevangen med en 6×120 gjennom vangen, 48 mm over
klossens egen skrue — begge sitter midt i sin egen deltykkelse, og delene er
48 mm høye hver. De to festene deler samme hjørne, og skal klossen rotere om
skruen sin, må den løfte et trinn som er naglet fast. X10 strøk den loddrette
5×60-en ned gjennom trinnet som sto her før — se J4 for hvorfor den ikke kunne
stå noe sted.

### J5-B — Bordkloss → stigevange *(STRØKET i X16)*

**Dette leddet finnes ikke lenger. Bygger du etter et ark fra før X16, er det
her arket er feil.** X9 la bordplaten på 700 ved å erklære 682 for en høyde
ingen trinn fikk stå i — platen skal løftes gjennom det båndet — og måtte så gi
forkanten et opplegg likevel. Det ble to bordklosser: 48×68 på høykant, én på
hver stigevanges innerflate, med to 6×80 hver. To trebiter som gjorde et trinns
jobb, i en stige som allerede kan lage en avsats i akkurat den høyden. **X16 snudde betingelsen:** 682 er høyden et trinn *skal* stå på,
støttetrinnet ligger der, og klossene er strøket sammen med sine fire skruer.

*Hva som forsvant med dem, kort: to deler av 48×68 [var 91 mm lange], fire
Treskruer 6×80, ett ledd i beslaglista, én rad i skrueretningene og
to rader i lastbanen — deriblant den ene skrueraden i hele sengen som hadde
lasten stående foran sin egen skruelinje [var 0,55 utnyttet]. Bæreflaten under
platens forkant gikk fra klossenes 5088 mm² til trinnets 9600 mm², og hylla er
igjen den samme hylla som i sengestilling.*

**Har du alt boret etter det gamle arket?** Klossenes to ⌀6 sto i stigevangens
utside [var 1377 og 1401 mm fra vangetoppen]. Det nye J4-hullet for
støttetrinnet står **1213 mm** fra den X18-kappede vangetoppen; på det arket
klossene ble boret etter sto det 1379 mm fra en vangetopp på 2037, altså 2 mm
fra det øverste av dem. Bor du det nye hullet uten videre, vandrer boret ned i det gamle og du får
et ovalt hull rundt en gjennomgående 6×120. Plugg det gamle hullet med limt
rundstokk og la limet herde før du borer det nye. Hele hulltabellen står i J4.

### J6 — Køyespile → sidevange

Spilene ligger **oppå** begge vanger, ikke i et spor og ikke på en lekt. Én skrue
ned i hver vange per spile. Forsenk hodet under flaten — det ligger madrass over.

Alle 14 køyespilene er nøyaktig like lange — 800 mm, samme stykke som
benkespilen. Den første ligger på X 20 og den siste på X 1970; delingen står i
[nøkkelmål](generated/nokkelmal.md).

### J7 og J21 — Rekkverksbord og avstivere

Rekkverksbordene ligger på **innsiden** av stolpene og stigevangene, mot sengen.
Skruene drives fra sengesiden. Bordene stopper i flukt med stigevangenes
innside, slik at klatreåpningen fortsetter rett opp forbi rekkverket. Man
klatrer **gjennom**, ikke over.

**X18 flyttet begge bånd, og de er målt fra SPILENE.** Byggherrens to mål er
130 mm fra spiletoppen opp til det nederste bordets underkant, og 120 mm fra
det bordets overkant opp til det øverste. Begge stemmer samtidig: nedre bord
ligger på **1653–1751** og øvre på **1871–1969**, med 68 mm bar stolpe over.
Det som følger av det:

* **åpningen under det nederste bordet er 10 mm.** Bordet ligger like over
  madrassen og dekker forkanten dens — det er en *lukket* åpning, ikke et
  klemvindu, og vedlegg B, avvik 6, er lukket med den. (Den første runden av
  X18 leste de 130 fra madrasstoppen i stedet for fra spilene og fikk 130 mm
  åpning ut av det. Det var ikke byggherrens tommestokk, det var
  koordinatorens datum.)
* **båndet mellom bordene er 120 mm, og 120 er over grensen 75 alene.** Det er
  avstiverraden som gjør det lovlig: fire avstivere per felt deler de 689
  millimeterne i luker på **59,4 mm**. Raden er ikke pynt, og den er ikke bare
  et opphengspunkt for det øverste bordet — den er selve klemdommen for det
  båndet.
* åpningen over det øverste bordet er **68 mm** mot grensen 75. Det er den
  samme åpningen vedlegg B, avvik 0, ble skrevet om da den var 58, og
  argumentet der dekker den fortsatt: ingen annen del i sengen står i det
  høydebåndet, så åpningen er ikke engang delvis omsluttet.
* barrieren står **326 mm** over madrassen mot EN 747s krav på 160.

**Og det er bare seks omlegg igjen, ikke åtte.** Stigevangene er kappet ved
1871, altså i flukt med det **øverste** bordets underkant, så det øverste
bordet har ingen vange å skrus i ved den indre enden — vangen slutter nøyaktig
der bordet begynner. Det bæres av avstiverraden, og det er vedlegg B, avvik 7.

**J21 — avstiverne.** Fire per felt av bunnspilevirket, 23×98 × 180 mm, lagt på
tvers over de to bordene i sporet mellom bordet og stolpeplanet, med 30 mm
omlegg på hvert bord. De 30 millimeterne er ikke valgt: en 5 mm skrue skal stå
3d fra avstiverens egen kappende og 3d fra bordets kant, altså 6d = 30 mm, og
180 = 120 + 30 + 30. Antallet er heller ikke valgt: tre avstivere i et 689 mm
felt gir 98,75 mm luker og faller på grensen, fire gir **59,4 mm** og holder.
Antallet settes av feltet og grensen, ikke av båndhøyden, så det er de samme
fire som før — det er bare lengden som fulgte båndet.
To 5×40 i hvert omlegg, drevet fra rommet.

**Dette er det ene stedet i sengen der stål synes på forsiden**, og det er
skrevet ned som det: 32 hoder på fronten. Den andre veien går ikke — en 5 mm
skrue som skulle krysse 36 mm bord ville komme ut av baksiden på en 23 mm
avstiver. Regelen i modellen er ikke slettet, den har fått ett navngitt unntak,
så begynner et *annet* ledd å synes på fronten, stopper bygget.

Det er ikke rekkverk på baksiden. Se sikkerhetsavsnittet.

### J8 og J8-B — Benkevange → hjørnestolpe

To ulike ledd, ett foran og ett bak.

**J8, foran — og X18 gjorde det til det samme leddet som J8-B.** Slik det var
tegnet lå vangebiten flatt mot stolpens innside med 95 mm omlegg, og de to
6×80 gikk rett gjennom det omlegget. Som bygget står vangen **buttet** mot
stolpens X-innside, i stolpenes eget plan, med forkanten i flukt med
stolpeforsiden — og et buttet ledd har ikke noe omlegg å skru gjennom.

Det er ikke et valg byggherren tok for utseendets skyld, og modellen fant det
ut på den harde måten: en vange som blir stående i sitt eget plan (Y 704..752)
og stoppes ved stolpens innside deler **en kant** med stolpen og ingenting
annet. Det finnes ingen flate der en skrue av noe slag kan krysse. Det eneste
planet der byggherrens setning i det hele tatt *er* et ledd, er stolpenes eget:
36 × 68 mm buttflate, som er stolpens egen dybde ganger vangens egen høyde.

Festet er derfor **lommeskruer**, og det er leddet dette huset allerede eide:
samme 65°, samme 20 mm sete, samme ⌀18 forstner og **samme vinkelkloss som
J8-B**. Ett 1:1-mønster tjener nå J8, J8-B og J12. Skruene drives fra vangens
innside — inne fra benkerommet, mens benken ennå er åpen — så stolpens forside
står uten skruehoder som før.

De to skruene er hele endefestet: 4,0 kN i skjær mot en endereaksjon på
0,5 kN. Det sto en bærekloss under denne enden til v12; se avsnitt 2 for
hvorfor den er borte.

**Og de 36 millimeterne vangen flyttet seg fram, koster noe.** Benkespilene er
800 mm og slutter på Y 752, så en vange på 740..788 gir dem 12 mm å ligge på
der de før hadde 48 — og 12 mm tar ikke kantavstanden til den 5 mm skruen som
holder en spileende nede. Det er **benkespileleddet** som lukker det, og det er
den ene halvdelen av byggherrens «ekstra støtter»: en 36×48 × 547 mm list
skrudd på vangens innside med overkanten i flukt med vangens, fire 5×60 per
benk satt i mellomrommene mellom spilene så ingen spileskrue kommer ned på en
av dem (J19). Da ligger spileenden på ledd og vange i ett plan, 48 mm bredt,
akkurat som før.

**J8-B, bak:** den bakre benkevangen går fra stolpe til stolpe og støter mot
stolpens sideflate med enden. Her går skruene **skrått** fra vangens forside inn
i stolpen. Forbor hele veien — en skråskrue nær en ende er den letteste måten å
sprekke en vange på.

**Hver skråskrue får et sete, og setet bores først.** Et 90° forsenk som møter
flaten i 25–30° kan ikke ligge i plan, og har aldri kunnet det. Det som ligger i
plan er et **flatbunnet sete boret langs skruens egen akse**: ⌀18 forstner.
Bunnen står vinkelrett på skruen, og dermed vinkelrett på hodet, så hodet legger
seg flatt og ender **helt under treet**. Alt om setene er tegnet opp på
[schematics/setedetalj.svg](schematics/setedetalj.svg) — snitt langs aksen,
munningen ovenfra, borjiggen og bruken av den.

**Dybden er 20 mm på J8-B og 18 mm på J10, og forskjellen har en grunn.** Et
forsenket hode i en flat bunn har to steder å lande. Det ene er bunnen. Det
andre er **kanten av forborhullet**: konusen går fra ⌀11,8 ned til ⌀6, og står
den på den kanten i stedet, ligger hodet 2,9 mm høyere enn tegningen sier. På en
skrue som står 25° på flaten spiser de 2,9 mm 1,23 mm av tredekket. Med 18 mm
sete ble regnestykket på J8-B:

| | hodet på bunnen | konusen på forborkanten |
|---|---:|---:|
| J8-B, 18 mm (før) | 2,26 mm | **1,03 mm** |
| J8-B, 20 mm (nå) | 3,11 mm | 1,88 mm |
| J10, 18 mm | 4,89 mm | 3,76 mm |

Kravet er 1,0 mm. En margin som forutsetter at skruen finner bunnen av sin egen
lomme er ingen margin, så J8-B er boret 2 mm dypere. J10 er ikke i nærheten og
står uendret. Alle tallene er målt på kroppene i modellen, og begge tilfellene
— hodet på bunnen og konusen på kanten — er egne asserter nå.

De 2 mm koster to ting og ingen av dem gjør vondt. Lommebunnen flytter seg
1,8 mm nærmere endeveden — men munningens egen nærmeste kant flytter seg ikke,
så det er bare hvem av dem som er nærmest som bytter plass. **X18 la 6 mm på
begge:** setet starter 40 mm fra enden i stedet for 34, fordi alle tre
skråskrueleddene i sengen nå bruker det samme runde tallet. Lommebunnen står
18,1 mm fra endeveden og munningens nærmeste kant 18,7. Og 20 mm av skruen går med i
lomma i stedet for 18, så J8-Bs 6×80 begraver 60 mm gjenger og J10s 5×60
begraver 42. Begge er kjørt gjennom de vanlige spiss-inne- og
spissdekningsasertene på nytt.

**Og treet MELLOM de to lommene er målt nå.** De to skråskruene i hver ende står
24 mm fra hverandre, som er rekkeregelen for en 6 mm skrue, men rekkeregelen
måler skruen og ikke hullet den ligger i: to ⌀18-lommer på 24 mm senteravstand
har 6 mm tre imellom. Det er nok her, og gulvet er skrevet ned til én
skruediameter slik at en senere endring ikke spiser det ubemerket.

**Vinkelklossen — borjiggen. To klosser, én per vinkel.** Et skrått hull startet
på frihånd vandrer, og det vandrer verst akkurat her: nær en ende, i en flate som
boret møter på skrå. Jiggen er derfor ikke en rampe boret hviler *på*, men et
hull det går *ned i*. Hver kloss er to biter av sengens egen 48×68, 200 mm
lange, skrudd flate mot flate. **⌀18 bores vinkelrett gjennom begge mens klossen
ennå er firkantet** — det er hele trikset — og først deretter kappes sålen av
under hullet på kappsag med bladet vippet **25° (J8-B)** hhv. **30° (J10)**.

Merk deg at vippen og flaten er komplementvinkler: 25° vipp gir en såle som står
**65°** på den borede flaten, og dermed 25° på hullaksen. Det er den vinkelen
leddet er regnet på. Kontrollmålet er munningen hullet etterlater i den ferdige
sålen — en ellipse på **42,6 × 18 mm** på 25°-klossen og **36 × 18 mm** på
30°-klossen. Mål den med tommestokken før klossen får røre sengen; er den for
kort, ble vippen satt på feil vinkel.

I bruk: klemt mot flaten med to tvinger, hullet over merket, offerkloss mot
endeveden, drill i gir 1 med slaget av. Både forstnerboret og forboret etterpå
går ned i det samme hullet. Klossene lages i steg 0 og er verkstedhjelpemidler,
ikke deler av sengen — de skal ikke bygges inn noe sted, og de går av restene
på 48×68-bordet.

I begge tilfeller er de to skruene hele endefestet. Det står ingen kloss under
noen av dem — de to skruene i hver ende tar reaksjonen i skjær med utnyttelse
0,13, og hullene fra steg 0 holder vangen i riktig høyde mens du skrur. Legg
gjerne en list eller en tvinge under enden hvis du er alene.

Vangen vipper ikke av at klossen er borte: den er festet i to punkter i hver
ende, over 68 mm høyde, og den andre enden står på en stubbefot.

### J10 — Benkevange → stubbefot

Foten står under vangen med hele endeflaten mot gulvet og hele toppflaten mot
vangen.

**X18: beslaget er ute, og det er to skruer i stedet — «ovenfra og fra
siden», som byggherren gjorde det.** Slik det var tegnet satt et vinkelbeslag i
hjørnet mellom fotens ytterside og vangens underside, med to skruer i hver
flik. Fire av de seks beslagene i sengen sto her. Som bygget står det i stedet:

* **Én 6×120 rett ovenfra**, ned gjennom vangens overkant og 52 mm inn i
  fotens endeved. Hodet forsenkes i vangens overkant, der benkespilene siden
  legger seg over det, så det synes ikke og det er ikke i veien.
* **Én 5×60 skråskrue fra siden**, nedenfra opp gjennom foten og inn i vangen,
  fra den fotsiden som vender inn mot benkeåpningen.

Én skråskrue og ikke to: foten er 48 mm dyp — like dyp som vangen den bærer —
og to 5 mm skråskruer ved siden av hverandre trenger 50. De to skruene måtte
skilles inne i vangen: den loddrette står 6 mm ut fra fotens senterlinje og
skråskruens sete 9 mm den andre veien, så aksene passerer 15 mm fra hverandre
der regelen krever 10,5.

*Hva det koster, sagt rett ut:* beslaget bandt foten til vangen i **strekk** i
to retninger. Endeved holder dårligere i uttrekk enn en flik gjør, og de to
skruene her er derfor ikke det samme leddet. Det de faktisk skal gjøre, er å
holde foten på plass — lasten står i **trykk** rett gjennom foten til gulvet,
og den går ikke gjennom noe feste i det hele tatt. Se vedlegg A.

Skråskruen får **samme slags sete som J8-B**: ⌀18 forstner, 18 mm langs skruens
egen akse, boret med 30°-vinkelklossen. Hodet ligger flatt i en flat bunn og
står 4,89 mm under treet — 3,76 mm selv om konusen skulle stå på kanten av
forborhullet. Setet spiser 18 mm av lengden, så 5×60-skruen begraver 42 mm.
J10 er ikke i nærheten av grensen og er derfor ikke boret dypere slik J8-B er.
Se J8-B for hele detaljen og
[schematics/setedetalj.svg](schematics/setedetalj.svg) for tegningen; de står
bare ett sted.

De **fremre** føttene står akkurat der vangebiten slutter. Vangebiten skal ikke
stikke ut forbi foten i det hele tatt — den ender på den.

### J11 og J11-F — Benkespile → benkevange og benkespileledd

Én skrue i hver ende, ned i treet under. Forsenk. Dette er en sitteflate.

**Bak (J11) går skruen i den bakre benkevangen som før. Foran (J11-F) går den i
LEDDET, ikke i vangen** — X18 flyttet vangen 36 mm fram, og det er 12 mm av den
igjen under spileenden. Se J8. Leddets overkant ligger i flukt med vangens, så
spilen ligger i ett plan uansett hvilken av de to den er skrudd i; det er bare
skruen som har flyttet seg innover.

### J11-E, J16 og J17 — endespilen og endelisten

De tre leddene helt ute ved veggen. De finnes fordi soveflaten nede skal være
like lang som overkøyen, og fordi den bakre hjørnestolpen står i veien for en
vanlig benkespile der.

**J17 — endelist → bakre hjørnestolpe.** Listen er 36×48 × 98 mm og skrus
**flatt på stolpens forside**, med overkanten i flukt med benkevangens overkant
(297 mm over gulvet). To 5×60 ved siden av hverandre langs listen. Regn på
skruelengden før du bytter den ut: 36 mm går gjennom listen og 24 mm inn i en
stolpe som er 36 mm tykk, så det står 12 mm igjen til baksiden — og baksiden av
den stolpen **er veggflaten**. En 6×80 går tvers igjennom. Dette er det eneste
leddet i sengen som går inn i den bakre stolpens forside; flaten er 98 × 1402 mm
og helt ubrukt ellers.

**J16 — endespile → bakre endelist** og **J11-E — endespile → FREMRE
endelist.** Én 5×60 ned i hver ende, akkurat som J11. Endespilen er 764 mm og
ikke 800: den starter på stolpens forside. Legg den helt inntil naboen —
spalten der skal være null, ikke «omtrent null».

**X18 ga endespilen en fremre endelist også, og den er speilbildet av J17.**
Den bygde benkevangen begynner først ved den fremre stolpens innside, så den
rekker ikke lenger ut under endespilen i det hele tatt — spilens forende hadde
ingenting igjen å ligge på. Den fremre endelisten er samme del som den bakre,
36×48 × 98 mm, skrudd **flatt på den fremre hjørnestolpens bakside** med
overkanten i flukt med benkevangens overkant, to 5×60 (J20). Skruene står 8 mm
under flatens midte, av samme grunn som J17 står 8 mm under sin: J8s to
lommeskruer kommer gjennom den samme stolpen 24 mm fra hverandre, og raden skal
stå midt mellom dem og ikke oppå den ene.

Begge lister henger i sine to skruer, uten kloss under, akkurat som J1, J8 og
J8-B. Lasttallet står i vedlegg A.

### J12 — Bordbærelekt → bakre hjørnestolpe

Lekta går fra stolpe til stolpe og støter mot stolpenes sideflater med endene,
akkurat som den bakre benkevangen. Men den bærer et bord, ikke bare seg selv,
og den skal kunne belastes rett ned uten å hvile på skruer i uttrekk. Slik det
var tegnet fikk hver ende et lite vinkelbeslag å hvile på, med den vannrette
fliken under lektas ende.

**X18: begge beslagene er ute, og leddet er blitt J8-B én etasje opp.** Lekta
har samme profil som den bakre benkevangen, den støter mot den samme flaten på
den samme stolpen, og den nås fra den samme siden — så den får det samme
festet: **to 6×80 skråskruer ut av flatbunnede ⌀18-seter i lektas forside**,
boret med den samme 25°-vinkelklossen, 24 mm fra hverandre i høyden. Ingen ny
vinkel, ingen ny jigg, ingen ny skrue.

*Det beslaget faktisk gjorde, og hva som gjør det nå:* den vannrette fliken var
**hylla lekta hvilte på mens den ble skrudd**. Hullparet er den hylla nå — et
forboret hullbilde passer i én eneste stilling, så lekta kan ikke skli ned mens
du står med drillen. Og lasten: de to skråskruene tar endereaksjonen i skjær,
akkurat som J8-Bs to gjør en meter lenger ned, med den samme utnyttelsen.

Lekta står **på høykant**. Legger du den flatt, ender overkanten 20 mm for
lavt, og platen når ikke det bakre opplegget sitt i bordstilling. Forbor.

Lekta må inn mens bakrammen ligger flat, av samme grunn som benkevangen: den er
kappet til å fylle nøyaktig mellom stolpene.

Lekta er det bakre opplegget for platen i bordstilling, og overkanten skal ligge
i nøyaktig samme høyde som **støttetrinnet** på stigen — trinn 2 på den bygde
stigen (trinn 3 på det gamle arket), overkant 682.
Da ligger platen rett på begge to, uten beslag og uten kile. *(X9 hadde to
bordklosser her i stedet for et trinn; X16 strøk dem — se J4.)*

**X9 flyttet den 140 mm opp, og ingenting annet ved den.** Samme del, samme
lengde, samme ledd — den skrus bare høyere: underkanten
gikk fra 474 til **614** og overkanten fra 542 til **682**, som er bordplatens
nye underside. Det er den lette halvdelen av pulten; den vanskelige sto ved
stigen, og X16 løste den ved å legge et trinn i den høyden i stedet for å henge
klosser under den. **Spikerslagsonen følger med:** sone 3 i veggen ligger nå
på 614–682 over ferdig gulv, altså −386..−318 fra høyderisset. Legger du
spikerslaget etter et gammelt ark, treffer skruene 140 mm for lavt. Sonene står
i [byggesteg](generated/byggesteg.md#før-steg-0--mål-rommet).

**X11 ga lekta et veggfeste også — J12-V, tre skruer inn i stenderne.** Sone 3
lå i veggen for lektas skyld, men fikk aldri en skrue: hele det bakre
opplegget for bordplaten hang i de to endefestene, med 1794 mm
fritt imellom. Nå går tre ⌀8 rett gjennom lekta og inn i veggen, midt i lektas
høyde, og spennvidden blir tre korte i stedet for én lang. Se J12-V nedenfor
for hvorfor det ikke rører noe av det som står over: endene bærer fortsatt seg
selv — nå i lommeskruene sine i stedet for i beslag — skruen ligger vannrett og
tar last i skjær, ikke i uttrekk, og hodene forsenkes i lektas **forside**, så
veggplanet er like flatt som før.

### J13 — Den løse platen

Platen er ikke et løst bord. Den er en liten enhet som **senkes rett ned** i den
stillingen den skal stå i, og løftes rett opp igjen. Alt annet i dette avsnittet
følger av den ene setningen: platen har null vandring i dybderetningen —
bakkanten *er* veggplanet og forkanten står 2 mm fra stigevangene — så den
eneste bevegelsen den har, er loddrett. Det gjelder platen **i setet**. Selve
byttet mellom de to setene er en annen sak, og den står nederst i avsnittet.

Vekten hviler på **tre**, ikke på stål: bakkanten på den bakre benkevangen
(sengestilling) eller på bordbærelekta (bordstilling), forkanten på **trinn 1**
i sengestilling og på **støttetrinnet** i bordstilling. Det er samme profil, samme
hylle og samme ledd i begge stillinger, og etter X16 er de to opplegglinjene
like store til millimeteren: 37 152 mm² totalt begge veier. *(Fra X9 til X15 sto
det to påskrudde bordklosser under forkanten i bordstilling, fordi pulthøyden da
var erklært forbudt for et trinn. Se det strøkne J5-B.)*

**Og regelen om bæreflate står, selv om grunnen til å skrive den om er borte.**
Modellens minstekrav på 5000 mm² gjaldt «per navngitt opplegg» så lenge hver
bærelinje var én del; X9 gjorde forkanten til to klosser, og da ble kravet
skrevet om til å gjelde **per bærelinje** — forkant og bakkant, hver for seg,
uansett hvor mange biter linja består av. X16 gjorde linja til én bit igjen, men
regelen blir stående i den generelle formen: den er riktigere, og den koster
ingenting. Verdien er den samme 5000, ingenting er unntatt, og trinnet gir
320 × 30 = **9600 mm²** der de to klossene ga 5088.

**Og styringen er også tre.** Det står ikke ett vinkelbeslag i denne
mekanismen — den jobben gjør de to lange lektene — og det står ingen lås i den
(vedlegg B, avvik 4). Ikke én ståldel.

**J13a — avstivningslekter, som også er styrelekter.** To 48×68-lekter på
høykant under platen, fra det bakre opplegget og helt fram til platens egen
forkant (750 mm). To ting på én gang:

* **de gjør platen stiv.** Uten dem holder ikke den 18 mm plata når noen setter
  seg på den; med dem er platen to T-bjelker. Se lasttabellen i vedlegg A.
* **de er hele sidestyringen.** De ligger 77 mm inn fra hver sidekant, som er
  nøyaktig **2 mm utenfor trinnenden**. De siste 30 mm av hver lekt står i den
  frie sjakten ved siden av trinnet — 48 mm høy og 32 mm dyp, den biten av
  trinnet som stikker bak stigevangen — så det er 48 × 30 mm tre mot endeved
  som stopper platen sidelengs, ikke en 2 mm stålflik.

**Og i bordstilling er det en trinnende som styrer, i nøyaktig det samme
planet.** Det er hele poenget med X16: samme profil, samme plan, samme passing.
Styrelekta møter 48 × 30 mm endeved mot trinn 1 nede og mot støttetrinnet oppe, med de
samme 2 millimeterne begge steder. *(Fra X9 til X15 sto det to bordklosser her i
stedet — samme ytterflater på X 835 og 1155, men 68 mm høye og med 53 mm omlegg
i dybden. Da var sjakten romsligere oppe enn nede; nå er de like.)*

Trinn 1 og støttetrinnet ender på nøyaktig samme sted i lengderetningen, så det
samme lektparet finner opplegget sitt i **begge** stillinger. De stopper platen
begge veier (den ene mot venstre, den andre mot høyre), og de stopper den i
å vri seg, fordi en vridning drar begge to samme vei — den ene kiler seg
uansett hvilken vei den vris. De 2 millimeterne er ikke slark: det er passingen
som gjør at platen kan senkes ned i det hele tatt.

**J13b — kilelektene under forkanten.** Trinnet er 320 mm langt og platen 574
bred, så 77 mm av forkanten utenfor hver styrelekt har ingenting under seg. To
korte kilelekter i flukt med forkanten bærer det hjørnet innover til
styrelekta.

**Hvorfor de finnes, og det er uendret:** dette er hjørnet et barn kneler på når
det klatrer opp fra benken, og det blir **ikke** bedre av at lektene flyttes
nærmere. En punktlast på et fritt platehjørne gir σ = 6P/t² = 18,5 MPa i 18 mm
plate uansett hvor nær nærmeste lekt står. Bare tre under hjørnet hjelper. Se
vedlegg A.

**Men de er kiler nå, ikke klosser.** Hver vinge er full 68 mm dyp ved **roten**,
der den støter mot styrelekta, og skråkappet i ett rett sagsnitt ned til **27 mm**
ved **spissen**, ute på platens egen ytterkant. Det lave ytterhjørnet — hele det
du så nedenfra — er borte, og det som står igjen følger momentet: en utkraging
har momentet sitt ved roten og ingenting ved spissen.

**Og kilen har TO skruer, ikke tre.** Det er K2 som gjorde det nødvendig, og
det er verdt å skjønne hvorfor, for det er ikke skruen som er problemet — det er
hullet den sitter i. Passer-på-flaten-regelen (`(n−1)·4d + 2·3d`) måler
**skaftet**: tre 5 mm skruer trenger 20 mm mellom seg og får plass på 77 mm. Men
hver av dem sitter i bunnen av et **⌀12 kontrabor**, og tre 12 mm hull med 20 mm
senteravstand står igjen med 8 mm tre imellom. På vingen slik den var før K2
(var 116 mm lang) kom det aldri opp, fordi raden hadde 35,5 mm å spre seg på; på 77 mm faller den ned
på 4d-minimum og hullene møtes nesten. To skruer åpner den til 32 mm — 20 mm
tre — og lastsiden merker det ikke: oppskruene er tvinger for en limfuge, og
hele gruppa lå under 0,05. Modellen asserter det nå: **et kontrabor har sin egen
senteravstand, 24 mm, uavhengig av hva skaftet trenger.**

**27 er ikke et tall noen likte.** Det er oppskruens eget sete. Hver J13-skrue
har hodet 27 mm under platens underside — det er nøyaktig det «⌀12 kontrabor
41 mm opp i en 68 mm lekt» betyr — så vingen må være minst så dyp overalt der en
skrue går gjennom den. På akkurat 27 er kontraboret gått i null, og hodet ligger
i flukt med kilens egen underside. Boreregelen er derfor **den samme for alle
fire delene** og leses slik: *bor ⌀12 opp til det står 27 mm igjen.* I styrelekta
er det de 41 millimeterne; i kilen er det 29 og 12 mm ved de to hullene,
dypest ved roten.

**Tallene.** Kilen er 175 560 mm³ mot 251 328 for den hele klossen — 30 % mindre
tre, og hele det lave ytterhjørnet vekk. Det verste bøyesnittet er **ikke**
roten: når h(x) smalner mot spissen, topper σ seg 51 mm fra spissen, der
h = 54 mm — nøyaktig to ganger spisshøyden. Der er den 2,17 MPa mot
f<sub>m,d</sub> = 16,6 for C24, altså utnyttelse **0,13**; roten selv ligger på
2,08 MPa og 0,13. Skjæret sitter i den
andre enden: i 27 mm-spissen er τ = 1,73 MPa mot f<sub>v,d</sub> = 2,77 (med
sprekkfaktoren k<sub>cr</sub> = 0,67), altså **0,62**. Det er det høyeste tallet på delen, og det er det tallet som sier at
spissen ikke skal bli tynnere. *K2 gjorde kilen kortere (116 → 77 mm) da platen
ble smalere, og bøyningen falt med den; skjæret i spissen er uendret, og det er
fortsatt det som styrer.*

*Den elegante løsningen tapte på et tall:* **18 mm kryssfinér-doblere** limt
under hvert forkanthjørne — ingenting som henger ned, usynlig, og
innsettingsveien merker dem ikke engang. Med **fullt samvirke** over limfugen er
det en 36 mm laminat: 6·1000/36² = 4,63 MPa, utnyttelse 0,67. Den går. **Uten
samvirke** deler de to 18 mm platene lasten hver for seg: 6·500/18² = 9,26 MPa,
utnyttelse **1,33**. Den stryker. Limfugen selv er ikke problemet — den ligger i
nøytralaksen, der langsgående skjær er størst, og der er τ = 1,5·1000/(77·36) =
0,54 MPa. Det er under D3-limet med god margin, men bare så vidt under finérens
egen rullskjær (~0,6–0,8 MPa design) — kortere dobler, samme last, høyere skjær;
K2 gjorde den avviste løsningen dårligere, ikke bedre. Det som avgjør er at **ingenting kan sikre den limfugen**. Hver eneste
andre limte fuge i denne platen har skruer som klemmer; her finnes det ingen
skrue som passer. 18 mm dobler under 18 mm plate er 36 mm materiale, og den
korteste skruen i denne sengen er en 5×40 — 4 mm av den ville kommet ut gjennom
platens overside, den ene flaten som aldri skal brytes — og et kontrabor får ikke
plass i 18 mm og fortsatt la det stå kjøtt igjen. Doblerne ville altså vært lim
alene, med 1,33 som nedre grense. En detalj hvis fallback er 1,33 går ikke under
et barns kne.

*Slankere lekter, 48×48, ble veid og lagt bort:* utnyttelsen blir 0,37, som er
helt greit. Men 48×48 er en profil sengen brukte to revisjoner (W3 og U5) på å
bli kvitt, og hvert eneste kutt i denne sengen er 90° på kappsag. Et kløyvkutt
for to 77 mm biter er ikke verdt en foreldreløs profil.

**Ingen skruer i bordplata.** Platen er bordplate halve livet, og seksten
skruehoder — eller seksten propper — midt i den er seksten merker. Lektene **limes**
(D3) og skrus **nedenfra**: ⌀12 kontrabor 41 mm opp i lektas underside, så en
5×40 gjennom de siste 27 mm av lekta og 13 mm inn i den 18 mm plata, med 5 mm
plate igjen over spissen. Kontraboret er ikke pynt — det er den eneste måten å
sikte gjengelengden på: rett gjennom 68 mm lekt ville en 5×80 tatt 12 mm og en
5×90 alle atten. De 41 millimeterne er den samme regelen som gjelder i
kilene, bare i tykkere tre: bor opp til det står 27 mm igjen. Se J13b.

I bruk står fugen uansett i trykk: platen *hviler* på lektas overkant, så
2 kN-lasten går aldri gjennom et festemiddel. Skruene har én lastsituasjon —
at enheten løftes etter et hjørne — og der er 62 N egenvekt (6,3 kg,
regnet av kroppene) mot 16 skruer.

*De to alternativene, og hvorfor de tapte:* skråskruer gjennom lektas side
treffer bare 18/cos30 = 21 mm plate før spissen bryter ut i overflaten. Hodet
kunne fått et flatbunnet sete, slik J8-B og J10 nå får, men et sete gjør
ingenting med de 21 millimeterne. Proppede topskruer er det
klassiske svaret og nesten usynlig i massiv furu — men denne plata er
**kryssfiner**, og en propp i et finérdekke er en skive endeved i en ubrutt
flate.

*Og her har K2 tatt fra oss et argument uten å gi oss et nytt.* Fram til v12 var
platen 652 mm bred — bredere enn de 600 mm limtre furu stopper på i hylla — og
kryssfiner var rett og slett det eneste som fantes i den bredden. 574 går inn i
en 600 mm limtreplate. Materialet står likevel: lasttabellen, uttrekket for
oppskruene og propp-argumentet over er alle regnet på kryssfiner, og et
materialvalg tas ikke om i en komfortrunde. Men det er et **valg** nå, ikke en
tvang, og det er ført opp som åpent punkt i innkjøpslista i stedet for å bli
stilltiende stående på en begrunnelse som er utløpt.

**Det som IKKE er låst: platen kan løftes rett opp.** Det er meningen — det er
slik den skifter stilling. **Valget er tatt, og det er ingen lås.** Begrunnelsen
står i vedlegg B, avvik 4, og den skal leses før noen bygger dette.

Treverket en lås ville tatt tak i, står der det sto: **tre mot tre** —
kilelektas endeved mot enden av den fremre benkevangen, tvers over de 63 mm i
sideklaringen. De to flatene ligger side om side i sengestilling og i samme
høydebånd; i bordstilling står kilelekta **385 mm** høyere — X9 tok løftet
mellom de to setene fra 245 til 385 — så en lås ville ikke hatt noe å ta i.
Den kan altså ikke stå på i feil stilling, og det følger av
geometrien og ikke av en instruks. Alle tre alternativene i
`docs/preview/laasvalg.png` virker over nettopp de 63 millimeterne og passer det
treet uendret, så dette er et **ettermonteringspunkt**: skulle låsen komme, er
det en skrue som dukker opp, ikke en trebit som endres. Det arket er historikk,
ikke en bestilling — det lages for hånd med `mise run mekanisme` og er ikke med
i byggeporten.

**Innsettingsveien er målt, ikke antatt.** Modellen sveiper hele enheten — plate,
to styrelekter, to kiler og seksten skruer — rett opp fra begge seter og krever at
ingenting treffer noe: **126 mm** fri vei i sengestilling og **214 mm** i
bordstilling. Det skal **68 mm** til for å løfte styrelektenes underkant fri av
låsedelens overkant, så det er **1,85 ganger** så mye vei nede og **3,15 ganger**
oppe. Taket er **trinn 2** i sengestilling og **trinn 4** i bordstilling —
begge deler er tre som *må* være der.

**X16 snudde hvilken av de to som er den trange.** Under X9 lå bordstillingen
nøyaktig på grensen (100) og sengestillingen romslig; nå er det motsatt.
Grunnen er den samme i begge ender: taket over bordsetet er ikke lenger trinnet
som *bar* platen, men trinnet **over** det — trinn 4 på 962, underkant 914 — så
løftet i bordstilling ble mer enn dobbelt så høyt. Og i sengestilling kom trinn 2
ned fra 572 til 489 med resten av det nedre løpet, så taket der falt tilsvarende.
Begge ligger godt over kravet.

*De 68 er ikke de 48 lekta lapper.* Fram til X10 sto det 48 her, og det er
lengden på **omfaret** — hvor mye av trinnenden styrelekta
ligger utenpå i høyden. Løftet som skal til for å komme fri av den er noe annet:
låsedelens overkant *er* platens egen underside, så lekta må opp hele sin egen
høyde, 68 mm. To forskjellige mål på samme sted, og modellen holder dem fra
hverandre nå. Med det gamle tallet spurte innsettingsprøven etter 2 × 48 = 96 mm
mot en bordstilling som da lå på 100 — riktig svar på feil spørsmål, og
[X10: 4 mm] fra å stryke på et tall som aldri var tallet.

**De 100 er kravet, og etter X16 er begge stillinger godt over det.** Modellen
har hele tiden krevd 100 mm rett løft i begge seter. Under X9 lå bordstillingen
**nøyaktig** på grensen — platetoppen på 700 og trinnet over støttetrinnet med underkant på 800 — fordi
det trinnet var lokket over platen og bare var løftet akkurat så mye at 700 gikk
opp. X16 la et trinn under platen i stedet, og da ble lokket trinn 4: taket over
en plate i bordstilling gikk fra 700 til **814**, og løftet fra 100 til 214.
Kravet er ikke slakket i noen ende; det er delen under platen som er byttet ut.
(Fram til X9 var tallene 159 og 179, med bordbærelekta som tak i
sengestilling; fram til K1 var det en stigekloss i begge tilfeller, med 109 og
124 mm — de klossene var 37 mm for lange og hang inn i veien uten å gjøre noen
nytte. Se K1, X9 og X16 i modellen.)

**Men stillingsbyttet er ikke ett langt loddrett løft — og det er verdt å lese
før du prøver.** De to fri veiene over gjelder *setet*: hvordan platen kommer
ned i det og opp av det. Selve byttet mellom de to setene må utenom stigen, for
over sengesetet er det stigen som er taket. Veien er målt på solidene, ramme for
ramme (`mise run film-mekanisme`), og filmen under **er** den prøven — ikke en
tegning av den:

0. **Ta av alle fire putene først.** Dette er ikke ryddighet: enheten bæres
   sidelengs i sjakten mellom benkespilenes overkant (320) og trinn 2s
   underside (441), og den sjakten er 121 mm høy for en enhet på 86. En 100 mm
   pute som ligger på benken har overflaten sin på **420** — 21 mm under
   sjaktens eget tak — så med putene på er det ikke plass til enheten i det hele
   tatt. Ombyggingen er fysisk sperret. *(X16 tok trinn 2 ned fra 572 til 489, så
   dette er blitt trangere: sjakten var 204 mm.)*
1. **Løft rett opp**, ca. 15 cm, til enheten står midt i overføringssjakten.
2. **Skyv platen sidelengs** inn over benken, til den er klar av stigen —
   **vannrett hele veien**. Sjakten mellom benkespilenes overkant (320) og
   trinn 2s underside (441) er 121 mm høy og enheten er 86: det står **35 mm**
   klaring i alt, delt likt over og under den under hele bæringen, mot et krav
   på 15. Dette er den trangeste av de to bæringene nå. (Før X9 var sjakten 154 mm, med taket
   i bordbærelekta på 474; lekta gikk opp med bordplaten, og det som er igjen
   som tak er trinn 2.)
3. **Trekk den litt fram**, så bakkanten står av bordbærelekta.
4. **Løft den opp** forbi bordbærelekta og opp i kryssebåndet — ute over benken
   er banen fri.
5. **Skyv den inn igjen** til bakkanten står over setelinjen.
6. **Skyv den sidelengs tilbake** over stigen, nå i båndet mellom
   støttetrinnets overkant (682) og trinn 4s underside (914).
7. **Senk den ned** i bordsetet.

Veien tilbake er den samme baklengs.

**Etappe 3 og 5 ser ut som fikling, og er det ikke.** Bordbærelekta går tvers
gjennom hele sengen på Y −48…0, altså akkurat der platens bakkant ligger, så
bakkanten *må* av linja dens før den kan gå opp — uansett hvor i lengden du
står. Alt det andre er ett løft, én bæring bort, én bæring tilbake og én
nedsenking.

**Etappe 6 er den X9 måtte betale for, og X16 fikk pengene igjen.** Enheten må
gå **over** sitt eget fremre opplegg på veien tilbake — det gjelder uansett hva
opplegget er laget av. Båndet er 682 (støttetrinnets overkant) til **914**
(trinn 4s underkant) = **232 mm**, enheten er 86, og det står **146 mm**
klaring igjen mot et krav på 15. *X9 hadde 32 mm her, over bordklossene, fordi
lokket den gang var det samme trinnet som sto rett over dem.* Det er dette
båndet X8 regnet til å være 29 mm for lite, med trinn 3 der det da sto.

*Slik var det ikke før.* Fram til K1 var sjakten 91 mm høy for en 91 mm høy
enhet — null klaring — og den eneste veien gjennom var å **vippe** den ene
langsiden tre grader opp og holde vippen gjennom hele bæringen, over en benk,
over hodehøyde. Det var ni grep og et to-personers løft. De 37 millimeterne som
ble kappet av hver stigekloss er hele forskjellen.

Den trangeste passeringen på hele veien er **2 mm** — nøyaktig den passingen
platen er tegnet med, mot stigevangen. Og platen kommer aldri *ut* av sengen:
den er bredere enn åpningene ved siden av stigen, så den blir i underetasjen
hele veien. Skal den helt ut, må den ut på høykant gjennom fronten.

![Platen fra sengesete til bordsete](img/hanna-mekanisme.gif)

*Stillingsbyttet, sju etapper, flatt. Ingen ramme i filmen har tre inne i tre —
det er en assert, ikke en påstand: `tools/render_animasjon.py` legger hver
stilling gjennom en separerende-akse-prøve mot hver eneste faste del i sengen og
nekter å lage filmen hvis noe kolliderer.*

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

### J12-V — Veggfeste gjennom bordbærelekta

Det andre veggfestet, og det er den samme skruen og den samme jobben en meter
lenger ned: **tre stykker gjennom bordbærelekta og inn i stenderne**, midt i
lektas høyde, 648 mm over ferdig gulv. Lekta ligger flatt mot veggen i hele
sin lengde akkurat som sidevangen gjør, så det trengs verken brakett eller
kloss her heller.

Fire innvendinger var verdt å svare på før leddet ble lagt, og ingen av dem
holdt:

* *«Lekta skal kunne belastes rett ned uten å hvile på skruer i uttrekk»* —
  det står fortsatt, og etter X18 er det lommeskruene i endene som svarer for
  det: de ligger på skrå og tar endereaksjonen i **skjær**, ikke i uttrekk.
  Denne skruen ligger **vannrett**, så en last rett ned tar den i skjær også.
* *«Veggplanet skal være helt flatt»* — regelen gjelder alt som stikker ut
  **bak** Y −48. En skrue som drives fra rommet, med hodet forsenket i lektas
  forside, legger ingenting til baksiden. Det er samme geometri som J14 alt
  har, og etter X18 står det ikke lenger noe beslag på den flaten heller.
* *«Lekta må inn mens bakrammen ligger flat»* — den gjør fortsatt det, i steg
  1. **Disse hullene kan ikke bores i verkstedet**: stenderne finnes bare i
  rommet. De bores i steg 2, etter at rammen er reist inntil veggen, samtidig
  med J14.
* *«Senga er referansen, ikke rommet»* — bakrammen er ett stivt lag, og J14
  har allerede dratt hele det laget inntil veggen før disse skruene finnes.
  De bestemmer ikke hvor lekta står; de tar bare last ut av midten av et
  spenn på 1894 mm som ikke hadde noe der.

Forsenk hodene under lektas forside. Det er den flaten ryggputa lener seg mot.

### J15 — Filtknotter

Under alle fire hjørnestolper og alle fire stubbeføtter. Slå dem i før du reiser
noe.

**Ikke under fotbrettet.** Den står på to sammenhengende striper, 36 × 272 mm
hver, og ikke på fire punkter — en ⌀40 tapp under en 36 mm stripe ville gjort
en stødig krakk til en vippe. Den veier 3,1 kg (3,3 med levert virke) og løftes med én hånd;
den dras ikke.

### J18 — Fotbrettbord → gavl (X14)

Åtte 6×80, én per landing: fire bord ganger to gavler. Skruen går rett ned
gjennom 48 mm dekkbord og står 32 mm inn i en 98 mm gavl, midt i gavlens 36 mm
— som er nøyaktig 2 × 3d over skruen, og grunnen til at gavlen er et 36-bord og
ikke et 23. Én skrue per landing er hele regelen: to landinger låser bordet mot
å dreie, og fire bord låser de to gavlene mot å rase. Ingenting i denne krakken
kan bevege seg uten å ta en skrue i skjær.

Forsenk hodene **under** flaten. Dette er den ene flaten i hele sengen som bare
føtter står på.

Krakken skrus ikke til sengen, og det er ikke en forglemmelse: F1 har målt at
det ikke finnes fast tre i denne bukta å skru den til, og en fast fotstøtte her
ville stått i det åpne gulvet mellom benkene. Se 8.2b.

---

## 5. Madrass og puter

Mål på madrass og puter: [nøkkelmål](generated/nokkelmal.md#madrass-og-puter).

### Overkøyen

**Sengen er dimensjonert rundt en standard madrass på 80 × 200 cm.** Det er
ikke et spesialmål, og madrassen skal ikke bestilles etter sengen — det er
sengen som er bygd etter madrassen. Rommet er noen millimeter smalere enn
200 cm, så madrassen presses de siste millimeterne inn mellom veggene. Det er
meningen: da ligger den i ro.

**Tykkelsen er 120 mm, og vinduet er 105–130.** Dette er ikke en smakssak, og
det er den ene grensen i sengen som er lett å bryte uten å vite det. Spalten
mellom madrassens overside og undersiden av det nederste rekkverksbordet skal
enten være **lukket** — under 25 mm — eller ligge i EN 747-båndet **60–75 mm**.
På den bygde sengen ligger bordet lavt, så det er den lukkede grenen som
gjelder:

* **For tynn** madrass åpner spalten seg opp i klemvinduet 25–60 mm — det gapet
  et lem kiler seg fast i i stedet for å gå igjennom.
* **For tykk** madrass står over bordets underkant, og bordet dekker ikke
  lenger madrasskanten — det ligger begravet i den.

**En vanlig 150 mm madrass er ulovlig i denne sengen.** Kjøp 12 cm; da ligger
bordet 10 mm over madrassen og dekker forkanten. Hele resonnementet og den
andre, tynne grenen står i avsnitt 7.3 og vedlegg B.

Tallene regnes ut av modellen av de to faste høydene — spilebunnen og
rekkverket — og står i [nøkkelmålene](generated/nokkelmal.md#madrass-og-puter).
**Maksmålet skal merkes permanent på sengen** (steg 11); EN 747 krever det, og
den som bytter madrass om ti år skal kunne lese grensen av sengen selv.

### Underetasjen — fire puter

Underetasjen er sofa, bord og ekstraseng i én, og **putene ER madrassen
nede**. Det er hele ideen bak nivået: det du sitter på om dagen er det du
sover på om natten, og de fire putene er derfor ikke fire løse gjenstander —
de er én seng, delt i fire.

**Soveflaten nede er 1990 × 800 mm — samme lengde som overkøyen.** Det ble den
i denne runden. Benkespilefeltet stoppet 98 mm fra veggen i hver ende, fordi en
vanlig benkespile går fra veggplanet og fram og ville skåret tvers gjennom den
bakre hjørnestolpen. Nå ligger det en kortere **endespile** der, 764 mm, som
starter på stolpens forside og hviler på en **endelist** skrudd flatt på den
samme stolpen. Listen settes i steg 5 sammen med resten av benkens bæreverk,
spilen i steg 7. Se J16/J17. Uten den er ikke dette en seng i full
lengde, og putekanten har ingenting under seg.

**Stolpen står i flaten.** Det er den ene tingen som ikke lot seg fjerne: de to
bakre hjørnestolpene tar et hjørne på 98 × 36 mm inne i soveflaten, helt ute ved
veggen i hver ende. Derfor skjæres et **hakk på 98 × 36 mm** i veggkanten på
hver av de to benkeputene. Brødkniv, ett minutt.

### Målene — dette er det du bestiller skum etter

| | Mål | Ant. |
|---|---|---:|
| **Benkepute** | **663 × 800 × 100 mm**, med hakk 98 × 36 mm i veggkanten | 2 |
| **Ryggpute** | **332 × 800 × 100 mm**, rent rektangel | 2 |

**Regnestykket er asserten.** Benkeputen er 1/3 av lengden og ryggputen 1/6, og
lagt etter hverandre dekker de fire nøyaktig hele flaten:

> 663 + 332 + 332 + 663 = **1990 mm**

1990 deler seg ikke på seks. Tredelen er derfor rundet ned og sjettedelen opp —
0,33 mm hver vei — og summen er eksakt. Det er summen som må stemme; ingen
kapper en tredels millimeter skum. Modellen sjekker dekningen som areal, ikke
som påstand: de fire puteflatene skal legge seg over soveflaten uten overlapp og
uten hull, ellers stopper `mise run build`.

**Alle fire er 100 mm tykke.** Lik tykkelse er ikke en forenkling, det er
kravet: fire like tykke puter er én flat seng, fire ulike er en seng med trinn i.
Valget av nettopp 100 mm står på fire tall:

* **Én skumplate dekker alt.** 80 × 200 cm er 800 × 2000 mm — 800 er nøyaktig
  flatens dybde og 2000 er 10 mm mer enn lengden. Fire tverrkapp, og du er
  ferdig. Det gjelder like godt for en billig skummadrass 80 × 200 som for en
  plate fra en skumforretning.
* **Sittehøyden** blir 320 + 100 = **420 mm**. Det er en voksen stolhøyde.
* **Bordplaten** ligger 280 mm over seteputen, undersiden 262 mm — et sittende
  kne står 135 mm over setet, så knærne går inn under platen med 127 mm luft.
  Går du til 120 mm skum blir de 260 og 242, og knærne går fortsatt inn. Dette
  var det strengeste av de fire tallene til og med v15, da platen lå 140 og 122
  over setet og bare et strakt lår kom under: 120 mm skum ville gjort de
  122 til 102 og stengt den. **X9 løste den bindingen** ved å flytte platen i
  stedet for puten, og skumtykkelsen står nå på de tre andre grunnene alene.
* **Hodehøyden** over soveflaten nede er 1080 mm opp til køyespilene (982 under
  sidevangene). Det er god sitte-opp-høyde for et barn.

120 mm skum finnes i samme handel og ville også virket — det er mykere å sitte
på, og det tar 20 mm av knerommet under pulten uten å stenge det. Da må **alle
fire** være 120.

### Midtsonen ligger 5 mm lavere, og putene er like tykke likevel

Platen i midten ligger 5 mm under benkeflaten (315 mot 320). Den gamle regelen
var at midtputen skulle være de 5 millimeterne tykkere. Den regelen er ute, av
to grunner: alle fire skal være like tykke, og **ingen puteskjøt ligger lenger
på en sonegrense** — skjøtene faller på 663 og 1327, mens sonene skifter på 645
og 1345. De 5 millimeterne tas av skummet, som er akkurat det V6 kappet
forsenkningen fra 18 til 5 for.

**Midtsonen er 700 mm bred, men platen er 574.** Etter K2 står det en **63 mm
åpen stripe** langs hver side av platen, hele 798 mm fra veggen og fram til
stigen. Den bygges nå ut av putene som ligger over den — benkeputen henger 18 mm
utenfor benkeenden og ryggputen tar resten. Skum bygger 63 mm ut uten videre:
sengens egen spilebunn over ligger på 44,5 mm mellom spilene, og benkene på
14,25. Stripene er der med hensikt: 63 mm ligger i EN 747-båndet 60–75 mm, der
hele lemmet går fritt, og de er prisen for at platen skal kunne senkes ned i
bordstillingen uten å treffe blindt. Se tabellen over lovlige platebredder i
[nøkkelmål](generated/nokkelmal.md#platebredden-er-kvantisert--lovlige-vinduer).

### Under benken er det et rom, og nå er det målt

Stubbeføttene bærer benkevangene på fire punkter i stedet for på en sokkel, og
det de lar bli igjen er et **kasserom under hver benk**: **229 mm høyt × 479
mm bredt × 800 mm dypt** — gulv til benkevangens underkant, bakre
hjørnestolpes innerside til stubbefotens ytterside, og vegg til fremre
benkevanges forside. Dybden er benkespilens egen lengde, for kassa skyves inn
**under** vangen og ikke forbi den. To slike rom, ett under hver benk; mellom
dem er gulvet åpent foran stigen, og der skal det ikke stå noe (D13). Både
rommet og innkjøringen foran det er målt tomme på solidene.

Høyden er et **minstemål**: rammen bygges i vater fra høyderisset over gulvets
høyeste punkt, så 229 mm er høyden akkurat der og mer overalt ellers. Tallene
står i [nøkkelmål](generated/nokkelmal.md#kasserommet-under-benkene).

### Hvor de ligger — og hvor de står

**Sengestilling:** alle fire flatt, etter hverandre. Benkepute, ryggpute,
ryggpute, benkepute, fra vegg til vegg.

**Sofastilling:** de to benkeputene ligger **nøyaktig der de lå** — de flyttes
aldri. De to ryggputene reises på høykant ytterst på hver benk, oppå seteputen,
med den 800 mm lange kanten inn i dybden: 100 mm tykke, 800 mm dype, 332 mm
høye, topp 752 mm over gulvet. Ombygging er altså **to puter, ikke fire**.

Ryggputen står der den står fordi det er det eneste stedet den får plass.
Ryggen mot bakveggen — det opplagte — går ikke: puten er 800 mm i sin andre
retning, og bak benken er det bare 645 mm vegg før gangbukta begynner, og fra
X 708 står bordplaten i veien. Stilt på høykant blir den 800 mm høy og rekker
til Z 1220 — det er ikke en sofarygg. Det ene stedet 800 mm står oppreist her, er
**på tvers av benken**, altså i enden — og da er svaret på hva denne sofaen er
også gitt: to seter som vender inn mot en pult, med ryggen i hver sin ende.
Benken er 800 mm dyp, ryggen er 800 mm bred, og det er plass til to i bredden.

To ting holder den: **bordbærelekta**, som går langs hele bakveggen på Z
**614–682** og som ryggputen lener seg mot over 100 × 68 mm, og hjørnestolpens
innerflate sideveis. X9 flyttet lekta 140 mm opp med bordplaten, og kontakten
flyttet seg oppover ryggen med den: den tok før i korsryggen, 54–122 mm over
setet, og tar nå midt på ryggen, 194–262. Det er de samme 68 millimeterne med
anlegg og de samme 100 × 68 mm kontaktflate — bare høyere oppe på ryggen.

Puten står derfor 48 mm fram fra veggplanet, og forkanten
lander 12 mm utenfor sengens forkant. Det er en løs skumpute i én stilling, ikke
sengens dybde — sengen er 836 mm dyp som før.

### Putene av FØR du bygger om

Plateenheten bæres **sidelengs inn over benken** i sjakten mellom benkespilenes
overkant (320) og trinn 2s underside (441) — **121 mm** — og enheten er 86 mm
høy, så det er 35 mm klaring å fordele over og under den. En 100 mm pute som
ligger på benken har overflaten på **420**, altså bare 21 mm under sjaktens eget
tak: da er det ikke plass til enheten i det hele tatt. Ombyggingen er fysisk
sperret med putene på, og modellen regner det ut selv. Første steg i begge
retninger: **ta av alle fire putene.**

*Sjakten var 154 mm til og med v15, med taket i bordbærelektas underside på
474. X9 tok lekta med opp i pulthøyde, og da ble trinn 2 taket — 204 mm. X16
tok hele det nedre løpet ned, trinn 2 med det, og sjakten er blitt den
trangeste passeringen i hele ombyggingen. 35 mm mot et krav på 15 er fortsatt
god margin, men den tåler ikke en pute.*

### Å skaffe skummet

| | Hva | Ca. pris | Merknad |
|---|---|---|---|
| **a** | Skummadrass 80 × 200 × 10 fra en møbelkjede, deles i fire | ≈ 450 kr | Klart billigst, og målet passer på millimeteren. Fastheten er i tynneste laget som sitteunderlag — legg en fastere topper på de to benkeputene |
| **b** | Industrisøm, skumplate 10 cm kvalitet 35P, 80 × 200, kappes til | ≈ 2 200 kr | Fastest og mest «møbelaktig». Du kapper selv, eller får det kappet |
| **c** | Kaldskum 39K, eller mål-tilpasset fra maaho.com | ≈ 4 300 kr | Dyrest, men du får riktig mål og riktig fasthet levert, uten å kappe |

**Alle tre trenger trekk.** Skum uten trekk smuldrer og blir skittent. Regn med
trekk som en egen post uansett hvilken vei du går — fem trekk, ett til
madrassen og fire til putene.

**Skjøt putene til hverandre** med borrelås eller trykknapper i trekkene. Ellers
sklir de fra hverandre den første natta noen sover der.

---

## 6. Notater til butikkturen

* **Hovedbordet må bestilles.** Ring før du drar. Det aller meste av sengen er
  det samme bordet, og butikken har sjelden nok av det på lager. Får du bare
  nærmeste nabo-dimensjon, er det mulig — men da er det én konstant i
  `generate_loftbed.py` som endres, og hele modellen må kjøres på nytt og
  kapplista regnes om. Ikke improviser på sagbenken.
* **Spilene er 23×98, ikke 36×98.** En spile ligger flatt, så tykkelsen er
  bæreretningen — og etter at spilekriteriet ble regnet på det en spile faktisk
  bærer (vedlegg A), er 23 mm nok med god margin. De 26 spilene er godt over en
  tredel av alle trebitene i sengen — 14 køyespiler og 10 benkespiler à 800 mm
  pluss de to endespilene à 764 — så valget tar 20,7 løpemeter ned fra det dyre bordet
  til det billige, sparer rundt 11 kg og gjør spilebunnen 13 mm lavere. **Og
  X18 la åtte biter til på det samme bordet:** rekkverkets avstivere er 180 mm
  av det samme virket, kappet av restene. 23×98
  justert er en hyllevare. Rekkverk, stolper og vanger står igjen på 36×98 og
  48×98 — de er belastet på høykant, og der er tykkelsen verdt å betale for.
* **Hovedbordet finnes bare i 4,8 m.** 36×98 C24 selges som fast lengde bare
  på 4800 mm; 4200 og 3600 finnes ikke i denne dimensjonen. Kappeplanen i
  innkjøpslista er lagt på 4,8 m-bord alene.
* **Kjøp alt konstruksjonsvirke som C24.** Det gjelder også lektdimensjonene
  36×48 og 48×68, som mange steder står i hylla bare som «klasse 1 lekt/rekke
  — ikke-bærende». Spør i skranken: stigevangene og stigeklossene (36×48),
  rungetrinnene og stubbeføttene (48×68) er alle bærende, og
  lasttabellen i vedlegg A regner C24.
* **36×48 er to bord etter X18.** Det var ett, og det holdt akkurat — to
  stigevanger, ti stigeklosser og to endelister med 68 mm til overs. X18 gjorde
  tre ting med den bunken: stigen mistet ett trinn og dermed to klosser,
  stigevangene ble 166 mm kortere hver, men benken fikk **to benkespileledd på
  547 mm og to fremre endelister** — og de to leddene alene er mer enn resten
  av bordet. Kapp de to vangene og de to leddene først; klossene og listene tar
  hva som helst av det som blir igjen.
  *(X9 la de to bordklossene på denne dimensjonen og skjøv fire stigeklosser
  over på et bord nummer to; X10 flyttet klossene til 48×68, og X16 strøk dem
  helt. Svinnet har vært innom 49 % på veien.)*
  Se [innkjøpslista](generated/innkjopsliste.md).
* **Platen kappes av 18 mm kryssfiner.** Etter K2 er den 574 mm bred og ville
  gått inn i en 600 mm limtreplate — men lasttabellen, uttrekket for
  oppskruene og propp-argumentet i J13 er alle regnet på kryssfiner, så
  materialet står. Det er et valg nå, ikke en tvang; se innkjøpslista.
* **Vil du kunne bygge om til frittstående seng senere?** Da trenger du to
  rekkverksbord til på baksiden og to bakre stolper i full høyde. Kjøp dem gjerne
  nå, og — viktigst — **forbor de bakre stolpene for rekkverket mens de ligger på
  bukken**. Resten av sengen er uendret; det er bare de fire delene.
* Kjøp litt ekstra av alle skruestørrelsene. De koster ingenting, og en tur
  tilbake koster en kveld.

---

## 7. Sikkerhet

Kravene er fra **EN 747-1:2024 og EN 747-2:2024** (køyesenger og loftsenger). Tallene sengen faktisk
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

**7.3 Madrasstykkelsen skal være 105–130 mm, og 120 er anbefalt.** Dette er den
viktigste tallgrensen i hele sengen, og den er ikke et tak — den er et **bånd**.
Åpningen mellom madrassens overflate og undersiden av det nederste
rekkverksbordet skal enten være **lukket**, altså under 25 mm, der ingenting
kan komme inn — eller ligge i **60–75 mm**, der hele lemmet går fritt
igjennom. Alt imellom, **25–60 mm**, er nettopp det gapet et lem kiler seg fast
i i stedet for å gå igjennom.

Madrassen er det eneste som styrer den åpningen. På den **bygde** sengen står
nederste bords underkant 130 mm over spilene, og da ser tabellen slik ut:

| Madrass | Åpning | Dom |
|---:|---:|---|
| 100 mm og under | 30 mm og mer | ✗ **FORBUDT** — klemvinduet |
| 105 mm | 25 mm | lovlig, **nøyaktig på grensen** — ingen margin |
| **120 mm** | **10 mm** | ✓ **anbefalt** — bordet ligger like over madrassen og dekker forkanten |
| 130 mm | 0 mm | lovlig, madrassen rekker akkurat opp i bordet |
| 140 mm og over | — | ✗ **FORBUDT** — madrassen står inne i selve rekkverksbordet, som da ikke dekker kanten lenger, det ligger begravet i den |

**Kjøp 12 cm.** En helt vanlig 15 cm madrass er *ulovlig* i denne sengen. Det er
ikke opplagt, og det er grunnen til at maksmålet skal merkes permanent på
sengen (steg 11) — linja 1653 mm over gulvet, som er nederste bords underkant
og altså en strek du kan se.

**7.3b HVORFOR TABELLEN SER ANNERLEDES UT ENN PÅ TEGNINGEN.** Tegningen hadde
nederste bord 185 mm over spilene, altså 65 mm over en 120 mm madrass, og da
var vinduet 110–125 mm og åpningen lå i 60–75-båndet: *luft* under bordet.
Byggherren satte bordet lavere, og da bytter regelen gren — åpningen er
**lukket** i stedet for klar. Begge er lovlige svar på det samme kravet, og den
bygde er den strammere av dem: 10 mm der tegningen hadde 65.

*(En tidligere runde leste byggherrens 130 mm fra madrasstoppen i stedet for
fra spilene, fikk 130 mm åpning ut av det og skrev det opp som sengens ene
ulovlige mål — vedlegg B, avvik 6, med krav om en mye tykkere madrass [var 175–190 mm]. Det var
en feillesning av datumet, ikke av tommestokken. Avviket er lukket.)*

**7.4 Ikke sett hele vekten på én bar spile.** Å gå på bar spilebunn er greit —
en fotsåle rekker alltid over minst to spiler, og det er den lasten spilen er
regnet for. Det som ikke er greit, er å hoppe, eller å sette hele vekten på én
spile midt i spennet, uten madrass over. Legg madrassen på før noen går opp; da
er spørsmålet uansett ute av bildet.

**7.5 Den løse platen skal alltid ligge i.** Den står som en stiver mellom
veggen og stigevangene: med platen i kan ikke stigefoten gå bakover. Skal du ha
den ut, ta stigen med i vurderingen — og ikke la noen klatre mens platen er
ute. **Byttet mellom de to stillingene er sju håndgrep, ikke ett loddrett
løft** — men det er sju *flate* håndgrep etter K1: enheten bæres vannrett, med
104 mm luft over og under, og skal ikke vippes. (Sjakten var 121 mm på
tegningen og er 294 på den bygde sengen: trinnet som gjorde den trang, ble
aldri kappet. Se X18.) Rekkefølgen og hvorfor den er
slik står i J13, med film.

**7.6 Ikke sett deg på platens kant, og ikke bruk den som trinn.** Den er
sikret mot å vippe, men den er ikke en avsats.

**7.7 Ettertrekk.** Ettertrekk rammeskruene etter fire uker og deretter en
gang i året. Sengen vibrerer hver gang noen snur seg.

**7.8 Aldersgrense.** Loftsenger og overkøyer anbefales ikke til barn under
**6 år**.

**7.9 Sjekk sengen når du flytter noe.** Blir sengen dratt ut fra veggen, mister
den både rekkverket sitt og stivheten sin.

**7.10 Alle kanter et barn kan nå skal være brutt.** Også de du ikke ser —
undersiden av plateenheten står i knehøyde for den som sitter ved pulten, og
etter X9 er knærne faktisk der inne og ikke oppe på benken. Kravet, stedene og
verktøyet står i avsnitt 3.

---

## 8. Kroppene i sengen

Modellen har fire **referansekropper**: et barn på **1200 mm**, bygget som én
solid av fjorten kuler, sylindre og bokser, med hvert segment som en brøkdel av
ståhøyden etter **AnthroKids** — de digitaliserte Snyder-studiene 1975/1977,
[math.nist.gov/~SRessler/anthrokids/](https://math.nist.gov/~SRessler/anthrokids/),
fri bruk. 1200 mm er 50-persentilen for omtrent 6–8 år, altså alderen EN 747
åpner overkøya i (7.8). To ligger i sengestilling, to sitter i bordstilling, og
begge stillingene har hver sin tegning: [sengestillingen i
bruk](img/bruk-sengestilling.svg) og [bordstillingen i
bruk](img/bruk-bordstilling.svg). **De to som sitter, sitter alminnelig
nå** — med beina ned, knærne inn under platen og sålene på fotbrettet (X14). Til og med v15 satt de i
skredderstilling, fordi det var den eneste måten å komme til et bord i
fanghøyde på; X9 gjorde bordet til en pult, og da forsvant den stillingen.

En kropp er **ikke en del**. Den kappes ikke, bærer ingenting, står i ingen
liste og er tatt ut av alle kontakt-, sammenhengs- og overlappskontroller. Det
eneste som er assertert om den, er at ingen av de fire ligger inne i noe tre
eller stål. Skummet er unntatt: en pute på 100 mm tar rumpa 12 mm inn og hodet
22 mm ned i soveflaten, som er hva skum gjør.

Det de er til for, er tallene. Alle er **målt på solidene**, ikke skrevet inn,
og hele lista står i [nøkkelmål](generated/nokkelmal.md#referansekroppen--hva-sengen-er-til-for).

**8.1 Man kan sitte helt rett opp i sofaen.** Kronen står i Z 1074 — seteflaten
420 pluss sittehøyden 654 — og køyespilenes underside i 1500. **426 mm** over
hodet. Det er rikelig, og det er målt på en kropp og ikke på en påstand.

**8.2 Knærne går inn under platen. Den er en pult.** Platen ligger **280 mm**
over seteflaten og har **262 mm** under seg. Et sittende barnekne står 135 mm
over setet, så kneet går inn med **127 mm** luft over seg. Nærmeste punkt på
kroppen står 71 mm fra platen. Man sitter ved denne flaten slik man sitter ved
et bord: beina ned, knærne under — og hoftene FRAM fra ryggputen, for det er
det å sitte *ved* noe betyr. Figurene er flyttet dit: hofteleddet står på X 472
mot 288 før, én lårlengde bak et kne som stikker en lårradius inn under
platekanten. Sålene henger fritt; se den siste bolken i dette avsnittet.

**Slik var det ikke før X9, og det er verdt å vite hvorfor tegningene så ut som
de gjorde.** Til og med v15 lå platen 140 mm over setet med 122 under seg, og
til og med v13 var det 118 og 100. Et barnelår er 115 mm tykt: 122 slapp inn et
**strakt lår** og ikke et bøyd kne. Bordet var da beskrevet som en lekeflate i
fanghøyde mellom to sofahalvdeler, og figurene satt i skredderstilling med
beina oppe på benken, fordi det var den eneste stillingen flaten tillot. Den
beskrivelsen og den stillingen er borte. De var sanne på 560 og er usanne på
700.

**Hva som ble kjøpt, og med hva.** X8 ba om nettopp denne pulten — platetopp
700, 280 over puten, med IKEA SMÅSTAD-pulten på 730 som referansen byggherren
kan peke på i en butikk — og fikk **nei**. Regnestykket i det neiet var riktig
og står fortsatt: platens forkant ligger alltid *under* et trinn, i
bordstilling var det trinn 3, og med trinn 3 der det da sto (underkant 739) ga
700 bare 39 mm fri vei opp mot de 100 modellen krever. Taket var 639.

Det neiet hvilte på én forutsetning ingen hadde skrevet ned: at **stigen var
fast og bordet måtte passe under den**. X9 er byggherren som overprøver sitt
eget vedtak, med syv ord — «700, og juster trinnene / evt. antall trinn» — og
da snur regnestykket. X9 løftet trinn 3 [var 61 mm, til 848], og da sto
underkanten på 800: nøyaktig 100 over en platetopp på 700. Pulten lå ikke
under taket sitt, den lå **på** det. Ingen regel ble slakket for å få den dit.

**Og X16 snudde den siste biten.** X9 kjøpte høyden ved å holde et bånd TOMT og
henge to bordklosser under platens forkant; X16 legger et trinn i den høyden i
stedet. Trinn 3 står på **682** — bordplatens underside — og lokket over løftet
er trinn 4, med underkanten på **914**. Platetoppen er den samme 700, men taket
gikk fra 700 til **814** og løftet fra 100 til **214**. Se J4 og J13.

**Prisen står i stigen, og den er reell.** X1/X2 skrev ned den jevne stigen som
en utseendebeslutning og slo fast at «stigen bestemmer og bordet følger». X9 er
den beslutningen solgt tilbake, av den som tok den, for det han ville ha mer.
Stigen er to løp som møtes på støttetrinnet, med **89 mm** forskjell mellom dem
(X9 hadde 51). Se J4 for hva som ble beholdt: stigningsgrensen, jevnheten inne i
hvert løp, og trinnantallet.

**Og det som er ærlig å si om høyden, står her.** 280 mm over puta er **92 mm
over albuen** til et sittende barn på 1200 mm. Det er en pulthøyde regnet for
en **stol**, brukt fra en **sofa**. Barnet legger underarmene oppå plata — de
ligger 6 mm over den i modellen — og har albuene i været. Referansen gjør
nøyaktig det samme: SMÅSTAD-pulten står 730 over gulvet og stolen som selges
til den 430, altså de samme 300 millimeterne. Byggherren valgte butikken, og
det er et gyldig valg, men det er ikke det samme som at høyden er ideell.

**8.2b Fotbrettet, og hvorfor høyden ikke er valgt (X14).** X9 førte opp én
ting som åpen: det fantes ingen fotskammel, og sålene hang i lufta. Nå står de
på tre. Fotbrettet er en **løs krakk** — to gavler 36×98 × 272 på høykant og
fire dekkbord 48×68 × 416 flatt oppå, kant i kant, åtte 6×80 (J18) og **ikke én
skrue inn i sengen**.

Høyden er det eneste interessante ved den, og den er ikke plukket. To rett
vinkler er ikke forhandlingsbare — leggen står i lodd og foten ligger flatt —
og da har beinet én fri variabel igjen: hvor mye låret faller fra hofta. De to
måtene en fotstøtte er feil på er begge en påstand om **puta**:

* **For høyt** — låret slipper puta og barnet sitter på sittebeina. Prøven er
  kontakt: lårets underside der puta SLUTTER kan ikke ligge over putas flate.
* **For lavt** — låret faller så mye at putekanten skjærer inn i det. Prøven er
  dybde: låret kan ikke presse dypere ned i skummet enn rumpa allerede gjør, og
  rumpas egen dybde er heller ikke skrevet inn — den er der hoftekula ligger.

Løst på den bygde kroppen og den bygde puta blir det båndet **134,8–153,9 mm**.
Og så er det treet som plukker ett tall ut av båndet: en krakk er to kurver,
noe å stå PÅ og noe å sette det på. Dekket ligger flatt (et bord på høykant er
en list, ikke et gulv for en såle), gavlen står på høykant (et bord som ligger
flatt er ingen gavl, og en pinne på ende er et bein med for lite fotavtrykk til
å hindre at en hæl velter den). Tre høykanthøyder ganger tre flattykkelser over
sengens fem dimensjoner er **ni kurver**, og båndet slipper igjennom nøyaktig
én: **98 + 48 = 146 mm**. Hvilket bord av den høyden og den tykkelsen er to
regler til og ingen smak — gavlen bærer dekkskruen på sin egen senterlinje, så
23 mm kan ikke (11,5 < 3d) og 36 er den tynneste av de to som kan; dekket
legges i bord tvers over dybden, så det smaleste bordet er det som kommer
nærmest dybden de to sålene faktisk ber om.

**Den er løs, og det er en avgjørelse med et mål bak seg.** F1 har allerede
målt at det ikke finnes fast tre i denne bukta å skru noe til: 689 mm utover,
1057 innover, 752 bakover og ingenting framover. En FAST fotstøtte her ville
dessuten stått i D11/D13s åpne gulv, som er der du setter føttene når platen er
sofa og der du går for å komme til stigen. Så den er møbel: den står under
platen i **begge** stillinger — 151 mm under platen i sengestilling, 536 under
pulten — den er aldri i soveflaten (som begynner på 315 og 420, mens brettet
topper ut på 146), og den skal aldri parkeres. Bredden er bukta D13 lar stå
mellom de to gangpassasjene, så begge passasjene er hele; dybden er de to
sålenes egen avstand rundet opp til hele bord. Dekket ER fotavtrykket, så
ingen last noe sted på det kan velte den — den må skyves, og det krever 0,93
ganger lasten som står på den.

Vil noen ha den helt bort, går den inn i kasserommet (146 < 229, 416 < 479,
272 < 800). Det er et **måleresultat og ikke en plan**: kasserommet er lovet
bort til kasser.

**Og ett tall sluttet fila å sitere.** Antropometritabellen oppgir popliteal
høyde som 0,28 H, og kommentaren over den påsto at alle fem referansemålene kom
ut av den bygde soliden. Tre gjør det. Popliteal høyde og sittende knehøyde
gjorde det aldri og kan ikke: kneledd til såle på denne kroppen er 313,2 mm mot
tabellens 336. De 22,8 er ingen gåte — 16,8 fordi foten er en boks sentrert på
ankelen, og 6,0 fordi legg pluss ankel summerer til 330. Fotbrettet er derfor
ikke utledet av 0,28 H; det er utledet av setet og av kroppen som ble bygget,
og avviket er regnet og assertert i stedet for å stå i en kommentar.

Tallene over er målt på solidene og står i
[nøkkelmål](generated/nokkelmal.md#referansekroppen--hva-sengen-er-til-for).
Hele resonnementet — både X8s nei og X9s ja, som står ved siden av hverandre —
er øverst i `generate_loftbed.py`.

**8.3 Fri høyde over ansiktet til den som ligger nede: 902 mm.** Målt fra
hodets overside til køyespilenes underside.

**8.4 Over den som ligger i køya står ingenting.** Køya er åpen oppover — det
er en assert. Rekkverket står **83 mm** over kroppens høyeste punkt og **148
mm** over ansiktet, og barrieren er 326 mm over madrassen (7. avsnitt) — alle
tre tallene satt av X18, som la det øverste bordet 120 mm over det nederste og
ikke i flukt med stolpetoppen. Rekkverket står altså lavere over den som ligger
der enn tegningen hadde det, og fortsatt godt over EN 747s 160 mm.

**8.5 Plassen å vokse i.** Et barn på 1200 mm legger beslag på 1402 av de 1990
millimeterne madrassen er lang. **588 mm igjen bak føttene.**

---

## Vedlegg A — lastbane

Regnedelen. Du trenger ikke lese dette for å bygge sengen.

**Radene under regnes av modellen (X13).** Fram til denne runden var vedlegg A
det ene stedet i prosjektet der tall var *regnet for hånd og skrevet inn*, og
tallsveipet i `tools/check_tall.py` måtte hvitliste dem ett for ett. Nå står
C24-arket og hver rad i `generate_loftbed.py` — søk `X13` — og byggeloggen
skriver dem ut på hver kjøring. Fire tall flyttet seg da regnestykket ble
maskinelt, og de er rettet her: lagerkapasiteten under trinnet delte på den
**karakteristiske** 2,5 der alle andre lagerrader delte på designverdien 2,31
(3,2 → 3,0 kN); endespilen var skalert med spennforholdet **i annen**, som er
måten en nedbøying skalerer og ikke en spenning (0,46 → 0,48);
spile-mot-vange-raden sto på 0,05 der 0,7 kN på 4704 mm² er 0,06; og
stolpen mot gulvet var avrundet til 45 der 3528 mm² endeved er 45,6 kN. A.6 sa
dessuten 0,15 om trinnet, som er 1 kN-tallet, mens A.2 for lengst hadde flyttet
raden til EN 747-2s 1,2 kN. Ingenting i sengen er rørt av dette — det er
regnestykkene som har byttet hånd.

Spennene i tabellene er delenes frie spenn, som følger av kapplista og
nøkkelmålene.

**Materiale:** C24 gran. f<sub>m,k</sub> = 24, f<sub>c,0,k</sub> = 21,
f<sub>c,90,k</sub> = 2,5, f<sub>v,k</sub> = 4,0 MPa, E<sub>mean</sub> = 11 000
MPa. γ<sub>M</sub> = 1,3. Bøyningen regnes med k<sub>mod</sub> = 0,9
(korttids- og dynamisk last).

**Størrelsesfaktoren k<sub>h</sub> er med.** Eurokode 5 lar heltre under 150 mm
bøyehøyde regnes med k<sub>h</sub> = (150/h)<sup>0,2</sup>, oppad begrenset til
1,3 — små tverrsnitt har færre svakheter per volum. Hvert eneste bærende
medlem i denne sengen er under 150 mm, så faktoren gjelder overalt, og
f<sub>m,d</sub> avhenger av bøyehøyden:

| Bøyehøyde h | 23 | 36 | 48 | 68 | 98 |
|---|---:|---:|---:|---:|---:|
| k<sub>h</sub> | 1,30 | 1,30 | 1,26 | 1,17 | 1,09 |
| **f<sub>m,d</sub> (MPa)** | **21,6** | **21,6** | **20,9** | **19,5** | **18,1** |

**Systemfaktoren k<sub>sys</sub> er IKKE med, og det er et valg.** Eurokode 5
tillater 1,1 for lastfordelende systemer, og spilefeltet kvalifiserer. Den står
ubrukt av én grunn: lastfordelingen er allerede kreditert på **lastsiden**, der
spilelasten deles på det antallet spiler foten eller madrassen faktisk dekker.
Å ta den en gang til på motstandssiden ville vært å telle samme fysikk to
ganger. Den ligger som reserve.

**Hvorfor k<sub>mod</sub> = 0,9 og ikke 1,1.** Eurokode 5 har en høyere klasse,
«øyeblikks», på 1,1 — men den er for vind og ulykkeslast, ikke for et barn som
setter seg ned. Lasttilfellet her er en kortvarig topplast, og 0,9 er klassen
for det. Kombinasjonen som styrer er 2 kN med k<sub>mod</sub> = 0,9, ikke 1 kN
vedvarende med 0,8. Vi bruker altså ikke 1,1 noe sted, og det er et bevisst
valg og ikke en forglemmelse.

**Knekkeradene er likevel regnet med k<sub>mod</sub> = 0,8, og det er den
konservative siden.** Alle knekketall i A.1–A.3 kommer av
f<sub>c,0,d</sub> = 21 · 0,8 / 1,3 = 12,92 N/mm², som er tallet modellen har
regnet knekking på i hele sin historie. Å sette 0,9 inn der ville hevet
f<sub>c,0,d</sub> til 14,5 og senket hver utnyttelse med 11 % — stigevangen fra
0,26 til 0,23. Vi lar 0,8 stå, både for å slippe to sett knekketall som ikke
er enige, og fordi det er den strenge av de to. Modellen skriver begge tall i
byggeloggen (EC5 6.3.2-blokken), så ingen trenger å regne det om for å se hva
valget koster.

**Skjær regnes med sprekkfaktoren k<sub>cr</sub> = 0,67.** Eurokode 5 krever at
skjærbredden reduseres for opptørkingssprekker: τ = 1,5·V/(k<sub>cr</sub>·b·h).
Den lå ikke inne før, og den flytter det ene skjærtallet i sengen som betyr
noe — kilelektas spiss, se A.4.

**Trykket** regnes med k<sub>mod</sub> = 0,8 (middels lang lastvarighet
— egenvekt og vedvarende opplegg), så f<sub>c,0,d</sub> = 21 × 0,8 / 1,3 =
**12,92 MPa** og f<sub>c,90,d</sub> = 2,5 × 0,8 / 1,3 = **1,54 MPa**. Trykk på
tvers av fiberretningen med k<sub>c,90</sub> = 1,5 gir **2,31 MPa**.

**Festemidler**, erfaringstall: treskrue 5 mm i skjær ≈ **1,5 kN**, 6 mm ≈
**2,0 kN**. Disse tallene **forutsetter taueffekt** — at skruens gjenger holder
de to delene sammen mens leddet lastes, slik at friksjonen i fugen bærer sin
del. Ren Johansen-teori uten taueffekt gir **1,15 kN** og **1,56 kN**. Begge
settene står her fordi raden skal være ærlig: bruker man de rene tallene, går
den høyeste skrueraden i sengen fra 0,33 til 0,43, og ingen rad passerer 1,0
med noen av dem. Forutsetningen er reell — alle skruene er forborede og trekker
delene sammen — men den er en forutsetning. Det finnes ikke en bolt i denne sengen, og etter X18 ikke ett beslag heller —
alt er forborede treskruer.

**Designlaster:** overkøye 100 kg + madrass, dynamisk faktor 2 → **2 kN**
punktlast. Trinn **1 kN**. Benk **1 kN**. Plate **2 kN** dynamisk (noen setter
seg eller kneler på den). Rekkverk **0,5 kN** vannrett.

**Spilelasten regnes per spile, ikke per person, og det er et valg.** En spile
bærer aldri en hel person alene. Feltet er tett — 98 mm brede spiler med 44,5 mm
åpning oppe og 14,25 mm nede — og både madrassen og foten er bredere enn én
spile. Kriteriet er derfor forankret i det som lar seg måle på tegningen:

* **Bar spilebunn, én fot.** En fotsåle er rundt 250 mm lang. Med delingen
  142,46 mm oppe rekker den alltid over **minst to** spiler, og over benken med
  delingen 112,25 mm alltid over minst tre. En person på 100 kg som står på bar
  bunn gir da høyst **0,5 kN på den hardest belastede spilen**. Dette er
  tilfellet som dimensjonerer spilen.

**Spennet er 752 mm, ikke 800.** Spilen er 800 mm lang, men den *hviler* på to
48 mm brede vanger, og et spenn regnes fra opplegg til opplegg: senter til
senter er 752 mm, fri åpning mellom vangene er 704. De 800 er kappmålet.
* **Med madrass, slik sengen skal brukes.** Madrassen kan bare spre lasten
  videre, aldri smalere, så per-spile-lasten er nødvendigvis **lavere** enn i
  tilfellet over. Ligger man, fordeles kroppen over nesten hele feltet; regnet
  med spredning over sju spiler er lasten 0,3 kN og utnyttelsen 0,42. Tallet
  står som illustrasjon — det er 0,5 kN-raden som er kravet.

Til sammenligning: en ribbebunn fra møbelhandelen er sjiktlimt bjørkefiner på
rundt 8 mm, og en hel 90 × 200-bunn veier under 7 kg. Per-spile-kapasiteten der
ligger langt under det en 23 × 98 C24-spile har (W = 8 640 mm³). Sammenligningen
er kontekst for at kriteriet er realistisk, ikke et bevis for at det er riktig —
beviset er radene under.

Det som IKKE er dekket, er å sette hele vekten på **én** bar spile midt i
spennet. Det er en bruksregel, ikke en beregning: se 7.4.

### A.1 Overkøyen

| Ledd | Bæremåte | Spenn / flate | Last | Utn. | Dom |
|---|---|---|---|---:|---|
| Køyespile 23×98, **bar bunn** | Bøyning, én fot over minst to spiler | 752 mm c/c | 0,5 kN på én spile | **0,50** | ✓ σ ≈ 10,9 MPa mot f<sub>m,d</sub> 21,6; nedbøying 4,1 mm |
| Køyespile 23×98, **med madrass** | Bøyning, kroppen spredt over feltet | 752 mm c/c | 0,3 kN på én spile | **0,30** | ✓ σ ≈ 6,5 MPa |
| Køyespile, **hele vekten på én bar spile** | Bøyning | 752 mm c/c | 1 kN på én spile | **1,01** | ✗ Nøyaktig på grensen. Se 7.4 — ikke en byggemåte, en bruksregel |
| Spile → sidevange | Trelagring, full vangebredde under hver spile | 48 mm opplegg | 0,7 kN | 0,06 | ✓ |
| Bakre sidevange, regnet som fritt spenn mellom hjørnestolpene | Bøyning | 1794 mm | 2 kN | **0,65** | ✓ Konservativt — se raden under |
| Bakre sidevange **som bygget** | Bøyning, men vangen er skrudd til veggen i hver stender den treffer, så den er understøttet flere ganger på veien | ≈ 331 mm mellom veggfestene (6 fester over 1984 mm, 165 mm inn fra hver vegg) | 2 kN | ≈ **0,08** | ✓ Dette er grunnen til at veggfestet ikke er valgfritt |
| Fremre sidevange 48×98 | Bøyning, avstivet av de to stigevangene | 1794 mm | 2 kN | < 0,65 | ✓ σ ≈ 11,7 MPa mot 18,1 |
| Vange → endebjelke | **Trelagring** 48 × 36 | ≈ 4,0 kN | ≤ 1 kN | 0,25 | ✓ Vangen hviler, den henger ikke |
| Bakre vange → bakre stolpetopp | **Trelagring** på stolpens endeved, 95 × 36 mm | ≈ 7,9 kN | < 1 kN | 0,13 | ✓ Ingen festemidler i lastens vei. Hele stolpetoppens endeved er opplegg |
| Endebjelke 36×98 | Bøyning. **Rammebinderen i hver ende:** begge sidevanger lander på den, så den tar reaksjonen deres tvers over enden. Regnet konservativt som hele designlasten midt på det frie spennet mellom stolpene | 836 mm | 2 kN | **0,40** | ✓ σ ≈ 7,3 MPa mot 18,1. W = 57 624 mm³ — 98 mm er bæreretningen uansett tykkelse, de 12 mm koster bare bredden |
| Endebjelke → hjørnestolpe (J1) | Skruskjær, 2 × 6 mm — hele endefestet, det står ingen kloss under | 4,0 kN | ≤ 1 kN | **0,25** | ✓ Med hele designlasten stående rett over hjørnet: 0,50 |
| Samme ledd, **kantavstander** | 18 mm (3d) til bjelkens ende langs fiberretningen, 19 mm (3,2d) til kanten i lastretningen, i 36 × 98 C24 | krav 3d = 18 mm | — | — | ✓ Et vanlig omlegg, ikke en sprø endeskjøt. Målt på modellen |
| Fremre hjørnestolpe 36×98 | Knekking om svak akse, verste frie lengde 1007 mm — X1 la hele løftet inn i det ene spennet benkevange → endebjelke | λ = 97, k<sub>c</sub> = 0,32 → N<sub>c,Rd</sub> ≈ **14,7 kN** | ≈ 1,5 kN | **0,10** | ✓ Svak akse er dimensjonerende, og margin er likevel god |
| Bakre hjørnestolpe 36×98 | Knekking, kortere stolpe, avstivet av benkevange og bordbærelekt. Fri lengde 1304 mm regnet konservativt, som om bare endebjelken holder | λ = 126, k<sub>c</sub> = 0,20 → N<sub>c,Rd</sub> ≈ **9,1 kN** | ≈ 1,5 kN | **0,16** | ✓ |
| Stolpe → gulv | Endeved mot gulv | 45,6 kN i treet | 1 kN | 0,02 | ✓ |

### A.2 Stigen

| Ledd | Bæremåte | Spenn / flate | Last | Utn. | Dom |
|---|---|---|---|---:|---|
| Rungetrinn 48×68 | Bøyning | 320 mm | **1,2 kN** | **0,18** | ✓ σ ≈ 3,7 MPa mot 20,9. Lasten er EN 747-2s prøvenivå for et trinn, ikke vårt eget anslag. Trinnet kjennes helt stivt |
| Trinn → stigekloss | **Trelagring** 36 × 36 | 1296 mm² → 3,0 kN | 0,5 kN | 0,17 | ✓ K1 kappet klossen 73 → 36 mm; flaten halveres, tallet fordobles og ligger fortsatt lavt |
| Stigekloss → stigevange | Skruskjær, 1 × 5 mm — klossflaten 36 × 48 mm tar ikke to | 1,5 kN | 0,5 kN | **0,33** | ✓ |
| Samme hjørne, **kombinert skjærvei** | Klossens skrue + trinnendens 6×120 gjennom stigevangen | 3,5 kN | 0,5 kN | 0,14 | ✓ Trinnet låser også klossen mot å rotere om sin ene skrue |
| Skrue i trinnenden | Bærer ingen vertikal last | — | ≈ 0 | — | ✓ Riktig utformet |
| Stigevange → gulv | Ren søyle helt ned til gulvet | — | 1 kN | — | ✓ Ingen festemiddel i klatrelastens vei nedover |
| Stigevange, knekking **ut av planet** | Fri lengde gulv → fremre sidevange, 1402 mm etter X1 | λ ≈ 135, k<sub>c</sub> ≈ 0,17 → 3,9 kN | 1 kN | **0,26** | ✓ men se vedlegg B, avvik 2. Vangen står med den tynne siden ut av planet |
| Stigevange → fremre sidevange (J3) | Skruskjær, 3 × 6 mm — 98 mm omlegg tar ikke fire i rad | 6,0 kN | < 1 kN | 0,17 | ✓ Samme detalj som hele rammen bruker |
| **Støttetrinnet under platens forkant** | Samme rad som «Rungetrinn» over — støttetrinnet er ikke en egen deltype. Platen legger 0,55 kN på den fremre bærelinja, mot trinnets egen prøvelast på 1,2 | 320 mm | 0,55 kN | < 0,18 | ✓ Bæreflaten er 320 × 30 = 9600 mm², nesten dobbelt av kravet på 5000 |
| Stigens stivhet i eget plan | Rammevirkning: to vanger + fire trinn (X18; tegnet med fem) | — | — | — | ✓ |

**To rader gikk UT av denne tabellen i X16, og det er verdt å si hvilke.**
X10 måtte gi bordklossene sine egne rader her: en skjærrad, og — verre — en
**eksentrisitetsrad**, fordi platas last sto ute på klossens hylle og ikke over
skruelinja. Det var et moment som lå i selve innfestingsflaten, båret som et
skruepar i motsatt skjær, og den raden lå på 0,55 — den høyeste skrueraden i
hele sengen. Begge deler forsvant med klossene: **ingen skrue i denne sengen har
lenger last stående foran sin egen skruelinje**, og den høyeste rene skrueraden
er nå J5 med 0,33. Et trinn bærer platen *over* vangen i stedet for på en
utkraging foran den, og da finnes momentet ikke.

### A.3 Underetasjen

| Ledd | Bæremåte | Spenn / flate | Last | Utn. | Dom |
|---|---|---|---|---:|---|
| Benkespile 23×98 | Bøyning — samme stykke som køyespilen | 752 mm c/c | 0,5 kN på én spile | **0,50** | ✓ Delingen er tettere her, 112,25 mm, så en fot tar minst tre spiler |
| Endespile 23×98 (V13) | Bøyning — samme stykke, kortere spenn | 722 mm c/c | 0,5 kN på én spile | **0,48** | ✓ Spennet er 30 mm kortere enn feltets, så raden over er den strenge |
| Endespile → endelist | Trelagring 98 × 36 | 3528 mm² → 8,2 kN | 0,25 kN | 0,03 | ✓ |
| Endelist → bakre stolpe (J17) | Skruskjær, 2 × 5 mm — hele festet, ingen kloss under | 3,0 kN | 0,25 kN | **0,08** | ✓ Med hele spilelasten stående rett over listen: 0,17 |
| Spile → benkevange | Trelagring 48 × 98 | 4704 mm² → 10,9 kN | 0,5 kN | 0,05 | ✓ |
| Bakre benkevange 48×68 | Bøyning over åpningen mellom stubbeføttene | 700 mm | 0,5 kN | **0,12** | ✓ Ved 1 kN: 0,24 |
| Fremre benkevangebit 48×68 | Bøyning, to opplegg, ingen utkraging | 584 mm | 0,5 kN | < 0,12 | ✓ Innerenden lander helt på stubbefoten — rent endeopplegg, null utkraging |
| Benkevange → stubbefot | **Trelagring** 48 × 68 | 3264 mm² → 7,5 kN | 0,5 kN | 0,07 | ✓ |
| Bakre benkevange → bakre stolpe (J8-B) | Skruskjær, 2 × 6 mm skråskruer — hele endefestet. Skruene står skrått i planet, lasten står loddrett på dem uansett | 4,0 kN | 0,5 kN | **0,13** | ✓ Ytre spenn stolpe → stubbefot ≈ 510 mm. Med hele kilonewtonen rett over hjørnet: 0,25 |
| Fremre benkevangebit → fremre stolpe (J8) | Skruskjær, 2 × 6 mm — hele endefestet | 4,0 kN | 0,5 kN | **0,13** | ✓ Samme sak, og med samme verste tall 0,25 |
| Stubbefot 48×68 | Knekking over 229 mm | λ ≈ 17 | 0,5 kN | ≈ 0 | ✓ Ikke en søyle, et opplegg |

### A.4 Plate og rekkverk

| Ledd | Bæremåte | Spenn / flate | Last | Utn. | Dom |
|---|---|---|---|---:|---|
| Plate 18 mm, **bar** | Bøyning over to opplegg | 750 mm | 2 kN dynamisk | **1,40** | ✗ Holder ikke alene. Denne raden er kalibrert på f<sub>m,d</sub> ≈ **6,95 MPa** for plata, og alle plateradene under bruker samme tall |
| Plate 18 mm **med to avstivningslekter 48×68 på høykant** | Lekta regnet alene — platen er ikke kreditert som flens, se J13a | 750 mm | 1 kN på hver | **0,26** | ✓ σ ≈ 5,1 MPa mot 19,5. Dette er hele grunnen til at lektene finnes |
| Samme lekt, **hele lasten over ÉN av dem** | Et kne lander like gjerne rett over en lekt som midt imellom | 750 mm | 2 kN dynamisk | **0,52** | ✓ Dette er jobben reserven i lekta gjør, og grunnen til at den ikke kan krympes |
| **Styrelektas forende → trinnet, gjennom plata** (V3) | Lekta står 2 mm utenfor trinnenden, så forenden har ikke opplegg under seg: reaksjonen går 26 mm sideveis gjennom plata (lektas senterlinje X 809 → trinnets opplegskant X 835 — samme trinnprofil og samme X i begge stillinger etter X16, så raden gjelder begge) | 26 mm arm, 100 mm effektiv bredde (konservativt) | 1 kN | **0,69** | ✓ σ = 4,81 MPa mot f<sub>m,d</sub> 6,95 **på tvers** av fiberretningen, og 0,28 mot 17,4 langs. Dette er platas dimensjonerende rad — prisen for å legge styringen der styringen må skje. Den holder **begge veier**, og det er grunnen til at fiberretningen er blitt en margin i stedet for et krav |
| **Fritt platehjørne, bar 18 mm plate** (V3, kontrollregning) | Punktlast på et fritt hjørne: utkraget stripe med effektiv bredde = egen lengde, så σ = P·a/(a·t²/6) = **6P/t²** og lengden faller ut | uavhengig av avstand | 1 kN kne | **2,66** | ✗ σ = 18,5 MPa. Gjelder like fullt hvor nær lekta står [var 213, 116 eller 77 mm] — **derfor ble kilelektene ikke fjernet**. Hjørnet ligger utenfor trinnenden og får ikke hjelp av støttetrinnet |
| **Kilelekt (vinge) under hjørnet, bøyning** (M5/V4/K2, 77 mm, 68 → 27 mm) | Utkraging fra styrelekta, med lasten på kilen selv. Med h(x) avtakende topper σ seg der h = 2 × spissen, altså 51 mm fra spissen — inne i delen, ikke ved roten | 77 mm, kritisk snitt h = 54 mm | 1 kN kne | **0,13** | ✓ σ = 2,17 MPa mot f<sub>m,d</sub> 16,6 i C24. Roten selv: 2,08 MPa, 0,13. K2 gjorde vingen kortere og tallet falt med den (var 0,18 på 116 mm) |
| **Kilelekt (vinge), skjær i spissen** (M5/V4) | Tverrskjær i delens tynneste snitt, 48 × 27 mm, med sprekkfaktoren: τ = 1,5·1000/(0,67·48·27) | 27 mm spisshøyde | 1 kN kne | **0,62** | ✓ 1,73 MPa mot f<sub>v,d</sub> = 2,77. Delens dimensjonerende tall, og det som sier at spissen ikke skal bli tynnere |
| Lekt → plate (J13a/J13b) | Limt fuge 48 × 750 mm + 6 skruer 5×40 opp fra kontrabor i hver styrelekt, 2 i hver kile, 13 mm gjenge i plata | uttrekk ≈ 0,27 kN per skrue (halvert for kryssfiner) | 0,12 kN, enheten (6,3 kg) løftet etter ett hjørne med faktor 2 | **< 0,05** | ✓ I bruk står fugen i trykk — platen hviler på lekta, lasten går ikke gjennom et festemiddel |
| Bordbærelekt 48×68 **på høykant** | Bøyning om sterk akse. **Dette er lekta som spenner fritt, ikke benkevangen:** i bordstilling hviler platen bak på bordbærelekta og foran på støttetrinnet (X16 — det var to bordklosser fra X9, og trinn 2 før det), og lekta går post til post uten støtte under | 1794 mm | 0,55 kN bordlast | **0,34** | ✓ σ ≈ 6,7 MPa mot 19,5 |
| Samme lekt, **noen lener seg tungt på bordet** | Halve den dynamiske designlasten havner på det bakre opplegget | 1794 mm | 1 kN | **0,62** | ✓ σ ≈ 12,1 MPa. Lektas dimensjonerende rad, og grunnen til at den ikke kan bli tynnere |
| Bordbærelekt → stolpe (X18) | Skruskjær, 2 × 6 mm skråskruer per ende — samme ledd som J8-B | 4,0 kN | 0,13 kN | 0,03 | ✓ Beslaget som bar enden er ute; de to lommeskruene tar reaksjonen i skjær |
| Rekkverksbord 36×98 | Bøyning om svak akse, vannrett last, innspent i begge ender | ≈ 760 mm | 0,5 kN | **0,10** | ✓ σ ≈ 2,2 MPa mot 21,6 |
| Rekkverksbord → stolpe | Skruskjær, 2 × 5 mm per omlegg | 3,0 kN | 0,25 kN | 0,08 | ✓ |
| Øvre rekkverksbords indre ende (X18) | Ingen vange å skru i — stigevangen er kappet nøyaktig i bordets underkant, så omlegget er 0 og ikke bare kort. Enden henger i avstiverraden, som binder de to bordene til én fagverksbjelke | — | — | — | ⚠ Se vedlegg B, avvik 7 |
| Rekkverksavstiver → bord (J21, X18) | Skruskjær, 2 × 5 mm per omlegg, 4 omlegg per bordpar | 3,0 kN | — | — | ✓ Raden er lastbanen for det øvre bordets indre ende — **og klemdommen for de 120 mm mellom bordene**, se vedlegg B, avvik 6 |

### A.5 Global stabilitet

| Retning | Hva som holder igjen | Dom |
|---|---|---|
| Langs rommet | De to sideveggene, og de fire hjørnestolpene som står inntil dem | ✓ |
| I dybden, øvre nivå | Portalramme i hver ende — to stolper og en endebjelke, festet i begge hjørner — pluss veggfestet J14, som binder hele den bakre sidevangen til veggen | ✓ Veggfestet fjerner all gynging |
| I dybden, nedre nivå | Den gjennomgående bakre benkevangen, de tolv benkespilene (ti pluss de to endespilene) og platen danner en vannrett skive som binder alle stolper og føtter sammen | ✓ |
| Vipping forover | Fotavtrykket er grunnere enn sengen er høy, men tyngdepunktet ligger godt innenfor det. Veggfestet er uansett det som avgjør | ✓ |

### A.6 De høyeste utnyttelsene

| Ledd | Utn. |
|---|---:|
| Plate, styrelektas forende gjennom plata inn i trinnet (V3) | **0,69** |
| Bakre sidevange regnet uten veggfestet | 0,65 |
| Bordbærelekt, noen lener seg tungt på bordet | **0,62** |
| Kilelekt under platehjørnet, skjær i 27 mm-spissen (med k<sub>cr</sub>) | **0,62** |
| Avstivningslekt under platen, hele lasten over én av dem | **0,52** |
| Køyespile og benkespile, 0,5 kN på én bar spile | **0,50** |
| Endespile (V13), 0,5 kN på én bar spile | 0,48 |
| Endebjelke (36×98) | 0,40 |
| Bordbærelekt på høykant, ren bordlast | 0,34 |
| Stigekloss → stigevange, klossens ene skrue regnet alene | **0,33** |
| Avstivningslekt under platen, 1 kN på hver | 0,26 |
| Stigevange, knekking ut av planet | **0,26** |
| Endebjelke → hjørnestolpe (J1), to skruer i skjær | **0,25** |
| Vange → endebjelke (trelagring) | 0,25 |
| Rungetrinn, bøyning (EN 747-2s 1,2 kN) | **0,18** |
| Stigevange → fremre sidevange (J3) | 0,17 |
| Trinn → stigekloss (trelagring) | 0,17 |
| Bakre hjørnestolpe, knekking | 0,16 |
| Kilelekt under platehjørnet, bøyning i det kritiske snittet | 0,13 |
| Benkevangeendene → stolpe (J8, J8-B), to skruer i skjær | 0,13 |
| Bakre benkevange over åpningen mellom stubbeføttene | 0,12 |
| Rekkverksbord, vannrett last | 0,10 |
| Alle andre ledd | ≤ 0,10 |

De øverste er forskjellige slags ledd — en plate, en vange uten sitt veggfeste
og to lekter — og det er slik det skal se ut. Ingen enkelt delfamilie er verken
flaskehalsen eller den overdimensjonerte.

**Og etter X16 er den høyeste rene skrueraden i hele sengen 0,33** — J5,
stigeklossens ene skrue. Toppen av denne lista er tre og ikke stål. Fram til
denne runden lå bordklossens skruepar øverst blant skruene på 0,55, og det var
den eneste raden i sengen der lasten sto foran sin egen skruelinje. Den finnes
ikke lenger, og det er en assert i modellen og ikke en observasjon her.

### A.7 Kilder

Tallene over er regnet etter Eurokode 5 (NS-EN 1995-1-1) med materialverdier
fra NS-EN 338. Kravene i avsnitt 7 er fra EN 747:

* EN 747-1:2007 §4.3 og EN 747-1:2012 §4.2.2 — åpningsbåndene. 2012-utgaven
  gir oppsamlingsregelen ≤ 7 / 12–25 / 60–75 / ≥ 200 mm, 2007-utgaven
  rekkverksregelen ≤ 5 eller 60–75 mm med probe-prøve (⌀60 skal passere fritt,
  ⌀75 skal ikke passere med 100 N).
  <https://cdn.standards.iteh.ai/samples/23918/> · <https://cdn.standards.iteh.ai/samples/34675/>
* EN 747-1:2024 — gjeldende utgave, som innfører «completely bound» og
  «partially bound opening» (def. 3.8/3.9). <https://cdn.standards.iteh.ai/samples/75666/>
* Prøveprotokoll for køyesenger, med lastnivåene EN 747-2 bruker:
  <https://quality.bluerock.hk/wp-content/uploads/2021/04/tests-protocole-for-Bunk-bedV3.pdf>

**Et ærlig forbehold om utgaven.** Den fritt tilgjengelige samplen av
EN 747-1:2024 stopper før kravkapitlet, så de eksakte millimeterne i
2024-utgaven er **ikke** verifisert her. Madrassvinduet 105–130 mm er utledet
av det bygde rekkverkets egen høyde over spilene og er lovlig under begge
utgavene vi *kan* lese. Skulle 2024-teksten vise seg å være mildere,
er sengen fortsatt riktig bygget; er den strengere, er dette stedet å se etter.

**Kilelekta under platehjørnet er den ene delen i sengen der skjær, ikke bøyning, er
dimensjonerende:** 0,62 i spissen mot 0,13 i det verste bøyesnittet. Det er
skjærtallet som holder spissen på 27 mm, ikke utseendet.

**Den høyeste skrueraden i sengen er nå stigeklossens ene 5 mm skrue, 0,33** —
og den er regnet uten hjelp fra trinnet som ligger på klossen og er skrudd ned
i den, og uten hjelp fra trinnendens egen 6×120 gjennom stigevangen. Med den
kombinerte skjærveien er den 0,14.

Forrige utgave hadde 0,50 øverst blant skrueradene: bæreklossen J1-B, som
hang på én 6 mm skrue. De åtte bæreklossene er borte, og de tre hjørnene de
sto i tar reaksjonen på delenes egne endefester i stedet — 0,25 og to ganger
0,13. Å fjerne klossene senket altså den høyeste skrueutnyttelsen i sengen.

Ingen ledd i den ferdige sengen har utnyttelse over 1,0. De to tilfellene som
gjør det, er begge dekket av bruksreglene: bar spilebunn under hopping (7.4) og
platen uten avstivningslekter — som ikke er en tillatt byggemåte, lektene skal
monteres.

---

## Vedlegg B — aksepterte avvik

Her står de bevisste valgene som ikke er det lærebokrene, med begrunnelsen,
slik at den som bygger vet hva han går med på.

**Avvik 0 — de 68 mm over rekkverket er ikke en åpning.**
De fire loddrette delene i fronten går til 2037 og det øverste
rekkverksbordet slutter på 1969, så mellom dem står det **68 mm**. Grensen for
en åpning over liggeflaten er 75, så tallet holder på egen hånd — men det er
ikke engang en åpning i standardens forstand, og påstanden er målt og ikke
antatt: det finnes ingen del i hele sengen i det høydebåndet utenom de fire
stolpeendene selv. En åpning som kan klemme, må være omsluttet — EN 747-1:2024
skiller uttrykkelig mellom «completely bound» og «partially bound» åpninger
(def. 3.8/3.9) — og dette er ikke engang delvis omsluttet oppover.

*Raden har vært skrevet tre ganger og handler om det samme stedet hver gang:*
tegningen hadde 58 mm der, X18s første runde satte det øverste bordet i flukt
med stolpetoppen og lukket åpningen til 0, og da byggherrens eget mål — 120 mm
over det nederste bordet — ble lest riktig, kom den tilbake på 68. Argumentet
over gjelder alle tre tallene, fordi det ikke handler om størrelsen.

Det som følger med avviket er kantbrytingssaken: stolpeenden står fritt over
bordet, og den kanten skal brytes som alle andre.

**Avvik 4b — den TYNNE madrassen er teknisk lovlig, og frarådes likevel.**
Åpningen mellom madrass og nederste rekkverksbord er lovlig både når den er
**lukket** — under 25 mm — og når den ligger i **60–75**-båndet, der hele
lemmet går fritt igjennom. På den bygde sengen er den lukkede grenen vinduet
105–130 mm, og den andre grenen tilsvarer en madrass på **55–70 mm**. Det er en
gyldig lesning av kravet, men 55–70 mm er ikke en madrass noen selger til en
loftseng, og den ville lagt liggeflaten 50–65 mm lavere med det
rekkverkshøyden gir tilbake. **Bygg etter 105–130 mm.** Den andre grenen står
her fordi den er sann, ikke fordi den er en anbefaling, og den er med vilje
holdt ute av billedmanualen.

*(På tegningen var det motsatt vei: der var 110–125 mm den ene grenen og «180
mm og oppover» den andre. Bordet flyttet seg, og med det byttet grenene
plass.)*

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
gulvet. *Det som erstatter det:* den løse platen, som en **stiver** — den fyller
klaringen mellom veggplanet og stigevangenes bakside med 2 mm til overs, så
stigefoten ikke kan gå bakover. Veggfestet (J14) holder resten av rammen i ro.

*Det er fortsatt en énveis stivning, og det er uendret.* Den gamle U-braketten
omsluttet trinnet og bandt platen til stigen i **strekk**, altså begge veier;
den er borte, fordi et beslag som griper om baksiden av en del ikke lar seg
senke ned — se J13. Stigefoten er dermed bare holdt framover av skruene opp i
den fremre sidevangen (J3).

**X18 flyttet den ene av de fire retningene, og det er verdt å lese.** Den
bygde benkevangen står i stolpenes eget plan, altså i det samme Y-båndet som
stigevangen. Målt ut av stigevangens fotavtrykk, retning for retning, med
avstanden til nærmeste faste del og hva som ligger imellom:

* **utover: 142 mm** til den fremre benkevangens ende. Før X18 var det 689 mm
  til den fremre hjørnestolpen, for vangen lå i et annet plan og var ikke noe
  å binde seg til. Nå ligger den i planet — og 142 mm er nøyaktig lengden på
  klossen utvei (ii) under alltid har handlet om. Mellomrommet er fortsatt
  D13s gangpassasje, som skal stå fri for fast tre i 142 mm bredde fra gulvet
  og helt opp til **Z 682**.
* **innover: 510 mm** til den andre benkevangens ende. Mellomrommet er
  stigeåpningen, 320 mm fri mot EN 747s minimum på 300. (Å binde de to
  stigevangene til hverandre gir dessuten ingenting i dybden — de er én ramme
  og flytter seg sammen.)
* **bakover: 752 mm** til den bakre benkevangen. Mellomrommet er D11s åpne bod,
  som skal stå fri opp til Z 297 — og over Z 229 er den samme søylen platens
  egen innsettingssjakt.
* **framover: INGENTING.** Det står ingen del foran stigen i det hele tatt, og
  det kan ikke stå noen: U3 fester forflaten i Y = 788, asserter at Y 788..800
  er tom, og spikrer den totale dybden til 836.

Grunnen til at det ikke er en avstivning der, er altså ikke at ingen har sett
etter. Det er at alle fire retningene ut av foten er volumer en annen regel
krever **tomme**. Skal båndet komme, må en av de reglene vike, og prisen er
kjent på forhånd:

* **(i) En terskelkloss tvers over gangpassasjen ved gulvet.** 48×68 lagt flatt,
  142 mm, fra stubbefotens innerende til stigevangens utside. Koster at
  gangpassasjen ikke lenger er fri fra gulvet: du får en 48 mm terskel å tråkke
  over, og D13 må endres.
* **(ii) En kloss i benkevangens eget plan og høydebånd** (Y 740..788,
  Z 229..297) som fortsetter den fremre benkevangen de siste 142 mm inn til
  stigen. **Etter X18 er dette blitt en mye kortere vei enn det var:** vangen
  ligger allerede i det planet og allerede i det høydebåndet, så klossen er en
  ren forlengelse av en del som står der, buttet i begge ender og festet med
  det samme lommeskrueparet vangen selv har (J8). Tåspalten under
  (Z 0..229) er urørt, men døråpningen inn i boden ved gulvnivå smalner fra
  700 mm til stigeåpningens 320.
* **(iii) La den være** — dagens tilstand: platen som énveis stiver, J3
  framover, og veggfestet som holder rammen.

Måtte modellen velge mellom de to som faktisk binder foten, ville den tatt
**(ii)**: den tar ingen fri gulvflate der noen går, og den legger ingenting å
snuble i tvers over en passasje. Den koster bredde i en åpning som allerede er
320 mm ved stigen. Men dette er byggerens valg, ikke modellens.

**Valget er tatt (aug. 2026): (iii) — åpent, med plan.** Ingen av treklossene
bygges. I stedet er dette merket som *krokpunktet*: den riktige
løsningen er en **metallkrok ved stigefoten som låser i fremover-retningen** —
en del som griper uten å okkupere noen av de fire fredede volumene, senkes på
plass sammen med platen, og gir stigefoten toveis hold uten terskler eller
smalere åpninger. Den bygges inn den dagen riktig beslag er funnet (kravene:
låser +Y, monterbar ovenfra, bryter ikke platens innsettingsbane — se J13 og
V2-loggen i modellen; *krokpunktet* er navnet på stedet, ikke en
revisjonskode). Frem til da: platen som énveis stiver, J3 framover,
veggfestet for rammen — som målt over.

*Betingelse:* platen **skal** alltid ligge i, i en av de to stillingene. Se 7.5.

**Avvik 3 — bar spilebunn tåler ikke dynamisk last.**
Én spile alene under full hoppelast er overbelastet. Med madrass på fordeles
lasten over flere spiler og utnyttelsen halveres. *Betingelse:* madrassen legges
på før noen går opp. Se 7.4.

**Avvik 4 — ingen lås i sengestilling.**
EN 747 4.1.1 vil ha at omstilling mellom to stillinger krever verktøy. En plate
som kan løftes rett opp gjør ikke det. Det er avviket, og det er tatt bevisst:
det står ingen lås i beslaglista, og det skal det ikke gjøre.
*Det som erstatter det:* tre ting, og de virker sammen.

* **Madrassen ligger oppå platen** og må fjernes før platen kan løftes. Det er
  en de-facto forrigling: du kommer ikke til platen uten først å ta av det
  barnet ligger på.
* **Dette er underetasjen.** Fallhøyden fra platens overside (315 mm) til gulvet
  er ~32 cm. Det er ikke fra køyehøyde.
* **Platen er en enhet på 6,3 kg** (4,1 kg plate + 2,2 kg lekt, regnet av
  kroppene i modellen, ikke sitert), og styrelektene tar alle sidelengs
  frihetsgrader. Den kan bare gå rett opp, og den går ikke rett opp av seg selv.

*Betingelse:* platen **skal** alltid ligge i, i en av de to stillingene. Se 7.5.
Ettermontering av lås er mulig uten å endre en eneste trebit — se J13.

**X18: ettermonteringspunktet har mistet overlappen sin.** Treverket står der
fortsatt, men den bygde benkevangen står 36 mm lenger fram enn den tegnede, og
de to endeflatene låsen skulle spenne over deler nå bare **10 mm** i dybden der
de før delte 46. De tre løsningene i `laasvalg.png` er regnet på et 40 mm
anlegg, og 10 mm er ikke det. Skal låsen komme, må den enten flyttes til et
annet par flater eller få en kloss som gir den 40 mm igjen. Det er ikke gjort,
og det er heller ikke skjult: modellen måler de 10 millimeterne og asserterer
dem.

**Avvik 5 — stigen har fire trinn der regelen sier fem, og ett klatresteg er
385 mm. AKSEPTERT aug. 2026.**
Byggherren kappet fire trinn, ikke fem: overkantene står på 297, 682, 962 og
1242 mm. De to nederste er med vilje platens to stillinger — «trinnene er laget
for den opprinnelige høyden av benk og bord» — og de to øverste er den samme
utledningen som før. Det som mangler, er trinnet på **489 mm**, og uten det er
steget fra trinn 1 til støttetrinnet **385 mm** mot husets grense på 281 og mot
EN 131s bånd 250–300 for jevn trinnavstand. Grensen er ikke hevet. De tre andre
stegene (280, 280 og 281) holder den som før.

*Målt i rommet, ikke på tegningen, og det er verre i én stilling:*

* **I sengestilling** ligger platen på 297–315 tvers over hele stigeåpningen,
  så foten starter på platens egen overside og steget opp til støttetrinnet er
  **367 mm**. Det er fortsatt over grensen.
* **I bordstilling** ligger platen *på* støttetrinnet. Trinnet er da ikke et
  trinn i det hele tatt, og det første treet en fot finner over gulvet er
  trinnet på 962 — **642 mm** over benkeflaten du står på. Stigen klatres ikke
  i bordstilling; det første trinnet nås fra benken.

**AKSEPTERT (aug. 2026) — og det er byggherrens observasjon som avgjør det.**
Barna klatrer ikke stigen slik en tegning leser den. De setter foten på
**benkekanten** på veien opp, «uten problemer», og den veien er

| Fra | Til | Steg |
|---|---|---:|
| trinn 1, 297 | benkesetet (pute), 420 | **123 mm** |
| benkesetet, 420 | støttetrinnet, 682 | **262 mm** |

— altså et største virkelig steg på **262 mm**, innenfor både husets 281 og EN
131s 250–300. Benkeflaten ligger 142 mm ved siden av stigen (D13s gangpassasje)
og er 663 mm lang, så det er et sidesteg opp på en avsats, ikke et strekk.

*Hva aksepten IKKE er:* grensen er ikke hevet, trinnet er ikke tegnet inn, og
stigens egen geometri er fortsatt 385 mm — modellen måler og skriver det tallet
hver gang den kjører, og
[nøkkelmålene](generated/nokkelmal.md#sikkerhetsmål-en-747) har begge radene
ved siden av hverandre. Det som er akseptert, er at klatreveien i dette rommet,
med denne benken, ikke går gjennom de 385 millimeterne.

*Opsjon, og modellen kan forsvare hver millimeter av den:* **kapp det femte
trinnet og sett det på 489 mm.** Samme 48×68 × 320 mm som de fire andre, samme
to stigeklosser, samme fire skruer, samme boremønster; hullet i vangen ligger
**1406 mm** fra vangetoppen. Med det på plass er det nedre løpet 192 + 193 mm,
hele stigen ligger innenfor 281 uten hjelp av benken, og ingenting annet i
sengen flytter seg. Dette var en **anbefaling** til aug. 2026 og er nå en
opsjon: byggherren bestemmer, og tallet står her ferdig regnet den dagen
benken flyttes eller putene byttes.

**Avvik 6 — LUKKET. Åpningen mellom madrass og nederste rekkverksbord er
10 mm, ikke 130.**
Avviket sto her i én runde og var **koordinatorens feillesning av et datum**,
ikke en feil på sengen. Byggherren målte 130 mm fra **spiletoppen** opp til
nederste bords underkant; modellen leste de 130 fra **madrasstoppen**, fikk en
130 mm åpning der grensen er 75, kunne ikke få byggherrens andre mål (120 mm
mellom bordene) til å gå opp samtidig, og skrev de 52 millimeterne som ikke
stemte inn i dette vedlegget sammen med et krav om en mye tykkere
madrass [var 175–190 mm]. Alt
det er strøket. En som bygger et rekkverk måler fra dekket han står på, ikke
fra en madrass som ikke ligger der ennå — og på hans datum går begge tallene
opp, de 52 millimeterne finnes ikke, og åpningen under bordet er 10 mm.

*Bånd for bånd på den bygde sengen, som modellen regner det:*

| Bånd | Høyde | Avstivere | Smaleste vei | Dom |
|---|---:|---:|---:|---|
| Madrasstopp → nedre bord | 10 mm | 0 | 10 mm | ✓ **lukket** — under 25 mm kommer ingenting inn, og det bordet dekker er madrasskanten |
| Nedre bord → øvre bord | 120 mm | 4 per felt | 59,4 mm | ✓ **bare på grunn av avstiverne** — 120 alene er over 75 |
| Øvre bord → stolpetopp | 68 mm | — | 68 mm | ✓ under 75, og ikke omsluttet (avvik 0) |

Barrieren over madrassen er 326 mm mot EN 747s krav på 160.

**Den ene raden å lese to ganger er den midterste.** Avstiverraden ble først
forstått som opphenget for det øverste bordets indre ende (avvik 7) og som en
bonus for klemvinduet. Med riktig datum er det omvendt rangert: uten raden er
båndet mellom bordene 120 mm mot grensen 75, og **da hadde sengen hatt et
ulovlig mål**. Avstiverne er det som gjør rekkverket lovlig. Tas én av dem ut,
er det ikke pynt som forsvinner.

*Madrassvinduet som følger av dette* står i 7.3: **105–130 mm, kjøp 120.** Ikke
kjøp en tykkere madrass for å «tette» noe — det er ingenting å tette, og over
130 mm står madrassen inne i selve rekkverksbordet.

**Avvik 7 — det øverste rekkverksbordets indre ende henger i avstiverraden.**
Stigevangene er kappet ved **1871 mm**, i flukt med det **øverste**
rekkverksbordets underkant og 166 mm under hjørnestolpene. Det nederste bordet
ligger på 1653–1751 og har dermed hele sitt omlegg på vangen som før — 48 × 98
mm, i full høyde. Det **øverste** bordet begynner på 1871, nøyaktig der vangen
slutter, og har ingenting å skrus i ved den indre enden: omlegget er ikke kort,
det er **null**. J7 har seks omlegg der tegningen hadde åtte.

*Hvem bærer det øverste bordet, ende for ende:*

* **den ytre enden:** hjørnestolpen, 95 × 98 mm omlegg, to 5×60 — uendret fra
  tegningen;
* **den indre enden:** avstiverraden. De fire avstiverne per felt binder de to
  bordene til én fagverksbjelke, og det nederste bordet er festet i vangen med
  fullt omlegg. Lasten går fra det øverste bordet, gjennom fire 23×98-biter i
  skjær, ned i det nederste bordet og derfra inn i stigevangen.

Det er en ekte lastbane, den er tegnet og den er regnet (vedlegg A: 3,0 kN per
omlegg), men den er ikke den lastbanen dette huset signerte på: et
rekkverksbord skal ha eget feste i begge ender. Datumrettelsen gjorde dessuten
avviket litt *renere* og ikke mindre — før sto bordets ende 68 mm over en
vangetopp og kunne ha fått en kloss under seg uten videre; nå møtes de to
delene i én linje.

*Tre veier, i stigende pris:*

* **La det stå, med avstiverraden som bærer.** Dagens tilstand. Betingelsen er
  at avstiverne faktisk sitter med to 5×40 i hvert omlegg, i alle fire, og at
  ingen av dem tas ut senere «fordi de bare er pynt». De er ikke pynt — de er
  både denne lastbanen og klemdommen for båndet mellom bordene.
* **Sett en kloss på vangetoppen** — 36×48, 98 mm høy, skrudd på vangens
  innside slik at den fortsetter vangen opp langs hele det øverste bordet — så
  bordet får 48 × 98 mm omlegg å skrus i, akkurat som det nederste. To klosser,
  fire skruer, ingen del flyttes.
* **Skjøt vangen opp til 2037** og skru bordet i den. Det er det tegningen
  hadde, og det er den dyreste av de tre nå som stigen står.

---

## Tegninger

| Tegning | Innhold |
|---|---|
| [byggerekkefolge.svg](schematics/byggerekkefolge.svg) | Oversikt over byggerekkefølgen, med samme nummer som byggesteg og MONTERING |
| [spikerslag.svg](schematics/spikerslag.svg) | Bakveggen som oppriss, X langs veggen og Z opp fra ferdig gulv: sonene som skal ha spikerslag, skravert i sin fulle bredde og høyde, høyderisset som tynn strek, og de ni veggfestene i to rader der de lander. Hver høyde står to ganger — over ferdig gulv, og i parentes som fortegnstall fra høyderisset, som er den du faktisk måler fra på en skjev gulvflate. Det eneste arket som ikke tegner sengen, men veggen — og det eneste som må leses før veggen lukkes. Sonene er modellens `WALL_ZONES` |
| [end-elevation.svg](schematics/end-elevation.svg) | Kortsiden: snitt A–A gjennom endebjelken, med veggen inntegnet. Hele dybden i ett bilde, hver etasje fra gulv til rekkverkstopp, og det arket som viser at sengen er usymmetrisk — bakre stolpe stopper i sengeflaten, fremre går helt opp til rekkverket |
| [ladder-detail.svg](schematics/ladder-detail.svg) | Stigen: vanger, stigeklosser, trinn, J3-skruene, hylla bak trinnet som platen hviler på i **begge** stillinger, og sjaktene ved siden av trinnendene der avstivningslektene løper. Etter X16 er **støttetrinnet** — 682, trinn 2 på den bygde stigen — tegnet som det opplegget bordplaten lander på, og løftesjakten over det er det de øvre trinnhøydene er regnet ut av. Arket sier «stigningen er to løp som møtes på et trinn» og viser hvorfor |
| [bench-detail.svg](schematics/bench-detail.svg) | Benken: vangeenden mot hjørnestolpen uten kloss, vangebiten som ender på stubbefoten, benkespilene og platekanten. Egen plan gjennom J8-Bs sete og skruevinkel |
| [setedetalj.svg](schematics/setedetalj.svg) | Skråskruesetene: snitt langs skrueaksen for begge vinkler, munningen ovenfra med veggen mellom lommene, vinkelklossen eksplodert og klossen i bruk |
| [panel-detail.svg](schematics/panel-detail.svg) | Plateenheten i begge stillinger: plate, to avstivningslekter, to kilelekter, glidesjakten ved trinnenden og skruen nedenfra ut av kontraboret. Ingen ståldel. Bordstillingen er tegnet som **pult** — begge opplegg på 682, forkanten på **støttetrinnet** (X16), og de 214 millimeterne rett løft opp til trinn 4 |
| [bruk-sengestilling.svg](img/bruk-sengestilling.svg) | Sengestillingen i bruk: én som sover i køya og én på nedre soveflate, med rekkverket over kroppen, fri høyde over ansiktet nede og madrassen som er igjen bak føttene. Rett oppriss av langsiden — stolper, stigevanger og trinn, sidevange, begge rekkverksbånd, benkevanger og stubbeføtter står der som de står i modellen, og hver målpil er differansen mellom to Z |
| [bruk-bordstilling.svg](img/bruk-bordstilling.svg) | Bordstillingen i bruk: to sittende på hver sin benkepute, vendt mot pulten, med knærne under platen og sålene på fotbrettet. Fri høyde over hodet, sittehøyde, plate over sete, kne til platekant og fotbrettets høyde |

**Arkene er tegnet om mot V14-geometrien.** De viser 574×798-platen, 750 mm
avstivningslekter, de to skråkappede kilelektene, bordbærelekta som 48×68 på
høykant, navnene sengestilling/bordstilling — og ingen bæreklosser under
bjelke- og vangeender, ingen U-brakett, ingen krokplate og ikke én M6, fordi
ingen av delene finnes. J2, J3
og J8 er tegnet med hodet på vangens innside, slik de skrus.

**Og de er ført videre til X16.** Det er fire ting å se etter, og de står på
arkene nå: trinnoverkantene på **297 / 489 / 682 / 962 / 1242** — stigningen
297 + 192 + 193 + 280 + 280 + 281 — der X9-arket hadde 297 / 572 / 848 /
1073 / 1298 og v15-arket 297 / 542 / 787 / 1032 / 1277; **støttetrinnet** på
682, som er bordplatens underside, der X9-arket hadde to påskrudde bordklosser;
bordbærelekta på Z 614–682 og bordplaten på 700, uendret siden X9; og de to
figurene i `bruk-bordstilling.svg`, som sitter alminnelig med knærne under
platen. Har du skrevet ut et ark før denne runden, er trinnhøydene og klossene
feil på det — se hulltabellen i J4.

**Og videre til X18 der arkene rører den bygde sengen.** `ladder-detail.svg`
har stigen med fire trinn, vangetoppen på 1871 og aksepten av avvik 5 skrevet
på arket; `byggerekkefolge.svg` har steg 9 med rekkverksbåndene der de faktisk
står — **Z 1653–1751 og 1871–1969** — og de åtte avstiverne 23×98 × 180 som
hører med. Står de tegnede båndene der i stedet (var 1708–1806 / 1881–1979),
er arket ditt eldre enn målingen.

**Tre av arkene regenereres av modellen: `setedetalj.svg`, `end-elevation.svg`
og `spikerslag.svg`.** De fire andre er håndtegnet. De er gått gjennom mot
`docs/generated/` og stemmer nå — spilene 23×98, lektene og vangene 48×68,
endebjelken 36×98, kontraboret 41 mm, endespiler og endelister inntegnet, fire
puter à 100 mm — men de har ingen port som holder dem der. Regelen står
derfor: **er et tall på et håndtegnet ark i strid med `docs/generated/`, er det
den genererte tabellen som gjelder.**
