<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Ügyfelek/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Mindenki, akivel {Name} dolgozik: emberenként vagy szervezetenként egy jegyzet.

## Almappák

| Mappa | Ki kerül ide |
|---|---|
| `Ügyfelek/` | Emberek és cégek, akiknek {Name} munkát végez |
| `Alkotótársak/` | Alkotótársak, kölcsönös csere, pénz nélkül |
| `Csapat/` | Akik {Name} mellett vagy megbízásából dolgoznak (szabadúszók, asszisztensek) |
| `Partnerek/` | Szervezetek, ahol {Name} szeretne jelen lenni (sajtó, helyszínek, platformok) |

## Hova kerül egy új érdeklődő

- Első megkeresés, még valódi brief nélkül: egy sor a `## Új` alá a `Ügyfelek/_Érdeklődők.md` fájlban (első használatkor jön létre).
- Egy "talán később" válasz: egy sor a `## Szem előtt tartani` alá a `Ügyfelek/_Érdeklődők.md` fájlban.
- Valódi brief, hívás vagy árajánlat van folyamatban: ügyféljegyzet `Ügyfelek/{client-name}.md` néven, `status: prospect` értékkel.

Ha egy érdeklődő egy lépéssel továbblép, tedd át a következő helyére, és töröld az előzőből.

## Info blokk (frontmatter)

Itt minden jegyzet (a `CLAUDE.md` fájlokat és a `_Érdeklődők.md` fájlt kivéve) így kezdődik:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Egy egyszerű mondat arról, kik ők, és mi a kapcsolat köztük és {Name} között."
---
```

- `type`: `client`, `collaborator`, `team` vagy `partner`.
- `status`: `active` (munka vagy kapcsolat az elmúlt 12 hónapban), `prospect` (beszélnek, de még nem dolgoztak együtt), `dormant` (12 hónapja vagy régebben nem volt kapcsolat), `closed` (végleg lezárult).
- `last-contact`: a legutóbbi hónap, amikor valódi kapcsolat vagy munka volt, `YYYY-MM`. Hagyd üresen, ha nem tudni.
- `tags`: `relationship`, aztán a típus, aztán 2-5 témacímke (iparág, ország, a munka fajtája), angolul, kisbetűvel, kötőjellel.
- `description`: egy mondat, idézőjelben. Mindig az utolsó sor.
- Nem kötelező: `aliases` (más nevek, amiken emlegetik őket), `project` (a mostani projekt).

## Szabályok

- **Nincs duplikáció.** Mielőtt jegyzetet hozol létre, keress rá a névre és a változataira (ékezetek, becenevek, márkanév vagy cégnév). Ha már van jegyzet, azt használd, és az új írásmódot add hozzá az `aliases` mezőhöz. Soha ne készíts második jegyzetet ugyanarról az emberről vagy cégről.
- **"Friss állapot fent, források lent" formátum** (17. alapszabály): felül, hogy kik ők és hol tartanak most a dolgok, alatta a dátumozott előzmények.
- **Legyen naprakész.** Ha {Name} valódi kapcsolatba kerül valakivel (e-mail, hívás, leadott munka), állítsd a `last-contact` mezőt az aktuális hónapra, és a `status` mezőt is, ha változott.
- **A kapcsolattartók** egy cégnél (képviselő, menedzser, szerkesztő) sima szövegként szerepelnek a cég jegyzetében, soha nem linkként (`[[...]]`), és nem kapnak saját jegyzetet. Ha máshol említenéd őket, a cégre linkelj: `[[Cég Neve|Kapcsolattartó Neve]]`.
- **A privát adatok** (telefonszám, e-mail, lakcím) csak az adott ember vagy cég jegyzetében szerepelnek. Soha ne másold át őket napi jegyzetekbe vagy más jegyzetekbe.
- A projektekből és napi jegyzetekből linkelj az emberekre (`[[wikilink]]`).
- Új almappát csak akkor hozz létre, ha újfajta kapcsolat jelenik meg. Előbb kérdezz.
