<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Kunder/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Alle {Name} jobber med: ett notat per person eller organisasjon.

## Undermapper

| Mappe | Hvem som hører hjemme her |
|---|---|
| `Kunder/` | Folk og bedrifter {Name} leverer arbeid til |
| `Samarbeidspartnere/` | Kreative samarbeidspartnere: begge parter gir og får, uten at penger er involvert |
| `Team/` | Folk som jobber med eller for {Name} (frilansere, assistenter) |
| `Partnere/` | Organisasjoner der {Name} vil bli kjent og synlig (presse, arenaer, plattformer) |

## Hvor en ny interessent havner

- En første kontakt uten noen ekte brief ennå: en linje under `## Nye` i `Kunder/_Interessenter.md` (lages første gang den trengs).
- Et svar som sier «kanskje senere»: en linje under `## Hold varm` i `Kunder/_Interessenter.md`.
- En ekte brief, en samtale eller et pristilbud på gang: et kundenotat `Kunder/{client-name}.md` med `status: prospect`.

Når en interessent kommer et steg videre, flytt den til neste sted og fjern den fra det forrige.

## Infoblokk (frontmatter)

Hvert notat her (unntatt `CLAUDE.md`-filer og `_Interessenter.md`) starter med:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Én enkel setning om hvem de er og forholdet til {Name}."
---
```

- `type`: `client`, `collaborator`, `team` eller `partner`.
- `status`: `active` (arbeid eller kontakt de siste 12 månedene), `prospect` (i kontakt, men har aldri jobbet sammen), `dormant` (ingen kontakt på 12 måneder eller mer), `closed` (avsluttet for godt).
- `last-contact`: den siste måneden med ekte kontakt eller arbeid, `YYYY-MM`. La den stå tom hvis du ikke vet.
- `tags`: `relationship`, så typen, så 2 til 5 emnetagger (bransje, land, type arbeid), på engelsk, små bokstaver, bindestreker.
- `description`: én setning, i doble anførselstegn. Alltid siste linje.
- Valgfritt: `aliases` (andre navn de går under), `project` (prosjektet akkurat nå).

## Regler

- **Ingen dobbeltnotater.** Før du lager et notat, søk etter navnet og variantene av det (aksenter, kortnavn, merkenavn eller firmanavn). Finnes det et notat, bruk det, og legg den nye skrivemåten til i `aliases`. Lag aldri et notat nummer to for samme person eller bedrift.
- **Formatet «status øverst, kilder under»** (hovedregel 17): hvem de er og hvordan det står nå øverst, datert historikk under.
- **Hold det oppdatert.** Når {Name} har ekte kontakt med noen (en e-post, en samtale, levert arbeid), sett `last-contact` til denne måneden, og oppdater `status` hvis den har endret seg.
- **Kontaktpersoner** i en bedrift (en agent, en leder, en redaktør) står som vanlig tekst inne i bedriftsnotatet, aldri som `[[lenker]]`, og får ikke eget notat. For å nevne dem andre steder, lenk til bedriften: `[[Company Name|Contact Name]]`.
- **Private opplysninger** (telefonnummer, e-postadresser, hjemmeadresser) ligger bare i notatet til den personen eller bedriften. Kopier dem aldri inn i dagboknotater eller andre notater.
- Lenk til folk fra prosjekter og dagboknotater med `[[wikilenker]]`.
- Lag en ny undermappe bare når det dukker opp en ny type forhold. Spør først.
