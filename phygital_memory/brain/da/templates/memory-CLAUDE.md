Viden, der bygger sig op over tid: beslutninger, research, ansøgninger og arkivet.

## Hvor hører hvad hjemme

| Indhold | Hører hjemme i |
|---|---|
| En beslutning med begrundelse, eller en undersøgelse af noget udefra (app, hjemmeside, kursus, konkurrent) | `beslutninger/YYYY-MM-DD-{title}.md` |
| Research (marked, tendenser, muligheder) | `research/{topic}.md` |
| Ansøgninger: job, legater, priser, åbne indkaldelser (oprettes første gang, den skal bruges) | `ansøgninger/{name}/` |
| Profiler af konkurrenter (oprettes første gang, den skal bruges) | `konkurrenter/{name}.md` |
| Penge: fakturaer, skat, betalinger. Privat | `økonomi/` |
| Arkiverede beslutninger | `arkiv/beslutninger/` |
| Færdig eller forældet research | `arkiv/research/` |
| Færdige projekter | `arkiv/{name}/` |
| Mødenoter | `beslutninger/`, hvis der kom en beslutning ud af mødet, ellers dagens note i `Dagbog/`. Foreslå kun en mappe til møder, når der er mange. |

## Infoblok (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: datoen, hvor noten blev skrevet.
- `status`: se nedenfor for beslutninger og ansøgninger. Alt andet: `active` eller `closed`.
- `tags`: typen, så emnet.
- Valgfrit: `project`, `deadline`, `description` (én sætning i dobbelte anførselstegn, sidste linje).

## Beslutningsnoter

Tag altid begrundelsen med: hvem der var med, hvad der satte det i gang, og hvad man valgte fra. Brug `> [!important]` til selve beslutningen og `> [!warning]` til kendte risici.

Beslutninger har også `updated:` lige efter `date:`. `date` er, hvornår den blev oprettet, `updated` er sidste gang, den blev gennemgået eller ændret.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (bliver stadig besluttet eller arbejdet på), `waiting` (venter på en anden), `paused`, `closed`.
- En beslutning, hvor `updated` er mere end 30 dage gammel, skal gennemgås. Oprydningshjælperen markerer den, indtil {Name} beholder den, lukker den eller arkiverer den (hver af dem sætter `updated` til den dag).
- En beslutning bliver kun flyttet til `arkiv/beslutninger/`, når {Name} siger det.

## Ansøgninger

Én mappe pr. ansøgning: `ansøgninger/{name}/`, med en `README.md`, der har fristen, linket, status og det, der blev sendt. Andre filer (svar, motivation) ligger ved siden af.

- `status`: `draft`, `submitted`, `accepted`, `rejected` eller `withdrawn`.
- Gem svarene i markdown. Store PDF'er og præsentationer bliver uden for mappen: lav et resumé af dem i en note.

## Regler

- Research er neutral som udgangspunkt (hovedregel 23).
- Flyt research, der er blevet overhalet, til `arkiv/research/` i stedet for at slette den.
- `økonomi/` er privat og står i `.claudeignore`. Åbn den kun, når {Name} beder om en bestemt fil (hovedregel 8).
