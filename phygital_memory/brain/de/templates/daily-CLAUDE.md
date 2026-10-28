<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Das Tagebuch von {Name}. Eine Datei pro Tag: `YYYY-MM-DD.md`. Offene Aufgaben stehen in `aufgaben.md`.

## Info-Block (Frontmatter)

Jede Tagesnotiz beginnt mit diesem Block. Ohne Ausnahme.

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

- `type`: immer `daily`.
- `date`: das Datum der Notiz, `YYYY-MM-DD`.
- `day`: der Wochentag, auf Englisch (Monday, Tuesday...).
- `week`: die ISO-Kalenderwoche, `WNN`.
- `month`: der Monat, auf Englisch (January, February...).
- `status`: `active`, solange der Tag offen ist, `completed`, sobald er 2 oder mehr Tage zurückliegt.
- `tags`: immer `daily`, dazu alle aus dieser festen Liste, die an dem Tag passiert sind. Denk dir nie andere Tags aus.
  - `problem`: etwas ist kaputtgegangen oder schiefgelaufen
  - `clients`: Arbeit für Kunden oder Kontakt mit Kunden
  - `meeting`: ein Call oder Meeting
  - `money`: Rechnungen, Zahlungen, Steuern, Geldanlagen
  - `research`: Recherche gemacht oder Ergebnisse
  - `decision`: {Name} hat etwas entschieden
  - `travel`: {Name} war unterwegs
  - `personal`: Gesundheit, Privates, alles außerhalb der Arbeit

## Regeln

- Datumsangaben folgen Hauptregel 30 (zuerst die Zeitzone des Computers, dann {Time zone}).
- Wer die Notiz anlegt (dein Agent oder eine geplante Aufgabe), schreibt zuerst den Info-Block. Hat eine Notiz keinen, kommt er beim nächsten Bearbeiten oben dazu.
- Keine Überschrift `# YYYY-MM-DD`. Der Dateiname ist der Titel.
- Die Tagesnotiz zeigt den aktuellen Stand des Tages: ein ordentliches Dokument pro Tag, Abschnitte werden direkt aktualisiert, nie ein Stapel wiederholter Einträge.
- Sitzungsprotokolle: eine fette Überschrift plus 1 oder 2 Sätze, Leute und Projekte als `[[Wikilinks]]`, Details kommen in die verlinkte Notiz.
- Die heutige Notiz enthält nur, was heute passiert ist. Offene Aufgaben von früheren Tagen gehören in `aufgaben.md`. Kopier sie nie in den nächsten Tag weiter.
- Wenn du die heutige Notiz anlegst, schau dir die Notizen von vor 2, 3 und 4 Tagen an. Alle, die noch `status: active` haben, werden `completed` und bekommen Tags aus der festen Liste für das, was an dem Tag eindeutig passiert ist. Schau nicht weiter zurück.

## tasks.md

Offene Aufgaben, die zu keinem Projekt gehören. Projektaufgaben kommen in die README des Projekts ("Stand und nächster Schritt"). Wird bei der ersten Nutzung angelegt:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Offen

- [ ] 2026-10-13: Rechnung an [[Ana]] schicken

## Erledigt

- [x] 2026-10-12: Zahnarzttermin machen (erledigt am 2026-10-13)
```

- Die neuesten offenen Aufgaben stehen oben, mit dem Datum, an dem sie dazukamen.
- Ist eine Aufgabe erledigt, hak sie ab, schreib das Datum dazu und verschieb sie nach `## Erledigt`.
- Erledigte Aufgaben, die älter als 30 Tage sind, können weg (vorher fragen, Hauptregel 9).
