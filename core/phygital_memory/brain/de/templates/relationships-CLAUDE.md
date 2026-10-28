<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Kunden/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Alle, mit denen {Name} zu tun hat: eine Notiz pro Person oder Organisation.

## Unterordner

| Ordner | Wer da reinkommt |
|---|---|
| `Kunden/` | Leute und Firmen, für die {Name} arbeitet |
| `Mitwirkende/` | Kreative Partner, gegenseitiger Austausch, ohne Geld |
| `Team/` | Leute, die mit oder für {Name} arbeiten (Freelancer, Assistenz) |
| `Partner/` | Organisationen, bei denen {Name} sichtbar werden will (Presse, Veranstaltungsorte, Plattformen) |

## Wohin eine neue Anfrage kommt

- Ein erster Kontakt ohne echtes Briefing: eine Zeile unter `## Neu` in `Kunden/_Interessenten.md` (wird bei der ersten Nutzung angelegt).
- Eine Antwort wie "vielleicht später": eine Zeile unter `## Warm halten` in `Kunden/_Interessenten.md`.
- Ein echtes Briefing, ein Gespräch oder ein Angebot in Arbeit: eine Kundennotiz `Kunden/{client-name}.md` mit `status: prospect`.

Wenn eine Anfrage eine Stufe weiterkommt, verschieb sie an den nächsten Ort und lösch sie am vorherigen.

## Info-Block (Frontmatter)

Jede Notiz hier (außer den `CLAUDE.md`-Dateien und `_Interessenten.md`) beginnt so:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Ein einfacher Satz dazu, wer sie sind und wie die Beziehung zu {Name} ist."
---
```

- `type`: `client`, `collaborator`, `team` oder `partner`.
- `status`: `active` (Arbeit oder Kontakt in den letzten 12 Monaten), `prospect` (im Gespräch, noch nie zusammengearbeitet), `dormant` (seit 12 Monaten oder länger kein Kontakt), `closed` (endgültig vorbei).
- `last-contact`: der letzte Monat mit echtem Kontakt oder echter Arbeit, `YYYY-MM`. Leer lassen, wenn unbekannt.
- `tags`: zuerst `relationship`, dann der Typ, dann 2 bis 5 Themen-Tags (Branche, Land, Art der Arbeit), auf Englisch, kleingeschrieben, mit Bindestrichen.
- `description`: ein Satz in doppelten Anführungszeichen. Immer die letzte Zeile.
- Optional: `aliases` (andere Namen für sie), `project` (aktuelles Projekt).

## Regeln

- **Nichts doppelt.** Bevor du eine Notiz anlegst, such nach dem Namen und seinen Varianten (Akzente und Umlaute, Kurznamen, Marke oder Firmenname). Gibt es schon eine Notiz, nimm sie und füg die neue Schreibweise bei `aliases` hinzu. Leg nie eine zweite Notiz für dieselbe Person oder Firma an.
- **Format "Stand oben, Belege unten"** (Hauptregel 17): wer sie sind und der aktuelle Stand oben, der datierte Verlauf darunter.
- **Aktuell halten.** Wenn {Name} echten Kontakt mit jemandem hat (eine E-Mail, ein Gespräch, gelieferte Arbeit), setz `last-contact` auf diesen Monat und pass `status` an, wenn er sich geändert hat.
- **Ansprechpersonen** in einer Firma (eine Agentin, ein Manager, eine Lektorin) stehen als normaler Text in der Firmennotiz, nie als `[[Links]]`, und bekommen keine eigene Notiz. Wenn du sie anderswo erwähnst, verlinke die Firma: `[[Firmenname|Name der Ansprechperson]]`.
- **Private Daten** (Telefonnummern, E-Mail-Adressen, Wohnadressen) stehen nur in der Notiz dieser Person oder Firma. Kopier sie nie in Tagesnotizen oder andere Notizen.
- Verlinke Leute aus Projekten und Tagesnotizen mit `[[Wikilinks]]`.
- Leg einen neuen Unterordner nur an, wenn eine neue Art von Beziehung auftaucht. Frag vorher.
