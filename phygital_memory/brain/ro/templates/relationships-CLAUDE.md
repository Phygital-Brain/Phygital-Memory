<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Clienți/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Toți oamenii cu care lucrează {Name}: o notă pentru fiecare persoană sau organizație.

## Subfoldere

| Folder | Cine intră aici |
|---|---|
| `Clienți/` | Oameni și firme pentru care {Name} face lucrări |
| `Colaboratori/` | Parteneri creativi, schimb reciproc, fără bani la mijloc |
| `Echipă/` | Oameni care lucrează cu {Name} sau pentru {Name} (freelanceri, asistenți) |
| `Parteneri/` | Organizații cu care {Name} își construiește o prezență (presă, locații, platforme) |

## Unde merge un potențial client nou

- Un prim contact, fără o cerere concretă încă: un rând la `## Noi` în `Clienți/_Potențiali-clienți.md` (se creează prima dată când e nevoie).
- Un răspuns de tipul "poate mai încolo": un rând la `## De ținut aproape` în `Clienți/_Potențiali-clienți.md`.
- O cerere concretă, un apel sau o ofertă de preț în lucru: o notă de client `Clienți/{client-name}.md` cu `status: prospect`.

Când un potențial client urcă o treaptă, mută-l în locul următor și scoate-l din cel de dinainte.

## Blocul de informații (frontmatter)

Fiecare notă de aici (în afară de fișierele `CLAUDE.md` și `_Potențiali-clienți.md`) începe cu:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "O propoziție simplă despre cine sunt și ce relație au cu {Name}."
---
```

- `type`: `client`, `collaborator`, `team` sau `partner`.
- `status`: `active` (muncă sau contact în ultimele 12 luni), `prospect` (se vorbește, dar nu s-a lucrat niciodată împreună), `dormant` (niciun contact de 12 luni sau mai mult), `closed` (s-a terminat definitiv).
- `last-contact`: cea mai recentă lună cu un contact real sau cu muncă, `YYYY-MM`. Lasă gol dacă nu se știe.
- `tags`: `relationship`, apoi tipul, apoi 2 până la 5 etichete de subiect (domeniu, țară, fel de muncă), în engleză, cu litere mici, cu cratime.
- `description`: o propoziție, între ghilimele duble. Mereu pe ultimul rând.
- Opționale: `aliases` (alte nume sub care sunt cunoscuți), `project` (proiectul de acum).

## Reguli

- **Fără dubluri.** Înainte să creezi o notă, caută numele și variantele lui (cu sau fără diacritice, nume scurte, numele brandului față de numele firmei). Dacă există o notă, folosește-o și adaugă noua scriere în `aliases`. Nu face niciodată o a doua notă pentru aceeași persoană sau firmă.
- **Formatul "adevărul de acum"** (regula principală 17): sus, cine sunt și situația de acum; dedesubt, istoricul cu date.
- **Ține-o la zi.** Când {Name} are un contact real cu cineva (un email, un apel, o lucrare predată), pune `last-contact` la luna asta, și `status` dacă s-a schimbat.
- **Persoanele de contact** dintr-o firmă (un agent, un manager, un editor) sunt text simplu în nota firmei, niciodată `[[linkuri]]`, și nu primesc notă proprie. Ca să le pomenești în altă parte, pune link spre firmă: `[[Company Name|Contact Name]]`.
- **Datele private** (telefoane, emailuri, adrese de acasă) stau doar în nota persoanei sau a firmei respective. Nu le copia niciodată în notele zilei sau în alte note.
- Pune linkuri spre oameni din proiecte și din notele zilei, cu `[[wikilinkuri]]`.
- Creează un subfolder nou doar când apare un fel nou de relație. Întreabă mai întâi.
