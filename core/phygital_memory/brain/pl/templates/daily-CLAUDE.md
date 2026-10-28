<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Codzienny dziennik, który prowadzi {Name}. Jeden plik na dzień: `YYYY-MM-DD.md`. Otwarte zadania są w `zadania.md`.

## Blok informacji (frontmatter)

Każda notatka dnia zaczyna się od tego bloku. Bez wyjątków.

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

- `type`: zawsze `daily`.
- `date`: data notatki, `YYYY-MM-DD`.
- `day`: dzień tygodnia, po angielsku (Monday, Tuesday...).
- `week`: numer tygodnia ISO, `WNN`.
- `month`: miesiąc, po angielsku (January, February...).
- `status`: `active`, dopóki dzień jest otwarty, `completed`, kiedy notatka ma 2 dni albo więcej.
- `tags`: zawsze `daily`, plus te z tej stałej listy, które pasują do tego dnia. Nigdy nie wymyślaj innych tagów.
  - `problem`: coś się zepsuło albo poszło nie tak
  - `clients`: praca dla klienta albo kontakt z klientem
  - `meeting`: rozmowa albo spotkanie
  - `money`: faktury, płatności, podatki, inwestycje
  - `research`: badania albo ich wyniki
  - `decision`: {Name} podejmuje jakąś decyzję
  - `travel`: {Name} jest w podróży
  - `personal`: zdrowie, życie prywatne, wszystko poza pracą

## Zasady

- Daty według głównej zasady 30 (najpierw strefa czasowa komputera, potem {Time zone}).
- Ten, kto tworzy notatkę (twój agent albo zaplanowane zadanie), najpierw pisze blok informacji. Notatka bez bloku dostaje go na górze przy najbliższej edycji.
- Bez nagłówka tytułu `# YYYY-MM-DD`. Tytułem jest nazwa pliku.
- Notatka dnia pokazuje aktualny stan dnia: jeden uporządkowany dokument na dzień, sekcje aktualizowane na miejscu, nigdy stos powtarzających się wpisów.
- Wpisy z sesji: pogrubiony nagłówek i 1 albo 2 zdania, osoby i projekty jako `[[wikilinki]]`, szczegóły w podlinkowanej notatce.
- Dzisiejsza notatka zawiera tylko to, co dzieje się dzisiaj. Otwarte zadania z wcześniejszych dni trafiają do `zadania.md`. Nigdy nie przepisuj ich do kolejnych dni.
- Kiedy tworzysz dzisiejszą notatkę, zajrzyj do notatek sprzed 2, 3 i 4 dni. Te, które dalej mają `status: active`, dostają `completed` i tagi ze stałej listy za to, co wyraźnie wydarzyło się tamtego dnia. Nie sięgaj dalej wstecz.

## tasks.md

Otwarte zadania, które nie należą do żadnego projektu. Zadania projektowe idą do README danego projektu („Stan i następny krok”). Plik powstaje przy pierwszym użyciu:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Otwarte

- [ ] 2026-10-13: Wysłać fakturę [[Anna|Annie]]

## Zrobione

- [x] 2026-10-12: Umówić się do dentysty (zrobione 2026-10-13)
```

- Najnowsze otwarte zadania na górze, z datą dodania.
- Kiedy zadanie jest zrobione, odhacz je, dopisz datę wykonania i przenieś do `## Zrobione`.
- Zrobione zadania starsze niż 30 dni można usunąć (najpierw zapytaj, główna zasada 9).
