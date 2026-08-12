# PRAKSIS — hvordan HANNA er bygd

Dette er ikke en del av manualen. `docs/hanna.pdf` settes sammen av en
eksplisitt liste i `tools/build_pdf.py` (`REF_DOCS`), og denne filen står ikke
i den. Den er skrevet for den som skal endre modellen eller tegningene, og den
sier hvilke regler som gjelder og hvorfor de er som de er.

De **felles** reglene i snekkerbua — én kilde, assertfilosofien, regler framfor
tilfeller, de allmenne tegnekonvensjonene, filmene og determinismen — står i
[PRAKSIS.md](../../../PRAKSIS.md) på rota. Her står bare det som er HANNAs
eget: delene, leddene, invariantene denne modellen hviler på, og billedspråket
i denne manualen.

---

## 1. Kjeden

Fellesregelen står i [PRAKSIS §1](../../../PRAKSIS.md#1-én-kilde-og-bare-én).
Kilden her er `generate_loftbed.py`, og dette er veien ut av den:

    generate_loftbed.py          modellen: mål, deler, festemidler, asserter
      ├─ tools/gen_doc_tables.py leser modellen → docs/generated/*.md,
      │                          docs/MONTERING.md, byggesteg.json
      ├─ tools/render_lineart.py leser modellen → docs/img/steg-NN.svg/.png
      │    ├─ tools/render_cutpage.py   steg 0 (kappeplanen)
      │    └─ tools/render_panel.py     steg 10 (den løse platen)
      ├─ tools/gen_glyphs.py     ikoner og piktogrammer
      └─ tools/build_pdf.py      setter sammen docs/hanna.pdf av det ferdige

`docs/ASSEMBLY.md` er den ene håndskrevne teksten. Den har lov til å navngi
deler og sitere J-numre, men den skal aldri gjenta et mål som et generert
fragment allerede bærer — den lenker til fragmentet i stedet.

**Hva som gikk galt før.** Leddtabellen fantes to steder: handelsnavn, antall
og forboring i `gen_doc_tables.py`, retning og medlemspar i
`render_lineart.py`. Ingenting bandt dem sammen bortsett fra en setning i hver.
Nå ligger hele `JOINTS` i modellen med maskinfelter, og begge verktøyene leser
den. Det er felles-PRAKSIS §1, funnet på den harde måten: **hvis to filer må
være enige om et tall, er tallet på feil sted.**

---

## 2. De fire assertfamiliene

Hva som gjør en assert verdt å skrive står i
[PRAKSIS §2](../../../PRAKSIS.md#2-assertfilosofien). Modellen har over hundre
av dem, og de faller i fire familier som følger av hva sengen er laget av: tre,
stål og en flate å skru i.

Inndataene er standardene. EC5 gir 3d kantavstand og 4d avstand mellom skruer;
EN 747 gir 75 mm åpning og 160 mm rekkverk over madrassen. Alt som følger av
dem er utregnet.

**Skruelengderegelen.** En gjennomgående treskrue må gå klar gjennom delen den
drives fra og ende inne i den andre:

    tykkelse(fra) < lengde < tykkelse(fra) + tykkelse(inn i)

For de fleste leddene i denne sengen er bare én av de to retningene mulig, og
da er retningen ikke en mening — den er utledet, og tabellen får bare være enig.
Der begge retninger holder målene, bestemmer tabellen, og
`docs/generated/skrueretninger.md` sier hvilke som er hvilke. Der ingen av dem
holder, er det ikke en rett gjennomskrue i det hele tatt, og `drive(...)` må si
det med `exempt=` og en grunn på norsk.

**Passer-på-flaten.** En rad med `n` skruer må ha
`(n-1) × 4d + 2 × 3d` millimeter av kontaktflaten å stå på. Dette er den mest
produktive asserten i filen, fordi antallet skruer i et ledd er akkurat den
typen tall som blir skrevet ned én gang og aldri kontrollert mot treet. Da den
ble slått på, strøk den fire tall som hadde stått uimotsagt: bæreklossene
(36 × 36 mm flate tar én 6 mm skrue, ikke to), stigeklossen, stigevangens
omlegg og beslagflikene. Bæreklossene er siden tatt helt ut av sengen — se
`ASSEMBLY.md` avsnitt 2 — men det var denne asserten som først målte flaten
deres, og det var det ene tallet, 1 skrue og ikke 2, som til slutt gjorde det
tydelig at klossen halverte stålet i stedet for å ta det bort.

Når et antall må ned, er svaret **ikke** å myke opp regelen. Svaret er å
skrive ned den reelle lastveien og regne på den — se den kombinerte
skjærveien i `ASSEMBLY.md` avsnitt 2.

**Kompletthet.** Ingen del får falle mellom to stoler:

* hver eneste tredel må stå i nøyaktig ett byggesteg (`resolve_steps`)
* hvert ledd må finnes så mange ganger i modellen som leddtabellen sier
* handlelista må være summen av de festemidlene som faktisk er plassert
* hver stegside må tegne minst ett feste av hver deletype den lister opp, og
  antallene på tegningen må stemme med antallene i tabellen (`check_coverage`)

Den siste er verdt å merke seg: den fanger ikke feil geometri, den fanger
**tause tegninger** — en kloss som står i deletabellen og aldri blir vist
festet noe sted.

**Orientering.** Et beslag som er skrudd fast i tre er ikke nødvendigvis
riktig vei. Vinkelbeslaget under bordbærelekta kan snus opp ned og fortsatt
treffe tre med begge flikene — det treffer bare oversiden av lekta i stedet for
undersiden, og lekta henger plutselig i to skruer i uttrekk i stedet for å stå
på stål. Derfor to asserter, ikke én:

* hver flik må ha tre bak seg i sin egen skrueretning, og
* et beslag som **bærer** noe (`bears=`) må ha den vannrette fliken skrudd rett
  opp, i undersiden av delen det bærer.

### Unntaket: delen som ikke er en boks

Modellen har hatt én invariant siden første linje: **hver tredel er en
akseparallell boks.** Det er den som gjør `.extents` til hele sannheten om en
del, og det er den «alt treverk er bokser» i §3 hviler på. V4 bryter den
nøyaktig én gang: de to fremre kilelektene under platen — vingene, M5 — er
skråkappet, 73 mm dype ved roten og 27 ved spissen.

Det er trygt, og grunnen er at **paringsflatene fortsatt er rektangler**. Vingen
møter platen over hele sin 116 × 48 mm toppflate, og den møter ingenting annet.
Flaten som ble kappet, er undersiden, og den berører ingen del i noen av de to
stillingene. `contacts()`, `patch_window()` og `bearing_area()` ser derfor
nøyaktig det de så før.

Delens `.extents` er med vilje fortsatt hele den omskrevne boksen. Da er hver
eneste klarings-, sveip- og overlappassert som leser `extents` fremdeles sann —
og den er nå **konservativ**, fordi den virkelige kroppen ligger strengt
innenfor den boksen assertene rydder plass til.

Det som **ikke** er konservativt, er alt som leser VOLUM eller tegner
SILHUETT. Begge deler leser soliden, ikke boksen, og skal fortsette å gjøre det.

Regelen videre: **en del som ikke er en boks er tillatt bare når paringsflatene
forblir rektangulære og den omskrevne boksen er den konservative konvolutten.**
Alt annet går tilbake til bokser.

### Referansekroppen: den fjerde kategorien

Sengen er laget av **tre** (kappes, står i lista, skrus), av **stål** (kjøpes,
står i lista, drives) og av **skum** (kjøpes, står ikke i kapplista, legges
på). Referansekroppen er den fjerde: **den er grunnen til at de tre andre
finnes.** Madrassen har vært en referansekropp siden begynnelsen; V14 legger
til fire barn — to som ligger i sengestilling, to som sitter i bordstilling.

Kategorien har madrassens regel, ord for ord:

* egen fargegruppe (`figures`), egen farge i STEP/GLB/USDZ;
* **ute** av kapplista, kontaktsjekken, sammenhengssjekken og
  overlappssjekken — den bærer ingenting og røres av ingenting;
* **inne** i `parts.tsv` (en diff på den er diffen på modellen) og i
  eksportene.

Ett tillegg som madrassen ikke trenger: kroppen er heller **ikke** i
`display_parts()`. Den lista er *sengen* — filmene, stegtegningene og
platesveipets kollisjonsprøve er bygd på den, og en kropp i en kollisjonsprøve
som handler om tre, ville felt en film som handler om tre. `scene_parts()` er
`display_parts` + kroppene, og det er dét som eksporteres.

**Boksinvarianten holder, og første halvdel er gratis her.** For kilen måtte
det argumenteres at paringsflatene fortsatt er rektangler; en kropp har
**ingen paringsflate i det hele tatt**. Den skjøtes ikke, så `contacts()`,
`patch_window()` og `bearing_area()` blir aldri spurt om den. Igjen står den
konservative halvdelen: `.extents` er den omskrevne boksen, og alt som leser
den, rydder mer plass enn kroppen tar. Tallene som **publiseres**, måles
likevel på soliden og aldri på boksen — den omskrevne boksen rundt et barn i
skredderstilling er en kube på 700 mm og sier ingenting sant om rommet over
hodet.

**Antropometrien er offentlig:** AnthroKids, de digitaliserte
Snyder-studiene fra 1975/1977
([math.nist.gov/~SRessler/anthrokids/](https://math.nist.gov/~SRessler/anthrokids/)).
Hvert segment er en brøkdel av ståhøyden H = 1200 mm (50-persentil ~6–8 år,
alderen EN 747 åpner overkøya i), og modellen leser de fem nøkkelmålene —
sittehøyde 0,545 H, knehasehøyde 0,28 H, knehøyde sittende 0,30 H,
skulderbredde 0,21 H, hodehøyde H/6 — **tilbake ut av den ferdige soliden** i
en assert. En figur som ikke lenger er 1200 mm høy, er ikke et måleinstrument.

**Klaringene er trykt, ikke assertert.** De harde assertene i denne modellen
handler om tre som må passe. Det ene som *er* assertert om kroppene, er at
ingen av dem ligger inne i noe tre eller stål; skummet er unntatt med vilje —
en pute på 100 mm tar rumpa 12 mm inn og hodet 22 mm ned i soveflaten, og en
figur som svevde oppå skummet i stedet, ville vært tegningen som lyver.

---

## 3. Festemidlene som geometri

### Grensen

Festemidlene er **modellert**, men de er ikke deler. Grensen går her:

| Er med | Er ikke med |
|---|---|
| `FASTENERS` (egen liste) | `parts` |
| `display_parts()` | `mode_parts()` |
| egen fargegruppe i `.usdz` | `CUT_LIST`, `parts.tsv` |
| tegningene | overlapp- og sammenhengssjekken |

Grunnen er enkel: en skrue **overlapper med vilje** de to delene den binder
sammen, så den ville strøket på overlappsjekken øyeblikkelig. Og en skrue er
ikke noe man kapper, så den har ingenting i kapplista å gjøre. `parts.tsv` er
byte-identisk med og uten festemidler, og det er en test i seg selv.

### Formen

En skrue er hode, forsenking, skaft og spiss. **Ingen gjenger i SOLIDEN.** En
modellert gjenge koster tusen trekanter for null lesbarhet i en 3D-visning.
Gjengen finnes bare i strektegningen, som en tegnet bølge langs konturen — se
«Én skrue, ett billedspråk» i §4 — og den er en tegnekonvensjon, ikke geometri.
Beslagene er bøyde plater bygd av bokser.

Et vinkelbeslags **andre** flik er ikke en ny rad med data. Den faller ut av
den første: en rett vinkel gjør `run` om til den andre flikens skrueretning og
drivvektoren om til retningen den fliken går. Det er derfor
orienteringsasserten i det hele tatt lar seg skrive.

### Nettene

En skrue er den eneste krumme kroppen i modellen, og på standard 0,001 mm
avvik trianguleres én skrue til flere trekanter enn hele sengen. Stålgruppen
eksporteres derfor på 0,15 mm.

**Rekkefølgen er ikke likegyldig.** OCC bufrer en triangulering på formen og
bytter den bare ut når det blir bedt om en *finere*. Gruppe-eksporten må derfor
kjøre **før** enkeltmesh-eksporten, ellers blir toleransen stilltiende ignorert.
Alt treverk er bokser — med det ene unntaket i §2, de to kilene, som ikke er
bokser, men som er like plane — og en plan flate trianguleres til de samme to
trekantene uansett avvik, så treet blir byte-identisk uansett.

---

## 4. Billedspråket i denne manualen

De allmenne konvensjonene — prikket linje mot pil, eksplodert langs
innsettingsaksen, stiplet for skjult, svart mot grått, ett steg per side, og
den ene pennen — står i
[PRAKSIS §4](../../../PRAKSIS.md#4-tegnekonvensjoner-som-holder-på-tvers).
Denne manualen har tatt dem i bruk bevisst. Pennen er `tools/layout.py`
(`RATIOS`), `Theme` deler den ut, og tallet er sengens egen bbox-diagonal delt
på 400, så alle tolv sidene følger den.

Ett tillegg til eksplosjonsregelen er HANNAs eget: **et beslag har ingen egen
akse og følger sine egne skruer ut**, med samme sprang som dem — «Kjeden i et
beslaghjørne» nedenfor.

### Skala

Én frihet er tatt utover pennen, og det er den samme enhver beslagtegning tar:
**diameteren er overdrevet**, med faktor `SCREW_FATTEN` — som står i
`tools/layout.py` sammen med pennen, fordi det er én knapp for hvor stort et
festemiddel tegnes. En 6 mm skrue på en to meter bred side er tynnere enn
streken sengen selv er tegnet med. **Lengden er sann**, med et gulv på
`FORESHORTEN_FLOOR` mot ren forkortning: en skrue drevet inn i papiret skal se
kort ut, men den skal fortsatt se ut som en skrue.

**Burde gulvet vært høyere for KORTE skruer?** Det er den nærliggende
innvendingen — en brøk behandler en 5×40 og en 6×120 likt, og det som gjør en
silhuett til en SKRUE er ikke lengden i millimeter, men hvor mye lengre den er
enn hodet er bredt. Hodet krymper ikke når lengden gjør det. Så sidene ble
målt, hver tegnet kropp mot sitt eget tegnede hode:

| Hoder lang | Hvem |
|---|---|
| 1,81–1,82 | 5×40, J10 (steg 5) og J12 (steg 1) — de korteste i boka |
| 2,22 | 5×60, J7 (steg 9) — den korteste GULVET selv lager |
| 2,3–5,1 | alt annet |

Svaret er nei, og målingen er hvorfor. De stubbete kroppene er ikke gulvet i
det hele tatt: en 5×40 projiseres i denne vinkelen til 35,6 av sine 40 mm, godt
klar av 28,8, så gulvet rører den aldri og et høyere gulv når den ikke. Og det
ville ikke nådd langt om det gjorde: et gulv får aldri tegne en skrue LENGRE
enn den er, så alt en kort skrue kan hente er de 12 % opp til sine sanne 40 mm
— 1,81 hoder blir 2,05, og det er ingen som ser. Det som avgjør hvor stubbet en
40 mm skrue ser ut, er hodet, altså `SCREW_FATTEN`, og det tallet ble avgjort
på sin egen prøve.

Innvendingen fortjener derfor ikke en knapp til, men en **snubletråd**:
`STUB_ASPECT` = 1,75, og `assert_no_stubs()` måler blekket. Ingen tegnet kropp
får komme ut kortere enn 1,75 av sitt eget hode. Verdien ligger like under det
sidene måler i dag, så den dagen et nytt kamera, en kortere skrue eller et
bredere hode lager en ekte pil av en av dem, stopper bygget og et menneske ser
på den — i stedet for at manualen stille skaffer seg en pilspiss der det skulle
stått et festemiddel.

### Én skrue, ett billedspråk

**Silhuetten finnes ett sted: `gen_glyphs.screw_profile()`.** Katalogglyfen i
beslagtabellen, raden i innsettpanelet og skruen som tegnes inn i selve
stegtegningen er den samme konturen, lagt inn i hvert sitt koordinatsystem —
forsenket hode, kjerne, gjenge, spiss.

Det var ikke slik før, og det er den feilen dette avsnittet finnes for.
Stegsiden tegnet sin egen sju-punkts kapsel: en flens i den ene enden, en pigg
i den andre, ingenting imellom. Blåst opp 3,0 ganger leste den som en **pil** —
og pil er reservert for tredeler som skal føres på plass, så siden brukte
byggerens ene formkode til å si feil ting. Samtidig sto den ekte silhuetten
i panelet ti centimeter unna. To billedspråk for én ting er det en
monteringsanvisning ikke har råd til, for det er formen leseren kjenner delen
igjen på.

Med den ekte konturen bærer formen gjenkjenningen, og faktoren trenger bare
bære størrelsen: **`SCREW_FATTEN` er 2,0** (var 3,0). Hodet er
`HEAD_DIA_RATIO` = 1,95 nominelle diametre og kjernen 0,72, så en 6×90 er
23,4 mm over hodet og 8,6 mm over kjernen der den før var 34 og 18. Siden har
fått en tredjedel av blekket sitt tilbake. `W_SCREW` fulgte med ned, fra 0,60
til 0,40 penn: konturen er streken rundt et ti millimeter bredt objekt, ikke
rundt sengen, og på 0,60 var skruen en svart splint med ingen plass til
fyllkoden inni seg.

**Gjengen er en tekstur, og en tekstur følger rasteret** — nøyaktig samme regel
som fyllkoden har (`gen_glyphs.thread_pitch`). Stigningen er den groveste av

> **formkravet** 1,15 × d, og **oppløsningskravet** at én TANN — en halv
> periode — aldri blir under `THREAD_MIN_PX` = 4,5 piksler der siden faktisk
> rastres.

Blir det da færre enn `THREAD_MIN_PITCHES` = 2,5 hele omdreininger igjen på
den gjengede strekningen, tegnes ingen gjenge: konturen faller tilbake på sin
egen omhyllingskurve — samme hode, samme kjerne, samme spiss, uten bølgen. Det
er én nedgradering, ikke et annet billedspråk.

Beviset ble tegnet, ikke argumentert. De to stedene endringen ble bedømt på er
hjørnet på steg 1 og stubbefotklyngen på steg 5, klippet ut av de ferdige
sidene før og etter (`docs/preview/krop-steg1-*.png`,
`krop-steg5-*.png` — `docs/preview/` er gjennomgangsmateriale og er ikke
sjekket inn, se `.gitignore`). Skal formen endres igjen, klippes de to samme
utsnittene på nytt: det er der en pil ser ut som en pil.

To ting til er verdt å vite. **Stigningen regnes av SANN diameter, ikke tegnet.**
Licensen er bredde; en stigning er et mål langs skruen, og regnes den av den
feite bredden dobles den sammen med bredden mens lengden står — da får en 5×40
to omdreininger på siden der glyfen viser sju. **Og siden må kjenne rasteret
sitt før den tegner**: `Page.px_per_unit` settes i `render_step()` med én gang,
ikke først i `write()`, fordi gjengen velges mens skruen tegnes.

### Kjeden i et beslaghjørne (R9)

**Et beslag og skruene som holder det er én demontering, ikke tre.** R1 sier
hvilken vei et beslag går av — minus resultanten av drivvektorene til skruene
som holder det — og det er en opplysning om leddet, ikke om papiret. Men den
sa ingenting om hvor LANGT, og ingenting i det hele tatt om skruene som går
gjennom beslaget. De to taushetene er det J12-hjørnet på steg 1 var ulesbart
av: beslaget fløt så langt av setet som papiret tillot, skruene bakket ut av
det med hvert sitt sprang som ikke hadde noe med beslagets å gjøre, og de tre
prikkede linjene skar hverandre midt i et hjørne leseren ser på som ett stykke
arbeid.

Regelen er **ett sprang, `d`, for hele klyngen**:

    sete --d--> beslaget --d--> hver av beslagets egne skruer

Beslaget står `d` fra setet langs demonteringsretningen. Hver skrue som sitter
i beslaget fortsetter fra der BESLAGET havnet, langs sin egen drivakse — som
aldri bøyes — til avstanden fra tegnet spiss til hullet i det flyttede
beslaget også er `d`. To like sprang leses som én bevegelse utover; tre ulike
leses som tre uhell som tilfeldigvis peker samme vei.

Det som fortsatt er fritt er `d` selv, og friheten tilhører KLYNGEN. Finnes det
ikke plass, tas et lengre slag — av alle sammen, samtidig. En enslig skrue som
lander oppå en annen kropp køer seg én kroppslengde lenger ut langs sin egen
akse (R2); en skrue i en klynge får ikke, for en køet skrue er en skrue ute av
takt. Stubbefothjørnet på steg 5 — fire 5×40 og en vinkel — trenger det andre
slaget; J12s to greier seg med det første.

To asserter holder den, og begge måler blekket:

* **Takten** (`assert_chain_rhythm`). Hver prikket linje i klyngen leses der
  den landet, og de skal være like lange. Slarken er 2 % av spranget, fordi
  beslagets lenke er flytevektoren nøyaktig mens skruens leses av spissen på
  den tegnede silhuetten — samme tall kommet fram to veier.
* **Nøstingen** (`assert_chain_untangled`). Ingen skrues linje krysser
  beslagets egen lenke tilbake til setet, og ingen linje går tvers gjennom en
  kropp i sin egen klynge. Det første er selve påstanden kjeden gjør; det
  andre er at en prikket linje gjennom en silhuett leses som silhuettens egen
  vei.

**Det som IKKE er asserta, og hvorfor.** To SØSKENLINJER som møtes like ved
beslaget. J12 driver én 5×40 inn i stolpen og én opp i lekta, i rett vinkel,
gjennom to hull som ligger 17 mm fra hverandre på papiret — og dette kameraet
setter lektaskruens hull på andre siden av stolpeskruens egen akse. Da må de to
møtes, og de møtes i et punkt på den aksen som ingen takt kan flytte: kortes
spranget, flytter krysset seg fra den prikkede linjen over på den SOLIDE
kroppen, som er verre. Det er en opplysning om hvor leddet ses fra, ikke et
valg tegningen tok, og reglene her asserter bare det tegningen kan adlyde.

**Merket til et beslag står på randen, ikke oppå.** Et vinkelbeslag 40×40 og et
merke på 49 mm er omtrent like store, så et merke som oppfyller R6 ved å sitte
PÅ beslaget, oppfyller den ved å SKJULE det — og leseren sitter igjen med en
bokstav der delen skulle vært. Halen merket søker ut fra ligger derfor på
beslagets egen utoverkant, den siden som vender fra setet, så det første
kandidatpunktet er et merke som tangerer platen i stedet for et som dekker den.

Beviset ble tegnet, ikke argumentert, i de to samme utsnittene som formvalget
ble avgjort i: `docs/preview/krop-steg1-v3.png` og `krop-steg5-v3.png`.

### Merking og sammenslåing

* **Bokstav i ring** (Ⓐ, Ⓑ …) knytter et festemiddel på tegningen til en rad i
  tabellen under bildet. Rekkefølgen er «flest først, uavgjort brytes på navn»,
  og både `gen_doc_tables.py` og `render_lineart.py` regner den ut av de samme
  radene, så de kan ikke bli uenige.
* **Fyllkoden: bokstaven én gang til, som mønster.** Et hjørne med fire
  festemidler i tvang leseren til å finne og lese et 5 mm tegn for å se hvilken
  skrue som var hvilken. Hver bokstav har derfor sitt eget fyll, og skruens
  silhuett bærer det — på stegtegningen, i snittene i innsettpanelet, i
  panelraden og i stegets egen festetabell:

  | | Fyll | Hvorfor der |
  |---|---|---|
  | Ⓐ | åpen | flest av — sekston heldekte skruer ville sortnet siden |
  | Ⓑ | skravert | |
  | Ⓒ | krysskravert | grovere rute enn Ⓑ, ellers er de to bare to gråtoner |
  | Ⓓ | heldekt | sjeldnest, og oftest et vinkelbeslag, som er heldekt fra før |

  Koden er redundant med vilje: formen skiller 5×40 fra 6×120, men ikke 6×80
  fra 6×90; bokstaven krever at leseren finner og leser et lite tegn; sammen
  holder de hverandre oppe, og ingen av dem trenger farge.

  **Men bare der formen faktisk svikter.** Fyllet er ikke gratis: det legger et
  mønster i hver eneste skrue på siden, og på en side der silhuettene skiller
  seg fra hverandre helt av seg selv gjør det bare siden travlere. Koden ble
  kjøpt for ett problem, og betales bare der problemet finnes. Vilkåret er
  regnet ut, ikke vurdert — to festemidler på samme side er **tvetydige av
  form** når

  > lengdeforskjellen er under **25 %** av den lengste, **og** diameterne er i
  > samme klasse (like) eller skiller seg med høyst **1 mm**.

  Finnes ett slikt par på siden, kodes **hele** sidens sett; finnes det ingen,
  står alle festemidlene i ren kontur, med bokstaver og antall som før. Hele
  settet, ikke bare paret: kodede og ukodede skruer om hverandre på ett ark er
  en tredje opplysning ingen har lært leseren.

  Tallene står ett sted, i `gen_glyphs.ambiguous_pairs()`, og svaret følger
  steget ut i `byggesteg.json` som `fill_code` — utledet av leddataene, ikke
  skrudd på for hånd (se §5). Med dagens ledd slår regelen til på **ett** steg:
  steg 5, der Ⓑ 5×70 og Ⓒ 6×80 er 12,5 % og ett diametertrinn fra hverandre.
  Steg 1 (6×90 mot 6×120) og steg 6 (5×60 mot 6×80) ligger begge på nøyaktig
  25 % og faller utenfor.

  **Ett mønster per silhuett (R8).** Gjengen og fyllkoden er to teksturer av
  samme størrelsesorden inne i en kropp som er ti–tolv millimeter bred, og
  legges de oppå hverandre leses ingen av dem — skraveringen og gjengetennene
  går sammen til et tauverk, og Ⓑ og Ⓒ blir like. Prøven ble tegnet begge
  veier før valget: med begge er B og C to teksturerte tau, med én hver er B
  rene parallelle streker og C rene ruter.

  Derfor tar koden kroppen fra gjengen — **men bare der koden faktisk ER et
  mønster**. `open` er fraværet av ett, og den deles ut til den bokstaven siden
  har flest av, så den vanligste skruen på en kodet side (seksten av tjue på
  steg 5) beholder gjengen sin og ser ut som det samme objektet den er på alle
  andre sider. Ingenting konkurrerer med den der, så ingenting er kjøpt ved å
  ta den bort. Regelen er `render_lineart.thread_cues()`, og
  `fyllkontrast.png` tegnes med den, ellers beviser prøven en tegning manualen
  ikke lager.

  **Retningen er asserta, ikke fyllet.** `render_lineart.assert_fill_code_rule()`
  måler det som ble tegnet: en side med et tvetydig par som likevel kom ut uten
  fyll stopper bygget — der har leseren ingenting igjen å skille de to på. Den
  motsatte feilen, fyll på en side som ikke trengte det, er en rapportlinje og
  ikke en stopp: den koster blekk, ikke anvisning.

  **Settet er bevist, ikke valgt.** `python tools/render_lineart.py
  --fill-contrast` skriver `docs/preview/fyllkontrast.png`: hver kode i den
  størrelsen den minste bokstavsiden faktisk gir en skrue, i innsettets
  størrelse, og i halv størrelse som stresstest. Prøven blir stående selv om
  bare én side i dag bruker koden: den er dokumentasjonen på hvorfor settet ser
  ut som det gjør, og den skal leses igjen den dagen et ledd bytter skrue.
  Prøven avgjorde to ting som
  ikke lot seg resonnere fram — **hodet alene kan ikke bære koden** (et
  forsenket hode er en 5 mm flens, sju piksler på siden, og der er alle
  mønstrene like, så hele silhuetten fylles), og **krysskraveringen må ha
  grovere rute enn skraveringen**. Skal settet endres, endres prøven først.
  Beslagene står utenfor: en vinkel er allerede en heldekt plate, og et mønster
  oppå den ville lest som en tredje slags flate.
* **En stegside med bare én type festemiddel får ingen bokstaver.** Ikonet i
  tabellen er allerede hele svaret — og da er det heller ingen fyllkode, for en
  kode med bare én verdi koder ingenting.
* **Antallet står ikke i bildet.** Hver skrue steget driver tegnes som sin egen
  kropp, så «2×» ved siden av én av dem sier ingenting bildet ikke sier.
  Antallene står i innsettpanelet og i stegets tabell, der tall leses i stedet
  for å telles. Kontrollen svekkes ikke av det: `check_coverage` teller
  KROPPENE siden har satt av, ikke tallene den har trykt.
* **Ett merke per tegnet kropp (R4), og bare én kropp der to silhuetter faller
  sammen (R2).** Spørsmålet er ikke hvor langt fra hverandre to festemidler er
  — det er om de to SILHUETTENE siden tegner havner på samme papir. To som gjør
  det kan bare tegnes én gang, og det ene merket står da for begge (antallet
  ligger i panelet). To som ikke rører hverandre er to ting leseren kan telle,
  selv 30 mm fra hverandre, og da er de to merker. Blir det trangt, er svaret
  ikke å slå dem sammen, men det ene trekket et eksplodert festemiddel uansett
  har: lenger ut langs sin egen akse. Begge deler er asserter som måler blekket
  (`assert_bodies_apart`).
* **Kontakt eller leder (R6).** Et merke skal enten RØRE en av kroppene det
  navngir — sitte på hodet som et flagg på en stang — eller ha en tynn strek
  inn til den.
  Det finnes ingen tredje plass. Et merke som svever ved siden av en klynge er
  ikke en anvisning, det er en gåte, og på steg 5 sto det tre av dem og gjettet
  samtidig. Regelen er priset inn i `layout.place()` — kontakt er verdt mer enn
  hvilken som helst mengde hvitt papir — og `assert_badges_anchored()` måler
  den etterpå av blekket: rører merket sin egen kropp, ender lederen på den, og
  starter den i merkets egen rand.
* **Ett merke per type per klynge (R7).** Åtte like bokstaver nedover en
  stigevange er ikke åtte opplysninger, det er én, gjentatt til den blir tapet
  — og tapetet er det som trenger bort merket som faktisk sier noe nytt.

  Første versjon av regelen slo sammen et LØP: samme bokstav, samme ledd,
  kroppene i en ubrutt kjede, ingenting fremmed imellom. Den var for forsiktig
  til å hjelpe der det trengtes. Stubbefothjørnet på steg 5 kom ut med elleve
  bokstaver over to ledd, fordi to ledd er to ledd og fordi Ⓓ-beslaget sto midt
  i hvert eneste løp og brøt det. Elleve bokstaver for FIRE slags festemidler,
  i et hjørne leseren ser på som ett stykke arbeid.

  Enheten er derfor ikke løpet, men **stedet**. En klynge er alt som ligger
  innenfor `CLUSTER_R_BADGES` = 16 merkeradier fra en kjerne — uansett ledd,
  uansett type — og inne i én klynge bærer hver TYPE nøyaktig ett merke, det
  første i sidens egen tegnerekkefølge. Merket står for hele familien sin.
  Innsettpanelet er fortsatt hele nøkkelen: hver type på siden har sin rad der,
  med antall, så ingenting av det leseren blir fortalt er borte — bare hvor
  mange ganger.

  Klyngen er en KULE og ikke en kjede, med vilje. Kjeding er transitiv, og på
  en side som spilefeltet ville én kjede slukt hele sengen og latt én bokstav i
  et hjørne stå for tjueåtte skruer en meter unna. En kjerne og en radius kan
  ikke gjøre det: et merke er aldri lenger fra kroppen det står for enn radien
  regelen er skrevet med.

  To asserter holder den ærlig, og begge måler blekket. **Dekning**
  (`assert_badges_cover`): hvert eneste tegnede festemiddel med en bokstav må
  ha den bokstavens merke blant merkene som står for NETTOPP DET — ikke et
  merke et sted på siden, ett hvis egen familie det er i. **Eierskap** (R5, i
  `assert_badges_anchored`): merket må ligge nærmere ETT AV medlemmene i sin
  egen familie enn noen fremmed kropp. Det er den gamle regelen med «min»
  utvidet fra én kropp til familien — som er nøyaktig det merket nå navngir.

  Resultatet, side for side: 5 → 4 merker på steg 1, 7 → 3 på steg 3, 11 → 7 på
  steg 5, 26 → 7 på steg 6, 6 → 6 på steg 9. 55 bokstaver ble 27.

  **Tillegget: en familie må SE UT som én, og den må være innen rekkevidde.**
  Sammenslåingen er kjøpt med et argument om BILDET — leseren ser en rekke av
  det samme og trenger å få det sagt én gang — og argumentet svikter i det
  bildet slutter å gjenta seg selv. Derfor to kutt til gjennom hver type, og de
  spør hver sin ting.

  *Homogenitet.* Spredningen i TEGNET lengde inne i familien,
  (lengste − korteste) / lengste, høyst `HOMOGENEITY_SPREAD` = 25 %. Det er den
  samme fjerdedelen fyllkodens tvetydighetsprøve bruker, og av samme grunn:
  under en fjerdedel er to lengder én lengde for øyet, over den er de to ting.
  Er typen ikke homogen, slås den ikke opp i sine enkeltdeler, den KUTTES i
  gapene: åtte like stigeskruer og én forkortet raring er ni kropper, to
  utseender og to merker. `assert_badges_homogeneous()` måler det på blekket —
  lengdene leses ut av `Page.record`, av de silhuettene som faktisk ble tegnet.

  *Rekkevidde.* Klyngen er en kule om en KJERNE, så to av medlemmene kan ligge
  to radier fra hverandre selv om ingen av dem ligger mer enn én radie fra
  kjernen — og da er regelens eget løfte («et merke er aldri lenger fra kroppen
  det står for enn radien») brutt. Samme grådige kule, kjørt inne i typen,
  holder løftet: den første kroppen i tegnerekkefølgen tar inn alt innenfor
  rekkevidde av seg selv, og resten sår neste merke. Asserten står i
  `assert_badges_anchored()` sammen med de andre målingene av merket.

  Med dagens sider slår **homogenitetskuttet ikke til noe sted**: J12-paret som
  saken begynte i måler 36,5 og 35,6 mm på papiret — 2,5 % fra hverandre, altså
  én ting sett to veier — og deler Ⓑ som før. Rekkeviddekuttet slår til ett
  sted: de to stubbefotbeslagene på steg 5 ligger 437 mm fra hverandre i én og
  samme klynge, og uten kuttet ville det andre hjørnets vinkel stått uten
  bokstav med sin egen Ⓓ en halv side unna.
* **KROPPER slås aldri sammen på tvers av ledd.** Regelen ble skrevet på steg
  3, der endebjelkens to 6×90 og bæreklossens ene møttes i det samme hjørnet
  og «3×» ville sendt byggeren til feil hull. Klossen er borte nå, men
  regelen står: to ledd i samme hjørne er to kropper. Regelen er ett flagg i
  `render_lineart.py` (`MERGE_ACROSS_JOINTS`), så den er en linje å snu og
  ikke en antakelse å lete etter — men den står av, og tegningene er tegnet
  med den av.

  Merk forskjellen fra R7: den regelen slår sammen BOKSTAVER og går gjerne på
  tvers av ledd, fordi en bokstav bare peker på en rad i en tabell. Denne
  regelen slår sammen KROPPER og et antall, og et antall i feil hull er en feil
  anvisning. Hver skrue tegnes fortsatt som sin egen kropp der den er sin egen
  kropp.
* **Et merke ligger nærmere sin egen familie enn noe annet (R5).** Et badge
  ved siden av feil skrue er ikke en trang tegning, det er en feil anvisning.
  Regelen er en assert som måler blekket: merkene leses ut av `Page.record`
  der de LANDET, og hvert av dem må ha en av kroppene det står for som
  nærmeste kropp — målt mot kroppenes egne kapsler, ikke mot punkter i
  nærheten av dem.
* **Innsettpanelet har ingen lederlinjer (R3).** Bokstaven knytter allerede
  merket til raden i panelet, og den gjør det for alle merkene — ikke for de
  fire som tilfeldigvis lå nærmest. Lupen er noe annet og blir stående: den
  bærer virkelig strektegning, og den korte lederen sier hvilket sted som er
  forstørret. R6-lederen er en tredje ting igjen: den er kort, den går fra ett
  merke til den ene kroppen merket navngir, og den finnes bare der merket ikke
  fikk plass oppå den.
* **Ingenting forsvinner.** Et merke som blir trengt bort gir antallet sitt til
  merket som trengte det bort, og `check_coverage` sammenligner totalen med
  stegets egen tabell. Og et merke som ble slått sammen slik at en DEL mistet
  sin eneste visning, får merket sitt tilbake (`restore_orphans`).
* **Over `EXPLODE_MAX` merker på én side** bytter siden til fantomstil.
  Tjueåtte skruer hengende i lufta over en seng er en hekk, ikke en anvisning.

### Ikonspesifikasjon

`tools/gen_glyphs.py` tegner alt som ikke er en projeksjon av sengen.

* **Festemiddelikonene** tegnes i én felles skala og bærer den i `viewBox`-
  høyden sin, så en 6×120 forblir lengre enn en 5×40 også inne i panelet på
  stegsiden. Navnene leses ut av `docs/generated/beslagliste.md`, så en ny
  skruestørrelse i leddtabellen gir et nytt ikon uten at noen rører glyphfila.
* **Piktogrammene** («før du begynner») er Lucide-baserte, ingen fyll, ingen
  tekst i ikonet. `docs/icons/lucide/` er **vendoret, ikke
  speilet**: der ligger bare de ikonene `PICTOGRAMS` faktisk slår opp, og
  ingenting annet. Et ikon som ikke står i den tabellen skal ut av katalogen —
  ellers vokser den til et halvt ikonbibliotek som ingen bygger leser og ingen
  lisensfil dekker meningsfullt. (Fem ubrukte ble slettet i denne runden:
  `baby`, `hammer`, `pencil`, `person-standing`, `phone`. `book-open` gikk
  samme vei da «blyanten først» avløste «les steg 0 først»-raden.)
* **To strektykkelser, og bare to.** `PICTO_STROKE` — 1,25 av 24 enheter — er
  vekten til alt som er en TING: verktøy, deler, senger, vegger, piler, hake og
  kryss. Menneskefiguren har sin egen, `FIGURE_STROKE`, som er halvparten.
  Skillet er ikke at mennesker skal være finere. På en ting er streken en
  **kant** rundt et volum, og tykkelsen leser som blekk; på en strekmann **er**
  streken kroppen, og tykkelsen leser som kroppsmasse. Derfor er det bare
  figuren som tynnes — en tynnere kant hadde bare gjort siden lysere uten å
  gjøre noe lettere.
* **Forholdet er målt, ikke gjettet.** Kilde: IKEAs egen anvisning til MYDAL
  køyeseng, `AA-2207941-1`, side 2, rendret i 600 dpi med `pdftoppm`. Målt to
  veier — perpendikulær strekbredde i pikslene, og etterpå mot PDF-ens egne
  `w`-operatorer, som ga samme svar.

  | målt på IKEA-mannen | piksler @600 dpi | forhold |
  |---|---:|---|
  | strekbredde | 17 (= 0,71 mm = 2,0 pt) | — |
  | hodediameter (ytre) | 293 | strek = **5,8 %** av hodet, altså **1:17** |
  | figurhøyde | 1091 (= 46 mm) | strek = **1,56 %**, hode = **26,9 %**, figuren 3,7 hodehøyder |

  Og en advarsel mot å lese dette for fort: **IKEA-mannen har den tykkeste
  streken i hele dokumentet**, bortsett fra det store nei-krysset (5,5 pt).
  Verktøyikonene deres er 1,0 pt — halve mannen — og beslagene i delelisten
  0,75 pt. Hierarkiet deres er det motsatte av vårt.

  Grunnen til at figuren deres likevel ser fin ut i streken, og vår ser tung ut,
  er ikke vekten. IKEA-mannen er en **kontur rundt en hvit kropp**, tegnet i
  46 mm: streken er kanten, kroppen er papiret, og da kan kanten være tung uten
  at figuren blir det. Vår er en **strekmann i 16 mm** — streken *er* kroppen.
  Det som da lar seg flytte over er forholdet inne i figuren: strek mot hode,
  1:17 hos dem, 1:3,7 hos oss.

  Hele veien til 1:17 går ikke: det blir 0,27 enheter = 0,22 mm, og en strekmann
  i 0,22 mm er grå, ikke svart. Prøven viser at den gråner allerede ved 0,4
  enheter når ikonet settes i 72 px, som er det Markdown-manualen setter det i.
  **Halve piktogramstreken** er det tynneste som er svart i begge medier —
  0,5 mm på papir i 19 mm, 1,9 px i 72 px — og den tar figuren fra 1:3,7 til
  1:7,4. Verktøyene og tingene beholder piktogramstreken, altså stikk i strid
  med IKEAs rangering; bevisst, fordi deres rangering følger av en 46 mm
  silhuett og vår av en 16 mm strekmann. Tegnes figuren om til silhuett en dag,
  snur den tilbake.

  **Hodet ble stående.** IKEAs hode er 26,9 % av figurhøyden, vårt 22,4 %. Å
  vokse dit ble prøvd og forkastet: hodet spiser da blyanten bak øret, og
  blyanten er den ene detaljen på siden som var vanskelig å få til å lese.
* **Figuren er ett skjelett tegnet fire ganger.** `to-personer`,
  `en-person-nei`, `blyant-foerst` og `skrutrekker-foerst-nei` deler hode
  (`r="2"`, ytre diameter 4,6 enheter), hals som starter nøyaktig på hodets
  sirkel, skulderpunkt i 8,6 og bein som spriker 0,5 til siden per enhet
  nedover. Bare posituren skiller dem. Ikonfila sier bare **hva** som er figur —
  `class="figur"` på gruppen figuren ligger i — og `gen_glyphs` bytter merket
  mot vekten når ikonet settes sammen. Vekten står ett sted, ikke fjorten;
  merket i en vendoret Lucide-fil stopper bygget, for da er en fil som skulle
  ligge urørt blitt rørt.
* **Merkebokstavene** er ett tegn i en sirkel, samme radius overalt.
* **De kodede glyfene.** Der et steg koder festemidlene sine, skrives
  skrueglyfen også i sin egen fyllkode (`treskrue-5x70-hatch.svg`), og det er
  den fila både innsettpanelets rad og stegets tabell bruker. Hvilke par som
  finnes bestemmes av STEGENE — av hvem som deler ut bokstaver **og** hvem
  regelen over slår til på; et par ingen side viser er en fil ingen leser, og
  den skal ut av katalogen. En side uten fyll bruker den bare glyfen, så
  tabellen viser det tegningen viser. Beslagsiden får i tillegg
  `fyllkode.svg` — de fire kodene i
  full størrelse, én per bokstav — og det er der koden læres. På en stegside er
  den en påminnelse.
* Alt skrives både som `.svg` (originalen) og `.png` (det Markdown-en bygger
  inn), så manualen leses på en maskin uten noe av dette installert.

---

## 5. Regenerering

```
mise run build        modellen + docs/generated/ + docs/MONTERING.md
mise run montering    strektegningene i docs/img/
mise run pdf          docs/hanna.pdf
```

De tre må være grønne i den rekkefølgen. `build` importerer modellen, så alle
assertene kjører der; `montering` importerer den igjen og legger
tegningsassertene (`check_coverage`) på toppen; `pdf` bruker de innsjekkede
filene som de er og trenger ikke build123d.

Tyngre, og bare når det trengs:

```
mise run build-full         + .glb og de skjulte-linje-projeksjonene
mise run usdz               .usdz for Quick Look (macOS)
mise run render-validate    de fem designvalideringsbildene
```

### Filmene

De tre `docs/img/hanna-*.gif` er utledet av modellen og `byggesteg.json` som alt
annet her, og de er voktet av `docs/img/hanna-filmer.stamp` —
[PRAKSIS §5](../../../PRAKSIS.md#5-filmene-er-utledet-som-alt-annet) sier
hvorfor. Selve rammene er skrap og skrives utenfor repoet
(`$TMPDIR/loftbed_film`).

```
mise run film               alle tre
mise run film-turntable     bare dreieskiva
mise run film-mekanisme     bare stillingsbyttet (kollisjonsprøve på hver ramme)
mise run film-bygg          bare oppbyggingen - den dyre
mise run film-check         er de innsjekkede filmene bygget av DENNE modellen?
```

De rendres **ikke** av `build`: de tar minutter og trenger macOS-verktøyene.
Arbeidsgangen når modellen eller et byggesteg endres er derfor
`mise run build` → `mise run film` (eller bare den deloppgaven som er berørt)
→ `git diff`; er filmen uendret, er den byte-identisk og diff-en taus.

Dreieskiva og mekanismen er funksjoner av `parts.tsv` alene, oppbyggingen også
av `byggesteg.json`, så en ren tekstendring i et steg krever bare `film-bygg`.
Stempelet vet det: `film-check` hasher nøyaktig de kildene hver enkelt film har.

**Mekanismefilmen er dessuten en assert.** Den viser platen fra sengesete til
bordsete, og hver eneste ramme legges gjennom en separerende-akse-prøve mot
hver faste del i sengen; kolliderer noe, nekter verktøyet å lage filmen. Første
utgave gjorde nettopp det — den kjørte platen 166 mm gjennom begge stigevangene
— og den feilen er grunnen til at prøven finnes.

**Og så saken som ble til fellesregelen om asserten som måler feil ting**
([PRAKSIS §2](../../../PRAKSIS.md#asserten-som-måler-feil-ting)).
Prøven over har hele tiden også *rapportert* et tall — «den trangeste
passeringen på hele veien» — og notatet ved siden av har sagt at tallet er
2,0 mm = `PANEL_FIT`. Det stemte ikke. Det den målte var 0,00 mm mot den bakre
benkevangen, på ramme 1, og den hadde målt det i to runder uten at noen så det,
nettopp fordi tallet så *riktig ut* i forhold til en påstand ingen hadde
kontrollert. Nullen var ekte: styrelektas bakflate **er** benkevangens forflate,
så de to trebitene ligger inntil hverandre i setet og blir liggende de første
millimeterne av løftet. Prøven leste setet og kalte det en nestenulykke.

Lærdommen er ikke «se bedre etter». Den er at et **rapportert** tall må ha en
definisjon som er like presis som en assert sin, og at definisjonen må stå i
koden og ikke i kommentaren over den. `mech_probe()` måler nå selv hvilke par
av deler som berører hverandre i de to setene, og holder dem utenfor
minimumet — de kollisjonsprøves fortsatt som alt annet.

### Hva slags side et steg får

Står i `tools/gen_doc_tables.build_steps()`, sammen med alt annet som
definerer et byggesteg, og følger med ut i `byggesteg.json`:
`page` («cutpage»/«panel»), `half_view`, `thumbnails`, `crop_to_subject`,
`no_fasteners`, `info_panel`, `avoid_top_left`. `render_lineart.py` slår dem
opp; den har ingen `if n == 0` og ingen navnematch på «Mattress» igjen. Det er
[PRAKSIS §3](../../../PRAKSIS.md#3-regler-ikke-tilfeller) i praksis: hvilken
side et steg får er en egenskap ved STEGET, og et steg er definert ett sted.

`fill_code` står i den samme lista og leses på samme måte, men er ikke skrevet
for hånd: den **regnes ut** av stegets eget sett festemidler
(`step_fill_code()`, regelen i §4). Om en side trenger fyllkoden er en
opplysning om skruene den driver, så ingen skal måtte huske å skru den på den
dagen et ledd bytter lengde — og ingen skal kunne skru den av.

**Ingenting i `docs/generated/` skal redigeres for hånd.** Alle Markdown-filene
der starter med en kommentar som sier det (`byggesteg.json` kan ikke bære en,
JSON har ingen kommentarer). Skal et tall endres, endres det i modellen.

### Determinismen

Alt utledet er sjekket inn — også `.png`-ene, `.svg`-ene og `parts.tsv` —
og `mise run check` kjører `build` + `montering` to fulle ganger og krever at
`docs/generated/`, `docs/MONTERING.md`, `docs/img/` og `parts.tsv` kommer ut
byte-identisk begge ganger. Hvorfor det er en assert og ikke en forventning,
og hva et brudd betyr, står i
[PRAKSIS §6](../../../PRAKSIS.md#6-determinismen-er-en-assert).

---

## 6. Ting som er bevisst ikke gjort

* **Gjenger på skruene.** Se over.
* **Filtknottene (J15) er ikke modellert.** De slås i endeveden før reisning og
  ville flyttet gulvplanet i modellen uten å si noe nytt.
* **Veggfestet (J14) er plassert, men ikke eksportert.** Halve skruen står i en
  vegg som ikke er modellert, og 52 mm stål bak Y = −48 ville gjort den
  eksporterte sengen 888 mm dyp. Det flate monteringsplanet på 836 mm er hele
  poenget med den baksiden, så skruene tegnes og eksporteres ikke.
* **Ingen ansikter, ingen hender, ingen fingre på referansekroppene.**
  Fjorten primitiver: rundt hode, sylindre for hals, overkropp, armer og bein,
  kule for hofta, boks for foten. Manualens abstraksjonsnivå. Et ansikt ville
  vært det eneste i hele boka som ikke er utledet av et mål.
* **Silhuett-filtrering av kroppene ble prøvd og forkastet.** Tanken var å
  hente bare `OutLineVCompound` for figurgruppa, så sømmene mellom lemmene
  ikke skulle vises. Målt: i et rett oppriss inneholder den compounden bare de
  *krumme* silhuettene og mister hver eneste rette frembringer — barnet kommer
  ut som elleve løse buer. Alle tre synlig-kant-compoundene sammen er 64 kanter
  på en som sitter og 70 på en som ligger, og det tegner et menneske. Regelen
  er derfor at kroppene tegnes som alt annet.
* **Madrassen er en referansekropp, ikke en del.** Den er ikke i kapplista.
