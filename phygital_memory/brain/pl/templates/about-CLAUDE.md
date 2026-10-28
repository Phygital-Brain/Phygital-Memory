<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

W tym folderze są najważniejsze fakty o tym, kim jest {Name}. Te notatki są źródłem prawdy dla całej reszty pracy.

## Pliki

| Plik | Co zawiera | Tag kategorii |
|---|---|---|
| `o-mnie.md` | Kim jest {Name}, jak pracuje i jak ma pracować agent | `identity` |
| `biografia.md` | Historia życia: {Name} | `identity` |
| `cele.md` | Cele i priorytety | `goals` |
| `firma.md` | Firma | `business` |
| `oferta.md` | Usługi, produkty, oferty | `business` |
| `odbiorcy.md` | Kto kupuje i jak trafia do tego, co robi {Name} | `customers` |
| `problemy.md` | Problemy do rozwiązania | `customers` (albo `goals`, jeśli {Name} nic nie sprzedaje) |
| `marka.md` | Głos, ton, słowa, których używać i których unikać | `brand` |
| `narzędzia.md` | Narzędzia i gdzie co leży | `tools` |
| `cv.md` | Przebieg pracy, wykształcenie, media, nagrody | `career` |

## Blok informacji (frontmatter)

Każdy plik tutaj (oprócz tego) zaczyna się tak:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Kim jest {Name} i jak ma z tą osobą pracować agent."
---
```

- `type`: zawsze `about`.
- `status`: `active` albo `outdated`, kiedy wiadomo, że jakiś fakt jest już nieaktualny.
- `updated`: data ostatniej zmiany faktów. Nie zmieniaj jej przy poprawkach literówek czy stylu.
- `tags`: najpierw `about`, potem tag kategorii pliku z tabeli wyżej, potem tagi tematów, które plik opisuje (po angielsku, małymi literami, z łącznikami). Zmieniaj tagi tematów, kiedy dochodzi albo znika jakaś sekcja.
- `description`: jedno zdanie w podwójnym cudzysłowie, które mówi, co jest w pliku. Zawsze ostatnia linia.

## Zasady

- Te pliki są źródłem prawdy. Nie kopiuj ich treści gdzie indziej: linkuj do nich.
- Format „aktualny stan na górze” (główna zasada 17): to, co prawdziwe dziś, na górze, a niżej źródła z datami.
- Pełna data urodzenia, którą podaje {Name}, jest zapisana tylko w `o-mnie.md`. Nigdy jej nie kopiuj ani nie podawaj w odpowiedzi. Sam rok urodzenia może być.
- Nowy plik twórz tylko wtedy, kiedy potrzebuje go nowy temat. Najpierw zapytaj (główna zasada 9).
- Podczas przeglądu zgłaszaj cele z `cele.md`, które nie mają żadnego aktywnego projektu.
