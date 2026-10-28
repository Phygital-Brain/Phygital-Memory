<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Dagboken til {Name}. Én fil per dag: `YYYY-MM-DD.md`. Åpne oppgaver ligger i `oppgaver.md`.

## Infoblokk (frontmatter)

Hvert dagboknotat starter med denne blokken. Ingen unntak.

```yaml
---
type: daily
date: 2026-10-13
day: Tuesday
week: W42
month: October
status: active
tags: [daily, meeting]
---
```

- `type`: alltid `daily`.
- `date`: datoen for notatet, `YYYY-MM-DD`.
- `day`: ukedagen, på engelsk (Monday, Tuesday ...).
- `week`: ISO-ukenummer, `WNN`.
- `month`: måneden, på engelsk (January, February ...).
- `status`: `active` så lenge dagen er åpen, `completed` når den er 2 eller flere dager gammel.
- `tags`: alltid `daily`, pluss de fra denne faste listen som passer for det som skjedde den dagen. Finn aldri på andre tagger.
  - `problem`: noe gikk i stykker eller gikk galt
  - `clients`: kundearbeid eller kontakt med kunder
  - `meeting`: en samtale eller et møte
  - `money`: fakturaer, betalinger, skatt, investeringer
  - `research`: research som ble gjort, eller funn
  - `decision`: {Name} bestemte noe
  - `travel`: {Name} var på reise
  - `personal`: helse, livet, alt utenom jobb

## Regler

- Datoer følger hovedregel 30 (først tidssonen på datamaskinen, så {Time zone}).
- Den som lager notatet (agenten din eller en planlagt oppgave), skriver infoblokken først. Et notat uten infoblokk får den lagt til øverst neste gang det redigeres.
- Ingen tittel-overskrift `# YYYY-MM-DD`. Filnavnet er tittelen.
- Dagboknotatet viser hvordan dagen står akkurat nå: ett ryddig dokument per dag, der delene oppdateres der de står, aldri en haug med gjentatte oppføringer.
- Øktlogger: overskrift i fet skrift og 1 eller 2 setninger, folk og prosjekter som `[[wikilenker]]`, detaljene i notatet det lenkes til.
- Dagens notat har bare det som skjer i dag. Åpne oppgaver fra tidligere dager hører hjemme i `oppgaver.md`. Kopier dem aldri videre.
- Når du lager dagens notat, se på notatene fra 2, 3 og 4 dager siden. De som fortsatt har `status: active`, blir `completed`, og får tagger fra den faste listen for det som tydelig skjedde den dagen. Ikke se lenger tilbake.

## tasks.md

Åpne oppgaver som ikke hører til et prosjekt. Prosjektoppgaver står i README-en til prosjektet («Status og neste steg»). Lages første gang den trengs:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Åpne

- [ ] 2026-10-13: Send fakturaen til [[Ana]]

## Ferdige

- [x] 2026-10-12: Bestille time hos tannlegen (ferdig 2026-10-13)
```

- De nyeste åpne oppgavene øverst, med datoen de ble lagt til.
- Når en oppgave er gjort: kryss den av, legg til datoen den ble gjort, og flytt den til `## Ferdige`.
- Ferdige oppgaver som er eldre enn 30 dager, kan fjernes (spør først, hovedregel 9).
