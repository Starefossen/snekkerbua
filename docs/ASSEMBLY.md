# Loftseng — Sammenføyninger og montering (Joinery & Assembly)

**SOM BYGGET — rev. 2.** Alle mål i mm. Koordinatsystem: Z opp (gulv Z = 0),
X langs rommet mellom de to veggene (X = 0 og X = 1990), Y = dybde,
Y = 0 er innerflaten på bakre vange.

Alt trevirke er **høvlet norsk standarddimensjon** (Byggmakker / Montér / Obi).
Alle sammenføyninger er **butt joints** løst med gjennomgående M8-låseskruer
(bræddebolter), treskruer, klosser/lekter og hyllevare vinkelbeslag.
Ingen overfres, ingen stemjern, ingen pocket-hole-jigg.

---

## 0. ÉN ÅPEN BESLUTNING — rekkverkets båndhøyder (C7)

Alt annet i denne beskrivelsen er fastlagt. Dette ene punktet må **du** velge før
trinn 7 i monteringen.

Med rekkverksbåndene på de opprinnelig tegnede høydene blir det to åpninger:

* sidevangens overkant **Z 1188** → nedre bånds underkant **Z 1330** = **142 mm**
* nedre bånds overkant **Z 1425** → øvre bånds underkant **Z 1550** = **125 mm**

EN 747 advarer mot åpninger i sonen **75–230 mm** i og rundt et køyesengrekkverk:
en kropp kan gli gjennom mens hodet ikke kan. **Begge åpningene ligger midt i den
sonen.** Dette er en reell klemfare, og bør endres. Velg ett av to:

| | Beskrivelse | Bånd (Z) | Åpninger | Materialbehov |
|---|---|---|---|---|
| **Alt. 1** | **Tre bord per side** | 1258..1353 · 1396..1491 · 1534..1629 | 70 / 43 / 43 mm | + 2 stk. 21×95 × 1984 og + 16 treskruer 5×60 |
| **Alt. 2** | **To bord, begge senket** | 1258..1353 · 1423..1518 | 70 / 70 mm | ingen ekstra |
| *(Alt. 0)* | *Som opprinnelig tegnet — **frarådes*** | 1330..1425 · 1550..1645 | **142 / 125 mm** | ingen ekstra |

Begge anbefalte alternativer holder rekkverkets overkant ≥ 160 mm over
madrasstoppen ved 140 mm madrass (madrasstopp Z ≈ 1274): alt. 1 gir 355 mm,
alt. 2 gir 244 mm. Resten av dokumentet bruker **alt. 1** i tellingene og
markerer hvor tallet endres ved alt. 2.

---

## 0b. Endringslogg fra første utkast (rev. 1 → rev. 2)

Sju konstruksjonsendringer er innarbeidet i geometrien og er ikke lenger
«anbefalinger». Kort om hva og hvorfor:

| Ref. | Endring | Hvorfor |
|---|---|---|
| **C1** | **To ekstra bakre stolper 48×73 × 1700** ved X 712..785 og X 1205..1278 i planet Y −96..−48, boltet gjennom bakre vange. Speilbilde av stigevangene. | Det bakre rekkverksbordet spente 1844 mm på bare to opplegg → σ = 33,0 MPa mot 16,6 tillatt, **utnyttelse 1,99 = brudd**, og 81 mm nedbøyning. Nå er maks spenn 639 mm → utnyttelse 0,69. Bonus: bakre vange får to ekstra opplegg, fritt spenn faller fra 1844 til 591 mm. |
| **C2** | **Bæreklosser under alle endebjelke- og benkevangeender** (J1-B, 4 stk. 36×48 L=48; J9-B, 4 stk. 36×48 L=73). | Uten dem gikk hele vertikallasten i boltskjær med bare **24 mm endeavstand** i endebjelken (EC5 krever 4d = 32 mm ved last på tvers av fibrene). Bruddformen ville blitt sprø oppflising av endeved. Nå bærer tre mot tre og boltene er rene strekkbånd. |
| **C3** | **Benkespilene er 34×98 × 906** (var 21×95). Benkeoverflaten flyttes derfor fra Z 280 til **Z 293**. | 21×95 over 810 mm fritt spenn gir **utnyttelse 1,96** hvis noen står på én spile, og 0,98 ved vanlig sitting. 34×98 gir 0,73 ved 1 kN punktlast og 3,1 mm nedbøyning. |
| **C4** | Køyespilene beholdes 21×95 × 806, men **antall og bruksbegrensning er dokumentert** (se § 8.5). | Kapasitet 0,60 kN per spile. Fungerer med madrass som fordeler lasten over ≥ 3 spiler; uten madrass kan en voksen knekke én spile. |
| **C5** | **Benkevangene er gjennomgående 48×73 × 1984** (var 2 × 645 per side). | Den løse platen hadde ingenting å kroke på i åpningen X 645..1345 i sengemodus. Nå er det en sammenhengende kant i hele lengden. Gir dessuten mindre kapping, stivere nedre nivå, og stigevangene får et festepunkt nede. |
| **C6** | **Fremre bordbærelekt 21×95 × 1984** på Y 837..858. Begge bordbærelekter ligger **Z 371..466**. | Uten fremre lekt måtte de to fremre beslagene ha 78 mm fall for å nå ned fra rungetoppen Z 560. Nå er alle fire krokbeslag av samme type og bordplaten lander på nøyaktig **Z 500**. |
| **C9** | **Alle liggende deler som går fra vegg til vegg kappes 1984 mm**, ikke 1990. | En 1990 mm lang del kan ikke manøvreres inn i en 1990 mm åpning: når den svinges ned til vannrett sveiper hjørnene √(995² + 61,5²) = 996,9 mm ut fra midten, dvs. ~2 mm for langt i hver ende. 1984 gir 3 mm klaring i hver ende. |

**C8 er ikke en geometriendring, men en boreinstruks:** boltehodene i
endebjelke→stolpe havner på stolpens veggside (X = 0 / X = 1990) hvor det ikke er
plass. De **forsenkes ⌀16 × 10 mm** med spadebor, og det brukes låseskrue
(bræddebolt) hvis firkanthals låser seg i bunnen av forsenkningen. Se J1.

### Følgevirkninger av C3 som du må kjenne til

Benkeoverflaten er nå **Z 293**, ikke 280. Derfor:

* **Krokbeslagene har et 16 mm steg**, ikke 3 mm: 259 (vangetopp) + 16 = 275
  (platens underkant) + 18 (plate) = **293** = benkespilenes overkant. Flukt. ✓
* **Bordbærelektene ligger 16 mm lavere enn i første utkast**, Z 371..466, slik at
  samme beslag gir 466 + 16 = 482 + 18 = **Z 500** i bordmodus. Nøyaktig
  som opprinnelig ønsket.
* **Stigens nederste rungetopp (Z 280) ligger nå 13 mm under benketoppen.** Det er
  uten betydning — rungen ligger utenfor benken i Y (Y 858..931 mot benkens
  Y −48..858) og brukes bare som trinn.
* **Platen er 680 × 828 (Y 30..858), ikke 860 dyp.** En dypere plate ville kollidere
  med stigevangene, som står i Y 858..906 og ligger midt i platens X-område.
  Følgen er at liggeflaten i sengemodus har et 78 mm grunt innhakk bakerst i
  midtpartiet (benkespilene går til Y −48, platen bare til Y 30). Med madrass
  eller pute over merkes det ikke.

> **Avvik mellom 3D-modellen og denne beskrivelsen — les dette.**
> I 3D-modellen er krokbeslagene ikke modellert, og bordbærelektene er derfor
> tegnet med overkant i platens underkant, **Z 482**. **Bygg dem 16 mm lavere,
> overkant Z 466 (Z 371..466)**, slik denne beskrivelsen sier. Beslagets 16 mm
> steg legger seg oppå lekta, og bordplatens overkant havner da på nøyaktig
> Z 500. Bygger du etter modellens 482 blir bordet 516 mm høyt.

---

## 1. Verktøyliste

| Verktøy | Merknad |
|---|---|
| Håndholdt drill/skrutrekker (batteri) | 18 V eller mer — 28 M8-hull, det lengste 121 mm gjennom heltre |
| Bor **⌀8,5** metallbor/trebor, **min. 200 mm langt** (slangebor eller forlenger) | For M8 gjennomgangshull |
| Bor ⌀3, ⌀4, ⌀4,5, ⌀5 til forboring | Forbor **alltid** i 21 mm bord og i all endeved |
| Bor ⌀20 (spade/slangebor) | Klaringshull for muttere i spilelektene — **8 stk.** |
| Bor ⌀16 (spadebor) | Forsenking for låseskruehoder i stolpenes veggside — **8 stk.** |
| Bor ⌀6,5 + forsenker ⌀13 | M6-hull gjennom bordplaten |
| Forsenker (kjeglesenker) | Alle treskruehoder i synlige flater |
| Bits: Torx T20 / T25 / T30 | Etter skruetype |
| Fastnøkkel eller pipe **13 mm** + skralle | M8-muttere |
| Fastnøkkel **10 mm** | M6-muttere (platebeslag) |
| Håndsag eller sirkelsag | Ingen gjæringer — alle kutt er 90° |
| Vinkelhake (min. 300 mm) og tommestokk/målebånd | |
| Vater, minst 600 mm | Endrammene må stå i lodd før vangene legges på |
| To skrutvinger (min. 300 mm åpning) | Holder deler mens du borer gjennom begge samtidig |
| Skrustikke eller ambolt + hammer | Bøying av krokbeslagenes 16 mm steg |
| Blyant, syl / spikerdor | Merking av borsentre |
| Filtknotter eller gulvbeskyttere ⌀40 | Under 8 stolper og 4 stubbeføtter (12 punkter) |

---

## 2. Handleliste — trevirke (høvlet)

Lengder er kjøpelengder; kapp etter kapplista i § 3.

| Dimensjon | Kjøp | Går til |
|---|---|---|
| **48×123** høvlet C24 | **3 stk. 2,4 m** | 2 sidevanger (1984), 2 endebjelker (1002) |
| **48×73** høvlet C24 | **4 stk. 3,6 m** + **2 stk. 2,4 m** + **1 stk. 3,0 m** | 4 hjørnestolper + 2 stigevanger + 2 bakre stolper (8 × 1700), 2 benkevanger (1984), 4 rungetrinn (420), 4 stubbeføtter (186) |
| **36×48** høvlet | **3 stk. 2,4 m** | 2 spilelekter (1984), 8 stigeklosser (73), 4 bæreklosser J1-B (48), 4 bæreklosser J9-B (73), 2 avstivningslekter under platen (820) |
| **21×95** høvlet | **3 stk. 4,8 m** + **3 stk. 4,2 m** | 13 køyespiler (806), 4 rekkverksbord (1984), 2 bordbærelekter (1984) |
| **34×98** høvlet | **2 stk. 4,8 m** | 10 benkespiler (906) |
| **18 mm limtreplate furu** | 1 plate **1200 × 800** | Løs plate 680 × 860 |

Ved **C7 alt. 1** (tre rekkverksbord per side): + **1 stk. 4,2 m** 21×95.

Løpemeter totalt: 48×123 ≈ 7,2 m · 48×73 ≈ 19,8 m · 36×48 ≈ 7,2 m ·
21×95 ≈ 27,0 m · 34×98 ≈ 9,6 m.

---

## 3. Kappliste — som bygget

| Del | Dim. | Lengde | Ant. | Posisjon (X / Y / Z) |
|---|---|---|---|---|
| Sidevange bak | 48×123 | **1984** | 1 | X 3..1987 · Y −48..0 · Z 1065..1188 |
| Sidevange front | 48×123 | **1984** | 1 | X 3..1987 · Y 810..858 · Z 1065..1188 |
| Endebjelke | 48×123 | 1002 | 2 | X 73..121 / 1869..1917 · Y −96..906 · Z 942..1065 |
| Hjørnestolpe | 48×73 | 1700 | 4 | X 0..73 / 1917..1990 · Y −96..−48 og 858..906 · Z 0..1700 |
| Stigevange | 48×73 | 1700 | 2 | X 712..785 / 1205..1278 · Y 858..906 · Z 0..1700 |
| **Bakre stolpe** | 48×73 | 1700 | 2 | X 712..785 / 1205..1278 · Y −96..−48 · Z 0..1700 |
| Rungetrinn | 48×73 | 420 | 4 | X 785..1205 · Y 858..931 · Z (T−48)..T, T = 280/560/840/1120 |
| **Benkevange** | 48×73 | **1984** | 2 | X 3..1987 · Y −48..0 og 810..858 · Z 186..259 |
| Stubbefot | 48×73 | 186 | 4 | X 572..645 / 1345..1418 · Y −48..0 og 810..858 · Z 0..186 |
| Spilelekt | 36×48 | **1984** | 2 | X 3..1987 · Y 0..36 og 774..810 · Z 1065..1113 |
| Stigekloss | 36×48 | 73 | 8 | X 785..821 / 1169..1205 · Y 858..931 · Z (T−96)..(T−48) |
| **Bærekloss J1-B** | 36×48 | 48 | 4 | X 73..121 / 1869..1917 · Y −96..−48 / 858..906 · Z 906..942 |
| **Bærekloss J9-B** | 36×48 | 73 | 4 | X 0..73 / 1917..1990 · Y −48..−12 (bak) / **822..858** (front) · Z 138..186 |
| Avstivningslekt plate | 36×48 | **770** | 2 | X 830..866 / 1160..1196 · Y 40..810 · under platen |
| Køyespile | 21×95 | 806 | 13 | Y 2..808 · Z 1113..1134 · X 20..1980, se § 5, J5 |
| Rekkverksbord | 21×95 | **1984** | 4 *(6 ved C7 alt. 1)* | Y −117..−96 og 906..927 · Z-bånd: se § 0 |
| **Bordbærelekt bak** | 21×95 | **1984** | 1 | X 3..1987 · Y −48..−27 · **Z 371..466** |
| **Bordbærelekt front** | 21×95 | **1984** | 1 | X 3..1987 · Y 837..858 · **Z 371..466** |
| **Benkespile** | **34×98** | 906 | 10 | Y −48..858 · **Z 259..293** · X: se § 5, J11 (deling 137,5) |
| Løs plate | 18 mm | **680 × 828** | 1 | X 655..1335 · **Y 30..858** · seng: Z 275..293 · bord: Z 482..500 |

**Nøkkelhøyder som bygget:** gulv 0 · benkevangens underkant 186 · vangetopp 259 ·
**benkeoverflate 293** · bordbærelektas overkant 466 · **bordplate 500** ·
endebjelkens underkant 942 · sidevangens underkant 1065 · spilebunn 1134 ·
madrasstopp ≈ 1274 · stolpetopp 1700.

---

## 4. Handleliste — beslag og festemidler

Norske handelsnavn. Alt er **elforsinket eller varmforsinket**.

| Post | Spesifikasjon | Behov | Kjøp |
|---|---|---|---|
| **A** | **Låseskrue (bræddebolt) M8 × 130, DIN 603, varmforsinket** | 8 | 10 stk. |
| **B** | **Låseskrue (bræddebolt) M8 × 120, DIN 603, varmforsinket** | 20 | 25 stk. |
| **C** | **Låsemutter M8 (nylock), DIN 985** | 28 | 40 stk. |
| **D** | **Karosseriskive M8 × ⌀25 × 2 mm** — én under hver mutter | 28 | 40 stk. |
| **E** | **Senkhodeskrue M6 × 30 + låsemutter M6 + skive M6** | 8 sett | 10 sett |
| **F** | **Treskrue 4 × 40 forsenket Torx** | 26 | 1 eske 200 |
| **G** | **Treskrue 5 × 40 forsenket Torx** | 36 | 1 eske 200 |
| **H** | **Treskrue 5 × 60 forsenket Torx** | 48 *(64 ved C7 alt. 1)* | 1 eske 200 |
| **I** | **Treskrue 5 × 70 forsenket Torx** | 68 | 1 eske 200 |
| **J** | **Treskrue 5 × 80 forsenket Torx** | 8 | 1 pk. 50 |
| **K** | **Treskrue 6 × 120 forsenket Torx** (konstruksjonsskrue) | 16 | 1 pk. 25 |
| **L** | **Vinkelbeslag 90 × 90 × 65 × 2,5 mm, varmforsinket** | 10 = 4 stubbeføtter + 2 stigevanger + 4 vegg | 12 stk. |
| **M** | **Flattstål 30 × 4 mm** til krokbeslag: 2 × 135 mm (bak) + 2 × 100 mm (front) | 4 | 1 lengde 1 m |
| **O** | Filtknotter / møbeltapper ⌀40 | 12 | 1 pk. |

**AS-BUILT TOTALER**

* **28 M8-bolter** — 8 stk. M8×130 + 20 stk. M8×120
* **28 M8-låsemuttere** + **28 karosseriskiver ⌀25**
* **8 M6-sett** (senkhodeskrue + skive + låsemutter)
* **202 treskruer**: 4×40 = 26 · 5×40 = 36 · 5×60 = 48 · 5×70 = 68 · 5×80 = 8 ·
  6×120 = 16   *(+ 16 stk. 5×60 ved C7 alt. 1 → 218 totalt)*
* **12 vinkelbeslag** 90×90×65
* **4 krokbeslag** bøyd av flattstål 30×4 (2 stk. × 135 mm bak, 2 stk. × 100 mm front)
* **12 filtknotter**

---

## 5. Sammenføyninger, ledd for ledd

Konvensjoner:
* «Hull ⌀8,5» = gjennomgangshull for M8. Bor **gjennom begge deler samtidig**
  mens de er tvunget sammen med skrutvinge — da kan hullene ikke bomme.
* Boltehodet står alltid på den **utvendige/tilgjengelige** siden,
  mutter + karosseriskive på innsiden.
* Kantavstander er kontrollert mot EC5: for M8 (d = 8) er minstekrav
  **3d = 24 mm** til ubelastet kant, **4d = 32 mm** til belastet kant og
  mellom bolter. Alle mål under er ≥ 32 mm der lasten går, ≥ 24 mm ellers.
* Treskruer: forbor ⌀ = 0,7 × skruediameter i alle deler tynnere enn 25 mm og
  i all endeved.

---

### J1 — Endebjelke → hjørnestolpe (4 ledd) · 2× M8×130 + 1 bærekloss hver

Endebjelken (48×123, X 73..121, Y −96..906, Z 942..1065) butter mot
**innerflaten** av begge hjørnestolpene i samme ende (venstre stolpe X 0..73,
innerflate X = 73). Dette er sengens viktigste ledd — hele overkøya står på det.

**Bærekloss J1-B — monteres først:**
36×48 kappet **48 mm** langt. Legges med 48 mm i X (X 73..121), 36 mm i Z
(**Z 906..942**), 48 mm i Y (samme Y-utstrekning som stolpen: Y −96..−48 bak,
Y 858..906 foran). Klossens **overkant Z 942 = endebjelkens underkant.**
Skru i **−X**-retning fra klossens frie ende inn i stolpen:
**2 × treskrue 5 × 80** (48 mm gjennom klossen + 32 mm inn i stolpen),
i klossens senter i Z (Z 924), ved Y = −84 og −60 bak (Y = 870 og 894 foran).
Forbor ⌀3,5 gjennom klossen.

**Boltene:**

| | Venstre ende | Høyre ende | Y | Z |
|---|---|---|---|---|
| Bolt 1 (bakre stolpe) | hull X 0 → 121 | hull X 1990 → 1869 | **−72** | **977** |
| Bolt 2 (bakre stolpe) | hull X 0 → 121 | hull X 1990 → 1869 | **−72** | **1030** |
| Bolt 3 (fremre stolpe) | hull X 0 → 121 | hull X 1990 → 1869 | **882** | **977** |
| Bolt 4 (fremre stolpe) | hull X 0 → 121 | hull X 1990 → 1869 | **882** | **1030** |

* Hulldybde 121 mm (73 stolpe + 48 endebjelke) → **⌀8,5-bor på minst 150 mm.**
* Kantavstand i Z: 977 − 942 = **35**, 1065 − 1030 = **35**, innbyrdes **53 mm**
  (= 6,6 d). ✓
* Kantavstand i Y: **24 mm** til begge sider (3 d) — minimum, og nettopp derfor er
  bæreklossen obligatorisk: med kloss under bærer treet vertikalt, og boltene tar
  bare horisontal utvipping.
* **Forsenking (C8):** bor ⌀16 × 10 mm dypt i stolpens ytterflate (X = 0 resp.
  X = 1990) rundt hullet, **før** ⌀8,5-hullet. Låseskruens firkanthals slås ned i
  forsenkningen med hammer; da låser hodet seg og mutteren trekkes fra innsiden
  alene. Etter forsenking stikker ingenting utenfor X = 0 / X = 1990.
* Grep: 121 − 10 = 111 + 2 skive + 8 mutter = **121 mm** → M8×130 gir ~9 mm
  gjenge til overs. ✓

---

### J2 — Sidevange → hjørnestolpe (4 ledd) · 2× M8×120 hver

Vangen **hviler på endebjelken** ved X 73..121 / 1869..1917 — det er der
vertikallasten går. Boltene er *strekkbånd* som holder vangen inn mot stolpen.

Bakre vange (Y −48..0) mot bakre stolpe (Y −96..−48): hull bores
**fra Y = −96 til Y = 0**, lengde 96 mm.
Fremre vange (Y 810..858) mot fremre stolpe (Y 858..906): hull bores
**fra Y = 906 til Y = 810**, lengde 96 mm.

| Bolt | X (venstre) | X (høyre) | Z |
|---|---|---|---|
| Øvre | **36** | **1954** | **1155** |
| Nedre | **36** | **1954** | **1100** |

* X 36 = stolpens senterlinje (0..73). Kantavstand 36 mm hver vei. ✓
* Z: vangen er 1065..1188. Kantavstand nedre **35**, øvre **33**, innbyrdes
  **55 mm**. ✓
* Boltehodet står på Y = −96 (bak) / Y = 906 (front) — begge frie flater.
* **Mutteren på nedre bolt (Z 1100) havner midt i spilelekta** (lekt Y 0..36 resp.
  Y 774..810, Z 1065..1113). Bor **⌀20 klaringshull tvers gjennom lekta** i disse
  punktene før lekta skrus på (se J4). Øvre bolt (Z 1155) ligger over lekta.
* Grep 96 + 2 skive + 8 mutter = 106 → M8×120 gir 14 mm til overs. ✓

---

### J3 — Stigevange → fremre sidevange (2 ledd) · 2× M8×120 hver

Stigevangene (48×73, Y 858..906) ligger flatt mot **utsiden** av den fremre
sidevangen (Y 810..858). Hull **fra Y = 906 til Y = 810**, lengde 96 mm.

| Bolt | X venstre vange | X høyre vange | Z |
|---|---|---|---|
| Øvre | **748** | **1242** | **1155** |
| Nedre | **748** | **1242** | **1100** |

* X 748 = senter i 712..785 (kantavstand 36 mm), X 1242 = senter i 1205..1278
  (kantavstand 37/36 mm). ✓
* **⌀20 klaringshull i den fremre spilelekta** ved X 748 og X 1242.
  Fremre lekt får dermed **fire** klaringshull (X 36, 748, 1242, 1954).
* Stigevangene går helt ned til gulvet (Z 0) og er boltet til vangen i skjær.
  De **bærer derfor også den fremre sidevangen**: største frie spenn på fronten
  er 591 mm, ikke 1748.

---

### J3b — Bakre stolpe → bakre sidevange (2 ledd) · 2× M8×120 hver

Speilbilde av J3: stolpen (48×73, Y −96..−48) mot baksiden av den bakre vangen
(Y −48..0). Hull **fra Y = −96 til Y = 0**, lengde 96 mm.

| Bolt | X venstre | X høyre | Z |
|---|---|---|---|
| Øvre | **748** | **1242** | **1155** |
| Nedre | **748** | **1242** | **1100** |

* **⌀20 klaringshull i den bakre spilelekta** ved X 748 og X 1242 — bakre lekt får
  også fire hull. **Til sammen 8 klaringshull.**
* Disse to stolpene er hele grunnen til at det bakre rekkverket holder (§ 7, L29).

---

### J4 — Spilelekt → sidevange (2 ledd) · 10 treskruer 5×70 hver

Lekt 36×48 × **1984**, 36 mm i Y og 48 mm i Z, overkant Z 1113, underkant Z 1065.

* Skru i Y-retning gjennom lektas 36 mm inn i vangens 48 mm: **5 × 70** gir 34 mm
  inngrep (14 mm igjen). Forsenk hodene.
* **Skrueposisjoner:** Z = **1089**, X = **100, 300, 500, 700, 900, 1100, 1300,
  1500, 1700, 1900** (c/c 200 mm).
* Ingen kolliderer med klaringshullene (nærmeste er X 700 mot hull X 748). ✓
* Bor de fire ⌀20-klaringshullene i hver lekt **før** montering.

---

### J5 — Køyespile → spilelekt (13 spiler) · 1 treskrue 4×40 per ende

Spile 21×95 × 806, Z 1113..1134, Y 2..808 (34 mm anlegg på hver lekt).

**X-posisjon, venstre kant** (deling **155,4 mm**, spalte **60,4 mm**). Spilefeltet
går X 20..1980, dvs. **10 mm klaring til hver vegg** — spilene skal ikke kile seg
mot pussen:

| # | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| X | 20 | 175 | 331 | 486 | 642 | 797 | 952 | 1108 | 1263 | 1419 | 1574 | 1729 | **1885** |

* Skruepunkt: spilens senter i X (X<sub>kant</sub> + 47), ved **Y = 18** og **Y = 792**.
* Forbor ⌀3 gjennom spilen — 21 mm bord sprekker ellers.

---

### J6 — Stigekloss → stigevange (8 klosser) · 2 treskruer 5×70 hver

Kloss 36×48 kappet **73 mm**: 36 mm i X, 48 mm i Z, 73 mm i Y (Y 858..931 — de
siste 25 mm stikker forbi vangens forkant Y 906, det er tilsiktet).

| Rungetopp T | Kloss Z | Venstre kloss X | Høyre kloss X |
|---|---|---|---|
| 280 | 184..232 | 785..821 | 1169..1205 |
| 560 | 464..512 | 785..821 | 1169..1205 |
| 840 | 744..792 | 785..821 | 1169..1205 |
| 1120 | 1024..1072 | 785..821 | 1169..1205 |

* Skru i X-retning **fra klossens frie flate inn i vangen**: venstre kloss i −X,
  høyre i +X. **5 × 70** = 36 mm gjennom kloss + 34 mm inn i vangens 73 mm. ✓
* Skruepunkter per kloss: **Z = T − 72** (24 mm til begge klosskanter),
  **Y = 870 og 894** (begge innenfor vangens Y 858..906). ✓
* Forbor ⌀3,5 gjennom klossen.
* Bæreflate for rungen: 36 × 73 = 2628 mm² → **6,1 kN** mot 0,5 kN last. ✓

---

### J7 — Rungetrinn → stigevange (4 trinn) · 1 treskrue 6×120 per ende

Rungen (48×73 × 420, X 785..1205, Y 858..931) **legges ned på de to klossene**.
Skruen holder den bare på plass — all vertikallast går via klossene.

* Skru **utenfra og inn**: venstre vange fra X = 712, høyre fra X = 1278.
  6 × 120 gir 73 mm gjennom vangen + 47 mm inn i rungens endeved.
* Punkt: **Z = T − 24**, **Y = 882**.
* Forbor ⌀4,5 gjennom vangen og ⌀4 i rungens endeved.

---

### J8 — Rekkverksbord → stolpe / stigevange · 2 treskruer 5×60 per festepunkt

Bord 21×95 × **1984**. Bakre bord på Y −117..−96 (utsiden av de bakre stolpene),
fremre bord på Y 906..927 (utsiden av de fremre stolpene og stigevangene).

* **5 × 60** = 21 mm gjennom bordet + 39 mm inn i den 48 mm dype stolpen. ✓
  (Bruk **ikke** 5×70 — den går tvers gjennom.)
* **Fire festepunkter per bord, foran og bak:** X **36, 748, 1242, 1954**.
  Bak er punktene hjørnestolpe – bakre stolpe – bakre stolpe – hjørnestolpe,
  foran hjørnestolpe – stigevange – stigevange – hjørnestolpe. Symmetrisk.
* To skruer per punkt, i bordets senter i X, 25 mm fra bordets over-/underkant:

| Bånd | **C7 alt. 1 (3 bord)** | C7 alt. 2 (2 bord) |
|---|---|---|
| 1 | Z 1258..1353 → skruer Z 1283 / 1328 | Z 1258..1353 → skruer Z 1283 / 1328 |
| 2 | Z 1396..1491 → skruer Z 1421 / 1466 | Z 1423..1518 → skruer Z 1448 / 1493 |
| 3 | Z 1534..1629 → skruer Z 1559 / 1604 | — |

* Forbor ⌀3 gjennom bordet.
* Skruetall: 2 bord/side × 4 punkter × 2 skruer × 2 sider = **32** (alt. 2),
  eller **48** (alt. 1).

---

### J9 — Benkevange → hjørnestolpe (4 ledd) · 1× M8×120 + 1 bærekloss hver

Den gjennomgående benkevangen (48×73, Z 186..259, høykant, 1984 lang) ligger mot
stolpens innerflate: bak mot Y = −48, foran mot Y = 858.

**Bærekloss J9-B — monteres først:** 36×48 kappet **73 mm**. 36 mm i Y —
bak **Y −48..−12**, foran **Y 822..858** (begge 36 mm inn fra stolpens
innerflate) — 48 mm i Z (**Z 138..186**, overkant = benkevangens underkant),
73 mm i X (X 0..73 / X 1917..1990).
Skru i Y-retning inn i stolpen: **3 × treskrue 5 × 70** (36 mm gjennom kloss +
34 mm inn i stolpens 48 mm). Punkter: Z = **162**, X = **15 / 36 / 57**.

**Bolten:** 1 × M8 × 120, hull **fra Y = −96 til Y = 0** (bak) /
**fra Y = 906 til Y = 810** (front), lengde 96 mm.

| | X venstre | X høyre | Z |
|---|---|---|---|
| Bolt | **36** | **1954** | **222** |

* Kantavstand i Z: 222 − 186 = **36**, 259 − 222 = **37**. ✓ I X: **36**. ✓
* Bare **én** bolt: vangen er 73 mm høy, og to bolter over hverandre ville gitt
  18 mm kantavstand (< 24). Klossen tar vertikallasten, bolten hindrer utvipping,
  og benkespilene låser vangen mot rotasjon.

---

### J10 — Benkevange → stubbefot (4 ledd) · 1 vinkelbeslag + 2 skråskruer

Stubbeføttene (48×73, Z 0..186) står **rett under** den gjennomgående
benkevangen ved X 572..645 og X 1345..1418, i begge Y-plan.
Vangen hviler direkte på fotens endeved: 48 × 73 = 3504 mm² → **8,1 kN**. ✓

* **Vinkelbeslag 90×90×65** på innerflaten (bak: Y = 0-flaten, front: Y = 858),
  ett ben opp på vangen, ett ned på foten. **4 × treskrue 5 × 40** per beslag.
* **2 × treskrue 6 × 120** skråskrudd (ca. 30°) gjennom vangens overkant ned i
  fotens endeved, ved X = fotens senter ± 20. Forbor ⌀4,5.

---

### J10b — Stigevange → fremre benkevange (2 ledd) · 1 vinkelbeslag hver

Fordi benkevangen nå er gjennomgående (C5), krysser den de to stigevangene ved
X 712..785 og X 1205..1278: vangens ytterflate Y = 858 ligger mot stigevangens
innerflate Y = 858, i Z 186..259.

* **1 vinkelbeslag 90×90×65** per stigevange, i hjørnet mellom benkevangens
  overside (Z 259) og stigevangens innerflate, **4 × treskrue 5 × 40**.
* Dette gir stigen et andre horisontalt holdepunkt 940 mm under boltene i J3 og
  halverer boltkraften der (§ 7, L17).

---

### J11 — Benkespile → benkevange (10 spiler) · 1 treskrue 5×70 per ende

Spile **34×98 × 906**, **Z 259..293**, Y −48..858 (48 mm anlegg på hver vange).

**X-posisjon, venstre kant** (deling **137,5 mm**, spalte **39,5 mm**).
Høyre benk er nøyaktig speilbilde av venstre:

| Venstre benk | 0 | 137,5 | 275 | 412,5 | 550 |
|---|---|---|---|---|---|
| **Høyre benk** | **1342** | **1479,5** | **1617** | **1754,5** | **1892** |

Ytterste spiler flukter med veggene (0 og 1990); de innerste stikker 3 mm ut over
benkevangens 645/1345-merke, uten betydning siden benkevangen er gjennomgående.

* Skruepunkt: spilens senter i X, **Y = −24** og **Y = 834**.
  5 × 70 = 34 mm gjennom spilen + 36 mm inn i vangens 73 mm. ✓
* Forbor ⌀3,5.
* Spalte 38,75 mm — godt under 60 mm, ingen klemfare.

---

### J12 — Bordbærelekt → stolpe (2 lekter × 4 opplegg) · 2 treskruer 5×60 hver

Begge lekter er 21×95 × **1984** og ligger **Z 371..466** (overkant 466).

* **Bakre lekt** på Y −48..−27, skrudd i innerflaten (Y = −48) på de to bakre
  hjørnestolpene **og** de to bakre stolpene fra C1.
* **Fremre lekt** på Y 837..858, skrudd i innerflaten (Y = 858) på de to fremre
  hjørnestolpene **og** de to stigevangene. Ingen kollisjon: stigevangene ligger
  Y 858..906, benkevangen Z 186..259.
* Festepunkter: **X 36, 748, 1242, 1954** — samme fire som rekkverket.
* To skruer per punkt, forskjøvet diagonalt: **(X<sub>p</sub> −12, Z 396)** og
  **(X<sub>p</sub> +13, Z 442)**. Kantavstand til lektas over-/underkant 25/24 mm. ✓
* **5 × 60** = 21 mm gjennom lekt + 39 mm inn i stolpens 48 mm. Forbor ⌀3.
* **Overkant Z 466** — ikke 482. Se avviksnotisen i § 0b: 3D-modellen viser 482
  fordi krokbeslagene ikke er modellert der.

---

### J13 — Krokbeslag → løs plate (4 beslag) · M6×30

Beslagene er bøyd av flattstål og har alle et **16 mm nedsteg**. Dermed lander
platens underkant nøyaktig 16 mm over den kanten beslaget hviler på:

| Modus | Beslaget hviler på | Kant Z | Plate u.k. | **Plate o.k.** |
|---|---|---|---|---|
| **Seng** | benkevangens overkant (bak Y −48..0, front Y 810..858) | 259 | 275 | **293** — flukt med benkespilene ✓ |
| **Bord** | bordbærelektas overkant (bak Y −48..−27, front Y 837..858) | 466 | 482 | **500** ✓ |

> **Platen er 680 × 828, Y 30..858** — ikke 860 mm dyp. Grunnen: platens X-område
> (655..1335) går forbi begge stigevangene, som står i Y 858..906. En plate som
> nådde til Y 890 ville kollidere med dem i begge moduser. Med forkanten på
> **Y = 858** flukter platen nøyaktig med stigevangenes innerflate, den fremre
> benkevangens ytterflate og den fremre bordbærelektas ytterflate. ✓

**Begge par er flattstål 30 × 4 mm**, montert ved **X 755 og X 1235**, hver med
**2 × M6×30** i flensen.

**Bakre par — lengde 135 mm:**

| Fra beslagets indre ende | Utforming | Y-posisjon |
|---|---|---|
| 0–60 mm | flens boltet flatt under platen, M6 ved 15 og 45 mm | Y 90 → 30 |
| 60–95 mm | rett utstikk i platens underkantplan | Y 30 → −5 |
| 95 mm | **16 mm nedsteg** | Y −5 |
| 95–135 mm | leppe som hviler på kanten | Y −5 → −45 |

**Fremre par — lengde 100 mm** (speilvendt, leppa peker utover mot forkanten):

| Fra beslagets indre ende | Utforming | Y-posisjon |
|---|---|---|
| 0–60 mm | flens boltet flatt under platen, M6 ved 15 og 45 mm | Y 758 → 818 |
| 60 mm | **16 mm nedsteg** | Y 818 |
| 60–100 mm | leppe som hviler på kanten | Y 818 → 858 |

**Anleggslengde på leppa:** bakre 40 mm på benkevangen (Y −48..0) og 18 mm på
bordbærelekta (Y −48..−27); fremre 40 mm på benkevangen (Y 810..858) og 21 mm på
bordbærelekta (Y 837..858). Alle godt innenfor det leppa trenger for 0,125 kN.

* Totalt **8 stk. M6×30 senkhodeskrue** med skive og låsemutter under platen.
  Forbor ⌀6,5 og forsenk ⌀13 i platens overside.
* Bøy stegene i skrustikke. Kontroller med tommestokk at platen ligger vannrett
  i begge moduser før du borer platehullene — juster ved å bøye litt.
* **Avstivningslekter:** 2 stk. 36×48 × **770** skrudd under platen i Y-retning
  (**Y 40..810**, klar av leppene) ved X 830..866 og X 1160..1196, med
  **6 × treskrue 5×40** hver ovenfra (forsenket). Reduserer nedbøyningen fra
  7,4 mm til ca. 1 mm ved 1 kN.

---

## 6. Monteringsrekkefølge

> **Sengen må monteres på plass i rommet.** Veggene står i X = 0 og X = 1990, og
> den ferdige rammen er akkurat 1990 mm bred — den kan ikke bæres inn eller
> vippes opp som en ferdig kasse. Ingen del må noen gang krysse X = 0 eller
> X = 1990.

### Trinn 0 — kapping og boring på bukk (gjør *alt* før noe monteres)

1. Kapp hele kapplista i § 3. Merk hver del med blyant.
   **Husk 1984 mm, ikke 1990, på alle liggende gjennomgående deler.**
2. Bor **⌀16 × 10 mm forsenkinger** i de fire hjørnestolpenes ytterflate
   (J1, 2 per stolpe = 8 stk.).
3. Bor **⌀20 klaringshull** i de to spilelektene — 4 i hver (X 36, 748, 1242,
   1954), til sammen 8.
4. Forbor alle treskruehull i 21 mm-bord og all endeved.
5. Bøy de fire krokbeslagene med 16 mm steg (J13).
6. **Ikke** bor M8-gjennomgangshullene ennå — de bores gjennom begge deler
   samtidig når delene er tvunget sammen, ellers bommer de.

### Trinn 1 — de to endrammene

Hver endramme = 2 hjørnestolper + 1 endebjelke + 2 bæreklosser J1-B.

1. Skru bæreklossene J1-B på stolpenes innerflate, **overkant nøyaktig Z 942**
   (mål fra stolpens nedre ende — den enden går mot gulvet).
2. Legg endebjelken på klossene, tving mot stolpene, kontroller 90° i begge hjørner.
3. Bor de fire ⌀8,5-hullene gjennom stolpe + bjelke (J1).
4. Sett i M8×130 låseskruer utenfra, slå firkanthalsen ned i forsenkningen,
   skive + låsemutter innenfra. Trekk til så treet får ~1 mm merke — ikke mer.

> **Takhøyde:** en ferdig endramme er 1002 × 1700, diagonal 1973 mm. Har du under
> ~2,05 m takhøyde kan den ikke vippes opp. Monter da stolpene stående ca. 200 mm
> ut fra veggen i X, bolt endebjelken på mens rammen står, og **skyv hele rammen
> sidelengs inn mot veggen** til slutt. Låseskruen krever ingen tilgang til hodet.

### Trinn 2 — reis endrammene

5. Sett venstre endramme mot venstre vegg (stolpeytterflate = X 0), høyre mot
   høyre vegg (X 1990). Lodd begge stolper i begge retninger.
6. **Avstiv midlertidig** med en skrålekt ned til gulvet i hver ende.

### Trinn 3 — sidevangene (det kritiske løftet)

7. Løft den **bakre vangen** (1984 mm) inn: hold den på skrå i X-Z-planet, senk
   og roter til vannrett *mens* du senker. Den lander på endebjelkenes overkant
   Z 1065, X 73..121 og 1869..1917.
8. Tving vangen inn mot begge bakre stolper, kontroller overkant Z 1188 og vater.
   Bor og bolt J2 (4 bolter).
9. Gjenta med den **fremre vangen**. Nå står rammen selv.
10. Kontroller diagonalene på oversiden — like innen 3 mm. Juster før du
    trekker til.

### Trinn 4 — mellomstolper (fire stk.)

11. Sett de to **stigevangene** (Y 858..906) på gulvet ved X 712..785 og
    X 1205..1278, klem mot den fremre vangens utside, lodd, bor og bolt **J3**.
12. Sett de to **bakre stolpene** (Y −96..−48) på nøyaktig samme X, mot baksiden
    av den bakre vangen, og bolt **J3b**.
13. Kontroller at alle **åtte** loddrette deler står med foten flatt på gulvet —
    de skal *bære*, ikke henge. Kile med tynne finérbiter om nødvendig.

### Trinn 5 — spilebunn

14. Skru spilelektene (36×48 × 1984) på vangenes innerflate, overkant Z 1113 (J4).
    Sett lekta på plass tørt først og kontroller at ⌀20-hullene treffer mutterne.
15. Legg de 13 køyespilene på og skru dem fast (J5).

### Trinn 6 — stige

16. Skru de 8 stigeklossene på stigevangenes innerflater (J6). **Mål hver
    klosshøyde fra gulvet**, ikke fra forrige kloss.
17. Legg rungene på og skru dem gjennom vangene (J7).

### Trinn 7 — rekkverk

18. **Velg C7-alternativ nå** (§ 0) og merk av båndhøydene på alle åtte stolper
    før du skrur.
19. Skru rekkverksbordene på (J8), fremre først.

### Trinn 8 — benker

20. Sett de fire stubbeføttene på plass (X 572..645 / 1345..1418, begge Y-plan).
21. Skru bæreklossene J9-B på hjørnestolpenes innerflate, overkant Z 186.
22. Legg de to gjennomgående benkevangene (1984 mm) inn — samme vippe-og-senke-
    manøver som sidevangene, men mye lettere. De lander på bæreklossene i begge
    ender og på stubbeføttene i midten.
23. Bolt **J9** (4 bolter), monter vinkelbeslag og skråskruer **J10**, og de to
    vinkelbeslagene mellom fremre benkevange og stigevangene **J10b**.
24. Skru på de 10 benkespilene 34×98 (J11). Kontroller at overflaten er **Z 293**.

### Trinn 9 — bord og plate

25. Skru på bakre og fremre bordbærelekt (J12), **overkant Z 466**, i alle fire
    festepunkter hver.
26. Bolt krokbeslagene under platen (J13). Prøveheng i begge moduser: platen skal
    ligge vannrett, i flukt med benkespilene (Z 293) i sengemodus og på Z 500 i
    bordmodus. Juster ved å bøye stegene litt.

### Trinn 10 — sikring og finish

27. **Fest rammen til veggen** hvis veggkonstruksjonen tillater det: 2 stk.
    vinkelbeslag 90×90 per ende, øverst på hver hjørnestolpe, med 6×80 treskrue
    inn i stender eller M8 ekspansjonsbolt i mur.
28. Filtknotter under alle 12 gulvpunkter.
29. Slip alle kanter, spesielt rungene og rekkverkstoppene.
30. Ettertrekk **alle 28 M8-muttere etter 2–4 uker** — trevirket krymper.
    Sett det i kalenderen.

---

## 7. LASTBANE-VERIFIKASJON — endelig, som bygget

**Materialforutsetninger:** C24 gran. f<sub>m,k</sub> = 24, f<sub>c,0,k</sub> = 21,
f<sub>c,90,k</sub> = 2,5, f<sub>v,k</sub> = 4,0 MPa, E<sub>mean</sub> = 11 000 MPa,
E<sub>0,05</sub> = 7 400 MPa. γ<sub>M</sub> = 1,3.
k<sub>mod</sub> = 0,8 (varig last) → f<sub>m,d</sub> = **14,8 MPa**;
k<sub>mod</sub> = 0,9 (korttid/dynamisk) → f<sub>m,d</sub> = **16,6 MPa**.
Trykk på tvers med k<sub>c,90</sub> = 1,5: **2,31 MPa**.

**Festemiddelkapasiteter** (konservative erfaringstall): treskrue 5 mm i skjær
**≈ 1,5 kN**, 6 mm **≈ 2,0 kN**; M8-bolt i *enkelt* skjær tre-mot-tre
**≈ 4–6 kN** (regnet med 4 kN).

**Designlaster:** overkøye 100 kg person + 10 kg madrass, dynamisk faktor 2 →
**2 kN punktlast**. Rungetrinn **1 kN**. Benk **1 kN**. Bordplate **0,5 kN**
kantlast. Rekkverk **0,5 kN** horisontalt.

**Frie spenn som bygget** (sidevanger og bordbærelekter, med de åtte stolpene):
121→712 = **591 mm** · 785→1205 = **420 mm** · 1278→1869 = **591 mm**.

---

### Kjede A — overkøyen: madrass → gulv

| # | Ledd | Bæremåte | Kapasitet | Last | Utn. | Dom |
|---|---|---|---|---|---|---|
| **L1** | Madrass → spile | Flatetrykk, fordeling over ≥ 3 spiler | — | 2 kN | — | ✓ |
| **L2** | **Køyespile 21×95, fritt spenn 774** | Bøyning | **0,60 kN/spile** → 1,8 kN over 3 spiler | 2 kN dynamisk | **1,11** | ⚠ **Eneste marginale ledd.** Statisk (1 kN) er utn. 0,55. Nedbøyning ved 0,6 kN: 7,2 mm. Se § 8.5. |
| **L3** | Spile → spilelekt | Trelagring 34 × 95 = 3230 mm² | 7,5 kN | 0,6 kN | 0,08 | ✓ |
| **L4** | Spilelekt → sidevange | Skruskjær, 5×70 c/c 200 | 3 skruer lokalt ≈ **4,5 kN** | 1,0 kN | 0,22 | ✓ |
| **L5** | **Bakre sidevange 48×123, bøyning** | Bøyning, W = 121 032 mm³ | M<sub>Rd</sub> = **2,01 kNm** | M = 2 kN × 0,591/4 = **0,30 kNm** | **0,15** | ✓ σ = **2,44 MPa**, δ = **0,11 mm**. |
| **L5-ref** | *Samme vange uten C1-stolpene (kontrollregning)* | Bøyning over 1844 mm | 2,01 kNm | **0,92 kNm** | 0,46 | ✓ σ = **7,62 MPa**, δ = **3,19 mm = L/578**. Vangen holdt også alene — C1 gir bare ekstra margin. |
| **L5b** | Skjær i vangen | τ = 1,5V/A | f<sub>v,d</sub> = 2,77 MPa | **0,25 MPa** | 0,09 | ✓ |
| **L5c** | Fremre sidevange | Identisk, avstivet av stigevangene | — | 591 mm | 0,15 | ✓ |
| **L6** | **Vange → endebjelke** | **Trelagring**, 48 × 48 = 2304 mm² | **5,3 kN** | ≤ 1,0 kN | 0,19 | ✓ Vangen *hviler*, den henger ikke i skruer. |
| **L7** | **Endebjelke → bærekloss J1-B** | **Trelagring**, 48 × 48 = 2304 mm² | **5,3 kN** | ≤ 1,0 kN | 0,19 | ✓ |
| **L8** | Bærekloss → stolpe | Skruskjær, 2 × 5×80 | **3,0 kN** | 1,0 kN | 0,33 | ✓ |
| **L8-ref** | *Uten J1-B (forkastet løsning)* | Kun boltskjær | — | 2 kN | — | ✗ Endeavstand i bjelken 24 mm mot kravet 4d = 32 mm. Bruddform: sprø oppflising av endeved. **Derfor er klossen bygget inn.** |
| **L9** | Endebjelke som bøyebjelke | Lasten kommer inn 0–48 mm fra opplegget | — | ~0 | ~0 | ✓ Bjelken er trykkstiver, ikke bøyebjelke. |
| **L10** | Hjørnestolpe 48×73 som søyle | Knekking, svak akse, L<sub>e</sub> = 1700 (konservativt) | λ = 123, k<sub>c</sub> = 0,21 → **9,5 kN** | ~1,0 kN | 0,11 | ✓ |
| **L11** | Stolpe → gulv | Endeved, 3504 mm² | 45 kN i treet; 0,29 MPa mot gulvet | 1,0 kN | 0,02 | ✓ |

---

### Kjede B — stigen

| # | Ledd | Bæremåte | Kapasitet | Last | Utn. | Dom |
|---|---|---|---|---|---|---|
| **L12** | **Rungetrinn 48×73 × 420** | Bøyning, W = 28 032 mm³ | M<sub>Rd</sub> = **0,47 kNm** | **0,105 kNm** | **0,23** | ✓ σ = 3,75 MPa, δ = **0,21 mm**. Trinnet kjennes helt stivt. |
| **L13** | Rung → stigekloss | **Trelagring** 36 × 73 = 2628 mm² | **6,1 kN** | 0,5 kN | 0,08 | ✓ |
| **L14** | Stigekloss → stigevange | Skruskjær, 2 × 5×70 | **3,0 kN** | 0,5 kN | 0,17 | ✓ |
| **L15** | J7-skrue i rungens endeved | Bærer **ingen** vertikal last | — | ~0 | — | ✓ Riktig utformet. |
| **L16** | **Stigevange → gulv** | Ren søyle ned til Z 0 | 9,5 kN | 1,0 kN | 0,11 | ✓ Ingen festemiddel i klatrelastens vei nedover. |
| **L17** | Stigevange → sidevange (J3) + benkevange (J10b) | Boltekobling oppe + vinkelbeslag nede | 2 × M8 = 8 kN; med J10b 940 mm under blir koblingskraften halvert | < 1,0 kN i boltparet | **0,25** | ✓ Var 0,45 uten J10b. Trekk til godt og **ettertrekk etter 2–4 uker**. |
| **L18** | Stigens sidestabilitet i X | Rammevirkning: 2 vanger + 4 runger + boltet topp | — | — | — | ✓ |

---

### Kjede C — benkene

| # | Ledd | Bæremåte | Kapasitet | Last | Utn. | Dom |
|---|---|---|---|---|---|---|
| **L19** | **Benkespile 34×98, fritt spenn 810** | Bøyning, W = 18 881 mm³ | **1,38 kN per spile** | 1,0 kN (stå på én spile) | **0,73** | ✓ σ = **10,72 MPa**, δ = **3,14 mm**. Ved vanlig sitting (0,5 kN) er utn. **0,36** og δ 1,6 mm. |
| **L19-ref** | *Samme med 21×95 (forkastet)* | Bøyning | 0,51 kN | 1,0 kN | **1,96** | ✗ Brudd. Dette er grunnen til C3. |
| **L20** | Spile → benkevange | Trelagring 48 × 98 = 4704 mm² | **10,9 kN** | 0,5 kN | 0,05 | ✓ |
| **L21** | **Benkevange 48×73 gjennomgående** | Bøyning over 700 mm åpning | M<sub>Rd</sub> = 0,63 kNm | 0,088 kNm | **0,14** | ✓ σ = 2,05 MPa, δ = 0,21 mm. Ved 1 kN: utn. 0,28, δ 0,42 mm. |
| **L22** | Benkevange → stubbefot | **Trelagring** 48 × 73 = 3504 mm² | **8,1 kN** | 0,5 kN | 0,06 | ✓ |
| **L23** | Benkevange → bærekloss J9-B → stolpe | Trelagring 36 × 73 = 2628 mm² → **6,1 kN**; kloss holdt av 3 × 5×70 = **4,5 kN** | | 0,5 kN | 0,11 | ✓ |
| **L23-ref** | *Uten J9-B (forkastet)* | Kun 1 M8-bolt | 4 kN | 0,5 kN | 0,13 | ⚠ Tallet var greit, men én bolt gir et **hengsel** — benkeenden ville vippe. |
| **L24** | Stubbefot → gulv | Endeved, 3504 mm² | 45 kN | 0,5 kN | 0,01 | ✓ |

---

### Kjede D — bordplate og rekkverk

| # | Ledd | Bæremåte | Kapasitet | Last | Utn. | Dom |
|---|---|---|---|---|---|---|
| **L25** | **Plate 18 mm furu, spenn 828 i Y** | Bøyning, 300 mm stripe | σ ved 0,5 kN = **6,39 MPa**, δ = 3,7 mm | 0,5 kN | **0,43** | ✓ som bord. Ved 1 kN: utn. **0,87**, δ 7,4 mm. **Monter avstivningslektene** (J13) — da faller δ til ca. 1 mm. |
| **L26** | Plate → krokbeslag | M6 i skjær, flattstål 30×4 / 60×4 | ≈ 3 kN per bolt | 0,125 kN per beslag | 0,04 | ✓ |
| **L27** | **Krokbeslag → bordbærelekt 21×95** | Bøyning om **sterk akse** (95 mm i Z), W = 31 588 mm³, spenn 591 | M<sub>Rd</sub> = **0,47 kNm** | **0,074 kNm** | **0,16** | ✓ σ = **2,34 MPa**, δ = **0,13 mm**. Ved 1 kN: 0,32. **Lekta må stå på høykant** — flatt lagt faller kapasiteten med faktor 20. |
| **L27-ref** | *Samme lekt uten C1-stolpene, spenn 1844* | Bøyning | 0,47 kNm | 0,23 kNm | 0,49 | ✓ (holdt også før, men δ var 4,0 mm) |
| **L28** | Bordbærelekt → stolpe | Skruskjær, 2 × 5×60 per punkt, 4 punkter | **3,0 kN** per punkt | 0,125 kN | 0,04 | ✓ |
| **L29** | **Rekkverksbord 21×95, horisontal last** | Bøyning om **svak akse**, maks spenn **639 mm** | **0,73 kN** | 0,5 kN | **0,69** | ✓ σ = **11,44 MPa**, δ = **3,37 mm**. Gjelder likt for bakre og fremre rekkverk — de fire festepunktene X 36/748/1242/1954 er symmetriske. |
| **L29-ref** | *Bakre rekkverk uten C1-stolpene* | Spenn 1844 mm | 0,73 kN | 0,5 kN | **1,99** | ✗ σ = 33,0 MPa, δ = **81 mm**. Dette var det alvorligste funnet, og er årsaken til C1. |
| **L30** | Rekkverksbord → stolpe | Skruskjær, 2 × 5×60 per punkt | **3,0 kN** | 0,25 kN | 0,08 | ✓ |

---

### Global stabilitet

| Retning | Motstand | Dom |
|---|---|---|
| **X (langs rommet)** | De to veggene; stolpene står inntil X 0 og X 1990. | ✓ — men rammen er ikke *festet*. **Gjør trinn 27** (vinkelbeslag i vegg). |
| **Y, øvre nivå** | Portalramme i hver ende: 2 stolper + endebjelke, 2 bolter per hjørne. Momentkapasitet per hjørne ved 53 mm boltavstand: **0,21 kNm**. | ✓ Den «mykeste» retningen; vinkelbeslag i vegg fjerner all gynging. |
| **Y, nedre nivå** | To gjennomgående benkevanger + 10 benkespiler danner en horisontal skive som knytter alle åtte stolper og fire stubbeføtter sammen. | ✓ Vesentlig stivere enn med delte benkevanger — en av gevinstene ved C5. |
| **Vipping forover** | Fotavtrykk 1002 mm dypt mot 1700 mm høyde; tyngdepunktet ligger godt innenfor. | ✓ |

---

### Endelig utnyttelsestabell

| Ledd | Utnyttelse | Dom |
|---|---|---|
| L2 køyespile 21×95, 2 kN dynamisk | **1,11** | ⚠ **eneste marginale** — se § 8.5 |
| L25 plate 18 mm ved 1 kN | 0,87 | ⚠ monter avstivningslektene |
| L19 benkespile 34×98 | **0,73** | ✓ |
| L29 rekkverksbord (639 mm) | **0,69** | ✓ |
| L5-ref bakre vange over 1844 mm | 0,46 | ✓ (kontrollregning) |
| L8 bærekloss → stolpe | 0,33 | ✓ |
| L17 stigevange → vange | 0,25 | ✓ |
| L12 rungetrinn | 0,23 | ✓ |
| L4 spilelekt → vange | 0,22 | ✓ |
| L6 / L7 trelagring vange–bjelke–kloss | 0,19 | ✓ |
| L27 bordbærelekt | 0,16 | ✓ |
| L5 bakre vange **som bygget** (591 mm) | **0,15** | ✓ |
| L21 benkevange | 0,14 | ✓ |
| L10 stolpeknekking | 0,11 | ✓ |
| Alle øvrige ledd | ≤ 0,11 | ✓ |

**Konklusjon:** ingen ledd i den bygde konstruksjonen har utnyttelse over 1,0.
Det eneste som ligger over 0,75 er køyespilene under en ren dynamisk
hopp-last (L2) og bordplaten uten avstivningslekter (L25); begge er dekket av
bruksreglene i § 8.

---

## 8. Sikkerhetsnotater

**8.1 Klemmespalter i rekkverket — DEN ENE ÅPNE BESLUTNINGEN.**
Se § 0. Velg alt. 1 eller alt. 2. Å bygge på de opprinnelige høydene gir
åpninger på 142 og 125 mm, midt i faresonen 75–230 mm.

**8.2 Madrasstykkelse.** Rekkverkshøyden er regnet for **maks 140 mm madrass**
(madrasstopp Z ≈ 1274). Tykkere madrass krever tilsvarende høyere rekkverk.
Skriv makstykkelsen på innsiden av en stolpe med tusj.

**8.3 Åpning i det fremre rekkverket.** Slik det er tegnet går rekkverksbordene
ubrutt forbi stigen — man klatrer **over** toppbordet. Det er vanlig på
loftsenger, men vurder å kappe det fremre rekkverket ved stigen (X 785..1205,
420 mm åpning) hvis brukeren er liten. Ikke gjør åpningen bredere enn ~400 mm.

**8.4 Aldersgrense.** Loftsenger og overkøyer anbefales generelt ikke til barn
under 6 år.

**8.5 Ikke stå på bar spilebunn (L2).** Køyespilene tåler **0,60 kN hver**.
Med madrass fordeles lasten over minst tre spiler og alt er greit; uten madrass
kan en voksen knekke én spile. Vil du ha margin her også: legg inn 15 spiler
i stedet for 13 (deling 135,4 mm) — det koster ett ekstra bord 21×95 og
16 skruer 4×40.

**8.6 Bordplaten skal ikke belastes på kanten.** Den henger på kroker og er ikke
låst. Ingen skal sette seg på bordkanten eller bruke platen som trinn. Vil du ha
en sperre: bor et ⌀6 hull ned gjennom beslagets leppe og ned i lekta, og stikk en
splint i.

**8.7 Monter avstivningslektene under platen (L25).** Uten dem bøyer platen
7,4 mm under 1 kN i midten.

**8.8 Ettertrekk.** Alle **28 M8-muttere** ettertrekkes etter 2–4 uker og
deretter årlig. Låsemutter (nylock), ikke vanlig mutter — sengen vibrerer hver
gang noen snur seg.

**8.9 Sikring mot vegg.** Gjør trinn 27. En loftseng som ikke er festet til noe
kan vandre noen millimeter i året, og da mister endebjelkene oppleggslengde.

---

## 9. Tegninger

Alle tegninger viser **som bygget**-geometrien, er målsatte, i riktige
proporsjoner, med borposisjoner markert som ⌀-merkede kryss. Målene er i mm og
stemmer med kapplista i § 3.

| Tegning | Innhold |
|---|---|
| [`schematics/side-elevation.svg`](schematics/side-elevation.svg) | Langsiden sett forfra: hjørnestolper, stigevanger (med de bakre stolpene rett bak), sidevange, rekkverksbånd, gjennomgående benkevange med bæreklosser, benkespiler 34×98 med topp Z 293, og alle boltposisjoner i X-Z-planet. |
| [`schematics/end-elevation.svg`](schematics/end-elevation.svg) | Kortsiden: stolpeparet, endebjelken med sine fire bolter og bæreklosser J1-B, sidevangene som hviler på endebjelken, bæreklosser J9-B, begge bordbærelekter og platen i begge høyder. |
| [`schematics/ladder-detail.svg`](schematics/ladder-detail.svg) | Stigevange + rungetrinn + stigekloss, med skrueposisjoner og alle fire trinnhøyder, samt vinkelbeslaget J10b mot benkevangen. |
| [`schematics/bench-detail.svg`](schematics/bench-detail.svg) | Gjennomgående benkevange mot hjørnestolpe med bærekloss J9-B, og benkevange på stubbefot med vinkelbeslag — med 34×98 benkespiler og benketopp Z 293. |
| [`schematics/panel-detail.svg`](schematics/panel-detail.svg) | Den løse platen i begge høyder (seng Z 293 / bord Z 500) med krokbeslagets 16 mm steg vist mot både benkevange og bordbærelekt. |
