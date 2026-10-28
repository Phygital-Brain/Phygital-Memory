Le conoscenze che si accumulano nel tempo: decisioni, ricerche, candidature e l'archivio.

## Dove va cosa

| Contenuto | Dove va |
|---|---|
| Una decisione con le sue ragioni, o lo studio di una cosa esterna (app, sito, corso, concorrente) | `decisioni/YYYY-MM-DD-{title}.md` |
| Ricerche (mercato, tendenze, opzioni) | `ricerche/{topic}.md` |
| Candidature: lavori, bandi, premi, call aperte (si crea la prima volta che serve) | `candidature/{name}/` |
| Schede dei concorrenti (si crea la prima volta che serve) | `concorrenti/{name}.md` |
| Soldi: fatture, tasse, pagamenti. Privato | `finanze/` |
| Decisioni archiviate | `archivio/decisioni/` |
| Ricerche finite o superate | `archivio/ricerche/` |
| Progetti finiti | `archivio/{name}/` |
| Appunti delle riunioni | `decisioni/` se ne è uscita una decisione, altrimenti la nota di quel giorno in `Diario/`. Proponi una cartella per le riunioni solo quando sono tante. |

## Blocco di informazioni (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: la data in cui è stata scritta la nota.
- `status`: per decisioni e candidature vedi sotto. Per tutto il resto: `active` o `closed`.
- `tags`: il tipo, poi l'argomento.
- Facoltativi: `project`, `deadline`, `description` (una frase, tra virgolette doppie, ultima riga).

## Note di decisione

Scrivi sempre il perché: chi c'era, cosa l'ha fatta nascere, a cosa si è rinunciato. Usa `> [!important]` per la decisione e `> [!warning]` per i rischi noti.

Le decisioni hanno anche `updated:` subito dopo `date:`. `date` è quando è stata creata, `updated` è l'ultima volta che è stata rivista o cambiata.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (ancora da decidere o in lavorazione), `waiting` (si aspetta qualcun altro), `paused`, `closed`.
- Una decisione con `updated` di più di 30 giorni fa va rivista. Il Custode del Cervello la segnala finché {Name} non la tiene, la chiude o la archivia (ognuna di queste cose mette `updated` a quel giorno).
- Una decisione va in `archivio/decisioni/` solo quando lo dice {Name}.

## Candidature

Una cartella per candidatura: `candidature/{name}/`, con un `README.md` che contiene la scadenza, il link, lo stato e cosa è stato inviato. Gli altri file (risposte, lettera di presentazione) stanno accanto.

- `status`: `draft`, `submitted`, `accepted`, `rejected` o `withdrawn`.
- Tieni le risposte in markdown. PDF grandi e presentazioni restano fuori dal vault: riassumili in una nota.

## Regole

- Le ricerche sono neutrali, se non si chiede altro (regola principale 23).
- Sposta le ricerche superate in `archivio/ricerche/` invece di eliminarle.
- `finanze/` è privata ed è in `.claudeignore`. Aprila solo quando {Name} chiede un file preciso (regola principale 8).
