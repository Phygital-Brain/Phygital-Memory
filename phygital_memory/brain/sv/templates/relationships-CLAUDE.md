<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Kunder/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Alla som {Name} jobbar med: en anteckning per person eller organisation.

## Undermappar

| Mapp | Vem som hamnar där |
|---|---|
| `Kunder/` | Personer och företag som {Name} levererar jobb till |
| `Samarbeten/` | Kreativa partner, utbyte åt båda håll, inga pengar inblandade |
| `Team/` | Personer som jobbar med eller åt {Name} (frilansare, assistenter) |
| `Partner/` | Organisationer som hjälper {Name} att synas (press, scener, plattformar) |

## Var en ny förfrågan hamnar

- En första kontakt utan någon riktig brief än: en rad under `## Nya` i `Kunder/_Förfrågningar.md` (skapas första gången den behövs).
- Ett svar som säger "kanske senare": en rad under `## Håll kontakten` i `Kunder/_Förfrågningar.md`.
- En riktig brief, ett samtal eller en offert på gång: en kundanteckning `Kunder/{client-name}.md` med `status: prospect`.

När en förfrågan tar ett steg framåt: flytta den till nästa ställe och ta bort den från det förra.

## Infoblock (frontmatter)

Varje anteckning här (utom `CLAUDE.md`-filer och `_Förfrågningar.md`) börjar med:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "En enkel mening om vilka de är och hur relationen med {Name} ser ut."
---
```

- `type`: `client`, `collaborator`, `team` eller `partner`.
- `status`: `active` (jobb eller kontakt under de senaste 12 månaderna), `prospect` (ni pratar, men har aldrig jobbat ihop), `dormant` (ingen kontakt på 12 månader eller mer), `closed` (slut för gott).
- `last-contact`: den senaste månaden med riktig kontakt eller riktigt jobb, `YYYY-MM`. Lämna tomt om du inte vet.
- `tags`: `relationship`, sedan typen, sedan 2 till 5 ämnestaggar (bransch, land, typ av jobb), på engelska, små bokstäver, bindestreck.
- `description`: en mening, inom dubbla citattecken. Alltid sista raden.
- Valfritt: `aliases` (andra namn som används för dem), `project` (aktuellt projekt).

## Regler

- **Inga dubbletter.** Innan du skapar en anteckning: sök på namnet och varianter av det (accenter, kortnamn, varumärke eller företagsnamn). Om det finns en anteckning, använd den och lägg till den nya stavningen i `aliases`. Gör aldrig en andra anteckning om samma person eller företag.
- **Formatet "läget överst, belägg under"** (huvudregel 17): vilka de är och läget nu överst, daterad historik under.
- **Håll det aktuellt.** När {Name} har riktig kontakt med någon (ett mejl, ett samtal, levererat jobb), sätt `last-contact` till den här månaden, och ändra `status` om det har ändrats.
- **Kontaktpersoner** på ett företag (en agent, en chef, en redaktör) skrivs som vanlig text i företagets anteckning, aldrig som `[[länkar]]`, och får ingen egen anteckning. För att nämna dem någon annanstans, länka till företaget: `[[Company Name|Contact Name]]`.
- **Privata uppgifter** (telefonnummer, mejladresser, hemadresser) finns bara i personens eller företagets egen anteckning. Kopiera dem aldrig till dagsanteckningar eller andra anteckningar.
- Länka till personer från projekt och dagsanteckningar med `[[wikilänkar]]`.
- Skapa en ny undermapp bara när en ny sorts relation dyker upp. Fråga först.
