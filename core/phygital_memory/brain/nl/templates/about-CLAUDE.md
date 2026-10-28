<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

In deze map staan de belangrijkste feiten over {Name}. Deze notities zijn de bron van waarheid voor al het andere werk.

## Bestanden

| Bestand | Waarvoor | Categorietag |
|---|---|---|
| `ik.md` | Wie {Name} is, hoe {Name} werkt, hoe de agent moet werken | `identity` |
| `biografie.md` | Het verhaal van {Name} | `identity` |
| `doelen.md` | Doelen en prioriteiten | `goals` |
| `bedrijf.md` | Het bedrijf | `business` |
| `aanbod.md` | Diensten, producten, aanbiedingen | `business` |
| `doelgroep.md` | Wie er koopt en hoe ze {Name} vinden | `customers` |
| `knelpunten.md` | Problemen die opgelost moeten worden | `customers` (of `goals` als {Name} niets verkoopt) |
| `merk.md` | Stem, toon, woorden die wel en niet passen | `brand` |
| `tools.md` | Tools, en waar wat staat | `tools` |
| `cv.md` | Werkervaring, opleiding, pers, prijzen | `career` |

## Infoblok (frontmatter)

Elk bestand hier (behalve dit) begint zo:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Wie {Name} is en hoe de agent voor {Name} moet werken."
---
```

- `type`: altijd `about`.
- `status`: `active`, of `outdated` als bekend is dat een feit niet meer klopt.
- `updated`: de datum waarop de feiten voor het laatst veranderden. Niet aanpassen bij tikfouten of stijlwijzigingen.
- `tags`: `about`, dan de categorietag van het bestand uit de tabel hierboven, dan onderwerptags die zeggen waar het bestand over gaat (Engels, kleine letters, koppeltekens). Werk de onderwerptags bij als er een deel bijkomt of verdwijnt.
- `description`: één zin, tussen dubbele aanhalingstekens, die zegt wat er in dit bestand staat. Altijd de laatste regel.

## Regels

- Deze bestanden zijn de bron van waarheid. Kopieer de inhoud niet naar andere plekken: link ernaar.
- Formaat "stand bovenaan, bronnen eronder" (hoofdregel 17): wat nu klopt bovenaan, gedateerde bronnen eronder.
- De volledige geboortedatum van {Name} staat alleen in `ik.md`. Kopieer of noem hem nooit in een antwoord. Het geboortejaar mag wel.
- Maak alleen een nieuw bestand als een nieuw onderwerp er een nodig heeft. Vraag het eerst (hoofdregel 9).
- Wijs bij een check-up op doelen in `doelen.md` waar geen actief project bij hoort.
