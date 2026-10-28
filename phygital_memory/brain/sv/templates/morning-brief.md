---
type: skill
status: active
tags: [morning-brief, planning]
---

En kort plan för dagen. Två lägen: **Översikt** (på begäran) och **Schema** (varje arbetsdag).

## Översikt

Utlösare: "morgonöversikt", "morning brief" eller samma sak på {Language}.

1. Läs `Dagbok/uppgifter.md`, den senaste dagsanteckningen, "Läge och nästa steg" i varje projekt med `status: active`, och beslut med status `open` eller `waiting`.
2. Om en kalender är ansluten, läs dagens händelser.
3. Svara med högst 6 korta rader:
   - Dagens 3 viktigaste saker, var och en med en `[[länk]]` till sin anteckning.
   - Vad {Name} väntar på från andra.
   - Ett beslut att fatta, om det finns något.
   - Dagens händelser, om en kalender är ansluten.
4. Skriv ingen fil. Om {Name} svarar med ny information, spara den enligt huvudregel 9.

## Schema

Utlösare: "ställ in min morgonöversikt", "set up my morning brief" eller samma sak på {Language}.

1. Fråga vilken tid (klickbara val: 7:00, 8:00, 9:00, 10:00), på de dagar {Name} jobbar. Hoppa över frågan om tiden redan valdes vid starten.
2. Skapa en schemalagd uppgift i agentappen, som körs i den här mappen, med den här prompten:

   > Öppna mappen med min andra hjärna. Läs `Skills/morgonöversikt/morgonöversikt.md` och ge mig min morgonöversikt.

3. Om schemalagda uppgifter inte finns, be {Name} att säga "morgonöversikt" när dagen börjar.
