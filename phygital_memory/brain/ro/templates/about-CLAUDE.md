<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Folderul ăsta ține faptele de bază despre {Name}. Notele de aici sunt sursa de adevăr pentru tot restul muncii.

## Fișiere

| Fișier | La ce folosește | Eticheta de categorie |
|---|---|---|
| `eu.md` | Cine este {Name}, cum lucrează, cum vrea să lucreze agentul | `identity` |
| `biografie.md` | Povestea de viață: de unde vine {Name} și cum a ajuns aici | `identity` |
| `obiective.md` | Obiective și priorități | `goals` |
| `afacere.md` | Afacerea | `business` |
| `servicii.md` | Servicii, produse, oferte | `business` |
| `clientelă.md` | Cine cumpără și cum ajunge la {Name} | `customers` |
| `probleme.md` | Probleme de rezolvat | `customers` (sau `goals` dacă {Name} nu vinde nimic) |
| `brand.md` | Voce, ton, cuvinte de folosit și de evitat | `brand` |
| `instrumente.md` | Instrumente și unde stă fiecare fel de lucru | `tools` |
| `cv.md` | Experiență de muncă, studii, presă, premii | `career` |

## Blocul de informații (frontmatter)

Fiecare fișier de aici (în afară de acesta) începe cu:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Cine este {Name} și cum vrea să lucreze agentul."
---
```

- `type`: mereu `about`.
- `status`: `active`, sau `outdated` când se știe că un fapt nu mai e valabil.
- `updated`: data la care s-au schimbat ultima dată faptele. Nu se schimbă pentru greșeli de tipar sau retușuri de stil.
- `tags`: `about`, apoi eticheta de categorie a fișierului din tabelul de mai sus, apoi etichete de subiect care spun ce acoperă fișierul (în engleză, cu litere mici, cu cratime). Actualizează etichetele de subiect când adaugi sau scoți o secțiune.
- `description`: o propoziție, între ghilimele duble, care spune ce conține fișierul. Mereu pe ultimul rând.

## Reguli

- Fișierele astea sunt sursa de adevăr. Nu le copia conținutul în altă parte: pune un link spre ele.
- Formatul "adevărul de acum" (regula principală 17): sus, situația de azi; dedesubt, dovezile cu dată.
- Data completă a nașterii stă doar în `eu.md`. Nu o copia și nu o repeta niciodată într-un răspuns. Anul nașterii se poate folosi.
- Creează un fișier nou doar când un subiect nou are nevoie de el. Întreabă mai întâi (regula principală 9).
- La un check-up, semnalează obiectivele din `obiective.md` care nu au niciun proiect activ.
