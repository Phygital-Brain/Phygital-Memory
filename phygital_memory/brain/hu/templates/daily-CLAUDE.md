<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

{Name} napi naplója. Minden napnak egy fájl: `YYYY-MM-DD.md`. A nyitott teendők a `teendők.md` fájlban vannak.

## Info blokk (frontmatter)

Minden napi jegyzet ezzel a blokkal kezdődik. Kivétel nélkül.

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

- `type`: mindig `daily`.
- `date`: a jegyzet dátuma, `YYYY-MM-DD`.
- `day`: a hét napja, angolul (Monday, Tuesday...).
- `week`: az ISO hét száma, `WNN`.
- `month`: a hónap, angolul (January, February...).
- `status`: `active`, amíg a nap nyitott, `completed`, ha már legalább 2 napos.
- `tags`: mindig `daily`, plusz azok ebből a fix listából, amik aznap történtek. Soha ne találj ki más címkét.
  - `problem`: valami elromlott vagy rosszul sült el
  - `clients`: ügyfélmunka vagy kapcsolat egy ügyféllel
  - `meeting`: hívás vagy megbeszélés
  - `money`: számlák, kifizetések, adók, befektetések
  - `research`: kutatás vagy új eredmények
  - `decision`: {Name} döntött valamiről
  - `travel`: {Name} úton volt
  - `personal`: egészség, magánélet, bármi a munkán kívül

## Szabályok

- A dátumok a 30. alapszabályt követik (először a gép időzónája, aztán {Time zone}).
- Aki létrehozza a jegyzetet (az ügynököd vagy egy ütemezett feladat), az írja meg először az info blokkot. Ha egy jegyzetből hiányzik, a következő szerkesztéskor kerüljön a tetejére.
- Nincs `# YYYY-MM-DD` címsor. A fájlnév a cím.
- A napi jegyzet a nap aktuális állapotát mutatja: naponta egy rendezett dokumentum, a szakaszokat helyben frissítjük, soha nem halmozunk egymásra ismétlődő bejegyzéseket.
- Munkanapló-bejegyzések: félkövér főcím plusz 1-2 mondat, az emberek és projektek `[[wikilink]]` formában, a részletek a linkelt jegyzetbe kerülnek.
- A mai jegyzetben csak a mai nap dolgai vannak. A korábbi napok nyitott teendői a `teendők.md` fájlba kerülnek. Soha ne másold át őket előre.
- Amikor létrehozod a mai jegyzetet, nézd meg a 2, 3 és 4 nappal ezelőtti jegyzeteket. Ami még `status: active`, az legyen `completed`, és kapjon címkéket a fix listából aszerint, ami aznap egyértelműen történt. Ennél régebbre ne nézz vissza.

## tasks.md

Azok a nyitott teendők, amik nem tartoznak projekthez. A projektek teendői a projekt README fájljába kerülnek ("Hol tart, mi a következő lépés"). Az első használatkor jön létre:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Nyitott

- [ ] 2026-10-13: Számla küldése, címzett: [[Ana]]

## Kész

- [x] 2026-10-12: Időpont a fogorvoshoz (kész: 2026-10-13)
```

- A legújabb nyitott teendők felül, azzal a dátummal, amikor felkerültek.
- Ha egy teendő kész, pipáld ki, írd mellé, mikor lett kész, és tedd át a `## Kész` alá.
- A 30 napnál régebbi kész teendők törölhetők (előbb kérdezz, 9. alapszabály).
