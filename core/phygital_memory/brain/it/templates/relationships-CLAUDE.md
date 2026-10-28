<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Clienti/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Tutte le persone e le realtà con cui lavora {Name}: una nota per persona o organizzazione.

## Sottocartelle

| Cartella | Chi ci va |
|---|---|
| `Clienti/` | Persone e aziende per cui {Name} fa dei lavori |
| `Collaboratori/` | Partner creativi, scambio alla pari, senza soldi di mezzo |
| `Team/` | Persone che lavorano con {Name} o per {Name} (freelance, assistenti) |
| `Partner/` | Organizzazioni con cui {Name} sta costruendo una presenza (stampa, locali, piattaforme) |

## Dove va un nuovo potenziale cliente

- Un primo contatto senza ancora un brief vero: una riga sotto `## Nuovi` in `Clienti/_Potenziali-clienti.md` (si crea la prima volta che serve).
- Una risposta tipo "magari più avanti": una riga sotto `## Da ricontattare` in `Clienti/_Potenziali-clienti.md`.
- Un brief vero, una chiamata o un preventivo in corso: una nota cliente `Clienti/{client-name}.md` con `status: prospect`.

Quando un potenziale cliente fa un passo avanti, spostalo nel posto successivo e toglilo da quello di prima.

## Blocco di informazioni (frontmatter)

Ogni nota qui dentro (tranne i file `CLAUDE.md` e `_Potenziali-clienti.md`) inizia così:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Una frase semplice su chi è e sul rapporto con {Name}."
---
```

- `type`: `client`, `collaborator`, `team` o `partner`.
- `status`: `active` (lavoro o contatti negli ultimi 12 mesi), `prospect` (ci si sta parlando, mai lavorato insieme), `dormant` (nessun contatto da 12 mesi o più), `closed` (finito per sempre).
- `last-contact`: il mese più recente con un contatto vero o un lavoro, `YYYY-MM`. Lascialo vuoto se non si sa.
- `tags`: `relationship`, poi il tipo, poi da 2 a 5 tag di argomento (settore, paese, tipo di lavoro), in inglese, minuscolo, con i trattini.
- `description`: una frase, tra virgolette doppie. Sempre l'ultima riga.
- Facoltativi: `aliases` (altri nomi usati per questa persona o realtà), `project` (progetto in corso).

## Regole

- **Niente doppioni.** Prima di creare una nota, cerca il nome e le sue varianti (accenti, nomi abbreviati, nome del brand o dell'azienda). Se una nota c'è già, usa quella e aggiungi la nuova grafia in `aliases`. Non fare mai una seconda nota per la stessa persona o azienda.
- **Formato "verità attuale"** (regola principale 17): in alto chi è e la situazione attuale, sotto la storia con le date.
- **Tienila aggiornata.** Quando {Name} ha un contatto vero con qualcuno (un'email, una chiamata, un lavoro consegnato), aggiorna `last-contact` a questo mese, e `status` se è cambiato.
- **Le persone di riferimento** di un'azienda (un agente, un manager, un editor) sono testo semplice dentro la nota dell'azienda, mai `[[link]]`, e non hanno una nota tutta loro. Per nominarle altrove, metti il link all'azienda: `[[Nome Azienda|Nome Persona]]`.
- **I dati privati** (telefoni, email, indirizzi di casa) stanno solo nella nota di quella persona o azienda. Non copiarli mai nelle note del giorno o in altre note.
- Collega le persone da progetti e note del giorno con i `[[wikilink]]`.
- Crea una nuova sottocartella solo quando compare un nuovo tipo di rapporto. Chiedi prima.
