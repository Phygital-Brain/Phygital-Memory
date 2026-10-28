Každý projekt je složka, která roste, jak přibývají informace. `README.md` je jediný vstupní bod.

## Co kam patří

| Obsah | Kam |
|---|---|
| Přehled, stav, termín, další kroky | `Projekty/{name}/README.md` |
| Pracovní poznámky, které si dělá {Name} | `Projekty/{name}/poznámky/{topic}.md` |
| Rešerše | `Projekty/{name}/rešerše/{topic}.md` |
| Zadání, specifikace, požadavky | `Projekty/{name}/zadání/{name}.md` |
| Koncepty, scénáře, psaný obsah | `Projekty/{name}/koncepty/{name}.md` |
| Nápady | `Projekty/{name}/nápady/{name}.md` |
| Zpětná vazba | `Projekty/{name}/zpětná-vazba/{name}.md` |
| Obrázky a média | `Projekty/{name}/média/` |
| Starší materiály z projektu | `Projekty/{name}/archiv/` |

Názvy složek jsou malými písmeny se spojovníky, bez čísel na začátku (`rešerše/`, ne `01-Research/`). Projekt si může přidat vlastní složku, když se nehodí žádná z těchhle.

## Jak vypadá README

1. Informační blok (níže), s `description`.
2. `## Co to je`: jeden nebo dva řádky s odkazem na [[cíle]].
3. `## Stav a další krok`: kde projekt je a jaký je další krok.
4. `## Jak to běží`: jen když sem něco zapisuje automaticky (naplánovaná úloha, skript).
5. `## Kde co je`: až když existují podsložky. Malá tabulka s odkazem na každou z nich.

## Informační blok (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (README, který má navíc `created`, `updated` a `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` nebo `done`. Stav v README je stav celého projektu.
- `project`: název složky projektu.
- `tags`: projekt, pak typ.

## Pravidla

- Nový projekt je jen `README.md`. Podsložky vytvářej, až když přijde obsah, který je potřebuje, a odkaž na ně z README.
- README je rozcestník. Neopakuj v něm obsah podsložek.
- Žádný `CLAUDE.md` uvnitř projektu. Pravidla pro jeden projekt patří do oddílu „Pravidla pro jednotlivé projekty“ níže.
- Do informačního bloku každé související poznámky dej `project:`.
- Hotový projekt se přesouvá do `Paměť/archiv/{name}/` jen tehdy, když to {Name} řekne.
- Každý projekt by měl sloužit nějakému cíli v [[cíle]]. Při prohlídce označ cíle bez projektu a projekty bez cíle.

## Pravidla pro jednotlivé projekty

<!-- Rules for one project only. Add a line when a project needs its own rule: "**Project-Name:** the rule." -->
