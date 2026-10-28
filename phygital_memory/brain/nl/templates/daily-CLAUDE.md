<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Het dagboek van {Name}. Eén bestand per dag: `YYYY-MM-DD.md`. Open taken staan in `taken.md`.

## Infoblok (frontmatter)

Elke dagnotitie begint met dit blok. Zonder uitzondering.

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

- `type`: altijd `daily`.
- `date`: de datum van de notitie, `YYYY-MM-DD`.
- `day`: de dag van de week, in het Engels (Monday, Tuesday...).
- `week`: ISO-weeknummer, `WNN`.
- `month`: de maand, in het Engels (January, February...).
- `status`: `active` zolang de dag nog loopt, `completed` zodra hij 2 of meer dagen oud is.
- `tags`: altijd `daily`, plus de tags uit deze vaste lijst die die dag van toepassing waren. Verzin nooit andere tags.
  - `problem`: er ging iets kapot of mis
  - `clients`: werk voor klanten of contact met klanten
  - `meeting`: een call of meeting
  - `money`: facturen, betalingen, belastingen, beleggingen
  - `research`: onderzoek gedaan of iets ontdekt
  - `decision`: {Name} heeft iets besloten
  - `travel`: {Name} was op reis
  - `personal`: gezondheid, privéleven, alles buiten het werk

## Regels

- Datums volgen hoofdregel 30 (eerst de tijdzone van de computer, dan {Time zone}).
- Wie de notitie maakt (je agent of een geplande taak), schrijft eerst het infoblok. Heeft een notitie geen infoblok, dan komt het er bovenaan bij, de volgende keer dat de notitie bewerkt wordt.
- Geen titelkop `# YYYY-MM-DD`. De bestandsnaam is de titel.
- De dagnotitie laat zien hoe de dag er nu voor staat: één overzichtelijk document per dag, delen worden ter plekke bijgewerkt, nooit een stapel herhaalde stukjes.
- Sessieverslagen: vetgedrukte kop plus 1 of 2 zinnen, mensen en projecten als `[[wikilinks]]`, details in de gelinkte notitie.
- De notitie van vandaag gaat alleen over vandaag. Open taken van eerdere dagen gaan naar `taken.md`. Kopieer ze nooit door.
- Als je de notitie van vandaag maakt, kijk dan naar de notities van 2, 3 en 4 dagen geleden. Staan die nog op `status: active`, dan worden ze `completed`, en krijgen ze tags uit de vaste lijst voor wat er die dag duidelijk gebeurd is. Kijk niet verder terug.

## tasks.md

Open taken die niet bij een project horen. Taken van een project staan in de README van dat project ("Stand en volgende stap"). Wordt gemaakt bij het eerste gebruik:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Open

- [ ] 2026-10-13: Factuur sturen naar [[Ana]]

## Klaar

- [x] 2026-10-12: Tandarts bellen voor een afspraak (klaar 2026-10-13)
```

- Nieuwste open taken bovenaan, met de datum waarop ze erbij kwamen.
- Is een taak klaar, vink hem dan af, zet de datum erbij en verplaats hem naar `## Klaar`.
- Afgeronde taken ouder dan 30 dagen mogen weg (vraag het eerst, hoofdregel 9).
