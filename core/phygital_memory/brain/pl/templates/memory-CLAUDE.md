Wiedza, która zbiera się z czasem: decyzje, badania, zgłoszenia i archiwum.

## Co gdzie trafia

| Treść | Dokąd |
|---|---|
| Decyzja z uzasadnieniem albo analiza czegoś z zewnątrz (aplikacji, strony, kursu, konkurencji) | `decyzje/YYYY-MM-DD-{title}.md` |
| Badania (rynek, trendy, opcje) | `badania/{topic}.md` |
| Zgłoszenia: praca, granty, nagrody, otwarte nabory (folder powstaje przy pierwszym użyciu) | `zgłoszenia/{name}/` |
| Profile konkurencji (folder powstaje przy pierwszym użyciu) | `konkurencja/{name}.md` |
| Pieniądze: faktury, podatki, płatności. Prywatne | `finanse/` |
| Zarchiwizowane decyzje | `archiwum/decyzje/` |
| Zakończone albo nieaktualne badania | `archiwum/badania/` |
| Zakończone projekty | `archiwum/{name}/` |
| Notatki ze spotkań | `decyzje/`, jeśli zapadła decyzja, w przeciwnym razie notatka z tego dnia w `Dziennik/`. Folder na spotkania proponuj dopiero, kiedy jest ich dużo. |

## Blok informacji (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: data napisania notatki.
- `status`: dla decyzji i zgłoszeń zobacz niżej. Cała reszta: `active` albo `closed`.
- `tags`: najpierw typ, potem temat.
- Opcjonalnie: `project`, `deadline`, `description` (jedno zdanie w podwójnym cudzysłowie, ostatnia linia).

## Notatki o decyzjach

Zawsze zapisuj, dlaczego: kto brał udział, co było powodem, z czego trzeba było zrezygnować. Użyj `> [!important]` dla samej decyzji i `> [!warning]` dla znanych ryzyk.

Decyzje mają też `updated:` zaraz po `date:`. `date` to dzień utworzenia, `updated` to ostatni raz, kiedy decyzję przejrzano albo zmieniono.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (decyzja albo praca jeszcze trwa), `waiting` (czeka na kogoś innego), `paused`, `closed`.
- Decyzja, której `updated` jest starsze niż 30 dni, wymaga przejrzenia. Opiekun mózgu ją zgłasza, dopóki {Name} nie zdecyduje: zostawić, zamknąć albo zarchiwizować (każdy z tych wyborów ustawia `updated` na ten dzień).
- Decyzja trafia do `archiwum/decyzje/` tylko wtedy, kiedy {Name} tak powie.

## Zgłoszenia

Jeden folder na zgłoszenie: `zgłoszenia/{name}/`, z plikiem `README.md`, w którym są termin, link, status i to, co zostało wysłane. Inne pliki (odpowiedzi, list motywacyjny) leżą obok.

- `status`: `draft`, `submitted`, `accepted`, `rejected` albo `withdrawn`.
- Odpowiedzi trzymaj w markdown. Duże PDF-y i prezentacje zostają poza mózgiem: streść je w notatce.

## Zasady

- Badania są domyślnie neutralne (główna zasada 23).
- Nieaktualne badania przenoś do `archiwum/badania/`, zamiast je usuwać.
- `finanse/` jest prywatny i wpisany do `.claudeignore`. Otwieraj go tylko wtedy, kiedy {Name} prosi o konkretny plik (główna zasada 8).
