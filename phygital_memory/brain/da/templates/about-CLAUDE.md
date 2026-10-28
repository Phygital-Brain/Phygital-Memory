<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Den her mappe rummer de vigtigste fakta om {Name}. De her noter er den sikre kilde for alt andet arbejde.

## Filer

| Fil | Hvad den er til | Kategori-tag |
|---|---|---|
| `mig.md` | Hvem {Name} er, hvordan {Name} arbejder, og hvordan {Name} vil have sin agent til at arbejde | `identity` |
| `biografi.md` | Historien om {Name} | `identity` |
| `mål.md` | Mål og prioriteter | `goals` |
| `virksomhed.md` | Virksomheden | `business` |
| `ydelser.md` | Ydelser, produkter, tilbud | `business` |
| `målgruppe.md` | Hvem der køber, og hvordan de finder {Name} | `customers` |
| `udfordringer.md` | Problemer, der skal løses | `customers` (eller `goals`, hvis {Name} ikke sælger noget) |
| `brand.md` | Stemme, tone, ord der skal bruges og undgås | `brand` |
| `værktøjer.md` | Værktøjer, og hvor hver slags ting ligger | `tools` |
| `cv.md` | Arbejdsliv, uddannelse, presse, priser | `career` |

## Infoblok (frontmatter)

Hver fil her (undtagen den her) starter med:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Hvem {Name} er, og hvordan {Name} vil have sin agent til at arbejde."
---
```

- `type`: altid `about`.
- `status`: `active`, eller `outdated`, når man ved, at en oplysning er forældet.
- `updated`: datoen, hvor oplysningerne sidst blev ændret. Rør den ikke ved rettelser af stavefejl eller stil.
- `tags`: `about`, så filens kategori-tag fra tabellen ovenfor, og så emne-tags, der siger, hvad filen handler om (på engelsk, med små bogstaver og bindestreger). Opdater emne-tags, når et afsnit kommer til eller bliver fjernet.
- `description`: én sætning i dobbelte anførselstegn, der siger, hvad filen indeholder. Altid den sidste linje.

## Regler

- De her filer er den sikre kilde. Kopiér ikke indholdet andre steder hen: link til dem.
- Formatet "status øverst, kilder nedenunder" (hovedregel 17): det, der gælder nu, øverst, og daterede kilder nedenunder.
- Den fulde fødselsdato for {Name} står kun i `mig.md`. Kopiér den aldrig, og nævn den aldrig i et svar. Fødselsåret er fint.
- Opret kun en ny fil, når et nyt emne har brug for det. Spørg først (hovedregel 9).
- Ved et tjek: marker mål i `mål.md`, som ikke har noget aktivt projekt.
