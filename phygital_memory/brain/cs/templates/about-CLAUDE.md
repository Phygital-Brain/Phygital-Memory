<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

V téhle složce jsou základní fakta o tom, kdo je {Name}. Tyhle poznámky jsou zdrojem pravdy pro všechnu další práci.

## Soubory

| Soubor | K čemu je | Štítek kategorie |
|---|---|---|
| `o-mně.md` | Kdo je {Name}, jak pracuje a jak má pracovat agent | `identity` |
| `biografie.md` | Příběh, který má za sebou {Name} | `identity` |
| `cíle.md` | Cíle a priority | `goals` |
| `podnikání.md` | Podnikání | `business` |
| `nabídka.md` | Služby, produkty, nabídky | `business` |
| `cílová-skupina.md` | Kdo nakupuje a jak se zákazníci dostanou k tomu, co nabízí {Name} | `customers` |
| `problémy.md` | Problémy, které je potřeba vyřešit | `customers` (nebo `goals`, pokud {Name} nic neprodává) |
| `značka.md` | Hlas, tón, slova, která používat a kterým se vyhnout | `brand` |
| `nástroje.md` | Nástroje a kde je jaký druh věcí | `tools` |
| `životopis.md` | Pracovní zkušenosti, vzdělání, média, ocenění | `career` |

## Informační blok (frontmatter)

Každý soubor tady (kromě tohohle) začíná takhle:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Kdo je {Name} a jak má pracovat agent."
---
```

- `type`: vždycky `about`.
- `status`: `active`, nebo `outdated`, když je známo, že nějaký fakt už neplatí.
- `updated`: datum, kdy se fakta naposledy změnila. Při opravě překlepu nebo stylu se nemění.
- `tags`: `about`, pak štítek kategorie souboru z tabulky výše, pak tematické štítky, které říkají, o čem soubor je (anglicky, malými písmeny, se spojovníky). Když se přidá nebo odebere oddíl, uprav tematické štítky.
- `description`: jedna věta v dvojitých uvozovkách, která říká, co v souboru je. Vždycky poslední řádek.

## Pravidla

- Tyhle soubory jsou zdrojem pravdy. Nekopíruj jejich obsah jinam: odkaž na ně.
- Formát „aktuální stav nahoře“ (hlavní pravidlo 17): nahoře to, co platí teď, pod tím zdroje s datem.
- Celé datum narození je jen v `o-mně.md`. Nikdy ho nekopíruj ani necituj v odpovědi. Rok narození je v pořádku.
- Nový soubor vytvoř jen tehdy, když ho potřebuje nové téma. Nejdřív se zeptej (hlavní pravidlo 9).
- Při prohlídce označ cíle v `cíle.md`, které nemají žádný aktivní projekt.
