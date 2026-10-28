<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Päiväkirja, jota {Name} pitää. Yksi tiedosto päivää kohti: `YYYY-MM-DD.md`. Avoimet tehtävät ovat tiedostossa `tehtävät.md`.

## Tietolohko (frontmatter)

Jokainen päivän muistiinpano alkaa tällä lohkolla. Ei poikkeuksia.

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

- `type`: aina `daily`.
- `date`: muistiinpanon päivämäärä, `YYYY-MM-DD`.
- `day`: viikonpäivä englanniksi (Monday, Tuesday...).
- `week`: ISO-viikkonumero, `WNN`.
- `month`: kuukausi englanniksi (January, February...).
- `status`: `active`, kun päivä on vielä auki, ja `completed`, kun se on 2 päivää vanha tai vanhempi.
- `tags`: aina `daily`, ja lisäksi tästä kiinteästä listasta ne, jotka sinä päivänä tapahtuivat. Älä koskaan keksi muita tageja.
  - `problem`: jokin hajosi tai meni pieleen
  - `clients`: asiakastyötä tai yhteydenpitoa asiakkaaseen
  - `meeting`: puhelu tai tapaaminen
  - `money`: laskut, maksut, verot, sijoitukset
  - `research`: tiedonhakua tai uusia löydöksiä
  - `decision`: {Name} päätti jotain
  - `travel`: {Name} oli matkoilla
  - `personal`: terveys, elämä, kaikki työn ulkopuolinen

## Säännöt

- Päivämäärät noudattavat pääsääntöä 30 (ensin tietokoneen aikavyöhyke, sitten {Time zone}).
- Se, joka luo muistiinpanon (agenttisi tai ajastettu tehtävä), kirjoittaa ensin tietolohkon. Jos muistiinpanosta puuttuu lohko, se lisätään ylös seuraavan muokkauksen yhteydessä.
- Ei otsikkoa `# YYYY-MM-DD`. Tiedoston nimi on otsikko.
- Päivän muistiinpanossa on päivän nykyinen tilanne: yksi siisti dokumentti päivää kohti. Osioita päivitetään paikallaan, eikä samoja merkintöjä kasata päällekkäin.
- Keskustelulokit: lihavoitu otsikko ja 1 tai 2 lausetta, ihmiset ja projektit `[[wikilinkkeinä]]`. Yksityiskohdat menevät linkitettyyn muistiinpanoon.
- Tämän päivän muistiinpanoon tulevat vain tämän päivän asiat. Aiempien päivien avoimet tehtävät menevät tiedostoon `tehtävät.md`. Älä koskaan kopioi niitä eteenpäin.
- Kun luot tämän päivän muistiinpanon, katso 2, 3 ja 4 päivää vanhat muistiinpanot. Jos jokin niistä on yhä `status: active`, muuta se muotoon `completed` ja lisää kiinteästä listasta tagit sille, mitä sinä päivänä selvästi tapahtui. Älä katso kauemmas taaksepäin.

## tasks.md

Avoimet tehtävät, jotka eivät kuulu mihinkään projektiin. Projektin tehtävät menevät sen projektin README-tiedostoon ("Tilanne ja seuraava askel"). Tiedosto luodaan, kun sitä tarvitaan ensimmäisen kerran:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Avoimet

- [ ] 2026-10-13: Lähetä lasku [[Ana|Analle]]

## Tehdyt

- [x] 2026-10-12: Varaa hammaslääkäri (tehty 2026-10-13)
```

- Uusimmat avoimet tehtävät ylimpänä, ja niissä päivä, jolloin ne lisättiin.
- Kun tehtävä on tehty, rastita se, lisää päivä, jolloin se tehtiin, ja siirrä se kohtaan `## Tehdyt`.
- Yli 30 päivää sitten tehdyt tehtävät voi poistaa (kysy ensin, pääsääntö 9).
