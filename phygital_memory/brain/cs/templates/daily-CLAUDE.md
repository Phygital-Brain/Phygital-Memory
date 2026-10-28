<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Denní deník, který si vede {Name}. Jeden soubor na den: `YYYY-MM-DD.md`. Otevřené úkoly jsou v `úkoly.md`.

## Informační blok (frontmatter)

Každá denní poznámka začíná tímhle blokem. Bez výjimek.

```yaml
---
type: daily
date: 2026-10-13
day: Tuesday
week: W42
month: October
status: active
tags: [daily, meeting]
---
```

- `type`: vždycky `daily`.
- `date`: datum poznámky, `YYYY-MM-DD`.
- `day`: den v týdnu, anglicky (Monday, Tuesday...).
- `week`: číslo týdne podle ISO, `WNN`.
- `month`: měsíc, anglicky (January, February...).
- `status`: `active`, dokud je den otevřený, `completed`, jakmile je poznámka 2 a víc dní stará.
- `tags`: vždycky `daily` a k tomu štítky z tohohle pevného seznamu podle toho, co se ten den stalo. Nikdy nevymýšlej jiné štítky.
  - `problem`: něco se rozbilo nebo nevyšlo
  - `clients`: práce pro klienty nebo kontakt s klientem
  - `meeting`: hovor nebo schůzka
  - `money`: faktury, platby, daně, investice
  - `research`: proběhla rešerše nebo jsou nová zjištění
  - `decision`: {Name} o něčem rozhoduje
  - `travel`: {Name} je na cestách
  - `personal`: zdraví, život, cokoli mimo práci

## Pravidla

- Data se řídí hlavním pravidlem 30 (nejdřív časové pásmo počítače, pak {Time zone}).
- Kdo poznámku vytvoří (tvůj agent nebo naplánovaná úloha), napíše jako první informační blok. Poznámka bez něj ho dostane nahoru při příští úpravě.
- Žádný nadpis `# YYYY-MM-DD`. Název souboru je nadpis.
- Denní poznámka drží aktuální stav dne: jeden přehledný dokument na den, oddíly se upravují na místě, nikdy hromada opakovaných záznamů.
- Záznamy ze sezení: tučný nadpis a 1 nebo 2 věty, lidé a projekty jako `[[wiki odkazy]]`, podrobnosti patří do odkazované poznámky.
- Dnešní poznámka obsahuje jen dnešní dění. Otevřené úkoly z dřívějších dní patří do `úkoly.md`. Nikdy je nekopíruj dopředu.
- Když vytváříš dnešní poznámku, podívej se na poznámky z doby před 2, 3 a 4 dny. Ty, které mají pořád `status: active`, přepni na `completed` a dej jim štítky z pevného seznamu podle toho, co se ten den zjevně stalo. Dál do minulosti se nedívej.

## tasks.md

Otevřené úkoly, které nepatří k žádnému projektu. Úkoly projektu patří do README daného projektu („Stav a další krok“). Soubor vznikne při prvním použití:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Otevřené

- [ ] 2026-10-13: Poslat fakturu, kterou čeká [[Anna]]

## Hotové

- [x] 2026-10-12: Objednat se k zubaři (hotovo 2026-10-13)
```

- Nejnovější otevřené úkoly nahoře, s datem, kdy přibyly.
- Když je úkol hotový, odškrtni ho, připiš datum dokončení a přesuň ho pod `## Hotové`.
- Hotové úkoly starší než 30 dní se můžou smazat (nejdřív se zeptej, hlavní pravidlo 9).
