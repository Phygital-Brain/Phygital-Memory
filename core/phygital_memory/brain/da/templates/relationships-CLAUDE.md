<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Kunder/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Alle, som {Name} arbejder sammen med: én note pr. person eller organisation.

## Undermapper

| Mappe | Hvem hører til her |
|---|---|
| `Kunder/` | Personer og firmaer, som {Name} laver arbejde for |
| `Samarbejdspartnere/` | Kreative partnere, hvor I hjælper hinanden, uden at der er penge med |
| `Team/` | Personer, der arbejder sammen med eller for {Name} (freelancere, assistenter) |
| `Netværk/` | Organisationer, hvor {Name} gerne vil blive kendt (presse, spillesteder, platforme) |

## Hvor en ny interessent hører hjemme

- En første kontakt uden et rigtigt oplæg endnu: en linje under `## Nye` i `Kunder/_Interessenter.md` (oprettes første gang, den skal bruges).
- Et svar, der siger "måske senere": en linje under `## Hold varm` i `Kunder/_Interessenter.md`.
- Et rigtigt oplæg, et opkald eller et tilbud på vej: en kundenote `Kunder/{client-name}.md` med `status: prospect`.

Når en interessent rykker et trin op, så flyt den til næste sted, og fjern den fra det forrige.

## Infoblok (frontmatter)

Hver note her (undtagen `CLAUDE.md`-filer og `_Interessenter.md`) starter med:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Én almindelig sætning om, hvem de er, og hvordan forholdet til {Name} er."
---
```

- `type`: `client`, `collaborator`, `team` eller `partner`.
- `status`: `active` (arbejde eller kontakt inden for de sidste 12 måneder), `prospect` (I taler sammen, men har aldrig arbejdet sammen), `dormant` (ingen kontakt i 12 måneder eller mere), `closed` (slut for altid).
- `last-contact`: den seneste måned med rigtig kontakt eller arbejde, `YYYY-MM`. Lad den stå tom, hvis du ikke ved det.
- `tags`: `relationship`, så typen, så 2 til 5 emne-tags (branche, land, slags arbejde), på engelsk, med små bogstaver og bindestreger.
- `description`: én sætning i dobbelte anførselstegn. Altid den sidste linje.
- Valgfrit: `aliases` (andre navne, de går under), `project` (det aktuelle projekt).

## Regler

- **Ingen dubletter.** Før du opretter en note, så søg efter navnet og varianter af det (accenter, korte navne, brandnavn eller firmanavn). Hvis der findes en note, så brug den, og tilføj den nye stavemåde i `aliases`. Lav aldrig en note mere for den samme person eller det samme firma.
- **Formatet "status øverst, kilder nedenunder"** (hovedregel 17): hvem de er, og hvordan det står nu, øverst, og daterede begivenheder nedenunder.
- **Hold det opdateret.** Når {Name} har rigtig kontakt med nogen (en mail, et opkald, leveret arbejde), så sæt `last-contact` til denne måned, og `status`, hvis den har ændret sig.
- **Kontaktpersoner** i et firma (en agent, en leder, en redaktør) står som almindelig tekst inde i firmaets note, aldrig som `[[links]]`, og får ikke deres egen note. Hvis de skal nævnes andre steder, så link til firmaet: `[[Company Name|Contact Name]]`.
- **Private oplysninger** (telefonnumre, mailadresser, privatadresser) står kun i den persons eller det firmas note. Kopiér dem aldrig over i dagsnoter eller andre noter.
- Link til personer fra projekter og dagsnoter med `[[wikilinks]]`.
- Opret kun en ny undermappe, når der dukker en ny slags forbindelse op. Spørg først.
