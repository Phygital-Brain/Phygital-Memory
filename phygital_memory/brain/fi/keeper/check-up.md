---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Siivousapurin kuntotarkastus: koko aivojen perusteellinen läpikäynti, kun {Name} pyytää. Mikään ei muutu, ennen kuin {Name} sanoo kyllä. (Päivittäinen siivous on tiedostossa `päivittäinen.md`.)

Milloin: "tarkista aivoni", "check up my brain", "siivoa aivoni", "tidy my brain", "aivojen kuntotarkastus", "brain check-up" tai sama kielellä {Language}.

## 1. Katso (älä vielä muuta mitään)

Hae koko kansiosta ja listaa ongelmat näihin ryhmiin:

- **Rikkinäiset linkit**: `[[linkit]]`, jotka osoittavat muistiinpanoihin, joita ei ole. Älä koskaan korjaa niitä luomalla tyhjää muistiinpanoa: oikea muistiinpano voi olla vielä synkronoitumassa (pääsääntö 28).
- **Orvot**: muistiinpanot, joihin mikään muu muistiinpano ei linkitä.
- **Tyhjät tai melkein tyhjät muistiinpanot** ja jäljelle jääneet paikkamerkit (`[name]`, `TBD`).
- **Väärä paikka**: tiedostot kansion juuressa (paitsi `CLAUDE.md`, `.claudeignore`, `.backups/` ja toisen agentin yhden rivin sääntötiedosto, kuten `AGENTS.md`), ja muistiinpanot, jotka eivät vastaa kansionsa "Mikä menee minne" -taulukkoa.
- **Vanhentuneet "Mikä menee minne" -taulukot**: `CLAUDE.md` listaa tiedostoja tai kansioita, joita ei ole, tai siitä puuttuu olemassa olevia (rivit, joissa lukee "luodaan, kun tarvitaan ensimmäisen kerran", ovat kunnossa).
- **Tietolohkot**: puuttuvat tai vajaat, verrattuna kansion `CLAUDE.md`-tiedostoon. Ei `status:`-riviä, alle 2 tagia kentässä `tags:`, projektin muistiinpano ilman `project:`-riviä, päivän tageja kiinteän listan ulkopuolelta.
- **Pysähtyneet projektit**: ei päivityksiä 60 päivään tai pidempään. Ehdota tilan päivitystä, `paused`-tilaa tai arkistointia.
- **Tavoitteet ilman projektia**: tavoitteet tiedostossa `Profiili/tavoitteet.md`, joilla ei ole yhtään aktiivista projektia.
- **Läpikäyntiä odottavat päätökset**: `updated` yli 30 päivää sitten, eikä tila ole `closed`.
- **Vanhat kontaktit**: `status: active`, mutta `last-contact` yli 12 kuukautta sitten. Ehdota tilaa `dormant`.
- **Vanhat tehtävät**: tiedoston `Päiväkirja/tehtävät.md` avoimet tehtävät, jotka ovat yli 30 päivää vanhoja.
- **Kaksoiskappaleet**: samat tiedot useammassa kuin yhdessä muistiinpanossa, tai kaksi muistiinpanoa samasta ihmisestä tai yrityksestä.
- **Hautautunut nykytila**: profiili- tai kontaktisivut, joilla vanhat päivitykset peittävät nykytilan (pääsääntö 17).
- **Ristiriitaiset säännöt**: pää-`CLAUDE.md`:n säännöt, jotka ovat ristiriidassa keskenään.
- **Yksityisyys**: salasanoja, avaimia tai yksityisiä numeroita tavallisissa muistiinpanoissa (pääsäännöt 25 ja 26). Ilmoita muistiinpano, älä koskaan itse tietoa.
- **Kirjoittaminen**: pitkiä ajatusviivoja (em dash) ja tekstitarkistuksen kaavoja muistiinpanoissa.
- **Uusi versio**: vertaa näiden aivojen versiota (pää-`CLAUDE.md`:n ensimmäinen rivi) uusimpaan Phygital Brainiin. Jos voit selata verkkoa, uusin on viimeisin julkaisu osoitteessa https://github.com/Phygital-Brain/phygital-brain/releases/latest. Jos et voi, käytä agenttiisi asennettua Phygital Brainin versiota, jos näet sen. Jos et pysty sanomaan, ohita tämä.

## 2. Raportoi

Lyhyt lista selkeällä kielellä, ryhmiteltynä kuten yllä. Jokaisesta ongelmasta: muistiinpano, mikä siinä on vialla ja mitä korjaukseksi ehdotat. Laita yksinkertaiset ja turvalliset korjaukset ensin (ajatusviivat, puuttuvat tagit, taulukoiden rivit).

Jos uudempi versio on saatavilla, aloita raportti yhdellä rivillä. Jos agentillasi on se jo: "Phygital Brainista on tullut uusi versio. Sano 'päivitä toiset aivoni' tai 'Upgrade my second brain', niin näet, mitä uutta siinä on." Jos ei ole: "Phygital Brainista on tullut uusi versio. Päivitä se ensin agenttiisi ja sano sitten 'päivitä toiset aivoni' tai 'Upgrade my second brain'."

## 3. Korjaa vain se, mikä hyväksytään

Ennen ensimmäistä korjausta tee varmuuskopio jokaisesta tiedostosta, jota muutat (Varmuuskopiot ja peruminen pää-`CLAUDE.md`:ssä).

Kysy (klikattavat vaihtoehdot, jos mahdollista): **Korjaa kaikki turvalliset**, **Käydään yksi kerrallaan**, **Pelkkä raportti**.

- Älä koskaan poista tai siirrä mitään ilman linkkitarkistusta ja selvää kyllä-vastausta (pääsääntö 21).
- Jos olet epävarma, arkistoi poistamisen sijaan.
- Kirjaa yksi rivi tämän päivän `Päiväkirja/`-muistiinpanoon: mitä tarkistettiin ja korjattiin.
