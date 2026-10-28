<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Asiakkaat/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Kaikki, joiden kanssa {Name} tekee töitä: yksi muistiinpano jokaisesta ihmisestä tai organisaatiosta.

## Alikansiot

| Kansio | Kuka sinne kuuluu |
|---|---|
| `Asiakkaat/` | Ihmiset ja yritykset, joille {Name} tekee töitä |
| `Yhteistyö/` | Luovat kumppanit: vastavuoroista yhteistyötä, ei rahaa |
| `Tiimi/` | Ihmiset, joiden kanssa tai avulla {Name} tekee töitä (freelancerit, avustajat) |
| `Kumppanit/` | Organisaatiot, joiden kautta {Name} haluaa tulla tunnetuksi (media, tapahtumapaikat, alustat) |

## Minne uusi kiinnostunut menee

- Ensimmäinen yhteydenotto ilman varsinaista toimeksiantoa: rivi otsikon `## Uudet` alle tiedostoon `Asiakkaat/_Kiinnostuneet.md` (luodaan, kun tarvitaan ensimmäisen kerran).
- Vastaus, jossa sanotaan "ehkä myöhemmin": rivi otsikon `## Palataan myöhemmin` alle tiedostoon `Asiakkaat/_Kiinnostuneet.md`.
- Oikea toimeksianto, puhelu tai tarjous työn alla: asiakasmuistiinpano `Asiakkaat/{client-name}.md`, jossa `status: prospect`.

Kun kiinnostunut etenee askeleen, siirrä se seuraavaan paikkaan ja poista edellisestä.

## Tietolohko (frontmatter)

Jokainen muistiinpano täällä (paitsi `CLAUDE.md`-tiedostot ja `_Kiinnostuneet.md`) alkaa näin:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Yksi selkeä lause siitä, keitä he ovat ja miten {Name} tuntee heidät."
---
```

- `type`: `client`, `collaborator`, `team` tai `partner`.
- `status`: `active` (työtä tai yhteydenpitoa viimeisen 12 kuukauden aikana), `prospect` (ollaan juteltu, mutta ei ole vielä tehty töitä yhdessä), `dormant` (ei yhteyttä 12 kuukauteen tai pidempään), `closed` (päättynyt lopullisesti).
- `last-contact`: viimeisin kuukausi, jolloin oli oikeaa yhteydenpitoa tai työtä, `YYYY-MM`. Jätä tyhjäksi, jos et tiedä.
- `tags`: ensin `relationship`, sitten tyyppi, sitten 2–5 aihetagia (ala, maa, työn laji), englanniksi, pienillä kirjaimilla, väliviivoilla.
- `description`: yksi lause lainausmerkeissä. Aina viimeisenä rivinä.
- Vapaaehtoiset: `aliases` (muut nimet, joilla heistä puhutaan), `project` (nykyinen projekti).

## Säännöt

- **Ei kaksoiskappaleita.** Ennen kuin luot muistiinpanon, hae nimellä ja sen muunnelmilla (ääkköset ja tarkkeet, lyhyet nimet, brändin nimi vs. yrityksen nimi). Jos muistiinpano on jo olemassa, käytä sitä ja lisää uusi kirjoitusasu kenttään `aliases`. Älä koskaan tee toista muistiinpanoa samasta ihmisestä tai yrityksestä.
- **Muoto "nykytila ylhäällä, havainnot alla"** (pääsääntö 17): ylhäällä keitä he ovat ja nykytilanne, alla päivätty historia.
- **Pidä ajan tasalla.** Kun {Name} on oikeasti yhteydessä johonkuhun (sähköposti, puhelu, toimitettu työ), päivitä `last-contact` tähän kuukauteen, ja `status`, jos se muuttui.
- **Yrityksen yhteyshenkilöt** (esimerkiksi taiteilijan agentti, esihenkilö tai kustannustoimittaja) kirjoitetaan tavallisena tekstinä yrityksen muistiinpanoon, ei koskaan `[[linkkeinä]]`, eikä heistä tehdä omaa muistiinpanoa. Kun mainitset heidät muualla, linkitä yritys: `[[Yrityksen nimi|Yhteyshenkilön nimi]]`.
- **Yksityiset tiedot** (puhelinnumerot, sähköpostiosoitteet, kotiosoitteet) ovat vain kyseisen ihmisen tai yrityksen muistiinpanossa. Älä koskaan kopioi niitä päivän muistiinpanoihin tai muihin muistiinpanoihin.
- Linkitä ihmiset projekteista ja päivän muistiinpanoista `[[wikilinkeillä]]`.
- Luo uusi alikansio vain, kun tulee uudenlainen suhde. Kysy ensin.
