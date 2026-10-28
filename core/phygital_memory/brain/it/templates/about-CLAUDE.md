<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Questa cartella contiene i fatti principali su {Name}. Queste note sono la fonte di verità per tutto il resto del lavoro.

## File

| File | A cosa serve | Tag di categoria |
|---|---|---|
| `io.md` | Chi è {Name}, come lavora, come vuole che lavori il suo agente | `identity` |
| `biografia.md` | La storia di {Name} | `identity` |
| `obiettivi.md` | Obiettivi e priorità | `goals` |
| `attività.md` | L'attività | `business` |
| `servizi.md` | Servizi, prodotti, offerte | `business` |
| `clientela.md` | Chi compra e come trova {Name} | `customers` |
| `problemi.md` | Problemi da risolvere | `customers` (oppure `goals` se {Name} non vende niente) |
| `brand.md` | Voce, tono, parole da usare e da evitare | `brand` |
| `strumenti.md` | Strumenti e dove si trova ogni tipo di cosa | `tools` |
| `cv.md` | Esperienze di lavoro, studi, stampa, premi | `career` |

## Blocco di informazioni (frontmatter)

Ogni file qui dentro (tranne questo) inizia così:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Chi è {Name} e come vuole che lavori il suo agente."
---
```

- `type`: sempre `about`.
- `status`: `active`, oppure `outdated` quando si sa che un fatto non è più vero.
- `updated`: la data in cui i fatti sono cambiati l'ultima volta. Non si tocca per errori di battitura o ritocchi di stile.
- `tags`: `about`, poi il tag di categoria del file dalla tabella sopra, poi i tag di argomento che dicono di cosa parla il file (in inglese, minuscolo, con i trattini). Aggiorna i tag di argomento quando aggiungi o togli una sezione.
- `description`: una frase, tra virgolette doppie, che dice cosa contiene il file. Sempre l'ultima riga.

## Regole

- Questi file sono la fonte di verità. Non copiare il loro contenuto altrove: metti un link.
- Formato "verità attuale" (regola principale 17): in alto com'è oggi, sotto le prove con la data.
- La data di nascita completa di {Name} sta solo in `io.md`. Non copiarla mai e non citarla mai in una risposta. L'anno di nascita va bene.
- Crea un file nuovo solo quando serve per un argomento nuovo. Chiedi prima (regola principale 9).
- In un check-up, segnala gli obiettivi di `obiettivi.md` che non hanno un progetto attivo.
