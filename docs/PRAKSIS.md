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

Én frihet er tatt, og det er den samme enhver beslagtegning tar: **diameteren
er overdrevet**, med faktor `SCREW_FATTEN`. En 6 mm skrue på en to meter bred
side er tynnere enn streken sengen selv er tegnet med. **Lengden er sann**, med
et gulv på `FORESHORTEN_FLOOR` mot ren forkortning: en skrue drevet inn i
papiret skal se kort ut, men den skal fortsatt se ut som en skrue.

### Merking og sammenslåing

* **Bokstav i ring** (Ⓐ, Ⓑ …) knytter et festemiddel på tegningen til en rad i
  tabellen under bildet. Rekkefølgen er «flest først, uavgjort brytes på navn»,
  og både `gen_doc_tables.py` og `render_lineart.py` regner den ut av de samme
  radene, så de kan ikke bli uenige.
* **En stegside med bare én type festemiddel får ingen bokstaver.** Ikonet i
  tabellen er allerede hele svaret.
* **`2×` betyr at ett merke står for to festemidler.** To skruer 30 mm fra
  hverandre er ett merke på en side av denne størrelsen.
* **Sammenslåing går aldri på tvers av ledd.** På steg 3 møtes endebjelkens to
  6×90 og bæreklossens ene i det samme hjørnet, og «3×» der ville sendt
  byggeren til feil hull. To ledd, to merker.
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
