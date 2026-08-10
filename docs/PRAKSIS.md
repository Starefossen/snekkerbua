# PRAKSIS — hvordan dette repoet er bygd

Dette er ikke en del av manualen. `docs/hanna.pdf` settes sammen av en
eksplisitt liste i `tools/build_pdf.py` (`REF_DOCS`), og denne filen står ikke
i den. Den er skrevet for den som skal endre modellen eller tegningene, og den
sier hvilke regler som gjelder og hvorfor de er som de er.

---

## 1. Én kilde, og bare én

**Ethvert tall som står i dokumentasjonen kommer fra `generate_loftbed.py`.**
Ikke «er kopiert fra» — kommer fra. Verktøyene i `tools/` importerer modellen,
leser modulglobalene og skriver ut. Ingen av dem definerer geometri, og ingen
av dem utleder noe modellen allerede vet.

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
den. Det er den regelen som gjelder: **hvis to filer må være enige om et tall,
er tallet på feil sted.**

---

## 2. Assertfilosofien

Modellen har over hundre `assert`. Nesten ingen av dem sjekker at et tall er
det tallet som står der. De sjekker **forhold mellom ting**, og de er utledet
av fysikk, ikke av en mening.

En god assert her har tre kjennetegn:

1. **Den er relasjonell.** `assert POST_W == 98` er verdiløs — den sier bare at
   98 er 98. `assert rail.extents[2][0] == post_top` sier at vangen faktisk
   hviler på stolpen, og den ryker i det øyeblikket noen flytter en av dem.
2. **Den er utledet av noe utenfor tegningen.** EC5 sier 3d kantavstand og 4d
   avstand mellom skruer. EN 747 sier 75 mm åpning og 160 mm rekkverk over
   madrassen. De tallene er inndata; alt som følger av dem er utregnet.
3. **Den forklarer seg selv når den ryker.** Meldingen skal si hvilket tall som
   ikke gikk opp, hva grensen var, og hvor man retter det. En assert man må
   lese kildekoden for å forstå er en assert man kommenterer bort.

### De fire familiene

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
omlegg og beslagflikene.

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

En skrue er hode, forsenking, skaft og spiss. **Ingen gjenger.** På
tegningsskala er det silhuetten som bærer informasjonen, og en modellert gjenge
koster tusen trekanter for null lesbarhet. Beslagene er bøyde plater bygd av
bokser.

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
Alt treverk er bokser, og en plan flate trianguleres til de samme to trekantene
uansett avvik, så treet blir byte-identisk uansett.

---

## 4. Tegnekonvensjoner

De som er hentet fra Agrawala/Heer/Klingner sitt arbeid med
monteringsanvisninger, og som denne manualen har tatt i bruk bevisst:

* **Prikket linje = festemiddel. Pil = tredel.** De to blandes aldri på samme
  side. En prikket linje er alltid en skrues vei inn i hullet sitt; en pil er
  alltid en tredel som skal føres på plass.
* **Eksplodert langs innsettingsaksen.** Et festemiddel som skal settes i,
  tegnes trukket rett ut langs sin egen akse — ikke ved siden av, ikke i
  margen. Leseren skal kunne følge linjen.
* **Stiplet = skjult, men virkelig.** Fantomlinjen er den eneste ærlige måten å
  vise en skrue som er helt inne i to stykker tre.
* **Svart = det du gjør nå, grått = det som allerede står.** Den nye delen
  tegnes hel selv der rammen dekker den, med den skjulte strekningen stiplet.
* **Ett steg = én operasjon = én side.**

### Skala

**Én penn.** Hver strekbredde, radius, marg og punktstørrelse på en stegside er
et multiplum av ett eneste mål:

    penn = diagonalen i tegningsobjektets egen bbox / 400

Tallet er sengens, ikke sidens, så hele pennsettet følger det som tegnes.
Tabellen står i `tools/layout.py` (`RATIOS`), og `Theme` deler den ut. Sidenære
størrelser — innsettpanelets bredde, eksplosjonens sprang, den hvite margen —
er fortsatt brøkdeler av SIDEN, for det er det de er. Regelen er den samme som
ellers i repoet: skal en strek bli tykkere, endres forholdstallet ett sted, og
alle tolv sidene følger etter.

Én frihet er tatt utover det, og det er den samme enhver beslagtegning tar:
**diameteren er overdrevet**, med faktor `SCREW_FATTEN` — som står i
`tools/layout.py` sammen med pennen, fordi det er én knapp for hvor stort et
festemiddel tegnes. En 6 mm skrue på en to meter bred side er tynnere enn
streken sengen selv er tegnet med. Faktoren er 3,0: på 2,2 var en 5×40 og en
6×90 elleve og tretten millimeter brede på en 1250 mm side, og forskjellen var
en avrundingsfeil. Nå er de femten og atten, og typen leses av silhuetten før
bokstaven leses. **Lengden er sann**, med et gulv på `FORESHORTEN_FLOOR` mot
ren forkortning: en skrue drevet inn i papiret skal se kort ut, men den skal
fortsatt se ut som en skrue.

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

  **Settet er bevist, ikke valgt.** `python tools/render_lineart.py
  --fill-contrast` skriver `docs/preview/fyllkontrast.png`: hver kode i den
  størrelsen den minste bokstavsiden faktisk gir en skrue, i innsettets
  størrelse, og i halv størrelse som stresstest. Prøven avgjorde to ting som
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
* **Kontakt eller leder (R6).** Et merke skal enten RØRE kroppen det navngir —
  sitte på hodet som et flagg på en stang — eller ha en tynn strek inn til den.
  Det finnes ingen tredje plass. Et merke som svever ved siden av en klynge er
  ikke en anvisning, det er en gåte, og på steg 5 sto det tre av dem og gjettet
  samtidig. Regelen er priset inn i `layout.place()` — kontakt er verdt mer enn
  hvilken som helst mengde hvitt papir — og `assert_badges_anchored()` måler
  den etterpå av blekket: rører merket sin egen kropp, ender lederen på den, og
  starter den i merkets egen rand.
* **Ett merke per løp (R7).** To eller flere festemidler av samme slag, i samme
  ledd, som ligger etter hverandre uten noe fremmed imellom, bærer ett merke.
  Åtte like bokstaver nedover en stigevange er ikke åtte opplysninger, det er
  én, gjentatt til den blir tapet. Vilkårene er strenge nettopp fordi merkets
  hele verdi er at det er entydig: samme bokstav, samme ledd, kroppene i en
  kjede, og ingenting fremmed innimellom. Merket som blir stående er det første
  i sidens egen tegnerekkefølge, og det er fortsatt underlagt R6.
* **Sammenslåing går aldri på tvers av ledd.** På steg 3 møtes endebjelkens to
  6×90 og bæreklossens ene i det samme hjørnet, og «3×» der ville sendt
  byggeren til feil hull. To ledd, to merker. Regelen er ett flagg i
  `render_lineart.py` (`MERGE_ACROSS_JOINTS`), så den er en linje å snu og
  ikke en antakelse å lete etter — men den står av, og tegningene er tegnet
  med den av.
* **Et merke ligger nærmere sitt eget feste enn noe annet (R5).** Et badge
  ved siden av feil skrue er ikke en trang tegning, det er en feil anvisning.
  Regelen er en assert som måler blekket: merkene leses ut av `Page.record`
  der de LANDET, og hvert av dem må ha sitt eget feste som nærmeste kropp —
  målt mot kroppenes egne kapsler, ikke mot punkter i nærheten av dem.
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
* **Piktogrammene** («før du begynner») er Lucide-baserte, én strektykkelse,
  ingen fyll, ingen tekst i ikonet. `docs/icons/lucide/` er **vendoret, ikke
  speilet**: der ligger bare de ikonene `PICTOGRAMS` faktisk slår opp, og
  ingenting annet. Et ikon som ikke står i den tabellen skal ut av katalogen —
  ellers vokser den til et halvt ikonbibliotek som ingen bygger leser og ingen
  lisensfil dekker meningsfullt. (Fem ubrukte ble slettet i denne runden:
  `baby`, `hammer`, `pencil`, `person-standing`, `phone`.)
* **Merkebokstavene** er ett tegn i en sirkel, samme radius overalt.
* **De kodede glyfene.** Der et steg deler ut bokstaver, skrives skrueglyfen
  også i sin egen fyllkode (`treskrue-5x40-hatch.svg`), og det er den fila både
  innsettpanelets rad og stegets tabell bruker. Hvilke par som finnes bestemmes
  av STEGENE, for det er der bokstavene deles ut; et par ingen side viser er en
  fil ingen leser. Beslagsiden får i tillegg `fyllkode.svg` — de fire kodene i
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

### Hva slags side et steg får

Står i `tools/gen_doc_tables.build_steps()`, sammen med alt annet som
definerer et byggesteg, og følger med ut i `byggesteg.json`:
`page` («cutpage»/«panel»), `half_view`, `thumbnails`, `crop_to_subject`,
`no_fasteners`, `info_panel`, `avoid_top_left`. `render_lineart.py` slår dem
opp; den har ingen `if n == 0` og ingen navnematch på «Mattress» igjen.
Grunnen er den samme som i §1: hvilken side et steg får er en egenskap ved
STEGET, og et steg er definert ett sted.

**Ingenting i `docs/generated/` skal redigeres for hånd.** Alle Markdown-filene
der starter med en kommentar som sier det (`byggesteg.json` kan ikke bære en,
JSON har ingen kommentarer). Skal et tall endres, endres det i modellen.

**Alt er sjekket inn** — også `.png`-ene, `.svg`-ene og `parts.tsv` — slik at
en diff viser hva en endring i modellen faktisk gjorde med tegningene. Det er
poenget med å ha dem i git: `git diff --stat` etter `mise run build` er
konsekvensanalysen.

Den avlesningen er verdiløs hvis kjeden selv kan gi to svar på samme spørsmål,
så determinismen er ikke en forventning — den er en assert:

```
mise run check        kjør hele kjeden to ganger, krev byte-identiske artefakter
```

`check` kjører `build` + `montering` to fulle ganger og sammenligner sjekksummen
av hver innsjekkede, utledede fil (`docs/generated/`, `docs/MONTERING.md`,
`docs/img/`, `parts.tsv`). Ryker den, er det **ikke** en modellendring: det er
en usortert `dict`, et tidsstempel, en `id()`-sortering eller en flyttallssum
som avhenger av rekkefølgen. Rett årsaken, ikke artefaktet.

---

## 6. Ting som er bevisst ikke gjort

* **Gjenger på skruene.** Se over.
* **Filtknottene (J15) er ikke modellert.** De slås i endeveden før reisning og
  ville flyttet gulvplanet i modellen uten å si noe nytt.
* **Veggfestet (J14) er plassert, men ikke eksportert.** Halve skruen står i en
  vegg som ikke er modellert, og 52 mm stål bak Y = −48 ville gjort den
  eksporterte sengen 888 mm dyp. Det flate monteringsplanet på 836 mm er hele
  poenget med den baksiden, så skruene tegnes og eksporteres ikke.
* **Madrassen er en referansekropp, ikke en del.** Den er ikke i kapplista.
