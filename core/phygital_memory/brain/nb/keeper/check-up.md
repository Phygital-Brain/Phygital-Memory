---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Helsesjekken til Ryddehjelperen: en grundig gjennomgang av hele hjernen, når {Name} ber om det. Ingenting endres før {Name} sier ja. (Den daglige ryddingen står i `daglig.md`.)

Utløser: «ta en helsesjekk av hjernen min», «check up my brain», «rydd i hjernen min», «tidy my brain», «helsesjekk av hjernen», «brain check-up» eller det samme på {Language}.

## 1. Se gjennom (ikke endre noe ennå)

Søk gjennom hele mappen og list opp problemene i disse gruppene:

- **Ødelagte lenker**: `[[lenker]]` som peker til notater som ikke finnes. Rett dem aldri ved å lage et tomt notat: det ekte notatet kan fortsatt holde på å synkroniseres (hovedregel 28).
- **Foreldreløse notater**: notater som ingen andre notater lenker til.
- **Tomme eller nesten tomme notater**, og plassholdere som er blitt stående igjen (`[name]`, `TBD`).
- **Feil sted**: filer i roten av mappen (unntatt `CLAUDE.md`, `.claudeignore`, `.backups/` og en regelfil på én linje for en annen agent, som `AGENTS.md`), og notater som ikke passer med tabellen «Hvor ting skal ligge» i mappen sin.
- **Utdaterte tabeller over hvor ting skal ligge**: en `CLAUDE.md` nevner filer eller mapper som ikke finnes, eller mangler noen som finnes (rader merket «lages første gang den trengs» er i orden).
- **Infoblokker**: mangler eller er ufullstendige, sammenlignet med `CLAUDE.md` i mappen. Ingen `status:`, færre enn 2 `tags:`, et prosjektnotat uten `project:`, dagboktagger som ikke står på den faste listen.
- **Prosjekter som står stille**: ingen oppdatering på 60 dager eller mer. Foreslå en statusoppdatering, `paused` eller arkivering.
- **Mål uten prosjekt**: mål i `Profil/mål.md` som ikke har noe aktivt prosjekt.
- **Beslutninger som bør gås gjennom**: `updated` for mer enn 30 dager siden, og status er ikke `closed`.
- **Gamle forhold**: `status: active`, men `last-contact` er mer enn 12 måneder siden. Foreslå `dormant`.
- **Gamle oppgaver**: åpne oppgaver i `Dagbok/oppgaver.md` som er eldre enn 30 dager.
- **Dobbelt opp**: de samme fakta i mer enn ett notat, eller to notater for samme person eller bedrift.
- **Utdatert status**: profilsider eller kontaktsider der gamle oppdateringer begraver hvordan det står nå (hovedregel 17).
- **Regler som kolliderer**: regler i hoved-`CLAUDE.md` som sier hverandre imot.
- **Personvern**: passord, nøkler eller private nummer som ligger i vanlige notater (hovedregel 25 og 26). Oppgi notatet, aldri verdien.
- **Skriving**: tankestreker og mønstre fra Skrivesjekken i notater.
- **Ny versjon**: sammenlign versjonen til denne hjernen (første linje i hoved-`CLAUDE.md`) med den nyeste Phygital Brain. Hvis du kan bruke nettet, er den nyeste den siste utgivelsen på https://github.com/Phygital-Brain/phygital-brain/releases/latest. Hvis ikke, bruk versjonen av Phygital Brain som er installert hos agenten din, hvis du kan se den. Hvis du ikke kan finne ut av det, hopp over dette.

## 2. Rapport

En kort liste med enkle ord, gruppert som over. For hvert problem: notatet, hva som er feil, og rettelsen du foreslår. Sett de enkle, trygge rettelsene først (tankestreker, tagger som mangler, rader i tabellene over hvor ting skal ligge).

Hvis det har kommet en nyere versjon, start rapporten med én linje. Hvis agenten din allerede har den: «Det har kommet en ny versjon av Phygital Brain. Si ‘Oppgrader den andre hjernen min’ for å se hva som er nytt.» Hvis ikke: «Det har kommet en ny versjon av Phygital Brain. Oppdater den hos agenten din først, og si så ‘Oppgrader den andre hjernen min’.»

## 3. Rett bare det som er godkjent

Før den første rettelsen: ta en sikkerhetskopi av hver fil du skal endre (Sikkerhetskopier og angre i hoved-`CLAUDE.md`).

Spør (med valg å klikke på når det går): **Rett alle de trygge**, **Én og én**, **Bare rapporten**.

- Slett eller flytt aldri noe uten lenkesjekken og et tydelig ja (hovedregel 21).
- Arkiver i stedet for å slette når du er i tvil.
- Skriv én linje i dagens notat i `Dagbok/`: hva som ble sjekket og rettet.
