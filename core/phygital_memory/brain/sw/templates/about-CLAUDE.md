<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Folda hii ina mambo ya msingi kuhusu {Name}. Noti hizi ndizo chanzo cha ukweli kwa kazi nyingine zote.

## Faili

| Faili | Ina nini | Lebo ya kundi |
|---|---|---|
| `mimi.md` | {Name} ni nani, anavyofanya kazi, na anavyotaka wakala wake afanye kazi | `identity` |
| `wasifu.md` | Hadithi ya maisha ya {Name} | `identity` |
| `malengo.md` | Malengo na vipaumbele | `goals` |
| `biashara.md` | Biashara yenyewe | `business` |
| `huduma.md` | Huduma, bidhaa, ofa | `business` |
| `walengwa.md` | Nani ananunua na wanampataje {Name} | `customers` |
| `changamoto.md` | Changamoto za kutatua | `customers` (au `goals` kama {Name} hauzi kitu) |
| `chapa.md` | Sauti, mtindo, maneno ya kutumia na ya kuepuka | `brand` |
| `zana.md` | Zana anazotumia na kila aina ya kitu kinakaa wapi | `tools` |
| `cv.md` | Historia ya kazi, elimu, habari kwenye vyombo vya habari, tuzo | `career` |

## Sehemu ya taarifa (frontmatter)

Kila faili hapa (isipokuwa hii) inaanza hivi:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "{Name} ni nani na anavyotaka wakala wake afanye kazi."
---
```

- `type`: kila mara `about`.
- `status`: `active`, au `outdated` ikijulikana kuwa jambo fulani limepitwa na wakati.
- `updated`: tarehe ambayo mambo yenyewe yalibadilika mara ya mwisho. Haibadilishwi kwa kurekebisha makosa ya kuandika au mtindo.
- `tags`: `about`, kisha lebo ya kundi la faili kutoka kwenye jedwali hapo juu, kisha lebo za mada zinazotaja faili inahusu nini (Kiingereza, herufi ndogo, vistari). Sasisha lebo za mada sehemu ikiongezwa au ikiondolewa.
- `description`: sentensi moja, ndani ya alama za nukuu mbili, inayosema faili hii ina nini. Kila mara ni mstari wa mwisho.

## Kanuni

- Faili hizi ndizo chanzo cha ukweli. Usinakili yaliyomo mahali pengine: weka kiungo kwake.
- Muundo wa "ukweli wa sasa juu, ushahidi chini" (kanuni kuu ya 17): ukweli wa sasa juu, ushahidi wenye tarehe chini yake.
- Tarehe kamili ya kuzaliwa ya {Name} inakaa ndani ya `mimi.md` tu. Usiinakili wala kuitaja kwenye jibu. Mwaka wa kuzaliwa peke yake ni sawa.
- Tengeneza faili mpya pale tu mada mpya inapohitaji. Uliza kwanza (kanuni kuu ya 9).
- Wakati wa ukaguzi, onyesha malengo kwenye `malengo.md` ambayo hayana mradi unaoendelea.
