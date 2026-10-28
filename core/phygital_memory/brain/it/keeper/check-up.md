---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Il check-up del Custode del Cervello: un controllo completo di tutto il cervello, quando {Name} lo chiede. Non cambia niente finché {Name} non dice sì. (Il riordino di ogni giorno è in `giro-quotidiano.md`.)

Quando si usa: "fai un check-up al mio cervello", "check up my brain", "metti in ordine il mio cervello", "tidy my brain", "check-up del cervello", "brain check-up", o la stessa cosa in {Language}.

## 1. Guarda (non cambiare ancora niente)

Cerca in tutta la cartella ed elenca i problemi in questi gruppi:

- **Link rotti**: `[[link]]` che puntano a note che non esistono. Non sistemarli mai creando una nota vuota: la nota vera potrebbe essere ancora in sincronizzazione (regola principale 28).
- **Note orfane**: note a cui nessun'altra nota fa un link.
- **Note vuote o quasi vuote**, e segnaposto rimasti (`[name]`, `TBD`).
- **Posto sbagliato**: file nella radice della cartella (tranne `CLAUDE.md`, `.claudeignore`, `.backups/` e il file di regole di una riga di un altro agente, come `AGENTS.md`), note che non corrispondono alla tabella "Dove va cosa" della loro cartella.
- **Tabelle "Dove va cosa" non aggiornate**: un `CLAUDE.md` elenca file o cartelle che non esistono, o non ne elenca alcuni che esistono (le righe con "si crea la prima volta che serve" vanno bene).
- **Blocchi di informazioni**: mancanti o incompleti rispetto al `CLAUDE.md` della cartella. Niente `status:`, meno di 2 `tags:`, una nota di progetto senza `project:`, tag del giorno fuori dalla lista fissa.
- **Progetti fermi**: nessun aggiornamento da 60 giorni o più. Suggerisci di aggiornare lo stato, di metterlo `paused` o di archiviarlo.
- **Obiettivi senza progetto**: obiettivi in `Profilo/obiettivi.md` senza un progetto attivo.
- **Decisioni da rivedere**: `updated` di più di 30 giorni fa e stato diverso da `closed`.
- **Rapporti vecchi**: `status: active` ma `last-contact` di più di 12 mesi fa. Suggerisci `dormant`.
- **Cose da fare vecchie**: cose da fare aperte in `Diario/cose-da-fare.md` di più di 30 giorni fa.
- **Doppioni**: gli stessi fatti in più di una nota, o due note per la stessa persona o azienda.
- **Verità non aggiornata**: pagine del Profilo o dei Contatti dove i vecchi aggiornamenti seppelliscono la situazione attuale (regola principale 17).
- **Regole in conflitto**: regole del `CLAUDE.md` principale che si contraddicono.
- **Privacy**: password, chiavi o numeri privati in note normali (regole principali 25 e 26). Segnala la nota, mai il valore.
- **Scrittura**: lineette lunghe (em dash) e schemi del Controllo di scrittura nelle note.
- **Nuova versione**: confronta la versione di questo cervello (la prima riga del `CLAUDE.md` principale) con l'ultima versione di Phygital Brain. Se puoi navigare sul web, l'ultima è la release più recente su https://github.com/Phygital-Brain/phygital-brain/releases/latest. Se non puoi, usa la versione di Phygital Brain installata nel tuo agente, se riesci a vederla. Se non riesci a capirlo, salta questo punto.

## 2. Resoconto

Un elenco breve con parole semplici, diviso nei gruppi qui sopra. Per ogni problema: la nota, cosa non va, la correzione che suggerisci. Metti prima le correzioni semplici e sicure (lineette lunghe, tag mancanti, righe delle tabelle "Dove va cosa").

Se è uscita una versione più nuova, comincia il resoconto con una riga. Se il tuo agente ce l'ha già: "È uscita una nuova versione di Phygital Brain. Di' 'aggiorna il mio secondo cervello' (o 'Upgrade my second brain') per vedere le novità." Se non ce l'ha: "È uscita una nuova versione di Phygital Brain. Prima aggiornala nel tuo agente, poi di' 'aggiorna il mio secondo cervello' (o 'Upgrade my second brain')."

## 3. Correggi solo quello che è approvato

Prima della prima correzione, fai una copia di sicurezza di ogni file che cambierai (Copie di sicurezza e annullare nel `CLAUDE.md` principale).

Chiedi (con opzioni da cliccare quando puoi): **Correggi tutte quelle sicure**, **Una alla volta**, **Solo il resoconto**.

- Non eliminare né spostare mai niente senza il controllo dei link e un sì chiaro (regola principale 21).
- Nel dubbio, archivia invece di eliminare.
- Scrivi una riga nella nota di oggi in `Diario/`: cosa è stato controllato e corretto.
