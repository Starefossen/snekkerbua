<!-- GENERERT AV generate_loftbed.py / tools/gen_doc_tables.py.
     IKKE REDIGER FOR HÅND - kjør `mise run build`. -->

# Skrueretninger

Hvilken vei hver skrue drives, og hvorfor akkurat den veien. Hvert festemiddel i denne sengen er modellert som en kropp med egen retningsvektor; tabellen under er skrevet ut av de kroppene, ikke av en setning noen holder ved like. Tegningene i [MONTERING.md](../MONTERING.md) tegner de samme kroppene.

**Utledet** betyr at bare én retning er fysisk mulig: skruen må gå klar gjennom delen den drives fra og ende inne i den andre, altså `tykkelse(fra) < lengde < tykkelse(fra) + tykkelse(inn i)`. **Fastsatt** betyr at begge retninger ville holdt målene, eller at skruen ikke er en rett gjennomskrue i det hele tatt (skråskrue, gjennomgående bolt, beslagflik) — da er retningen den som står i leddtabellen, og den er satt for hånd og kontrollert mot geometrien.

**Der begge veier holder målene, avgjør fronten.** Sengens front — alt fra vangenes ytterflate og fram til stolpeplanet — er den eneste flaten noen ser på, og det skal ikke stå et skruehode i den. Ledd som griper i en del i det laget skrus derfor innenfra og ut, og linjene under sier det. Modellen asserter det: ingen festemiddelhoder på en romvendt flate.

**Hvor på delen hullet står** — så mange mm inn fra en navngitt ende og en navngitt kant, og senteravstanden mellom hullene — står i «festeplassering»-tabellen i det steget som eier leddet, i [byggesteg](byggesteg.md). Det er én plasseringslinje per rad i tabellen under, og den bijeksjonen er en assert på det ferdige blekket: en retning uten plassering, eller en plassering uten retning, feller bygget.

| Ledd | Festemiddel | Retning | Grunnlag |
|---|---|---|---|
| **J1** | 2× Treskrue 6×80 forsenket Torx | **Treskrue 6×80 forsenket Torx** gjennom endebjelke (36×98) → inn i hjørnestolpe (36×98), mot venstre vegg (speilvendt i den andre enden) | utledet av tykkelsene |
| **J2** | 2× Treskrue 6×80 forsenket Torx | **Treskrue 6×80 forsenket Torx** gjennom fremre sidevange (48×98) → inn i fremre hjørnestolpe (36×98), utover mot rommet | fastsatt — begge veier holder målene — skrudd innenfra og ut, så hodet ikke havner på den romvendte forflaten |
| **J2-B** | 2× Treskrue 6×120 forsenket Torx | **Treskrue 6×120 forsenket Torx** gjennom bakre sidevange (48×98) → inn i bakre hjørnestolpe (36×98), rett ned | utledet av tykkelsene |
| **J3** | 3× Treskrue 6×80 forsenket Torx | **Treskrue 6×80 forsenket Torx** gjennom fremre sidevange (48×98) → inn i stigevange (36×48), utover mot rommet | fastsatt — begge veier holder målene — skrudd innenfra og ut, så hodet ikke havner på den romvendte forflaten |
| **J4** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom rungetrinn (48×68) → inn i stigekloss (36×48), rett ned | fastsatt — begge veier holder målene |
| **J4** | 1× Treskrue 6×120 forsenket Torx | **Treskrue 6×120 forsenket Torx** gjennom stigevange (36×48) → inn i rungetrinn (48×68), mot høyre vegg (speilvendt i den andre enden) | utledet av tykkelsene |
| **J5** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom stigekloss (36×48) → inn i stigevange (36×48), mot venstre vegg (speilvendt i den andre enden) | fastsatt — begge veier holder målene |
| **J6** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom køyespile (23×98) → inn i sidevange (48×98), rett ned | utledet av tykkelsene |
| **J7** | 2× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom rekkverksbord (36×98) → inn i hjørnestolpe / stigevange (36×98), utover mot rommet | fastsatt — begge veier holder målene — skrudd innenfra og ut, så hodet ikke havner på den romvendte forflaten |
| **J8** | 2× Treskrue 6×80 forsenket Torx | **Treskrue 6×80 forsenket Torx** gjennom fremre benkevange (48×68) → inn i fremre hjørnestolpe (36×98), utover mot rommet | fastsatt — begge veier holder målene — skrudd innenfra og ut, så hodet ikke havner på den romvendte forflaten |
| **J8-B** | 2× Treskrue 6×80 forsenket Torx | **Treskrue 6×80 forsenket Torx** gjennom bakre benkevange (48×68) → inn i bakre hjørnestolpe (36×98), mot venstre vegg, 25° skrått innover mot veggen — skruen står i et flatbunnet sete, ⌀18 forstner 20 mm ned langs skruens egen akse (vinkelklossen), så hodet ligger helt under flaten (speilvendt i den andre enden) | fastsatt — skråskrue gjennom vangens forside nær enden |
| **J10** | 2× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom beslagfliken og mot høyre vegg inn i stubbefot (48×68) (speilvendt i den andre enden) | fastsatt |
| **J10** | 2× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom beslagfliken og rett opp inn i benkevange (48×68) | fastsatt |
| **J10** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom stubbefot (48×68) → inn i benkevange (48×68), rett opp, 30° skrått mot venstre vegg — skruen står i et flatbunnet sete, ⌀18 forstner 18 mm ned langs skruens egen akse (vinkelklossen), så hodet ligger helt under flaten (speilvendt i den andre enden) | fastsatt — skråskrue nedenfra opp i vangen |
| **J10** | 1× Vinkelbeslag 90×90×40×2,5 varmforsinket | **Vinkelbeslag 90×90×40×2,5 varmforsinket** ligger på stubbefot og bøyer om hjørnet til benkevange; skruene i fliken går mot høyre vegg (speilvendt i den andre enden) | fastsatt |
| **J11** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom benkespile (23×98) → inn i benkevange (48×68), rett ned | utledet av tykkelsene |
| **J11-E** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom endespile (23×98) → inn i fremre benkevange (48×68), rett ned | utledet av tykkelsene |
| **J16** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom endespile (23×98) → inn i endelist (36×48), rett ned | fastsatt — begge veier holder målene |
| **J17** | 2× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom endelist (36×48) → inn i bakre hjørnestolpe (36×98), innover mot veggen | fastsatt — begge veier holder målene |
| **J12** | 1× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom beslagfliken og mot venstre vegg inn i bakre hjørnestolpe (36×98) (speilvendt i den andre enden) | fastsatt |
| **J12** | 1× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom beslagfliken og rett opp inn i bordbærelekt (48×68) | fastsatt |
| **J12** | 1× Vinkelbeslag 40×40×20 | **Vinkelbeslag 40×40×20** ligger på bakre hjørnestolpe og bøyer om hjørnet til bordbærelekt; skruene i fliken går mot venstre vegg (speilvendt i den andre enden) | fastsatt |
| **J13a** | 6× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom avstivningslekt (48×68) → inn i løs plate (18 mm plate, 574 bred), rett opp — hodet står 41 mm inne i avstivningslekt, i bunnen av kontraboret, så skruen tar 13 mm i løs plate og ingenting går gjennom den andre siden | fastsatt — begge veier holder målene |
| **J13b** | 2× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom fremre kilelekt (48×68) → inn i løs plate (18 mm plate, 574 bred), rett opp — hodet står 27 mm under plata i alle tre hullene, så kontraboret grunner ut mot den skråkappede tuppen (dypest ved roten, null ved tuppen) og skruen tar 13 mm i løs plate uansett | fastsatt — begge veier holder målene |

**6** av retningene er utledet av målene alene, **18** er fastsatt for hånd. Alle sammen kontrolleres ved hver bygging: skruekroppen må ha hodet i plan med flaten den drives fra, spissen inne i delen den tar tak i, og ingenting av seg selv i noen annen del.

Veggfestet (J14) står ikke her — det går rett gjennom den bakre sidevangen og inn i veggen, og har ingen andre del å gå inn i.
