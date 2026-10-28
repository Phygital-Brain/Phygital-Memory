<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Dagboken för {Name}. En fil per dag: `YYYY-MM-DD.md`. Öppna uppgifter finns i `uppgifter.md`.

## Infoblock (frontmatter)

Varje dagsanteckning börjar med det här blocket. Inga undantag.

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

- `type`: alltid `daily`.
- `date`: anteckningens datum, `YYYY-MM-DD`.
- `day`: veckodagen, på engelska (Monday, Tuesday...).
- `week`: ISO-veckonumret, `WNN`.
- `month`: månaden, på engelska (January, February...).
- `status`: `active` medan dagen pågår, `completed` när den är 2 eller fler dagar gammal.
- `tags`: alltid `daily`, plus de taggar från den här fasta listan som hände den dagen. Hitta aldrig på andra taggar.
  - `problem`: något gick sönder eller blev fel
  - `clients`: kundjobb eller kontakt med kunder
  - `meeting`: ett samtal eller möte
  - `money`: fakturor, betalningar, skatt, investeringar
  - `research`: research som gjorts eller nya rön
  - `decision`: {Name} bestämde något
  - `travel`: {Name} var ute och reste
  - `personal`: hälsa, privatliv, allt utanför jobbet

## Regler

- Datum följer huvudregel 30 (datorns tidszon först, sedan {Time zone}).
- Den som skapar anteckningen (din agent eller en schemalagd uppgift) skriver infoblocket först. En anteckning utan infoblock får det tillagt överst nästa gång den redigeras.
- Ingen rubrik `# YYYY-MM-DD`. Filnamnet är titeln.
- Dagsanteckningen visar läget för dagen: ett städat dokument per dag, där avsnitten uppdateras på plats, aldrig en hög av upprepade inlägg.
- Sessionsloggar: en fet rubrik plus 1 eller 2 meningar, personer och projekt som `[[wikilänkar]]`, detaljerna hamnar i den länkade anteckningen.
- Dagens anteckning innehåller bara det som hänt i dag. Öppna uppgifter från tidigare dagar hamnar i `uppgifter.md`. Kopiera dem aldrig framåt.
- När du skapar dagens anteckning, titta på anteckningarna från 2, 3 och 4 dagar sedan. De som fortfarande har `status: active` blir `completed` och får taggar från den fasta listan för det som tydligt hände den dagen. Titta inte längre bakåt.

## tasks.md

Öppna uppgifter som inte hör till ett projekt. Projektuppgifter hamnar i projektets README ("Läge och nästa steg"). Skapas första gången den behövs:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Öppna

- [ ] 2026-10-13: Skicka fakturan till [[Ana]]

## Klara

- [x] 2026-10-12: Boka tid hos tandläkaren (klar 2026-10-13)
```

- De nyaste öppna uppgifterna överst, med datumet då de lades till.
- När en uppgift är klar: bocka av den, lägg till datumet då den blev klar och flytta den till `## Klara`.
- Klara uppgifter som är äldre än 30 dagar kan tas bort (fråga först, huvudregel 9).
