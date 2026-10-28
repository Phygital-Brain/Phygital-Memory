<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Klienci/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Wszyscy, z którymi pracuje {Name}: jedna notatka na osobę albo organizację.

## Podfoldery

| Folder | Kto tu trafia |
|---|---|
| `Klienci/` | Osoby i firmy, dla których {Name} wykonuje pracę |
| `Współtwórcy/` | Partnerzy twórczy, wymiana na zasadzie wzajemności, bez pieniędzy |
| `Zespół/` | Osoby, z którymi {Name} pracuje w zespole albo które {Name} zatrudnia (freelancerzy, asystenci) |
| `Partnerzy/` | Organizacje, dzięki którym {Name} buduje swoją obecność (media, miejsca wydarzeń, platformy) |

## Gdzie trafia nowe zapytanie

- Pierwszy kontakt, jeszcze bez konkretnego briefu: linia pod `## Nowe` w `Klienci/_Zapytania.md` (plik powstaje przy pierwszym użyciu).
- Odpowiedź w stylu „może później”: linia pod `## Podtrzymać kontakt` w `Klienci/_Zapytania.md`.
- Konkretny brief, rozmowa albo wycena w toku: notatka klienta `Klienci/{client-name}.md` ze `status: prospect`.

Kiedy zapytanie przechodzi krok dalej, przenieś je w następne miejsce i usuń z poprzedniego.

## Blok informacji (frontmatter)

Każda notatka tutaj (oprócz plików `CLAUDE.md` i `_Zapytania.md`) zaczyna się tak:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Jedno proste zdanie o tym, kim są i jak współpracuje z nimi {Name}."
---
```

- `type`: `client`, `collaborator`, `team` albo `partner`.
- `status`: `active` (praca albo kontakt w ostatnich 12 miesiącach), `prospect` (rozmowy trwają, jeszcze bez wspólnej pracy), `dormant` (brak kontaktu od 12 miesięcy lub dłużej), `closed` (zakończone na dobre).
- `last-contact`: ostatni miesiąc z prawdziwym kontaktem albo pracą, `YYYY-MM`. Zostaw puste, jeśli nie wiadomo.
- `tags`: najpierw `relationship`, potem typ, potem od 2 do 5 tagów tematycznych (branża, kraj, rodzaj pracy), po angielsku, małymi literami, z łącznikami.
- `description`: jedno zdanie w podwójnym cudzysłowie. Zawsze ostatnia linia.
- Opcjonalnie: `aliases` (inne nazwy, których się dla nich używa), `project` (bieżący projekt).

## Zasady

- **Bez duplikatów.** Zanim utworzysz notatkę, poszukaj nazwy i jej wariantów (polskie znaki albo ich brak, zdrobnienia, odmiana imion, nazwa marki zamiast nazwy firmy). Jeśli notatka istnieje, użyj jej i dopisz nową pisownię do `aliases`. Nigdy nie twórz drugiej notatki dla tej samej osoby albo firmy.
- **Format „aktualny stan na górze”** (główna zasada 17): kim są i jaki jest obecny stan na górze, historia z datami niżej.
- **Aktualność.** Kiedy {Name} ma z kimś prawdziwy kontakt (mail, rozmowa, oddana praca), ustaw `last-contact` na ten miesiąc, a `status`, jeśli się zmienił.
- **Osoby kontaktowe** w firmie (agent, menedżer, redaktor) to zwykły tekst w notatce firmy, nigdy `[[linki]]`, i nie dostają własnej notatki. Żeby wspomnieć o nich gdzie indziej, linkuj firmę: `[[Nazwa firmy|Imię osoby]]`.
- **Prywatne dane** (telefony, maile, adresy domowe) są tylko w notatce tej osoby albo firmy. Nigdy nie kopiuj ich do notatek dnia ani innych notatek.
- Linkuj osoby z projektów i notatek dnia przez `[[wikilinki]]`.
- Nowy podfolder twórz tylko wtedy, kiedy pojawia się nowy rodzaj relacji. Najpierw zapytaj.
