Tudás, ami idővel gyűlik: döntések, kutatások, pályázatok és az archívum.

## Mi hova kerül

| Tartalom | Hova kerül |
|---|---|
| Döntés indoklással, vagy egy külső dolog (app, weboldal, kurzus, versenytárs) vizsgálata | `döntések/YYYY-MM-DD-{title}.md` |
| Kutatás (piac, trendek, lehetőségek) | `kutatás/{topic}.md` |
| Pályázatok: állások, támogatások, díjak, nyílt felhívások (első használatkor jön létre) | `pályázatok/{name}/` |
| Versenytársak profiljai (első használatkor jön létre) | `versenytársak/{name}.md` |
| Pénz: számlák, adók, kifizetések. Privát | `pénzügyek/` |
| Archivált döntések | `archívum/döntések/` |
| Lezárt vagy elavult kutatások | `archívum/kutatás/` |
| Befejezett projektek | `archívum/{name}/` |
| Megbeszélések jegyzetei | `döntések/`, ha döntés született belőle, különben az aznapi `Napló/` jegyzet. Megbeszélés-mappát csak akkor javasolj, ha sok ilyen jegyzet van. |

## Info blokk (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: a jegyzet megírásának napja.
- `status`: döntéseknél és pályázatoknál lásd lent. Minden másnál: `active` vagy `closed`.
- `tags`: a típus, aztán a téma.
- Nem kötelező: `project`, `deadline`, `description` (egy mondat, idézőjelben, az utolsó sor).

## Döntési jegyzetek

Mindig legyen benne a miért: kik vettek részt benne, mi indította el, milyen kompromisszum született. A döntéshez `> [!important]`, az ismert kockázatokhoz `> [!warning]` jelölést használj.

A döntéseknél közvetlenül a `date:` után jön az `updated:` is. A `date` a létrehozás napja, az `updated` az, amikor utoljára átnézték vagy módosították.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (még döntés előtt áll vagy dolgoznak rajta), `waiting` (valaki másra vár), `paused`, `closed`.
- Ha egy döntés `updated` dátuma 30 napnál régebbi, át kell nézni. A Rendrakó addig jelzi, amíg {Name} meg nem tartja, le nem zárja vagy nem archiválja (mindegyik az aznapi dátumra állítja az `updated` mezőt).
- Egy döntés csak akkor kerül az `archívum/döntések/` mappába, ha {Name} ezt kéri.

## Pályázatok

Minden pályázatnak egy mappa: `pályázatok/{name}/`, benne egy `README.md` a határidővel, a linkkel, az állapottal és azzal, hogy mit küldtek be. A többi fájl (válaszok, motivációs levél) mellette van.

- `status`: `draft`, `submitted`, `accepted`, `rejected` vagy `withdrawn`.
- A válaszokat markdownban tárold. A nagy PDF-ek és diák az agy mappáján kívül maradnak: foglald össze őket egy jegyzetben.

## Szabályok

- A kutatás alapból semleges (23. alapszabály).
- Az elavult kutatást ne töröld, hanem tedd át az `archívum/kutatás/` mappába.
- A `pénzügyek/` privát, és szerepel a `.claudeignore` fájlban. Csak akkor nyisd meg, ha {Name} egy konkrét fájlt kér belőle (8. alapszabály).
