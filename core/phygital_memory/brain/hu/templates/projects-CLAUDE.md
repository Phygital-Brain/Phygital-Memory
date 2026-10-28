Minden projekt egy mappa, ami az információkkal együtt nő. A `README.md` az egyetlen belépési pont.

## Mi hova kerül

| Tartalom | Hova kerül |
|---|---|
| Áttekintés, állapot, határidő, következő lépések | `Projektek/{name}/README.md` |
| {Name} munkajegyzetei | `Projektek/{name}/jegyzetek/{topic}.md` |
| Kutatás | `Projektek/{name}/kutatás/{topic}.md` |
| Brief, specifikáció, követelmények | `Projektek/{name}/briefek/{name}.md` |
| Piszkozatok, forgatókönyvek, megírt szövegek | `Projektek/{name}/piszkozatok/{name}.md` |
| Ötletek | `Projektek/{name}/ötletek/{name}.md` |
| Visszajelzések | `Projektek/{name}/visszajelzések/{name}.md` |
| Képek és média | `Projektek/{name}/média/` |
| A projekt régi anyagai | `Projektek/{name}/archívum/` |

A mappanevek kisbetűsek, kötőjellel, számos előtag nélkül (`kutatás/`, nem `01-Research/`). Egy projekt saját mappát is kaphat, ha egyik sem illik.

## A README felépítése

1. Info blokk (lent), `description` mezővel.
2. `## Mi ez`: egy-két sor, a [[célok]] jegyzetre linkelve.
3. `## Hol tart, mi a következő lépés`: hol áll most, mi a következő lépés.
4. `## Hogyan működik`: csak ha valami automatikusan ír ide (egy ütemezett feladat, egy szkript).
5. `## Mi hol van`: csak ha már vannak almappák. Egy kis táblázat, ami mindegyikre linkel.

## Info blokk (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (a README, amiben `created`, `updated` és `description` is van), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` vagy `done`. A README állapota a projekt állapota.
- `project`: a projektmappa neve.
- `tags`: a projekt, aztán a típus.

## Szabályok

- Egy új projekt csak egy `README.md`. Almappát csak akkor hozz létre, ha olyan tartalom érkezik, aminek kell, és linkeld a README-ből.
- A README a tartalomjegyzék. Ne ismételd meg benne az almappák tartalmát.
- Projekten belül nincs `CLAUDE.md`. Az egy projektre vonatkozó szabályok lent, a "Szabályok projektenként" részbe kerülnek.
- Minden kapcsolódó jegyzet info blokkjába kerüljön `project:`.
- Egy befejezett projekt csak akkor kerül a `Emlékezet/archívum/{name}/` mappába, ha {Name} ezt kéri.
- Minden projekt szolgáljon egy célt a [[célok]] jegyzetből. Átvizsgáláskor jelezd a projekt nélküli célokat és a cél nélküli projekteket.

## Szabályok projektenként

<!-- Csak egy projektre vonatkozó szabályok. Írj ide egy sort, ha egy projektnek saját szabály kell: "**Projekt-Neve:** a szabály." -->
