<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Klienti/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Všichni, se kterými {Name} pracuje: jedna poznámka na člověka nebo organizaci.

## Podsložky

| Složka | Kdo tam patří |
|---|---|
| `Klienti/` | Lidé a firmy, pro které {Name} dělá zakázky |
| `Spolutvůrci/` | Tvůrčí partneři, vzájemná výměna, bez peněz |
| `Tým/` | Lidé z týmu: kolegové a ti, které si {Name} najímá (lidé na volné noze, asistenti) |
| `Partneři/` | Organizace, se kterými {Name} buduje svoje jméno (média, místa akcí, platformy) |

## Kam patří nová poptávka

- První kontakt bez skutečného zadání: řádek pod `## Nové` v `Klienti/_Poptávky.md` (vznikne při prvním použití).
- Odpověď ve stylu „možná později“: řádek pod `## Udržovat kontakt` v `Klienti/_Poptávky.md`.
- Skutečné zadání, hovor nebo rozpracovaná cenová nabídka: poznámka o klientovi `Klienti/{client-name}.md` se `status: prospect`.

Když se poptávka posune o krok dál, přesuň ji na další místo a z předchozího ji smaž.

## Informační blok (frontmatter)

Každá poznámka tady (kromě souborů `CLAUDE.md` a `_Poptávky.md`) začíná takhle:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Jedna obyčejná věta: kdo to je a jakou roli hraje v tom, co dělá {Name}."
---
```

- `type`: `client`, `collaborator`, `team` nebo `partner`.
- `status`: `active` (práce nebo kontakt za posledních 12 měsíců), `prospect` (probíhá jednání, zatím žádná spolupráce), `dormant` (bez kontaktu 12 a více měsíců), `closed` (definitivně skončilo).
- `last-contact`: poslední měsíc se skutečným kontaktem nebo prací, `YYYY-MM`. Když se neví, nech prázdné.
- `tags`: `relationship`, pak typ, pak 2 až 5 tematických štítků (obor, země, druh práce), anglicky, malými písmeny, se spojovníky.
- `description`: jedna věta v dvojitých uvozovkách. Vždycky poslední řádek.
- Volitelně: `aliases` (jiná jména, pod kterými se o nich mluví), `project` (aktuální projekt).

## Pravidla

- **Žádné duplicity.** Než vytvoříš poznámku, hledej jméno i jeho varianty (s diakritikou a bez ní, zkrácená jména, název značky a název firmy). Když poznámka existuje, použij ji a nový tvar přidej do `aliases`. Nikdy nevytvářej druhou poznámku pro stejného člověka nebo firmu.
- **Formát „aktuální stav nahoře“** (hlavní pravidlo 17): nahoře kdo to je a jak to teď vypadá, pod tím historie s daty.
- **Drž to aktuální.** Když má {Name} s někým skutečný kontakt (e-mail, hovor, odevzdaná práce), nastav `last-contact` na tenhle měsíc, a pokud se změnil, i `status`.
- **Kontaktní osoby** ve firmě (agent, manažer, redaktor) jsou obyčejný text uvnitř poznámky o firmě, nikdy `[[odkazy]]`, a nemají vlastní poznámku. Když je potřeba je zmínit jinde, odkaž na firmu: `[[Název firmy|Jméno kontaktu]]`.
- **Soukromé údaje** (telefony, e-maily, adresy bydliště) jsou jen v poznámce daného člověka nebo firmy. Nikdy je nekopíruj do denních ani jiných poznámek.
- Na lidi odkazuj z projektů a denních poznámek pomocí `[[wiki odkazů]]`.
- Novou podsložku vytvoř, jen když se objeví nový druh vztahu. Nejdřív se zeptej.
