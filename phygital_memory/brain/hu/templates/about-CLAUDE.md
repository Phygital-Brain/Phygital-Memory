<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Ebben a mappában vannak a legfontosabb tények {Name} életéről és munkájáról. Ezek a jegyzetek számítanak a hiteles forrásnak minden más munkához.

## Fájlok

| Fájl | Mire való | Kategóriacímke |
|---|---|---|
| `én.md` | Ki {Name}, hogyan dolgozik, és hogyan dolgozzon neki az ügynöke | `identity` |
| `életrajz.md` | {Name} története | `identity` |
| `célok.md` | Célok és prioritások | `goals` |
| `vállalkozás.md` | A vállalkozás | `business` |
| `szolgáltatások.md` | Szolgáltatások, termékek, ajánlatok | `business` |
| `célközönség.md` | Kik vásárolnak, és hogyan találnak rá {Name} munkájára | `customers` |
| `problémák.md` | Megoldandó problémák | `customers` (vagy `goals`, ha {Name} nem árul semmit) |
| `márka.md` | Hang, stílus, használandó és kerülendő szavak | `brand` |
| `eszközök.md` | Eszközök, és hogy mi hol van | `tools` |
| `önéletrajz.md` | Szakmai múlt, tanulmányok, sajtómegjelenések, díjak | `career` |

## Info blokk (frontmatter)

Itt minden fájl (ezt az egyet kivéve) így kezdődik:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Ki {Name}, és hogyan dolgozzon neki az ügynöke."
---
```

- `type`: mindig `about`.
- `status`: `active`, vagy `outdated`, ha tudjuk, hogy egy tény már elavult.
- `updated`: az a nap, amikor a tények utoljára változtak. Elírás vagy stílus javításakor nem változik.
- `tags`: először `about`, aztán a fájl kategóriacímkéje a fenti táblázatból, aztán témacímkék arról, miről szól a fájl (angolul, kisbetűvel, kötőjellel). Ha egy szakasz bekerül vagy kikerül, frissítsd a témacímkéket.
- `description`: egy mondat, idézőjelben, arról, mi van a fájlban. Mindig az utolsó sor.

## Szabályok

- Ezek a fájlok a hiteles forrás. Ne másold át a tartalmukat máshova: linkelj rájuk.
- "Friss állapot fent, források lent" formátum (17. alapszabály): a mostani állapot felül, a dátumozott források alatta.
- {Name} teljes születési dátuma csak a `én.md` fájlban szerepel. Soha ne másold át, és ne idézd egy válaszban. A születési évet nyugodtan használhatod.
- Új fájlt csak akkor hozz létre, ha egy új témának tényleg kell. Előbb kérdezz (9. alapszabály).
- Átvizsgáláskor jelezd azokat a célokat a `célok.md` fájlban, amelyekhez nincs aktív projekt.
