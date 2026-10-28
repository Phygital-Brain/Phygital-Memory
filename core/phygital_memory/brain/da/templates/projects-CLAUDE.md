Hvert projekt er en mappe, der vokser, efterhånden som der kommer information. `README.md` er den eneste indgang.

## Hvor hører hvad hjemme

| Indhold | Hører hjemme i |
|---|---|
| Overblik, status, deadline, næste skridt | `Projekter/{name}/README.md` |
| Arbejdsnoter fra {Name} | `Projekter/{name}/noter/{topic}.md` |
| Research | `Projekter/{name}/research/{topic}.md` |
| Oplæg, specifikation, krav | `Projekter/{name}/briefs/{name}.md` |
| Kladder, manuskripter, skrevet indhold | `Projekter/{name}/kladder/{name}.md` |
| Idéer | `Projekter/{name}/idéer/{name}.md` |
| Feedback | `Projekter/{name}/feedback/{name}.md` |
| Billeder og medier | `Projekter/{name}/medier/` |
| Gammelt materiale fra projektet | `Projekter/{name}/arkiv/` |

Mappenavne skrives med små bogstaver og bindestreger, uden tal foran (`research/`, ikke `01-Research/`). Et projekt kan få sin egen mappe, når ingen af de her passer.

## Sådan ser README ud

1. Infoblok (se nedenfor), med en `description`.
2. `## Hvad det er`: en eller to linjer, med link til [[mål]].
3. `## Status og næste skridt`: hvor det står, og det næste skridt.
4. `## Sådan kører det`: kun hvis noget automatisk skriver her (en planlagt opgave, et script).
5. `## Hvor tingene ligger`: først når der er undermapper. En lille tabel med et link til hver af dem.

## Infoblok (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (README, som også har `created`, `updated` og `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` eller `done`. README'ens status er projektets status.
- `project`: navnet på projektmappen.
- `tags`: projektet, så typen.

## Regler

- Et nyt projekt er bare en `README.md`. Opret først undermapper, når der kommer indhold, der har brug for dem, og link til dem fra README.
- README er indholdsfortegnelsen. Gentag ikke indholdet fra undermapperne i den.
- Ingen `CLAUDE.md` inde i et projekt. Regler for ét projekt står under "Regler for de enkelte projekter" nedenfor.
- Skriv `project:` i infoblokken på hver note, der hører til.
- Et færdigt projekt bliver kun flyttet til `Hukommelse/arkiv/{name}/`, når {Name} siger det.
- Hvert projekt bør hjælpe med et mål i [[mål]]. Ved et tjek: marker mål uden projekt og projekter uden mål.

## Regler for de enkelte projekter

<!-- Regler for kun ét projekt. Tilføj en linje, når et projekt har brug for sin egen regel: "**Projekt-Navn:** reglen." -->
