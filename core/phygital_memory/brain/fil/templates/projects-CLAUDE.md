Bawat project ay isang folder na lumalaki habang dumarating ang impormasyon. Ang `README.md` ang tanging pasukan.

## Saan ilalagay

| Content | Ilagay sa |
|---|---|
| Overview, status, deadline, mga susunod na hakbang | `Proyekto/{name}/README.md` |
| Mga working note ni {Name} | `Proyekto/{name}/notes/{topic}.md` |
| Research | `Proyekto/{name}/research/{topic}.md` |
| Brief, spec, mga kailangan | `Proyekto/{name}/brief/{name}.md` |
| Draft, script, nakasulat na content | `Proyekto/{name}/draft/{name}.md` |
| Mga idea | `Proyekto/{name}/ideya/{name}.md` |
| Feedback | `Proyekto/{name}/feedback/{name}.md` |
| Mga larawan at media | `Proyekto/{name}/media/` |
| Lumang materyal mula sa project na ito | `Proyekto/{name}/archive/` |

Maliliit na titik ang mga pangalan ng folder, may gitling, walang numero sa unahan (`research/`, hindi `01-Research/`). Puwedeng magdagdag ang isang project ng sarili nitong folder kapag walang bumabagay sa mga ito.

## Ayos ng README

1. Info block (sa ibaba), may `description`.
2. `## Ano ito`: isa o dalawang linya, naka-link sa [[layunin]].
3. `## Status at susunod na hakbang`: kung nasaan na ito, ang susunod na hakbang.
4. `## Paano ito tumatakbo`: lang kung may awtomatikong nagsusulat dito (isang naka-schedule na task, isang script).
5. `## Nasaan ang mga bagay`: lang kapag may subfolder na. Isang maliit na table na nagli-link sa bawat isa.

## Info block (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (ang README, na may `created`, `updated` at `description` din), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` o `done`. Ang status ng README ang status ng project.
- `project`: ang pangalan ng folder ng project.
- `tags`: ang project, saka ang uri.

## Mga patakaran

- Ang bagong project ay isang `README.md` lang. Gumawa lang ng subfolder kapag may dumating na content na nangangailangan nito, at i-link ito mula sa README.
- Ang README ang index. Huwag ulitin dito ang laman ng mga subfolder.
- Walang `CLAUDE.md` sa loob ng isang project. Ang mga patakaran para sa isang project ay nasa "Mga patakaran bawat project" sa ibaba.
- Isama ang `project:` sa info block ng bawat kaugnay na note.
- Ililipat lang ang tapos nang project sa `Alaala/archive/{name}/` kapag sinabi ni {Name}.
- Dapat tumutulong ang bawat project sa isang layunin sa [[layunin]]. Sa isang check-up, ituro ang mga layuning walang project at ang mga project na walang layunin.

## Mga patakaran bawat project

<!-- Mga patakaran para sa isang project lang. Magdagdag ng linya kapag kailangan ng isang project ng sarili nitong patakaran: "**Pangalan-ng-Project:** ang patakaran." -->
