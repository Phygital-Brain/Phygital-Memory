<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Notatki i preferencje do umiejętności, których używa agent, plus Opiekun mózgu.

## Struktura

```
Umiejętności/{skill-name}/
  {skill-name}.md albo SKILL.md   co robi ta umiejętność
  notes.md                        głos i preferencje, jakie ma {Name} dla tej umiejętności
  references/                     przykłady i dłuższe materiały
```

## Zainstalowane

| Umiejętność | Folder | Co robi |
|---|---|---|
| Opiekun mózgu | `opiekun-mózgu/` | Codzienne porządki samodzielnie i przegląd, kiedy {Name} poprosi |
| Poranne podsumowanie | `poranne-podsumowanie/` | Krótki plan dnia, na prośbę albo w każdy dzień roboczy |
| Import | `import/` | Przenosi notatki z innych aplikacji według planu, który {Name} najpierw zatwierdza |
| Przygotowanie do spotkania | `przygotowanie-do-spotkania/` | Krótka ściąga przed rozmową, z notatek w mózgu |
| Narzędzia do myślenia | `myślenie/` | Podważa pomysł, szuka wzorców, szuka notatek, które sobie przeczą |
| Połączone aplikacje | `połączone-aplikacje/` | Z których aplikacji czyta mózg i jakie są dla nich zasady |
| No AI Slop | `no-ai-slop/` | Sprawdzanie tekstu: poprawia tekst, żeby brzmiał po ludzku, albo wskazuje wzorce AI (autor: Peter Yang, licencja MIT, nigdy nieedytowane) |

## Zasady

- Jeden folder na umiejętność, nazwa w kebab-case.
- Kiedy dochodzi nowa umiejętność, dopisz wiersz do tabeli wyżej.
- Żeby dodać umiejętność albo połączyć aplikację, najpierw sprawdź propozycje Phygital Brain: `suggested-skills/README.md` i `suggested-apps/README.md` przez konektor Phygital Brain albo online pod adresem https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Jeśli coś tam jest, postępuj według tej strony. Kiedy {Name} zapyta „co mogę dodać do mojego mózgu?”, „what can I add to my brain?”, pokaż obie listy: najpierw to, co pasuje do tego, czym zajmuje się {Name}, i pomiń aplikacje, które są już połączone, oraz umiejętności, które są już zainstalowane.
- `SKILL.md`, który pochodzi od kogoś innego, nigdy nie jest edytowany. Żeby dopasować umiejętność, dodaj `notatki.md` w jej folderze.
- `opiekun-mózgu/codzienny-porządek.md` czyta zaplanowane zadanie. Zmieniaj go tylko po to, żeby zmienić to, co robi codzienne uruchomienie, i trzymaj go w prostej formie: bez linków, bez wyróżnień.
