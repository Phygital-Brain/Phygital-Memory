<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Denne mappen har de viktigste fakta om {Name}. Disse notatene er fasiten for alt annet arbeid.

## Filer

| Fil | Hva den er til | Kategoritagg |
|---|---|---|
| `meg.md` | Hvem {Name} er, hvordan {Name} jobber, og hvordan agenten skal jobbe | `identity` |
| `biografi.md` | Historien til {Name} | `identity` |
| `mål.md` | Mål og prioriteringer | `goals` |
| `bedrift.md` | Bedriften | `business` |
| `tilbud.md` | Tjenester, produkter, tilbud | `business` |
| `målgruppe.md` | Hvem som kjøper, og hvordan de finner {Name} | `customers` |
| `utfordringer.md` | Problemer som skal løses | `customers` (eller `goals` hvis {Name} ikke selger noe) |
| `merkevare.md` | Stemme, tone, ord som skal brukes og unngås | `brand` |
| `verktøy.md` | Verktøy, og hvor hver type ting ligger | `tools` |
| `cv.md` | Arbeidserfaring, utdanning, presse, priser | `career` |

## Infoblokk (frontmatter)

Hver fil her (unntatt denne) starter med:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Hvem {Name} er, og hvordan agenten skal jobbe for {Name}."
---
```

- `type`: alltid `about`.
- `status`: `active`, eller `outdated` når man vet at noe er utdatert.
- `updated`: datoen fakta sist ble endret. Endres ikke når du bare retter skrivefeil eller stil.
- `tags`: `about`, så filens kategoritagg fra tabellen over, så emnetagger som sier hva filen handler om (engelsk, små bokstaver, bindestreker). Oppdater emnetaggene når en del legges til eller fjernes.
- `description`: én setning, i doble anførselstegn, som sier hva filen inneholder. Alltid siste linje.

## Regler

- Disse filene er fasiten. Ikke kopier innholdet andre steder: lenk til dem.
- Formatet «status øverst, kilder under» (hovedregel 17): slik det er nå øverst, daterte kilder under.
- Den fulle fødselsdatoen til {Name} ligger bare i `meg.md`. Kopier den aldri, og siter den aldri i et svar. Fødselsåret går fint.
- Lag en ny fil bare når et nytt emne trenger det. Spør først (hovedregel 9).
- I en helsesjekk: pek ut mål i `mål.md` som ikke har noe aktivt prosjekt.
