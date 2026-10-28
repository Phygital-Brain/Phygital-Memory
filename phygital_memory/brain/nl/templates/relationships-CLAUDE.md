<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Klanten/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Iedereen met wie {Name} werkt: één notitie per persoon of organisatie.

## Submappen

| Map | Wie daar komt |
|---|---|
| `Klanten/` | Mensen en bedrijven voor wie {Name} werk levert |
| `Samenwerkingen/` | Creatieve partners, je helpt elkaar, er gaat geen geld in om |
| `Team/` | Mensen die met of voor {Name} werken (freelancers, assistenten) |
| `Partners/` | Organisaties waarmee {Name} zichtbaarheid opbouwt (pers, locaties, platforms) |

## Waar een nieuwe lead heen gaat

Een lead is iemand die misschien klant wordt.

- Een eerste contact zonder echte briefing: een regel onder `## Nieuw` in `Klanten/_Leads.md` (wordt gemaakt bij het eerste gebruik).
- Een antwoord als "misschien later": een regel onder `## Warm houden` in `Klanten/_Leads.md`.
- Een echte briefing, call of offerte die loopt: een klantnotitie `Klanten/{client-name}.md` met `status: prospect`.

Gaat een lead een stap verder, verplaats hem dan naar de volgende plek en haal hem weg uit de vorige.

## Infoblok (frontmatter)

Elke notitie hier (behalve `CLAUDE.md`-bestanden en `_Leads.md`) begint zo:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Eén gewone zin over wie ze zijn en wat ze met {Name} te maken hebben."
---
```

- `type`: `client`, `collaborator`, `team` of `partner`.
- `status`: `active` (werk of contact in de afgelopen 12 maanden), `prospect` (in gesprek, nog nooit samengewerkt), `dormant` (12+ maanden geen contact), `closed` (voorgoed voorbij).
- `last-contact`: de laatste maand met echt contact of werk, `YYYY-MM`. Laat leeg als het onbekend is.
- `tags`: `relationship`, dan het type, dan 2 tot 5 onderwerptags (branche, land, soort werk), Engels, kleine letters, koppeltekens.
- `description`: één zin, tussen dubbele aanhalingstekens. Altijd de laatste regel.
- Mag erbij: `aliases` (andere namen die voor hen gebruikt worden), `project` (huidig project).

## Regels

- **Geen dubbele notities.** Zoek voordat je een notitie maakt naar de naam en varianten ervan (accenten, korte namen, merknaam of bedrijfsnaam). Bestaat er al een notitie, gebruik die dan en zet de nieuwe schrijfwijze bij `aliases`. Maak nooit een tweede notitie voor dezelfde persoon of hetzelfde bedrijf.
- **Formaat "stand bovenaan, bronnen eronder"** (hoofdregel 17): wie ze zijn en hoe het er nu voor staat bovenaan, de gedateerde geschiedenis eronder.
- **Houd het actueel.** Heeft {Name} echt contact met iemand (een mail, een call, opgeleverd werk), zet `last-contact` dan op deze maand, en pas `status` aan als die veranderd is.
- **Contactpersonen** bij een bedrijf (een agent, een manager, een redacteur) staan als gewone tekst in de bedrijfsnotitie, nooit als `[[links]]`, en krijgen geen eigen notitie. Wil je ze ergens anders noemen, link dan naar het bedrijf: `[[Bedrijfsnaam|Naam contactpersoon]]`.
- **Privégegevens** (telefoonnummers, mailadressen, woonadressen) staan alleen in de notitie van die persoon of dat bedrijf. Kopieer ze nooit naar dagnotities of andere notities.
- Link vanuit projecten en dagnotities naar mensen met `[[wikilinks]]`.
- Maak alleen een nieuwe submap als er een nieuw soort relatie bijkomt. Vraag het eerst.
