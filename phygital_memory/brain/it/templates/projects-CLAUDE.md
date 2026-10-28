Ogni progetto è una cartella che cresce man mano che arrivano informazioni. `README.md` è l'unico punto di ingresso.

## Dove va cosa

| Contenuto | Dove va |
|---|---|
| Panoramica, stato, scadenza, prossimi passi | `Progetti/{name}/README.md` |
| Gli appunti di lavoro di {Name} | `Progetti/{name}/appunti/{topic}.md` |
| Ricerche | `Progetti/{name}/ricerche/{topic}.md` |
| Brief, specifiche, requisiti | `Progetti/{name}/brief/{name}.md` |
| Bozze, copioni, testi | `Progetti/{name}/bozze/{name}.md` |
| Idee | `Progetti/{name}/idee/{name}.md` |
| Feedback | `Progetti/{name}/feedback/{name}.md` |
| Immagini e media | `Progetti/{name}/media/` |
| Materiale vecchio di questo progetto | `Progetti/{name}/archivio/` |

I nomi delle cartelle sono in minuscolo con i trattini, senza numeri davanti (`ricerche/`, non `01-Research/`). Un progetto può aggiungere una sua cartella quando nessuna di queste va bene.

## Com'è fatto il README

1. Blocco di informazioni (sotto), con una `description`.
2. `## Cos'è`: una o due righe, con un link a [[obiettivi]].
3. `## Stato e prossimo passo`: a che punto è, il prossimo passo.
4. `## Come funziona`: solo se qualcosa di automatico scrive qui (un'attività programmata, uno script).
5. `## Dove sono le cose`: solo quando ci sono sottocartelle. Una piccola tabella con un link a ognuna.

## Blocco di informazioni (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (il README, che ha anche `created`, `updated` e `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` o `done`. Lo stato del README è lo stato del progetto.
- `project`: il nome della cartella del progetto.
- `tags`: il progetto, poi il tipo.

## Regole

- Un progetto nuovo è solo un `README.md`. Crea sottocartelle solo quando arrivano contenuti che ne hanno bisogno, e metti nel README un link a ognuna.
- Il README è l'indice. Non ripetere lì dentro il contenuto delle sottocartelle.
- Niente `CLAUDE.md` dentro un progetto. Le regole per un solo progetto vanno in "Regole per progetto" qui sotto.
- Metti `project:` nel blocco di informazioni di ogni nota collegata.
- Un progetto finito va in `Memoria/archivio/{name}/` solo quando lo dice {Name}.
- Ogni progetto dovrebbe servire a un obiettivo in [[obiettivi]]. In un check-up, segnala gli obiettivi senza progetto e i progetti senza obiettivo.

## Regole per progetto

<!-- Rules for one project only. Add a line when a project needs its own rule: "**Project-Name:** the rule." -->
