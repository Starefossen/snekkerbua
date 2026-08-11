<!-- GENERERT AV generate_loftbed.py / tools/gen_doc_tables.py.
     IKKE REDIGER FOR HÅND - kjør `mise run build`. -->

# Skrueretninger

Hvilken vei hver skrue drives, og hvorfor akkurat den veien. Hvert festemiddel i denne sengen er modellert som en kropp med egen retningsvektor; tabellen under er skrevet ut av de kroppene, ikke av en setning noen holder ved like. Tegningene i [MONTERING.md](../MONTERING.md) tegner de samme kroppene.

**Utledet** betyr at bare én retning er fysisk mulig: skruen må gå klar gjennom delen den drives fra og ende inne i den andre, altså `tykkelse(fra) < lengde < tykkelse(fra) + tykkelse(inn i)`. **Fastsatt** betyr at begge retninger ville holdt målene, eller at skruen ikke er en rett gjennomskrue i det hele tatt (skråskrue, gjennomgående bolt, beslagflik) — da er retningen den som står i leddtabellen, og den er satt for hånd og kontrollert mot geometrien.

| Ledd | Festemiddel | Retning | Grunnlag |
|---|---|---|---|
| **J1** | 2× Treskrue 6×90 forsenket Torx | **Treskrue 6×90 forsenket Torx** gjennom endebjelke (48×98) → inn i hjørnestolpe (36×98), mot venstre vegg (speilvendt i den andre enden) | utledet av tykkelsene |
| **J1-B** | 1× Treskrue 6×90 forsenket Torx | **Treskrue 6×90 forsenket Torx** gjennom bærekloss under endebjelke (36×48) → inn i hjørnestolpe (36×98), mot venstre vegg (speilvendt i den andre enden) | utledet av tykkelsene |
| **J2** | 2× Treskrue 6×80 forsenket Torx | **Treskrue 6×80 forsenket Torx** gjennom fremre hjørnestolpe (36×98) → inn i fremre sidevange (48×98), innover mot veggen | fastsatt — begge veier holder målene |
| **J2-B** | 2× Treskrue 6×120 forsenket Torx | **Treskrue 6×120 forsenket Torx** gjennom bakre sidevange (48×98) → inn i bakre hjørnestolpe (36×98), rett ned | utledet av tykkelsene |
| **J3** | 3× Treskrue 6×80 forsenket Torx | **Treskrue 6×80 forsenket Torx** gjennom stigevange (36×48) → inn i fremre sidevange (48×98), innover mot veggen | fastsatt — begge veier holder målene |
| **J4** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom rungetrinn (48×73) → inn i stigekloss (36×48), rett ned | fastsatt — begge veier holder målene |
| **J4** | 1× Treskrue 6×120 forsenket Torx | **Treskrue 6×120 forsenket Torx** gjennom stigevange (36×48) → inn i rungetrinn (48×73), mot høyre vegg (speilvendt i den andre enden) | utledet av tykkelsene |
| **J5** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom stigekloss (36×48) → inn i stigevange (36×48), mot venstre vegg (speilvendt i den andre enden) | fastsatt — begge veier holder målene |
| **J6** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom køyespile (36×98) → inn i sidevange (48×98), rett ned | utledet av tykkelsene |
| **J7** | 2× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom rekkverksbord (36×98) → inn i hjørnestolpe / stigevange (36×98), utover mot rommet | fastsatt — begge veier holder målene |
| **J8** | 2× Treskrue 6×80 forsenket Torx | **Treskrue 6×80 forsenket Torx** gjennom fremre hjørnestolpe (36×98) → inn i fremre benkevange (48×73), innover mot veggen | fastsatt — begge veier holder målene |
| **J8-B** | 2× Treskrue 6×90 forsenket Torx | **Treskrue 6×90 forsenket Torx** gjennom bakre benkevange (48×73) → inn i bakre hjørnestolpe (36×98), mot venstre vegg, 25° skrått innover mot veggen (speilvendt i den andre enden) | fastsatt — skråskrue gjennom vangens forside nær enden |
| **J9-B** | 1× Treskrue 6×90 forsenket Torx | **Treskrue 6×90 forsenket Torx** gjennom bærekloss under bakre benkevange (36×48) → inn i bakre hjørnestolpe (36×98), mot venstre vegg (speilvendt i den andre enden) | utledet av tykkelsene |
| **J9-F** | 1× Treskrue 6×60 forsenket Torx | **Treskrue 6×60 forsenket Torx** gjennom bærekloss under fremre benkevange (36×48) → inn i fremre hjørnestolpe (36×98), utover mot rommet | fastsatt — begge veier holder målene |
| **J10** | 2× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom beslagfliken og mot høyre vegg inn i stubbefot (48×73) (speilvendt i den andre enden) | fastsatt |
| **J10** | 2× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom beslagfliken og rett opp inn i benkevange (48×73) | fastsatt |
| **J10** | 1× Treskrue 5×70 forsenket Torx | **Treskrue 5×70 forsenket Torx** gjennom stubbefot (48×73) → inn i benkevange (48×73), rett opp, 30° skrått mot venstre vegg (speilvendt i den andre enden) | fastsatt — skråskrue nedenfra opp i vangen |
| **J10** | 1× Vinkelbeslag 90×90×40×2,5 varmforsinket | **Vinkelbeslag 90×90×40×2,5 varmforsinket** ligger på stubbefot og bøyer om hjørnet til benkevange; skruene i fliken går mot høyre vegg (speilvendt i den andre enden) | fastsatt |
| **J11** | 1× Treskrue 5×60 forsenket Torx | **Treskrue 5×60 forsenket Torx** gjennom benkespile (36×98) → inn i benkevange (48×73), rett ned | utledet av tykkelsene |
| **J12** | 1× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom beslagfliken og mot venstre vegg inn i bakre hjørnestolpe (36×98) (speilvendt i den andre enden) | fastsatt |
| **J12** | 1× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom beslagfliken og rett opp inn i bordbærelekt (48×73) | fastsatt |
| **J12** | 1× Vinkelbeslag 40×40×20 | **Vinkelbeslag 40×40×20** ligger på bakre hjørnestolpe og bøyer om hjørnet til bordbærelekt; skruene i fliken går mot venstre vegg (speilvendt i den andre enden) | fastsatt |
| **J13a** | 6× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom avstivningslekt (48×73) → inn i løs plate (18 mm plate, 652 bred), rett opp — hodet står 46 mm inne i avstivningslekt, i bunnen av kontraboret, så skruen tar 13 mm i løs plate og ingenting går gjennom den andre siden | fastsatt — begge veier holder målene |
| **J13b** | 3× Treskrue 5×40 forsenket Torx | **Treskrue 5×40 forsenket Torx** gjennom fremre tverrlekt (48×73) → inn i løs plate (18 mm plate, 652 bred), rett opp — hodet står 46 mm inne i fremre tverrlekt, i bunnen av kontraboret, så skruen tar 13 mm i løs plate og ingenting går gjennom den andre siden | fastsatt — begge veier holder målene |

**7** av retningene er utledet av målene alene, **17** er fastsatt for hånd. Alle sammen kontrolleres ved hver bygging: skruekroppen må ha hodet i plan med flaten den drives fra, spissen inne i delen den tar tak i, og ingenting av seg selv i noen annen del.

Veggfestet (J14) står ikke her — det går rett gjennom den bakre sidevangen og inn i veggen, og har ingen andre del å gå inn i.
