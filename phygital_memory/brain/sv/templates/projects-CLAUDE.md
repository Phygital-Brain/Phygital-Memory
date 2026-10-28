Varje projekt är en mapp som växer när det kommer in mer information. `README.md` är den enda ingången.

## Var allt hamnar

| Innehåll | Hamnar i |
|---|---|
| Översikt, läge, deadline, nästa steg | `Projekt/{name}/README.md` |
| Arbetsanteckningar från {Name} | `Projekt/{name}/anteckningar/{topic}.md` |
| Research | `Projekt/{name}/research/{topic}.md` |
| Brief, specifikation, krav | `Projekt/{name}/underlag/{name}.md` |
| Utkast, manus, skriven text | `Projekt/{name}/utkast/{name}.md` |
| Idéer | `Projekt/{name}/idéer/{name}.md` |
| Feedback | `Projekt/{name}/feedback/{name}.md` |
| Bilder och media | `Projekt/{name}/media/` |
| Gammalt material från projektet | `Projekt/{name}/arkiv/` |

Mappnamn skrivs med små bokstäver och bindestreck, utan nummer framför (`research/`, inte `01-Research/`). Ett projekt kan lägga till en egen mapp när ingen av de här passar.

## Så ser README ut

1. Infoblock (se nedan), med en `description`.
2. `## Vad det är`: en eller två rader, med länk till [[mål]].
3. `## Läge och nästa steg`: var projektet står, nästa steg.
4. `## Hur det körs`: bara om något automatiskt skriver här (en schemalagd uppgift, ett skript).
5. `## Var saker finns`: bara när det finns undermappar. En liten tabell som länkar till var och en.

## Infoblock (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (README, som också har `created`, `updated` och `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` eller `done`. README:ns status är projektets status.
- `project`: projektmappens namn.
- `tags`: projektet, sedan typen.

## Regler

- Ett nytt projekt är bara en `README.md`. Skapa undermappar först när det kommer innehåll som behöver dem, och länka till dem från README.
- README är innehållsförteckningen. Upprepa inte innehållet från undermapparna i den.
- Ingen `CLAUDE.md` inuti ett projekt. Regler för ett enskilt projekt skrivs under "Regler per projekt" nedan.
- Ta med `project:` i infoblocket i varje anteckning som hör till projektet.
- Ett avslutat projekt flyttas till `Minne/arkiv/{name}/` bara när {Name} säger det.
- Varje projekt ska hjälpa till att nå ett mål i [[mål]]. Vid en hälsokoll: flagga mål utan projekt och projekt utan mål.

## Regler per projekt

<!-- Rules for one project only. Add a line when a project needs its own rule: "**Project-Name:** the rule." -->
