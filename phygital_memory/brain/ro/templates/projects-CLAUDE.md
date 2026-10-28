Fiecare proiect e un folder care crește pe măsură ce vin informații. `README.md` e singura poartă de intrare.

## Unde merge fiecare lucru

| Conținut | Unde merge |
|---|---|
| Prezentare, stadiu, termen limită, pașii următori | `Proiecte/{name}/README.md` |
| Notițele de lucru pe care le scrie {Name} | `Proiecte/{name}/notițe/{topic}.md` |
| Cercetări | `Proiecte/{name}/cercetări/{topic}.md` |
| Brief, specificații, cerințe | `Proiecte/{name}/briefuri/{name}.md` |
| Ciorne, scenarii, texte scrise | `Proiecte/{name}/ciorne/{name}.md` |
| Idei | `Proiecte/{name}/idei/{name}.md` |
| Feedback | `Proiecte/{name}/feedback/{name}.md` |
| Imagini și media | `Proiecte/{name}/media/` |
| Materiale vechi din proiectul ăsta | `Proiecte/{name}/arhivă/` |

Numele folderelor sunt cu litere mici și cu cratime, fără numere în față (`cercetări/`, nu `01-Research/`). Un proiect își poate face propriul folder când niciunul dintre acestea nu se potrivește.

## Cum arată README-ul

1. Blocul de informații (mai jos), cu un `description`.
2. `## Ce este`: unul sau două rânduri, cu link spre [[obiective]].
3. `## Stadiu și pasul următor`: unde a ajuns, pasul următor.
4. `## Cum funcționează`: doar dacă scrie ceva automat aici (o activitate programată, un script).
5. `## Unde sunt lucrurile`: doar după ce există subfoldere. Un tabel mic, cu un link spre fiecare.

## Blocul de informații (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (README-ul, care mai are și `created`, `updated` și `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` sau `done`. Stadiul din README e stadiul proiectului.
- `project`: numele folderului proiectului.
- `tags`: proiectul, apoi tipul.

## Reguli

- Un proiect nou e doar un `README.md`. Creează subfoldere doar când vine conținut care are nevoie de ele, și pune link spre ele din README.
- README-ul e cuprinsul. Nu repeta în el ce e în subfoldere.
- Fără `CLAUDE.md` în interiorul unui proiect. Regulile pentru un singur proiect merg mai jos, la "Reguli pentru fiecare proiect".
- Pune `project:` în blocul de informații al fiecărei note legate de proiect.
- Un proiect terminat se mută în `Memorie/arhivă/{name}/` doar când spune {Name}.
- Fiecare proiect ar trebui să ajute la un obiectiv din [[obiective]]. La un check-up, semnalează obiectivele fără proiect și proiectele fără obiectiv.

## Reguli pentru fiecare proiect

<!-- Rules for one project only. Add a line when a project needs its own rule: "**Project-Name:** the rule." -->
