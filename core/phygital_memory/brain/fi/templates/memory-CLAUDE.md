Tieto, joka kertyy ajan mittaan: päätökset, selvitykset, hakemukset ja arkisto.

## Mikä menee minne

| Sisältö | Minne |
|---|---|
| Päätös perusteluineen, tai selvitys jostain ulkopuolisesta (sovellus, verkkosivu, kurssi, kilpailija) | `päätökset/YYYY-MM-DD-{title}.md` |
| Selvitykset (markkinat, trendit, vaihtoehdot) | `selvitykset/{topic}.md` |
| Hakemukset: työpaikat, apurahat, palkinnot, avoimet haut (luodaan, kun tarvitaan ensimmäisen kerran) | `hakemukset/{name}/` |
| Kilpailijoiden profiilit (luodaan, kun tarvitaan ensimmäisen kerran) | `kilpailijat/{name}.md` |
| Raha: laskut, verot, maksut. Yksityistä | `raha-asiat/` |
| Arkistoidut päätökset | `arkisto/päätökset/` |
| Valmiit tai vanhentuneet selvitykset | `arkisto/selvitykset/` |
| Valmiit projektit | `arkisto/{name}/` |
| Tapaamisten muistiinpanot | `päätökset/`, jos tapaamisesta syntyi päätös, muuten sen päivän `Päiväkirja/`-muistiinpano. Ehdota omaa kansiota tapaamisille vasta, kun niitä on paljon. |

## Tietolohko (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: päivä, jolloin muistiinpano kirjoitettiin.
- `status`: päätöksistä ja hakemuksista alla. Kaikki muu: `active` tai `closed`.
- `tags`: ensin tyyppi, sitten aihe.
- Vapaaehtoiset: `project`, `deadline`, `description` (yksi lause lainausmerkeissä, viimeisenä rivinä).

## Päätösmuistiinpanot

Kirjaa aina perustelut: ketkä olivat mukana, mikä johti päätökseen, mitä punnittiin mitäkin vastaan. Käytä `> [!important]` itse päätökselle ja `> [!warning]` tiedossa oleville riskeille.

Päätöksissä on lisäksi `updated:` heti `date:`-rivin jälkeen. `date` on luontipäivä, `updated` on viimeisin kerta, kun päätös käytiin läpi tai sitä muutettiin.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (vielä päätettävänä tai työn alla), `waiting` (odottaa jotakuta muuta), `paused`, `closed`.
- Päätös, jonka `updated` on yli 30 päivää vanha, pitää käydä läpi. Siivousapuri nostaa sen esiin, kunnes {Name} pitää sen voimassa, sulkee sen tai arkistoi sen (jokainen näistä asettaa `updated`-päiväksi sen päivän).
- Päätös siirretään kansioon `arkisto/päätökset/` vain, kun {Name} sanoo niin.

## Hakemukset

Yksi kansio jokaiselle hakemukselle: `hakemukset/{name}/`, ja siinä `README.md`, jossa on määräpäivä, linkki, tila ja se, mitä lähetettiin. Muut tiedostot (vastaukset, hakemusteksti) ovat sen vieressä.

- `status`: `draft`, `submitted`, `accepted`, `rejected` tai `withdrawn`.
- Pidä vastaukset markdownina. Isot PDF:t ja diat pysyvät aivojen ulkopuolella: tee niistä tiivistelmä muistiinpanoon.

## Säännöt

- Selvitykset ovat oletuksena puolueettomia (pääsääntö 23).
- Siirrä vanhentuneet selvitykset kansioon `arkisto/selvitykset/` poistamisen sijaan.
- `raha-asiat/` on yksityinen ja listattu tiedostossa `.claudeignore`. Avaa se vain, kun {Name} pyytää tiettyä tiedostoa (pääsääntö 8).
