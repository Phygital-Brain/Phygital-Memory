<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Nandito ang mga pangunahing impormasyon tungkol kay {Name}. Ang mga note na ito ang batayan ng lahat ng iba pang trabaho.

## Mga file

| File | Para saan | Category tag |
|---|---|---|
| `profile.md` | Sino si {Name}, paano siya magtrabaho, paano niya gustong magtrabaho ang agent niya | `identity` |
| `talambuhay.md` | Ang kuwento ni {Name} | `identity` |
| `layunin.md` | Mga layunin at prayoridad | `goals` |
| `negosyo.md` | Ang negosyo | `business` |
| `serbisyo.md` | Serbisyo, produkto, alok | `business` |
| `mamimili.md` | Sino ang bumibili at paano nila nahahanap si {Name} | `customers` |
| `problema.md` | Mga problemang dapat lutasin | `customers` (o `goals` kung walang ibinebenta si {Name}) |
| `brand.md` | Boses, tono, mga salitang gagamitin at iiwasan | `brand` |
| `tools.md` | Mga tool at kung saan nakalagay ang bawat uri ng bagay | `tools` |
| `cv.md` | Karanasan sa trabaho, pag-aaral, press, mga parangal | `career` |

## Info block (frontmatter)

Bawat file dito (maliban sa isang ito) ay nagsisimula sa:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Sino si {Name} at paano niya gustong magtrabaho ang agent niya."
---
```

- `type`: laging `about`.
- `status`: `active`, o `outdated` kapag alam nang luma na ang isang detalye.
- `updated`: ang petsa ng huling pagbabago sa mga detalye. Hindi ginagalaw kapag typo o istilo lang ang inayos.
- `tags`: `about`, saka ang category tag ng file mula sa table sa itaas, saka mga topic tag na nagsasabi kung tungkol saan ang file (English, maliliit na titik, may gitling). I-update ang mga topic tag kapag may bahaging idinagdag o tinanggal.
- `description`: isang pangungusap, nasa double quotes, na nagsasabi kung ano ang laman ng file. Laging ang huling linya.

## Mga patakaran

- Ang mga file na ito ang batayan. Huwag kopyahin ang laman nila sa ibang lugar: mag-link sa kanila.
- Format na "kasalukuyang totoo" (pangunahing patakaran 17): ang totoo ngayon sa itaas, ang may-petsang ebidensya sa ibaba.
- Ang buong petsa ng kapanganakan ni {Name} ay nasa `profile.md` lang. Huwag itong kopyahin o banggitin sa sagot. Puwede ang taon ng kapanganakan.
- Gumawa lang ng bagong file kapag may bagong paksang nangangailangan nito. Magtanong muna (pangunahing patakaran 9).
- Sa isang check-up, ituro ang mga layunin sa `layunin.md` na walang aktibong project.
