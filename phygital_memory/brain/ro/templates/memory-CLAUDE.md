Cunoștințe care se adună în timp: decizii, cercetări, candidaturi și arhiva.

## Unde merge fiecare lucru

| Conținut | Unde merge |
|---|---|
| O decizie cu motivele ei, sau analiza unui lucru din afară (aplicație, site, curs, concurent) | `decizii/YYYY-MM-DD-{title}.md` |
| Cercetări (piață, tendințe, variante) | `cercetări/{topic}.md` |
| Candidaturi: joburi, finanțări, premii, apeluri deschise (se creează prima dată când e nevoie) | `candidaturi/{name}/` |
| Profiluri de concurenți (se creează prima dată când e nevoie) | `concurenți/{name}.md` |
| Bani: facturi, taxe, plăți. Privat | `finanțe/` |
| Decizii arhivate | `arhivă/decizii/` |
| Cercetări terminate sau învechite | `arhivă/cercetări/` |
| Proiecte terminate | `arhivă/{name}/` |
| Notițe de la întâlniri | `decizii/` dacă din întâlnire a ieșit o decizie, altfel nota din `Jurnal/` a zilei respective. Propune un folder pentru întâlniri doar când sunt multe. |

## Blocul de informații (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: data la care a fost scrisă nota.
- `status`: vezi mai jos pentru decizii și candidaturi. Pentru tot restul: `active` sau `closed`.
- `tags`: tipul, apoi subiectul.
- Opționale: `project`, `deadline`, `description` (o propoziție, între ghilimele duble, pe ultimul rând).

## Notele de decizie

Pune mereu motivul: cine a fost implicat, ce a declanșat decizia, la ce s-a renunțat în schimb. Folosește `> [!important]` pentru decizia propriu-zisă și `> [!warning]` pentru riscurile cunoscute.

Deciziile au și `updated:` imediat după `date:`. `date` e ziua în care a fost creată, `updated` e ultima dată când a fost revăzută sau schimbată.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (încă se hotărăște sau se lucrează la ea), `waiting` (depinde de altcineva), `paused`, `closed`.
- O decizie al cărei `updated` e mai vechi de 30 de zile trebuie revăzută. Îngrijitorul creierului o semnalează până când {Name} o păstrează, o închide sau o arhivează (fiecare dintre ele pune `updated` la ziua respectivă).
- O decizie se mută în `arhivă/decizii/` doar când spune {Name}.

## Candidaturi

Un folder pentru fiecare candidatură: `candidaturi/{name}/`, cu un `README.md` care conține termenul limită, linkul, stadiul și ce s-a trimis. Celelalte fișiere (răspunsuri, scrisoare de intenție) stau lângă el.

- `status`: `draft`, `submitted`, `accepted`, `rejected` sau `withdrawn`.
- Păstrează răspunsurile în markdown. PDF-urile mari și prezentările rămân în afara creierului: rezumă-le într-o notă.

## Reguli

- Cercetările sunt neutre, dacă nu se cere altfel (regula principală 23).
- Mută cercetările depășite în `arhivă/cercetări/` în loc să le ștergi.
- `finanțe/` e privat și trecut în `.claudeignore`. Deschide-l doar când {Name} cere un anumit fișier (regula principală 8).
