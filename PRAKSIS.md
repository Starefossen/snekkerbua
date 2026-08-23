# PRAKSIS — arbeidsmåten i snekkerbua

Dette er reglene som gjelder på tvers av prosjektene her, og bare de: hvorfor
et tall bare får finnes ett sted, hva som gjør en assert verdt å skrive,
hvorfor determinismen selv er en assert, og hvordan et tegnet eller filmet
resultat kan måles i stedet for å bedømmes.

Det som er ett prosjekts eget — delenavn, leddfamilier, hvilke invarianter
akkurat den modellen hviler på, tegnespråket i akkurat den manualen — står i
prosjektets egen PRAKSIS:

* [prosjekter/hanna/docs/PRAKSIS.md](prosjekter/hanna/docs/PRAKSIS.md) — loftsengen

Ingen av disse filene er en del av noen manual. De er skrevet for den som skal
endre en modell eller en tegning.

---

## 1. Én kilde, og bare én

**Ethvert tall som står i dokumentasjonen kommer fra prosjektets modell.**
Ikke «er kopiert fra» — kommer fra. Verktøyene i `tools/` importerer modellen,
leser modulglobalene og skriver ut. Ingen av dem definerer geometri, og ingen
av dem utleder noe modellen allerede vet.

En håndskrevet tekst har lov til å navngi deler og sitere leddnumre, men den
skal aldri gjenta et mål som et generert fragment allerede bærer — den lenker
til fragmentet i stedet.

Regelen bak alt sammen: **hvis to filer må være enige om et tall, er tallet på
feil sted.**

---

## 2. Assertfilosofien

Modellene her har hundrevis av `assert`. Nesten ingen av dem sjekker at et tall
er det tallet som står der. De sjekker **forhold mellom ting**, og de er utledet
av fysikk, ikke av en mening.

En god assert har tre kjennetegn:

1. **Den er relasjonell.** `assert POST_W == 98` er verdiløs — den sier bare at
   98 er 98. `assert rail.extents[2][0] == post_top` sier at vangen faktisk
   hviler på stolpen, og den ryker i det øyeblikket noen flytter en av dem.
2. **Den er utledet av noe utenfor tegningen.** En standard sier 3d kantavstand
   og 4d avstand mellom skruer; en annen sier 75 mm åpning og 160 mm rekkverk
   over madrassen. De tallene er inndata; alt som følger av dem er utregnet.
3. **Den forklarer seg selv når den ryker.** Meldingen skal si hvilket tall som
   ikke gikk opp, hva grensen var, og hvor man retter det. En assert man må
   lese kildekoden for å forstå er en assert man kommenterer bort.

Hvilke assertfamilier et prosjekt får, følger av hva prosjektet er laget av, og
står i prosjektets egen PRAKSIS.

### Asserten som måler feil ting

Et **rapportert** tall må ha en definisjon som er like presis som en assert sin,
og definisjonen må stå i koden og ikke i kommentaren over den. Et tall som ser
riktig ut i forhold til en påstand ingen har kontrollert, kan stå feil i flere
runder uten at noen ser det — nettopp fordi det ser riktig ut.

Regelen for hele repoet: *hvis en kommentar sier hva et tall betyr, og koden
ikke gjør det, er kommentaren en påstand og tallet er pynt.*

---

## 3. Regler, ikke tilfeller

Hva slags behandling noe får, er en **egenskap ved tingen**, og den er definert
ett sted. Et byggesteg som skal tegnes på en annen slags side sier det selv, i
den ene tabellen som definerer steget, og følger med ut i den maskinlesbare
beskrivelsen. Verktøyet som tegner slår opp; det har ingen `if n == 0` og ingen
navnematch på en deletekst.

Grunnen er den samme som i §1: et `if` på et navn eller et nummer er en andre
kilde til det samme svaret, og den kilden blir stående igjen den dagen tingen
endrer navn.

Det samme gjelder valg som kunne vært en bryter: er vilkåret regnbart, regnes
det ut av dataene og skrus verken av eller på for hånd.

---

## 4. Tegnekonvensjoner som holder på tvers

Disse er hentet fra Agrawala/Heer/Klingner sitt arbeid med
monteringsanvisninger, og de gjelder enhver tegnet anvisning her:

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

### Skala: én penn

Hver strekbredde, radius, marg og punktstørrelse på en stegside er et multiplum
av ett eneste mål:

    penn = diagonalen i tegningsobjektets egen bbox / 400

Tallet er gjenstandens, ikke sidens, så hele pennsettet følger det som tegnes.
Sidenære størrelser — hjørneblokkenes bredde, eksplosjonens sprang, den hvite
margen — er fortsatt brøkdeler av SIDEN, for det er det de er. Regelen er den
samme som ellers: skal en strek bli tykkere, endres forholdstallet ett sted, og
alle sidene følger etter.

**Motoren vet ingenting om det den tegner.** `tools/layout.py` svarer på de to
spørsmålene enhver påskrift stiller — *hvor stor* og *hvor er det plass* — av
regler, ikke av koordinater noen syntes så bra ut. Den er repoets utpekte
**delekandidat**: den ligger fortsatt inne i HANNA, fordi en generalisering uten
en andre bruker er en gjetning om hva den andre brukeren trenger. Kommer
prosjekt nummer to med en tegnet anvisning, er det denne fila som flyttes opp
først.

### Prøven tegnes, ikke argumenteres

Et valg om hvordan noe SER ut avgjøres på blekket: det samme utsnittet klippes
ut av den ferdige siden før og etter, og de to legges ved siden av hverandre.
Prøvebildene er gjennomgangsmateriale og sjekkes ikke inn — men hvilke to
utsnitt saken ble avgjort i, skrives ned, slik at neste endring kan klippes på
nøyaktig samme sted.

Og der prøven avgjorde noe, settes en **snubletråd** i stedet for enda en
knapp: en assert som måler det tegnede resultatet og stopper bygget den dagen
et nytt kamera eller et nytt mål flytter det utenfor det prøven godtok.

---

## 5. Filmene er utledet som alt annet

En film her er ikke en illustrasjon ved siden av modellen, den er en avlesning
av den: rammene kommer av modellen og den maskinlesbare stegbeskrivelsen,
rammenummeret driver kamera, forskyvning og innfading, og ingenting leser en
klokke — så to kjøringer gir byte-identiske filer, og `git diff` på dem er
konsekvensanalysen akkurat som på tegningene. Selve rammene er skrap og skrives
utenfor repoet.

Filmene rendres **ikke** av `build`: de tar minutter og trenger verktøy
`build` ikke krever. Nettopp derfor må de voktes. Hver film skriver sha256 av
kildene sine i en stempelfil, og en `film-check` — som er en del av
`mise run check` — hasher de samme filene på nytt og feiler hvis en film er
eldre enn modellen den påstår å vise. En innsjekket film som viser en eldre
utgave er akkurat den slags stille avvik resten av kjeden er bygget for å
hindre; kontrollen koster millisekunder og rendrer ingenting.

**En film kan dessuten være en assert.** Viser den en bevegelse, kan hver
eneste ramme legges gjennom en kollisjonsprøve mot resten av modellen, og
verktøyet nekter å lage filmen hvis noe treffer noe. Det er en prøve på
bevegelsen som ingen stillbildeassert kan gjøre.

---

## 6. Determinismen er en assert

**Alt utledet er sjekket inn** — også `.png`-ene, `.svg`-ene og
regresjonsavtrykket av modellen — slik at en diff viser hva en endring i
modellen faktisk gjorde med tegningene. Det er poenget med å ha dem i git:
`git diff --stat` etter et bygg er konsekvensanalysen.

Den avlesningen er verdiløs hvis kjeden selv kan gi to svar på samme spørsmål,
så determinismen er ikke en forventning — den er en assert:

```
mise run check        kjør hele kjeden to ganger, krev byte-identiske artefakter
```

`check` kjører hele kjeden to fulle ganger og sammenligner sjekksummen av hver
innsjekkede, utledede fil. Ryker den, er det **ikke** en modellendring: det er
en usortert `dict`, et tidsstempel, en `id()`-sortering eller en flyttallssum
som avhenger av rekkefølgen. Rett årsaken, ikke artefaktet.

**Ingenting som er generert skal redigeres for hånd.** Hver genererte fil
starter med en kommentar som sier det, der formatet tillater en. Skal et tall
endres, endres det i modellen.

---

## 7. Overdimensjonering gjemmer seg i kriteriet, ikke i tabellen

Et lasttall er ikke en måling. Det er et valg, og valget arves videre uten at
noen ser på det igjen. Spilene i Hanna bar «1 kN på én spile» i flere runder —
et selvvalgt tall, ikke et krav fra noen standard — og det tallet alene var det
som gjorde 36 mm nødvendig. Da kriteriet ble forankret i noe som lar seg måle
på tegningen, at en fotsåle på 250 mm alltid rekker over minst to spiler ved
den delingen feltet faktisk har, falt lasten til 0,5 kN og virket til 23 mm.
Ingen fysikk endret seg. Kriteriet ble ærlig.

**Forankre kriteriet i noe verifiserbart, og skriv ned hva det er forankret i.**
Et tall som følger av geometrien i modellen kan etterprøves av den neste som
leser. Et tall noen valgte kan bare tros.

**Sammenlign med noe som finnes.** En ribbebunn fra møbelhandelen er sjiktlimt
bjørk på 8 mm. Ligger regnestykket ditt en størrelsesorden over det folk sover
på hver natt, er det kriteriet som skal undersøkes, ikke virket. Sammenligningen
er kontekst og aldri bevis — den forteller hvor du skal lete, ikke hva svaret er.

**Skill reserve-med-jobb fra margin på margin.** Avstivningslektene under platen
står på 0,26 i idealtilfellet, og det ser romslig ut helt til man spør hva som
skjer når kneet lander rett over den ene lekta i stedet for midt imellom: 0,52.
Reserven hadde en jobb. Sikkerhetsfaktorer stablet oppå hverandre uten navn har
ingen. Skriv hvilken av delene et tall er, ellers blir all slakk like hellig —
eller like fristende å barbere.

**Stivhet er ikke bruddmargin.** Å stå på et bord uten at det synlig beveger seg
sier noe om E, og E er den samme i C16 og C24. En 23×98 på 800 mm bøyer seg
knapt 8 mm under 80 kg — usynlig — og ligger samtidig på utnyttelse over 1. Den
prøven er verdiløs som argument for at noe er overdimensjonert, og verdifull som
kalibrering av at regnestykket stemmer. Bruk den til det den duger til.

## 8. Butikken er en designforutsetning

Modellen kan regne hvilken som helst dimensjon. Butikken fører fem. Det er
butikken som vinner, og det er billigere å vite det før kapplista skrives enn
etterpå.

**Dimensjoner:** 48×73 sto i modellen i mange runder fordi det er standard på
papiret. Det fantes ikke i hylla; 48×68 gjorde. Hele nedstrømskjeden — koter,
skruevinduer, kontraborets dybde — måtte regnes om for fem millimeter.

**Salgslengder:** en kappeplan som pakker perfekt i 4,2 m er verdiløs hvis
dimensjonen bare selges i 4,8. Kappeplanen skal beskrive det virket som faktisk
kan bæres ut av butikken, også når det gir mer svinn på papiret.

**Pakkestørrelser:** skruer selges i hundre. Å presse skruesortimentet fra fire
typer til tre sparte null pakker — behovet krysset bare 100 på en annen type —
og kostet skjærkapasitet i hvert rammeledd. **Optimum og minimum er ikke samme
sak.** Regn i pakker, ikke i typer.

**Sorteringsklasse er en dimensjon til.** Lasttabellen regner C24. Står bordet i
hylla som «klasse 1 lekt/rekke — ikke-bærende», er det ikke det bordet
regnestykket handler om, uansett hva målene sier. Spør i skranken.
