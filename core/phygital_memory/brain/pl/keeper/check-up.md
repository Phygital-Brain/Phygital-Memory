---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Przegląd, który robi Opiekun mózgu: dokładne spojrzenie na cały mózg, kiedy {Name} o to poprosi. Nic się nie zmienia, dopóki {Name} nie powie „tak”. (Codzienne porządki są w `codzienny-porządek.md`.)

Kiedy: „zrób przegląd mojego mózgu”, „check up my brain”, „posprzątaj w moim mózgu”, „tidy my brain”, „przegląd mózgu”, „brain check-up” albo to samo w języku {Language}.

## 1. Przejrzyj (na razie nic nie zmieniaj)

Przeszukaj cały folder i wypisz problemy w tych grupach:

- **Zepsute linki**: `[[linki]]` do notatek, które nie istnieją. Nigdy nie naprawiaj ich, tworząc pustą notatkę: prawdziwa notatka może się jeszcze synchronizować (główna zasada 28).
- **Osierocone notatki**: notatki, do których nie linkuje żadna inna.
- **Puste albo prawie puste notatki** i pozostawione symbole zastępcze (`[name]`, `TBD`).
- **Złe miejsce**: pliki w katalogu głównym folderu (oprócz `CLAUDE.md`, `.claudeignore`, `.backups/` i jednolinijkowego pliku z zasadami dla innego agenta, na przykład `AGENTS.md`), notatki, które nie pasują do tabeli „Co gdzie trafia” swojego folderu.
- **Nieaktualne tabele „Co gdzie trafia”**: `CLAUDE.md` wymienia pliki albo foldery, których nie ma, albo pomija te, które są (wiersze z dopiskiem „powstaje przy pierwszym użyciu” są w porządku).
- **Bloki informacji**: brakujące albo niepełne w porównaniu z `CLAUDE.md` folderu. Brak `status:`, mniej niż 2 `tags:`, notatka projektu bez `project:`, tagi dnia spoza stałej listy.
- **Projekty bez ruchu**: brak aktualizacji od ponad 60 dni. Zaproponuj aktualizację statusu, `paused` albo archiwum.
- **Cele bez projektu**: cele w `Profil/cele.md` bez żadnego aktywnego projektu.
- **Decyzje do przejrzenia**: `updated` ponad 30 dni temu i status inny niż `closed`.
- **Stare kontakty**: `status: active`, ale `last-contact` ponad 12 miesięcy temu. Zaproponuj `dormant`.
- **Stare zadania**: otwarte zadania w `Dziennik/zadania.md` starsze niż 30 dni.
- **Duplikaty**: te same fakty w więcej niż jednej notatce albo dwie notatki o tej samej osobie lub firmie.
- **Zakopany aktualny stan**: strony w profilu albo kontaktach, gdzie stare aktualizacje przykrywają obecny stan (główna zasada 17).
- **Sprzeczne zasady**: zasady w głównym `CLAUDE.md`, które sobie przeczą.
- **Prywatność**: hasła, klucze albo prywatne numery w zwykłych notatkach (główne zasady 25 i 26). Zgłoś notatkę, nigdy samą wartość.
- **Pisanie**: długie myślniki i wzorce ze „Sprawdzania tekstu” w notatkach.
- **Nowa wersja**: porównaj wersję tego mózgu (pierwsza linia głównego `CLAUDE.md`) z najnowszym Phygital Brain. Jeśli możesz przeglądać internet, najnowsza wersja to najnowsze wydanie na https://github.com/Phygital-Brain/phygital-brain/releases/latest. Jeśli nie możesz, użyj wersji Phygital Brain zainstalowanej w twoim agencie, jeśli ją widzisz. Jeśli nie da się tego ustalić, pomiń ten punkt.

## 2. Raport

Krótka lista prostymi słowami, pogrupowana jak wyżej. Przy każdym problemie: notatka, co jest nie tak, poprawka, którą proponujesz. Najpierw proste, bezpieczne poprawki (długie myślniki, brakujące tagi, wiersze w tabelach „Co gdzie trafia”).

Jeśli jest nowsza wersja, zacznij raport od jednej linii. Jeśli twój agent już ją ma: „Jest nowa wersja Phygital Brain. Powiedz «Zaktualizuj mój drugi mózg» albo «Upgrade my second brain», żeby zobaczyć, co nowego.” Jeśli nie: „Jest nowa wersja Phygital Brain. Najpierw zaktualizuj ją w swoim agencie, a potem powiedz «Zaktualizuj mój drugi mózg» albo «Upgrade my second brain».”

## 3. Poprawiaj tylko to, co zatwierdzone

Przed pierwszą poprawką zrób kopię zapasową każdego pliku, który zmienisz („Kopie zapasowe i cofanie” w głównym `CLAUDE.md`).

Zapytaj (najlepiej z opcjami do kliknięcia): **Popraw wszystkie bezpieczne**, **Po kolei**, **Tylko raport**.

- Nigdy nie usuwaj ani nie przenoś bez sprawdzenia linków i wyraźnego „tak” (główna zasada 21).
- W razie wątpliwości archiwizuj zamiast usuwać.
- Zapisz jedną linię w dzisiejszej notatce w `Dziennik/`: co zostało sprawdzone i poprawione.
