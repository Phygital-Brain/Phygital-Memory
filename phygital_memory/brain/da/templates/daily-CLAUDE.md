<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Dagbogen for {Name}. Én fil pr. dag: `YYYY-MM-DD.md`. Åbne opgaver står i `opgaver.md`.

## Infoblok (frontmatter)

Hver dagsnote starter med den her blok. Ingen undtagelser.

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

- `type`: altid `daily`.
- `date`: notens dato, `YYYY-MM-DD`.
- `day`: ugedagen, på engelsk (Monday, Tuesday...).
- `week`: ISO-ugenummer, `WNN`.
- `month`: måneden, på engelsk (January, February...).
- `status`: `active`, mens dagen er i gang, `completed`, når den er 2 dage gammel eller mere.
- `tags`: altid `daily`, plus dem fra den her faste liste, der skete den dag. Find aldrig på andre tags.
  - `problem`: noget gik i stykker eller gik galt
  - `clients`: arbejde for kunder eller kontakt med kunder
  - `meeting`: et opkald eller et møde
  - `money`: fakturaer, betalinger, skat, investeringer
  - `research`: research eller nye fund
  - `decision`: {Name} besluttede noget
  - `travel`: {Name} var ude at rejse
  - `personal`: helbred, privatliv, alt uden for arbejdet

## Regler

- Datoer følger hovedregel 30 (computerens tidszone først, ellers {Time zone}).
- Den, der opretter noten (din agent eller en planlagt opgave), skriver infoblokken først. En note uden infoblok får den tilføjet øverst, næste gang den bliver redigeret.
- Ingen `# YYYY-MM-DD`-overskrift. Filnavnet er titlen.
- Dagsnoten viser, hvordan dagen står lige nu: ét ryddeligt dokument pr. dag, hvor afsnittene bliver opdateret på stedet, aldrig en bunke af gentagne poster.
- Samtalelogs: fed overskrift plus 1 eller 2 sætninger, personer og projekter som `[[wikilinks]]`, detaljerne i den note, der linkes til.
- Dagens note indeholder kun det, der sker i dag. Åbne opgaver fra tidligere dage hører til i `opgaver.md`. Kopiér dem aldrig videre.
- Når du opretter dagens note, så kig på noterne fra for 2, 3 og 4 dage siden. Dem, der stadig har `status: active`, bliver til `completed` og får tags fra den faste liste for det, der tydeligt skete den dag. Kig ikke længere tilbage.

## tasks.md

Åbne opgaver, der ikke hører til et projekt. Opgaver i et projekt står i projektets README ("Status og næste skridt"). Oprettes første gang, den skal bruges:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Åbne

- [ ] 2026-10-13: Send fakturaen til [[Ana]]

## Færdige

- [x] 2026-10-12: Bestil tid hos tandlægen (færdig 2026-10-13)
```

- De nyeste åbne opgaver øverst, med datoen, de blev tilføjet.
- Når en opgave er færdig, så sæt flueben, tilføj datoen, den blev færdig, og flyt den til `## Færdige`.
- Færdige opgaver, der er mere end 30 dage gamle, kan fjernes (spørg først, hovedregel 9).
