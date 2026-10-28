Wissen, das sich mit der Zeit ansammelt: Entscheidungen, Recherche, Bewerbungen und das Archiv.

## Wo was hinkommt

| Inhalt | Kommt nach |
|---|---|
| Entscheidung mit Begründung, oder eine Analyse von etwas Externem (App, Website, Kurs, Konkurrenz) | `entscheidungen/YYYY-MM-DD-{title}.md` |
| Recherche (Markt, Trends, Optionen) | `recherche/{topic}.md` |
| Bewerbungen: Jobs, Förderungen, Preise, offene Ausschreibungen (wird bei der ersten Nutzung angelegt) | `bewerbungen/{name}/` |
| Profile von Konkurrenten (wird bei der ersten Nutzung angelegt) | `konkurrenz/{name}.md` |
| Geld: Rechnungen, Steuern, Zahlungen. Privat | `finanzen/` |
| Archivierte Entscheidungen | `archiv/entscheidungen/` |
| Abgeschlossene oder veraltete Recherche | `archiv/recherche/` |
| Abgeschlossene Projekte | `archiv/{name}/` |
| Meeting-Notizen | `entscheidungen/`, wenn dabei eine Entscheidung herauskam, sonst die `Tagebuch/`-Notiz von dem Tag. Schlag einen eigenen Meeting-Ordner erst vor, wenn es viele sind. |

## Info-Block (Frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: das Datum, an dem die Notiz geschrieben wurde.
- `status`: für Entscheidungen und Bewerbungen siehe unten. Alles andere: `active` oder `closed`.
- `tags`: zuerst der Typ, dann das Thema.
- Optional: `project`, `deadline`, `description` (ein Satz in doppelten Anführungszeichen, letzte Zeile).

## Entscheidungsnotizen

Schreib immer das Warum dazu: wer beteiligt war, was den Anstoß gab, welcher Kompromiss eingegangen wurde. Nimm `> [!important]` für die Entscheidung selbst und `> [!warning]` für bekannte Risiken.

Entscheidungen haben außerdem `updated:` direkt nach `date:`. `date` ist der Tag, an dem sie angelegt wurde, `updated` der Tag, an dem sie zuletzt geprüft oder geändert wurde.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (wird noch entschieden oder umgesetzt), `waiting` (wartet auf jemand anderen), `paused`, `closed`.
- Eine Entscheidung, deren `updated` mehr als 30 Tage zurückliegt, muss geprüft werden. Der Aufräumhelfer markiert sie, bis {Name} sie behält, schließt oder archiviert (jedes davon setzt `updated` auf diesen Tag).
- Eine Entscheidung kommt nur nach `archiv/entscheidungen/`, wenn {Name} das sagt.

## Bewerbungen

Ein Ordner pro Bewerbung: `bewerbungen/{name}/`, mit einer `README.md`, in der die Frist, der Link, der Stand und das Eingereichte stehen. Andere Dateien (Antworten, Motivationsschreiben) liegen daneben.

- `status`: `draft`, `submitted`, `accepted`, `rejected` oder `withdrawn`.
- Halte Antworten in Markdown fest. Große PDFs und Präsentationen bleiben außerhalb des Gehirns: Fass sie in einer Notiz zusammen.

## Regeln

- Recherche ist standardmäßig neutral (Hauptregel 23).
- Verschieb überholte Recherche nach `archiv/recherche/`, statt sie zu löschen.
- `finanzen/` ist privat und steht in `.claudeignore`. Öffne den Ordner nur, wenn {Name} nach einer bestimmten Datei fragt (Hauptregel 8).
