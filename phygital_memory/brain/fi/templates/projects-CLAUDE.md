Jokainen projekti on kansio, joka kasvaa sitä mukaa kuin tietoa tulee. `README.md` on ainoa sisäänkäynti.

## Mikä menee minne

| Sisältö | Minne |
|---|---|
| Yleiskuva, tilanne, määräpäivä, seuraavat askeleet | `Projektit/{name}/README.md` |
| Omat työmuistiinpanot, jotka {Name} kirjoittaa | `Projektit/{name}/muistiinpanot/{topic}.md` |
| Selvitykset | `Projektit/{name}/selvitykset/{topic}.md` |
| Briiffi, määrittely, vaatimukset | `Projektit/{name}/briiffit/{name}.md` |
| Luonnokset, käsikirjoitukset, kirjoitettu sisältö | `Projektit/{name}/luonnokset/{name}.md` |
| Ideat | `Projektit/{name}/ideat/{name}.md` |
| Palaute | `Projektit/{name}/palaute/{name}.md` |
| Kuvat ja media | `Projektit/{name}/media/` |
| Projektin vanha materiaali | `Projektit/{name}/arkisto/` |

Kansioiden nimet ovat pienillä kirjaimilla ja väliviivoilla, ilman numeroita alussa (`selvitykset/`, ei `01-Research/`). Projekti voi lisätä oman kansion, kun mikään näistä ei sovi.

## README-tiedoston rakenne

1. Tietolohko (alla), jossa on `description`.
2. `## Mikä se on`: yksi tai kaksi riviä, linkki [[tavoitteet]].
3. `## Tilanne ja seuraava askel`: missä mennään ja mikä on seuraava askel.
4. `## Miten se toimii`: vain jos jokin automaattinen kirjoittaa tänne (ajastettu tehtävä, skripti).
5. `## Mistä löytyy mitäkin`: vasta kun alikansioita on. Pieni taulukko, jossa linkki jokaiseen.

## Tietolohko (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (README, jossa on myös `created`, `updated` ja `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` tai `done`. README-tiedoston tila on koko projektin tila.
- `project`: projektikansion nimi.
- `tags`: ensin projekti, sitten tyyppi.

## Säännöt

- Uusi projekti on pelkkä `README.md`. Luo alikansioita vasta, kun tulee sisältöä, joka niitä tarvitsee, ja linkitä ne README-tiedostosta.
- README on hakemisto. Älä toista siinä alikansioiden sisältöä.
- Ei `CLAUDE.md`-tiedostoa projektin sisällä. Yhden projektin säännöt menevät alla olevaan kohtaan "Projektikohtaiset säännöt".
- Lisää `project:` jokaisen projektiin liittyvän muistiinpanon tietolohkoon.
- Valmis projekti siirretään kansioon `Muisti/arkisto/{name}/` vain, kun {Name} sanoo niin.
- Jokaisen projektin pitäisi palvella jotain tavoitetta, joka on muistiinpanossa [[tavoitteet]]. Kuntotarkastuksessa merkitse tavoitteet, joilla ei ole projektia, ja projektit, joilla ei ole tavoitetta.

## Projektikohtaiset säännöt

<!-- Vain yhtä projektia koskevat säännöt. Lisää rivi, kun projekti tarvitsee oman säännön: "**Projektin-nimi:** sääntö." -->
