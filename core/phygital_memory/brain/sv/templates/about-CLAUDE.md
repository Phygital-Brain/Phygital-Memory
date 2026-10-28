<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Den här mappen innehåller de viktigaste fakta om {Name}. De här anteckningarna är källan att lita på för allt annat arbete.

## Filer

| Fil | Vad den är till för | Kategoritagg |
|---|---|---|
| `jag.md` | Vem {Name} är, hur {Name} jobbar och hur agenten ska jobba | `identity` |
| `biografi.md` | Berättelsen om {Name} | `identity` |
| `mål.md` | Mål och prioriteringar | `goals` |
| `företag.md` | Företaget | `business` |
| `erbjudande.md` | Tjänster, produkter, erbjudanden | `business` |
| `målgrupp.md` | Vem som köper och hur de hittar {Name} | `customers` |
| `problem.md` | Problem som ska lösas | `customers` (eller `goals` om {Name} inte säljer något) |
| `varumärke.md` | Röst, ton, ord att använda och undvika | `brand` |
| `verktyg.md` | Verktyg och var olika saker finns | `tools` |
| `cv.md` | Arbetslivserfarenhet, utbildning, press, priser | `career` |

## Infoblock (frontmatter)

Varje fil här (utom den här) börjar med:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Vem {Name} är och hur agenten ska jobba."
---
```

- `type`: alltid `about`.
- `status`: `active`, eller `outdated` när man vet att en uppgift inte stämmer längre.
- `updated`: datumet då fakta senast ändrades. Ändras inte vid rättade stavfel eller språkputs.
- `tags`: först `about`, sedan filens kategoritagg från tabellen ovan, sedan ämnestaggar för vad filen handlar om (på engelska, små bokstäver, bindestreck). Uppdatera ämnestaggarna när ett avsnitt läggs till eller tas bort.
- `description`: en mening, inom dubbla citattecken, som säger vad filen innehåller. Alltid sista raden.

## Regler

- De här filerna är källan att lita på. Kopiera inte innehållet någon annanstans: länka till dem.
- Formatet "läget överst, belägg under" (huvudregel 17): det som gäller nu överst, daterade belägg under.
- Det fullständiga födelsedatumet för {Name} finns bara i `jag.md`. Kopiera det aldrig och nämn det aldrig i ett svar. Födelseåret går bra.
- Skapa en ny fil bara när ett nytt ämne behöver en. Fråga först (huvudregel 9).
- Vid en hälsokoll: flagga mål i `mål.md` som inte har något aktivt projekt.
