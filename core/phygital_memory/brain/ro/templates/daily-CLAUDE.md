<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Aici ține {Name} jurnalul de zi cu zi. Un fișier pe zi: `YYYY-MM-DD.md`. Lucrurile de făcut care sunt încă deschise stau în `de-făcut.md`.

## Blocul de informații (frontmatter)

Fiecare notă a zilei începe cu blocul ăsta. Fără excepții.

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

- `type`: mereu `daily`.
- `date`: data notei, `YYYY-MM-DD`.
- `day`: ziua săptămânii, în engleză (Monday, Tuesday...).
- `week`: numărul săptămânii ISO, `WNN`.
- `month`: luna, în engleză (January, February...).
- `status`: `active` cât timp ziua e deschisă, `completed` după ce au trecut 2 zile sau mai multe.
- `tags`: mereu `daily`, plus oricare din lista fixă de mai jos care s-a întâmplat în ziua aceea. Nu inventa niciodată alte etichete.
  - `problem`: ceva s-a stricat sau a mers prost
  - `clients`: muncă pentru clienți sau contact cu clienți
  - `meeting`: un apel sau o întâlnire
  - `money`: facturi, plăți, taxe, investiții
  - `research`: documentare sau lucruri descoperite
  - `decision`: {Name} a hotărât ceva
  - `travel`: {Name} a fost în călătorie
  - `personal`: sănătate, viață, orice în afară de muncă

## Reguli

- Datele urmează regula principală 30 (întâi fusul orar al calculatorului, apoi {Time zone}).
- Cine creează nota (agentul tău sau o activitate programată) scrie întâi blocul de informații. O notă fără bloc îl primește sus data viitoare când e modificată.
- Fără titlu `# YYYY-MM-DD`. Numele fișierului e titlul.
- Nota zilei arată cum stau lucrurile în ziua aceea: un singur document ordonat pe zi, cu secțiuni actualizate pe loc, niciodată o grămadă de intrări repetate.
- Jurnalele de sesiune: un titlu îngroșat plus 1 sau 2 propoziții, oamenii și proiectele ca `[[wikilinkuri]]`, detaliile merg în nota legată.
- Nota de azi conține doar ce se întâmplă azi. Lucrurile de făcut rămase din zilele trecute merg în `de-făcut.md`. Nu le copia niciodată mai departe.
- Când creezi nota de azi, uită-te la notele de acum 2, 3 și 4 zile. Cele care au încă `status: active` devin `completed` și primesc etichete din lista fixă, pentru ce s-a întâmplat clar în ziua aceea. Nu te uita mai în urmă.

## tasks.md

Lucrurile de făcut care nu țin de un proiect. Cele ale unui proiect merg în README-ul proiectului ("Stadiu și pasul următor"). Se creează prima dată când e nevoie:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## De făcut

- [ ] 2026-10-13: Trimite factura către [[Ana]]

## Făcute

- [x] 2026-10-12: Fă o programare la dentist (făcut 2026-10-13)
```

- Cele mai noi lucruri de făcut stau sus, cu data la care au fost adăugate.
- Când un lucru e făcut, bifează-l, adaugă data la care s-a făcut și mută-l la `## Făcute`.
- Lucrurile făcute de mai mult de 30 de zile se pot scoate (întreabă mai întâi, regula principală 9).
