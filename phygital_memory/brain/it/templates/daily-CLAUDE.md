<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Il diario di ogni giorno di {Name}. Un file per giorno: `YYYY-MM-DD.md`. Le cose da fare ancora aperte stanno in `cose-da-fare.md`.

## Blocco di informazioni (frontmatter)

Ogni nota del giorno inizia con questo blocco. Nessuna eccezione.

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

- `type`: sempre `daily`.
- `date`: la data della nota, `YYYY-MM-DD`.
- `day`: il giorno della settimana, in inglese (Monday, Tuesday...).
- `week`: il numero della settimana ISO, `WNN`.
- `month`: il mese, in inglese (January, February...).
- `status`: `active` finché il giorno è aperto, `completed` quando ha 2 o più giorni.
- `tags`: sempre `daily`, più quelli di questa lista fissa che riguardano cose successe quel giorno. Non inventare mai altri tag.
  - `problem`: qualcosa si è rotto o è andato storto
  - `clients`: lavoro per clienti o contatti con clienti
  - `meeting`: una chiamata o una riunione
  - `money`: fatture, pagamenti, tasse, investimenti
  - `research`: ricerche fatte o cose scoperte
  - `decision`: {Name} ha deciso qualcosa
  - `travel`: {Name} era in viaggio
  - `personal`: salute, vita privata, tutto quello che non è lavoro

## Regole

- Le date seguono la regola principale 30 (prima il fuso orario del computer, poi {Time zone}).
- Chi crea la nota (il tuo agente o un'attività programmata) scrive per primo il blocco di informazioni. Se una nota non ce l'ha, aggiungilo in cima la prossima volta che viene modificata.
- Niente titolo `# YYYY-MM-DD`. Il nome del file è il titolo.
- La nota del giorno contiene lo stato attuale della giornata: un solo documento ordinato per giorno, con le sezioni aggiornate sul posto, mai una pila di voci ripetute.
- Registri di sessione: un titolo in grassetto più 1 o 2 frasi, persone e progetti come `[[wikilink]]`, i dettagli vanno nella nota collegata.
- La nota di oggi contiene solo quello che succede oggi. Le cose da fare aperte dei giorni prima vanno in `cose-da-fare.md`. Non copiarle mai in avanti.
- Quando crei la nota di oggi, guarda le note di 2, 3 e 4 giorni fa. Quelle ancora `status: active` diventano `completed` e ricevono i tag della lista fissa per quello che chiaramente è successo quel giorno. Non guardare più indietro.

## tasks.md

Le cose da fare aperte che non appartengono a un progetto. Quelle di un progetto vanno nel README del progetto ("Stato e prossimo passo"). Si crea la prima volta che serve:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Da fare

- [ ] 2026-10-13: Mandare la fattura ad [[Ana]]

## Fatte

- [x] 2026-10-12: Prenotare il dentista (fatto il 2026-10-13)
```

- Le cose da fare più recenti in alto, con la data in cui sono state aggiunte.
- Quando una cosa è fatta, spuntala, aggiungi la data in cui è stata fatta e spostala sotto `## Fatte`.
- Le cose fatte da più di 30 giorni si possono togliere (chiedi prima, regola principale 9).
