<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

In diesem Ordner stehen die wichtigsten Fakten über {Name}. Diese Notizen sind die verlässliche Quelle für alles andere.

## Dateien

| Datei | Wofür | Kategorie-Tag |
|---|---|---|
| `ich.md` | Wer {Name} ist, wie {Name} arbeitet und wie der Agent arbeiten soll | `identity` |
| `biografie.md` | Die Geschichte von {Name} | `identity` |
| `ziele.md` | Ziele und Prioritäten | `goals` |
| `unternehmen.md` | Das Unternehmen | `business` |
| `angebot.md` | Dienstleistungen, Produkte, Angebote | `business` |
| `zielgruppe.md` | Wer kauft und wie diese Leute {Name} finden | `customers` |
| `probleme.md` | Probleme, die gelöst werden sollen | `customers` (oder `goals`, wenn {Name} nichts verkauft) |
| `marke.md` | Stimme, Tonfall, Wörter, die {Name} benutzt und meidet | `brand` |
| `werkzeuge.md` | Tools und wo was liegt | `tools` |
| `lebenslauf.md` | Berufsweg, Ausbildung, Presse, Auszeichnungen | `career` |

## Info-Block (Frontmatter)

Jede Datei hier (außer dieser) beginnt so:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Wer {Name} ist und wie der Agent arbeiten soll."
---
```

- `type`: immer `about`.
- `status`: `active`, oder `outdated`, wenn bekannt ist, dass ein Fakt nicht mehr stimmt.
- `updated`: das Datum, an dem sich die Fakten zuletzt geändert haben. Bleibt bei Tippfehlern oder Stilkorrekturen unverändert.
- `tags`: zuerst `about`, dann der Kategorie-Tag der Datei aus der Tabelle oben, dann Themen-Tags dafür, worum es in der Datei geht (Englisch, kleingeschrieben, mit Bindestrichen). Pass die Themen-Tags an, wenn ein Abschnitt dazukommt oder wegfällt.
- `description`: ein Satz in doppelten Anführungszeichen, der sagt, was in der Datei steht. Immer die letzte Zeile.

## Regeln

- Diese Dateien sind die verlässliche Quelle. Kopier ihren Inhalt nicht woandershin, sondern verlinke sie.
- Format "Stand oben, Belege unten" (Hauptregel 17): der aktuelle Stand oben, datierte Belege darunter.
- Das vollständige Geburtsdatum von {Name} steht nur in `ich.md`. Kopier es nie und nenn es nie in einer Antwort. Das Geburtsjahr ist okay.
- Leg eine neue Datei nur an, wenn ein neues Thema eine braucht. Frag vorher (Hauptregel 9).
- Markier beim Check-up Ziele in `ziele.md`, zu denen es kein aktives Projekt gibt.
