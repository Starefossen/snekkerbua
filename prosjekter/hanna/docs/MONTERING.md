<!-- GENERERT AV tools/gen_doc_tables.py under `mise run build`.
     IKKE REDIGER FOR HÅND. Strektegningene lages av
     `mise run montering` (tools/render_lineart.py). -->

# HANNA

## Loftseng med sofa, bord og ekstraseng under

![HANNA](img/hanna-hero.png)

| Bredde | Dybde | Høyde |
|---:|---:|---:|
| **1990 mm** | **836 mm** | **2037 mm** |

70 deler · 12 steg (0–11) · 2 personer · passer standard madrass 80 × 200 cm

Sengen står inntil bakveggen og inntil begge sidevegger, og skrus fast i bakveggen. **Bygg bakfra og utover.**

Ord og begrunnelser: [ASSEMBLY.md](ASSEMBLY.md). Full steg-for-steg-tekst: [byggesteg](generated/byggesteg.md).

---

# Mål rommet først

Nisja er hverken i vinkel eller i vater, og senga skal stå i begge deler. **Senga er referansen, ikke rommet — bygg i vater og lodd, og ta skjevheten i delene som møter vegg og gulv.**

1. Vent til vegger og gulv er ferdige. **Mens veggen er åpen: legg spikerslag i sonene under.** Etterpå kommer du ikke til.
2. Slå et vannrett høyderiss rundt hele nisja med linjelaser, 1000 mm over ferdig gulv. Alt måles fra risset, aldri fra gulvet — spikerslagsonene under står i begge notasjoner, og det er riss-kolonnen du setter dem etter.
3. Sett laseren som loddlinje midt i nisja. Mål ut til hver endevegg i rutenett: 5 høyder × 3 dybder på hver vegg. Legg sammen paret i hvert punkt. **Minste sum er nisjas minste bredde.**
4. Er minste bredde et annet tall enn 1990: sett den inn som `WALL_SPAN` i `generate_loftbed.py` og kjør `mise run build`. Kapplista regner seg om.
5. Gulv: mål ned fra risset i sengas fire hjørner og på midten. Merk det høyeste punktet på gulvet. Senga bygges ned fra det.
6. Kapp verksteddelene nå. Romdelene tilpasses på stedet: stolper og føtter kappes 15 mm for lange og trimmes i bunn til rammen står i vater — strek opp med avstandskloss, meddrag. Sidevangene kappes 10 mm for lange i hver veggende og finkappes etter målt bredde. Ytterste endespile strekes opp etter veggen med fast avstand, så fugen blir jevn.
7. **De fire hjørnestolpene står helt inntil endeveggen — null klaring.** Derfor strekes veggsiden på hver av dem, hver gang: sett stolpen på plass, hold den i lodd, og strek opp veggsiden med avstandskloss der veggen buler. Høvle av til stolpen står i lodd inntil veggen. Ingen monn i bredden — det er tre som skal bort, ikke legges til. Buler veggen og du lar det stå, skyver bulen hele rammen ut av lodd.
8. Kapp kanter som møter vegg eller gulv med lite bakfall. Da er det bare den synlige kanten som bestemmer fugen.

<img src="img/maal-rommet.png" alt="Nisja som rom, med oppriss og plan ved siden av: høyderisset 1000 mm over ferdig gulv går som en ring rundt alle tre veggene, loddplanet står midt i nisja, og hver endevegg måles i 5 høyder × 3 dybder" height="406">


**Slik strekes en del opp mot vegg og gulv:**

| Slik | Ikke slik | |
|:---:|:---:|---|
| <img src="img/ikon/meddrag-ja.svg" alt="meddrag-ja" height="72"> <img src="img/ikon/hake.svg" alt="ja" height="26"> | <img src="img/ikon/punktmaal-nei.svg" alt="punktmaal-nei" height="72"> <img src="img/ikon/kryss.svg" alt="nei" height="26"> | **Avstandskloss, ikke tommestokk.** Klossen følger veggen hele veien, og blyanten mot klossens ytterkant gir emnet veggens form. Ett punktmål gir en rett strek mot en vegg som ikke er rett. |

**Spikerslag i veggen** — legg dem mens veggen er åpen:

| Sone | Fra ferdig gulv | Fra høyderisset (1000) | Vegg | Del som skal ha feste |
|---:|---|---|---|---|
| 1 | **0–1402** | **-1000..+402 krysser risset** | Hjørnene, mot endeveggene | Hjørnestolpe, bak (veggside) (2 stk.) |
| 2 | **229–297** | **-771..-703 under risset** | Bakveggen | Benkevange, bak (gjennomgående) |
| 3 | **474–542** | **-526..-458 under risset** | Bakveggen | Bordbærelekt, bak |
| 4 | **1402–1500** | **+402..+500 over risset** | Bakveggen | Sidevange, øvre |

To notasjoner, samme sone. **Målt fra ferdig gulv** er modellens egen Z. **Målt fra høyderisset** er den samme høyden minus 1000 — minus er *under* laserlinja, pluss er *over* den. Gulvet er skjevt og risset er ikke: står du ved den åpne veggen med målebåndet på laserlinja, er det den andre kolonnen du setter sonene etter.

Gulv-kolonnen er fra **ferdig gulv**. Legges gulvet etterpå, må påforingshøyden legges til — i begge kolonner, for risset slås fra ferdig gulv det også.

⚠️ Høyderisset skal gå hele veien rundt nisja og møte seg selv. Gjør det ikke det, står laseren feil.

---

# Før du begynner

**Svart strek** er delen du setter opp nå. **Grå strek** er det som allerede står.

**Festemidlene er tegnet, ikke antydet.** Hver skrue, bolt og hvert beslag på stegsidene er den samme kroppen som står i modellen, i sin egen lengde og langs sin egen akse — så en skrue som peker feil vei eller er for lang stopper byggingen av manualen, ikke først byggingen av sengen.

**Trukket ut av hullet:** på de fleste stegene er festemidlene tegnet et stykke ut langs sin egen akse, med en **prikket linje** ned i hullet de skal i og en **prikk** der hullet er. Den prikkede linjen betyr festemiddel og ingenting annet; **piler** brukes bare om tredeler som skal føres sammen. På de stegene som setter tjue-tretti like skruer — spilene — er de tegnet **der de havner** i stedet: hodet fylt, og den delen som ligger begravd i treet **stiplet**.

**Bokstaven i ringen** (Ⓐ, Ⓑ …) sier hvilken av stegets typer et festemiddel er, og går igjen i tabellen under bildet. Den sitter alltid **på** skruen den gjelder, eller har en tynn strek bort til den — den peker aldri i løse lufta. Der to skruer på samme side er nesten like lange, skilles de i tillegg med **fyll** i silhuetten — den samme bokstaven én gang til, så du ser hvilken av dem det er uten å lese: åpen, skravert, krysskravert, heldekt. Ellers står skruene i ren kontur, for da skiller lengden dem selv. Hele koden står på [beslagsiden](#beslag).

**Antallet står ikke i bildet.** Festemidlene er tegnet ett for ett, der de går — bare to som havner nøyaktig oppå hverandre på papiret er tegnet én gang. Hvor mange det er i alt står i ruta i hjørnet og i tabellen under bildet. **Ruta i hjørnet** viser leddet i snitt, med delene i riktig innbyrdes størrelse, skravur på snittflatene og festemidlene i full lengde — hodet på skrusiden, spissen inne i mottakerdelen.

| Slik | Ikke slik | |
|:---:|:---:|---|
| <img src="img/ikon/to-personer.svg" alt="to-personer" height="72"> <img src="img/ikon/hake.svg" alt="ja" height="26"> | <img src="img/ikon/en-person-nei.svg" alt="en-person-nei" height="72"> <img src="img/ikon/kryss.svg" alt="nei" height="26"> | **To personer.** Bakrammen veier mye og skal reises loddrett. |
| <img src="img/ikon/underlag.svg" alt="underlag" height="72"> <img src="img/ikon/hake.svg" alt="ja" height="26"> | <img src="img/ikon/dra-nei.svg" alt="dra-nei" height="72"> <img src="img/ikon/kryss.svg" alt="nei" height="26"> | **Mykt underlag.** Bygg rammene flatt på papp eller teppe. Ikke dra delene over gulvet. |
| <img src="img/ikon/sorter.svg" alt="sorter" height="72"> <img src="img/ikon/hake.svg" alt="ja" height="26"> |  | **Sorter delene** etter kapplista, og merk hver del på en flate som blir skjult. |
| <img src="img/ikon/blyant-foerst.svg" alt="blyant-foerst" height="72"> <img src="img/ikon/hake.svg" alt="ja" height="26"> | <img src="img/ikon/skrutrekker-foerst-nei.svg" alt="skrutrekker-foerst-nei" height="72"> <img src="img/ikon/kryss.svg" alt="nei" height="26"> | **Blyanten først.** Merk av hvert kapp og hvert hull før du skrur — all saging og all boring skjer i steg 0, før noe reises. |
| <img src="img/ikon/verktoy.svg" alt="verktoy" height="72"> <img src="img/ikon/hake.svg" alt="ja" height="26"> |  | **Verktøy:** drill med bor, torxbits, tommestokk, vater og vinkelhake. |
| <img src="img/ikon/forbor.svg" alt="forbor" height="72"> <img src="img/ikon/hake.svg" alt="ja" height="26"> |  | **Forbor.** I bordene og i all endeved er forboring et krav. |
| <img src="img/ikon/veggfeste-ja.svg" alt="veggfeste-ja" height="72"> <img src="img/ikon/hake.svg" alt="ja" height="26"> | <img src="img/ikon/fritt-staaende-nei.svg" alt="fritt-staaende-nei" height="72"> <img src="img/ikon/kryss.svg" alt="nei" height="26"> | **Sengen skal skrus fast i veggen.** Den er ikke beregnet på å stå fritt — veggen er sperren på baksiden. |

---

# Beslag

<img src="img/beslag/notasjon.svg" alt="5 = tykkelse i mm, 60 = lengde i mm, 100x = antall" height="104">

<img src="img/beslag/fyllkode.svg" alt="Fyllkoden: A åpen, B skravert, C krysskravert, D heldekt" height="96">

**Fyllkode.** Der to skruer på samme side er nesten like lange, skilles de med fyll — ellers står festemidlene i ren kontur.

| | |
|:---:|---|
| <img src="img/beslag/treskrue-5x60.svg" alt="Treskrue 5×60 forsenket Torx" height="44"> **96x** | Treskrue 5×60 forsenket Torx |
| <img src="img/beslag/treskrue-5x40.svg" alt="Treskrue 5×40 forsenket Torx" height="44"> **36x** | Treskrue 5×40 forsenket Torx |
| <img src="img/beslag/treskrue-6x80.svg" alt="Treskrue 6×80 forsenket Torx" height="44"> **26x** | Treskrue 6×80 forsenket Torx |
| <img src="img/beslag/treskrue-6x120.svg" alt="Treskrue 6×120 forsenket Torx" height="44"> **14x** | Treskrue 6×120 forsenket Torx |
| <img src="img/beslag/filtknott-d40.svg" alt="Filtknott / møbeltapp ⌀40" height="44"> **8x** | Filtknott / møbeltapp ⌀40 |
| <img src="img/beslag/veggfeste-8x100.svg" alt="Veggfeste etter veggtype (treskrue 8×100 i stender, eller plugg + skrue i mur)" height="44"> **6x** | Veggfeste etter veggtype (treskrue 8×100 i stender, eller plugg + skrue i mur) |
| <img src="img/beslag/vinkelbeslag-90x90x40.svg" alt="Vinkelbeslag 90×90×40×2,5 varmforsinket" height="179"> **4x** | Vinkelbeslag 90×90×40×2,5 varmforsinket |
| <img src="img/beslag/vinkelbeslag-40x40x20.svg" alt="Vinkelbeslag 40×40×20" height="84"> **2x** | Vinkelbeslag 40×40×20 |

Hvor hver enkelt går, og hva som forbores: [beslagliste](generated/beslagliste.md). Hvilken vei hver enkelt drives, og hvorfor: [skrueretninger](generated/skrueretninger.md).

---

# Delene

| Del | Dim. | Lengde | Ant. | Kapp |
|---|---|---:|---:|---|
| Løs plate | 18 mm plate, 574 bred | 798 | **1** | nå |
| Benkespile | 23×98 | 800 | **10** | nå |
| Køyespile | 23×98 | 800 | **14** | nå |
| Endespile | 23×98 | 764 | **2** | på stedet |
| Stigevange | 36×48 | 2037 | **2** | på stedet |
| Endelist | 36×48 | 98 | **2** | på stedet |
| Stigekloss | 36×48 | 36 | **10** | nå |
| Hjørnestolpe, front | 36×98 | 2037 | **2** | på stedet |
| Hjørnestolpe, bak (veggside) | 36×98 | 1402 | **2** | på stedet |
| Endebjelke | 36×98 | 836 | **2** | nå |
| Rekkverksbord, front | 36×98 | 832 | **4** | på stedet |
| Benkevange, bak (gjennomgående) | 48×68 | 1794 | **1** | nå |
| Bordbærelekt, bak | 48×68 | 1794 | **1** | nå |
| Avstivningslekt under plate | 48×68 | 750 | **2** | nå |
| Benkevange, front (bit) | 48×68 | 642 | **2** | på stedet |
| Rungetrinn | 48×68 | 320 | **5** | nå |
| Stubbefot | 48×68 | 229 | **4** | på stedet |
| Kilelekt under platens forkant (skråkappet) | 48×68 | 77 | **2** | nå |
| Sidevange, øvre | 48×98 | 1984 | **2** | på stedet |

**70 deler.** **Ant.** er antallet — det samme tallet som står som `4×` på stegsidene. **Dim.** og **Lengde** er i millimeter.

**Kapp:** «nå» er delene verkstedet gjør ferdig. «på stedet» er de 22 delene som møter en endevegg eller gulvet — de kappes med overmål og finkappes i rommet. Overmålet står i [kapplista](generated/kappliste.md).

Posisjoner: [kappliste](generated/kappliste.md). Hva du skal kjøpe: [innkjøpsliste](generated/innkjopsliste.md).

---

# 0

## Kapping, forboring og forsenking

![Steg 0](img/steg-00.png)

| | |
|:---:|---|
| <img src="img/beslag/filtknott-d40.svg" alt="Filtknott / møbeltapp ⌀40" height="30"> **8x** | Filtknott ⌀40 |

Ledd **J15** → [beslagliste](generated/beslagliste.md)

⚠️ Romdelene skal IKKE kappes ferdig nå. Kapplista sier hvilke — de kappes med overmål og finkappes i rommet.

[Steg 0 i ord](generated/byggesteg.md#steg-0--kapping-forboring-og-forsenking)

---

# 1

## Bakrammen — bygg den flatt på gulvet

![Steg 1](img/steg-01.png)

| Ant. | Del | Dim. | Lengde |
|---:|---|---|---:|
| **1×** | Benkevange, bak (gjennomgående) | 48×68 | 1794 |
| **1×** | Bordbærelekt, bak | 48×68 | 1794 |
| **2×** | Hjørnestolpe, bak (veggside) | 36×98 | 1402 |
| **1×** | Sidevange, øvre | 48×98 | 1984 |

| | | |
|:---:|:---:|---|
| <img src="img/ikon/merke-a.svg" alt="A" height="20"> | <img src="img/beslag/treskrue-5x40.svg" alt="Treskrue 5×40 forsenket Torx" height="30"> **4x** | Treskrue 5×40 |
| <img src="img/ikon/merke-b.svg" alt="B" height="20"> | <img src="img/beslag/treskrue-6x120.svg" alt="Treskrue 6×120 forsenket Torx" height="30"> **4x** | Treskrue 6×120 |
| <img src="img/ikon/merke-c.svg" alt="C" height="20"> | <img src="img/beslag/treskrue-6x80.svg" alt="Treskrue 6×80 forsenket Torx" height="30"> **4x** | Treskrue 6×80 |
| <img src="img/ikon/merke-d.svg" alt="D" height="20"> | <img src="img/beslag/vinkelbeslag-40x40x20.svg" alt="Vinkelbeslag 40×40×20" height="58"> **2x** | Vinkelbeslag 40×40×20 |

Bokstavene viser hvor på tegningen hver type går.

Ledd **J2-B**, **J8-B**, **J12** → [beslagliste](generated/beslagliste.md)

⚠️ Mål diagonalene i rammen — de skal være like.

[Steg 1 i ord](generated/byggesteg.md#steg-1--bakrammen--bygg-den-flatt-på-gulvet)

---

# 2

## Reis bakrammen og skru den fast i veggen

![Steg 2](img/steg-02.png)

| | |
|:---:|---|
| <img src="img/beslag/veggfeste-8x100.svg" alt="Veggfeste etter veggtype (treskrue 8×100 i stender, eller plugg + skrue i mur)" height="30"> **6x** | Veggfeste |

Ledd **J14** → [beslagliste](generated/beslagliste.md)

⚠️ Vater langs sidevangen, og lodd på begge stolper.

[Steg 2 i ord](generated/byggesteg.md#steg-2--reis-bakrammen-og-skru-den-fast-i-veggen)

---

# 3

## Endebjelkene og de fremre stolpene

![Steg 3](img/steg-03.png)

| Ant. | Del | Dim. | Lengde |
|---:|---|---|---:|
| **2×** | Endebjelke | 36×98 | 836 |
| **2×** | Hjørnestolpe, front | 36×98 | 2037 |

| | |
|:---:|---|
| <img src="img/beslag/treskrue-6x80.svg" alt="Treskrue 6×80 forsenket Torx" height="30"> **8x** | Treskrue 6×80 |

Ledd **J1** → [beslagliste](generated/beslagliste.md)

⚠️ Vater på begge endebjelker, og kontroller at de ligger i nøyaktig samme høyde.

[Steg 3 i ord](generated/byggesteg.md#steg-3--endebjelkene-og-de-fremre-stolpene)

---

# 4

## Fremre sidevange

![Steg 4](img/steg-04.png)

| Ant. | Del | Dim. | Lengde |
|---:|---|---|---:|
| **1×** | Sidevange, øvre | 48×98 | 1984 |

| | |
|:---:|---|
| <img src="img/beslag/treskrue-6x80.svg" alt="Treskrue 6×80 forsenket Torx" height="30"> **4x** | Treskrue 6×80 |

Ledd **J2** → [beslagliste](generated/beslagliste.md)

⚠️ Mål avstanden mellom de to sidevangene i begge ender og på midten. Den skal være lik overalt — det er madrassbredden, og madrassen er kappet nøyaktig etter den.

[Steg 4 i ord](generated/byggesteg.md#steg-4--fremre-sidevange)

---

# 5

## Fremre benkevanger, stubbeføtter og endelister

![Steg 5](img/steg-05.png)

| Ant. | Del | Dim. | Lengde |
|---:|---|---|---:|
| **2×** | Benkevange, front (bit) | 48×68 | 642 |
| **2×** | Endelist | 36×48 | 98 |
| **4×** | Stubbefot | 48×68 | 229 |

| | | |
|:---:|:---:|---|
| <img src="img/ikon/merke-a.svg" alt="A" height="20"> | <img src="img/beslag/treskrue-5x40.svg" alt="Treskrue 5×40 forsenket Torx" height="30"> **16x** | Treskrue 5×40 |
| <img src="img/ikon/merke-b.svg" alt="B" height="20"> | <img src="img/beslag/treskrue-5x60.svg" alt="Treskrue 5×60 forsenket Torx" height="30"> **8x** | Treskrue 5×60 |
| <img src="img/ikon/merke-c.svg" alt="C" height="20"> | <img src="img/beslag/treskrue-6x80.svg" alt="Treskrue 6×80 forsenket Torx" height="30"> **4x** | Treskrue 6×80 |
| <img src="img/ikon/merke-d.svg" alt="D" height="20"> | <img src="img/beslag/vinkelbeslag-90x90x40.svg" alt="Vinkelbeslag 90×90×40×2,5 varmforsinket" height="72"> **4x** | Vinkelbeslag 90×90×40×2,5 |

Bokstavene viser hvor på tegningen hver type går.

Ledd **J8**, **J10**, **J17** → [beslagliste](generated/beslagliste.md)

⚠️ Ingenting skal krysse gulvet mellom de to benkene.

[Steg 5 i ord](generated/byggesteg.md#steg-5--fremre-benkevanger-stubbeføtter-og-endelister)

---

# 6

## Stigen

![Steg 6](img/steg-06.png)

| Ant. | Del | Dim. | Lengde |
|---:|---|---|---:|
| **5×** | Rungetrinn | 48×68 | 320 |
| **10×** | Stigekloss | 36×48 | 36 |
| **2×** | Stigevange | 36×48 | 2037 |

| | | |
|:---:|:---:|---|
| <img src="img/ikon/merke-a.svg" alt="A" height="20"> | <img src="img/beslag/treskrue-5x60.svg" alt="Treskrue 5×60 forsenket Torx" height="30"> **20x** | Treskrue 5×60 |
| <img src="img/ikon/merke-b.svg" alt="B" height="20"> | <img src="img/beslag/treskrue-6x120.svg" alt="Treskrue 6×120 forsenket Torx" height="30"> **10x** | Treskrue 6×120 |
| <img src="img/ikon/merke-c.svg" alt="C" height="20"> | <img src="img/beslag/treskrue-6x80.svg" alt="Treskrue 6×80 forsenket Torx" height="30"> **6x** | Treskrue 6×80 |

Bokstavene viser hvor på tegningen hver type går.

Ledd **J3**, **J4**, **J5** → [beslagliste](generated/beslagliste.md)

⚠️ Mål lysåpningen mellom stigevangene øverst og nederst — den skal være lik.

[Steg 6 i ord](generated/byggesteg.md#steg-6--stigen)

---

# 7

## Benkespiler og endespiler

![Steg 7](img/steg-07.png)

| Ant. | Del | Dim. | Lengde |
|---:|---|---|---:|
| **10×** | Benkespile | 23×98 | 800 |
| **2×** | Endespile | 23×98 | 764 |

| | |
|:---:|---|
| <img src="img/beslag/treskrue-5x60.svg" alt="Treskrue 5×60 forsenket Torx" height="30"> **24x** | Treskrue 5×60 |

Ledd **J11**, **J11-E**, **J16** → [beslagliste](generated/beslagliste.md)

⚠️ Kjenn over hele benken med håndflaten: ingen skruehoder skal stikke opp.

[Steg 7 i ord](generated/byggesteg.md#steg-7--benkespiler-og-endespiler)

---

# 8

## Køyespiler

![Steg 8](img/steg-08.png)

| Ant. | Del | Dim. | Lengde |
|---:|---|---|---:|
| **14×** | Køyespile | 23×98 | 800 |

| | |
|:---:|---|
| <img src="img/beslag/treskrue-5x60.svg" alt="Treskrue 5×60 forsenket Torx" height="30"> **28x** | Treskrue 5×60 |

Ledd **J6** → [beslagliste](generated/beslagliste.md)

⚠️ Alle spiler skal dekke hele bredden av begge vanger. Ligger en spile bare halvveis på vangen, flytt den.

[Steg 8 i ord](generated/byggesteg.md#steg-8--køyespiler)

---

# 9

## Rekkverk foran

![Steg 9](img/steg-09.png)

| Ant. | Del | Dim. | Lengde |
|---:|---|---|---:|
| **4×** | Rekkverksbord, front | 36×98 | 832 |

| | |
|:---:|---|
| <img src="img/beslag/treskrue-5x60.svg" alt="Treskrue 5×60 forsenket Torx" height="30"> **16x** | Treskrue 5×60 |

Ledd **J7** → [beslagliste](generated/beslagliste.md)

⚠️ Mål åpningene over madrassoverflaten mot tallene i nøkkelmålene. De er sikkerhetskravet i denne sengen.

[Steg 9 i ord](generated/byggesteg.md#steg-9--rekkverk-foran)

---

# 10

## Løs plate med fire lekter — og ingen beslag

![Steg 10](img/steg-10.png)

| Ant. | Del | Dim. | Lengde |
|---:|---|---|---:|
| **2×** | Avstivningslekt under plate | 48×68 | 750 |
| **2×** | Kilelekt under platens forkant (skråkappet) | 48×68 | 77 |
| **1×** | Løs plate | 18 mm plate, 574 bred | 798 |

| | |
|:---:|---|
| <img src="img/beslag/treskrue-5x40.svg" alt="Treskrue 5×40 forsenket Torx" height="30"> **16x** | Treskrue 5×40 |

Ledd **J13a**, **J13b** → [beslagliste](generated/beslagliste.md)

⚠️ Skyv platen sidelengs. Den skal bevege seg et par millimeter og så stoppe mot trinnenden — begge veier, i begge stillinger.

[Steg 10 i ord](generated/byggesteg.md#steg-10--løs-plate-med-fire-lekter--og-ingen-beslag)

---

# 11

## Madrass og puter

![Steg 11](img/steg-11.png)

| Ant. | Del | Dim. | Lengde |
|---:|---|---|---:|
| **2×** | Benkepute, skum **100 mm** (663 × 800 mm, hakk 98 × 36 i veggkanten) |  |  |
| **1×** | Madrass 80 × 200 cm, **120 mm tykk** (vindu 110–125 mm) |  |  |
| **2×** | Ryggpute, skum **100 mm** (332 × 800 mm) |  |  |

⚠️ Ettertrekk alle festemidler som kan ettertrekkes.

[Steg 11 i ord](generated/byggesteg.md#steg-11--madrass-og-puter)

---

Tegningene i `docs/img/` er projisert ut av modellen og sjekket inn i git. De lages på nytt med `mise run montering`.
