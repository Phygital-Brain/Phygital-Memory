---
type: skill
status: active
tags: [brain-keeper, check-up]
---

A Rendrakó átvizsgálása: alapos ránézés az egész agyra, amikor {Name} kéri. Semmi nem változik, amíg {Name} igent nem mond. (A napi rendrakás a `napi.md` fájlban van.)

Mikor indul: "nézd át az agyamat", "rakj rendet az agyamban", "vizsgáld át az agyamat", "check up my brain", "tidy my brain", "brain check-up", vagy ugyanez {Language} nyelven.

## 1. Nézz körül (még ne változtass semmit)

Keress végig az egész mappán, és sorold fel a problémákat ezekben a csoportokban:

- **Hibás linkek**: `[[linkek]]`, amik nem létező jegyzetre mutatnak. Ezeket soha ne javítsd egy üres jegyzet létrehozásával: lehet, hogy a valódi jegyzet még szinkronizálódik (28. alapszabály).
- **Árva jegyzetek**: jegyzetek, amikre egyetlen másik jegyzet sem linkel.
- **Üres vagy majdnem üres jegyzetek**, és bennmaradt helykitöltők (`[name]`, `TBD`).
- **Rossz hely**: fájlok a mappa gyökerében (kivéve a `CLAUDE.md`, a `.claudeignore`, a `.backups/` és egy másik ügynök egysoros szabályfájlja, például az `AGENTS.md`), és jegyzetek, amik nem illenek a mappájuk "Mi hova kerül" táblázatához.
- **Elavult "Mi hova kerül" táblázatok**: egy `CLAUDE.md` olyan fájlokat vagy mappákat sorol fel, amik nem léteznek, vagy kihagy olyanokat, amik léteznek (az "első használatkor jön létre" jelölésű sorok rendben vannak).
- **Info blokkok**: hiányoznak vagy hiányosak a mappa `CLAUDE.md` fájlja szerint. Nincs `status:`, 2-nél kevesebb `tags:`, projektjegyzet `project:` nélkül, napi címkék a fix listán kívül.
- **Elhanyagolt projektek**: 60 napja vagy régebben nem frissültek. Javasolj állapotfrissítést, `paused` állapotot vagy archiválást.
- **Projekt nélküli célok**: az `Rólam/célok.md` olyan céljai, amelyekhez nincs aktív projekt.
- **Átnézendő döntések**: az `updated` 30 napnál régebbi, és az állapot nem `closed`.
- **Régi kapcsolatok**: `status: active`, de a `last-contact` 12 hónapnál régebbi. Javasold a `dormant` állapotot.
- **Régi teendők**: nyitott teendők a `Napló/teendők.md` fájlban, amelyek 30 napnál régebbiek.
- **Ismétlődések**: ugyanazok a tények több jegyzetben, vagy két jegyzet ugyanarról az emberről vagy cégről.
- **Elavult állapot**: Rólam vagy Kapcsolatok oldalak, ahol a régi frissítések alá van temetve a mostani állapot (17. alapszabály).
- **Ütköző szabályok**: a fő `CLAUDE.md` olyan szabályai, amik ellentmondanak egymásnak.
- **Adatvédelem**: jelszavak, kulcsok vagy privát számok sima jegyzetekben (25. és 26. alapszabály). A jegyzetet nevezd meg, az értéket soha.
- **Írás**: gondolatjelek (em dash) és az Írásellenőrzés mintái a jegyzetekben.
- **Új verzió**: hasonlítsd össze ennek az agynak a verzióját (a fő `CLAUDE.md` első sora) a Phygital Brain legújabb verziójával. Ha tudsz böngészni a weben, a legújabb a legutóbbi kiadás itt: https://github.com/Phygital-Brain/phygital-brain/releases/latest. Ha nem tudsz, használd a Phygital Brain ügynöködben telepített verzióját, ha látod. Ha nem tudod megállapítani, hagyd ki.

## 2. Jelentés

Egy rövid lista egyszerű szavakkal, a fenti csoportok szerint. Minden problémánál: a jegyzet, mi a baj, és milyen javítást javasolsz. Az egyszerű, biztonságos javítások kerüljenek előre (gondolatjelek, hiányzó címkék, sorok a "Mi hova kerül" táblázatokban).

Ha van újabb verzió, a jelentés elején írj róla egy sort. Ha az ügynöködben már megvan: "Megjelent a Phygital Brain új verziója. Mondd azt, hogy 'Frissítsd a második agyamat' (vagy 'Upgrade my second brain'), és megmutatom, mi az új." Ha még nincs meg: "Megjelent a Phygital Brain új verziója. Először frissítsd az ügynöködben, aztán mondd azt, hogy 'Frissítsd a második agyamat' (vagy 'Upgrade my second brain')."

## 3. Csak azt javítsd, amit jóváhagytak

Az első javítás előtt készíts mentést minden fájlról, amit módosítani fogsz (Mentések és visszavonás a fő `CLAUDE.md` fájlban).

Kérdezd meg (ha lehet, kattintható opciókkal): **Javítsd az összes biztonságosat**, **Menjünk egyenként**, **Csak a jelentést kérem**.

- Soha ne törölj vagy helyezz át semmit linkellenőrzés és egyértelmű igen nélkül (21. alapszabály).
- Ha bizonytalan vagy, inkább archiválj, ne törölj.
- Írj egy sort a mai `Napló/` jegyzetbe: mit néztél át, és mit javítottál.
