---
type: skill
status: active
tags: [morning-brief, planning]
---

En kort plan for dagen. To måder: **Overblik** (når man beder om det) og **Fast tid** (hver arbejdsdag).

## Overblik

Udløser: "morgenoverblik", "morning brief" eller det samme på {Language}.

1. Læs `Dagbog/opgaver.md`, den nyeste dagsnote, "Status og næste skridt" for hvert projekt med `status: active`, og beslutninger med status `open` eller `waiting`.
2. Hvis en kalender er forbundet, så læs dagens aftaler.
3. Svar med højst 6 korte linjer:
   - Dagens 3 vigtigste ting, hver med et `[[link]]` til sin note.
   - Hvad {Name} venter på fra andre.
   - Én beslutning, der skal tages, hvis der er en.
   - Dagens aftaler, hvis en kalender er forbundet.
4. Skriv ikke nogen fil. Hvis {Name} svarer med ny information, så gem den efter hovedregel 9.

## Fast tid

Udløser: "sæt mit morgenoverblik op", "set up my morning brief" eller det samme på {Language}.

1. Spørg om tidspunktet (knapper: 7:00, 8:00, 9:00, 10:00) på de dage, {Name} arbejder. Spring spørgsmålet over, hvis opsætningen allerede har sat tidspunktet.
2. Opret en planlagt opgave i agent-appen, der kører på den her mappe, med den her prompt:

   > Åbn mappen med min anden hjerne. Læs `Skills/morgenoverblik/morgenoverblik.md`, og giv mig mit morgenoverblik.

3. Hvis planlagte opgaver ikke findes, så fortæl {Name}, at det bare er at sige "morgenoverblik", når dagen starter.
