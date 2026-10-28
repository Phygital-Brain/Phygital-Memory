Kunnskap som bygger seg opp over tid: beslutninger, research, søknader og arkivet.

## Hvor ting skal ligge

| Innhold | Legges i |
|---|---|
| En beslutning med begrunnelse, eller en vurdering av noe utenfra (app, nettside, kurs, konkurrent) | `beslutninger/YYYY-MM-DD-{title}.md` |
| Research (marked, trender, alternativer) | `research/{topic}.md` |
| Søknader: jobber, stipender, priser, åpne utlysninger (lages første gang den trengs) | `søknader/{name}/` |
| Profiler av konkurrenter (lages første gang den trengs) | `konkurrenter/{name}.md` |
| Penger: fakturaer, skatt, betalinger. Privat | `økonomi/` |
| Arkiverte beslutninger | `arkiv/beslutninger/` |
| Ferdig eller utdatert research | `arkiv/research/` |
| Ferdige prosjekter | `arkiv/{name}/` |
| Møtenotater | `beslutninger/` hvis det kom en beslutning ut av møtet, ellers notatet for den dagen i `Dagbok/`. Foreslå en egen møtemappe bare når det blir mange. |

## Infoblokk (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: datoen notatet ble skrevet.
- `status`: se under for beslutninger og søknader. Alt annet: `active` eller `closed`.
- `tags`: typen, så emnet.
- Valgfritt: `project`, `deadline`, `description` (én setning, i doble anførselstegn, siste linje).

## Beslutningsnotater

Ta alltid med hvorfor: hvem som var med, hva som satte det i gang, og hva man valgte bort. Bruk `> [!important]` for selve beslutningen og `> [!warning]` for kjente risikoer.

Beslutninger har også `updated:` rett etter `date:`. `date` er når den ble laget, `updated` er siste gang den ble gått gjennom eller endret.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (blir fortsatt bestemt eller jobbet med), `waiting` (venter på noen andre), `paused`, `closed`.
- En beslutning der `updated` er mer enn 30 dager gammel, bør gås gjennom. Ryddehjelperen peker den ut helt til {Name} beholder den, lukker den eller arkiverer den (alle tre setter `updated` til den dagen).
- En beslutning flyttes til `arkiv/beslutninger/` bare når {Name} sier det.

## Søknader

Én mappe per søknad: `søknader/{name}/`, med en `README.md` som har fristen, lenken, statusen og hva som ble sendt. Andre filer (svar, motivasjonsbrev) ligger ved siden av.

- `status`: `draft`, `submitted`, `accepted`, `rejected` eller `withdrawn`.
- Hold svarene i markdown. Store PDF-er og presentasjoner blir liggende utenfor hjernen: oppsummer dem i et notat.

## Regler

- Research er nøytral som standard (hovedregel 23).
- Flytt research som er erstattet av nyere, til `arkiv/research/` i stedet for å slette den.
- `økonomi/` er privat og står i `.claudeignore`. Åpne den bare når {Name} ber om en bestemt fil (hovedregel 8).
