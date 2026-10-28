Kila mradi ni folda inayokua kadiri taarifa zinavyoingia. `README.md` ndiyo mlango mmoja wa kuingilia.

## Kinakwenda wapi

| Kilichomo | Kinakwenda |
|---|---|
| Maelezo ya jumla, hali, tarehe ya mwisho, hatua zinazofuata | `Miradi/{name}/README.md` |
| Noti za kazi za {Name} | `Miradi/{name}/noti/{topic}.md` |
| Utafiti | `Miradi/{name}/utafiti/{topic}.md` |
| Maelekezo, maelezo ya kiufundi, mahitaji | `Miradi/{name}/maelekezo/{name}.md` |
| Rasimu, miswada, maandishi | `Miradi/{name}/rasimu/{name}.md` |
| Mawazo | `Miradi/{name}/mawazo/{name}.md` |
| Maoni | `Miradi/{name}/maoni/{name}.md` |
| Picha na media | `Miradi/{name}/rasilimali/` |
| Vitu vya zamani vya mradi huu | `Miradi/{name}/hifadhi/` |

Majina ya folda ni herufi ndogo zenye vistari, bila namba mwanzoni (`utafiti/`, si `01-Utafiti/`). Mradi unaweza kuongeza folda yake mwenyewe pale ambapo hakuna kati ya hizi inayofaa.

## Mpangilio wa README

1. Sehemu ya taarifa (hapa chini), pamoja na `description`.
2. `## Ni nini`: mstari mmoja au miwili, na kiungo kwa [[malengo]].
3. `## Hali na hatua inayofuata`: mradi umefika wapi, na hatua inayofuata.
4. `## Jinsi unavyoendeshwa`: pale tu kitu cha kiotomatiki kinapoandika hapa (kazi iliyopangwa kwa ratiba, script).
5. `## Vitu viko wapi`: pale tu folda ndogo zinapokuwepo. Jedwali dogo lenye kiungo kwa kila moja.

## Sehemu ya taarifa (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (README, ambayo pia ina `created`, `updated` na `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` au `done`. Hali ya README ndiyo hali ya mradi.
- `project`: jina la folda ya mradi.
- `tags`: mradi, kisha aina.

## Kanuni

- Mradi mpya ni `README.md` tu. Tengeneza folda ndogo pale tu kinapoingia kitu kinachozihitaji, na uweke kiungo kwazo kutoka kwenye README.
- README ndiyo orodha kuu. Usirudie ndani yake yaliyomo kwenye folda ndogo.
- Hakuna `CLAUDE.md` ndani ya mradi. Kanuni za mradi mmoja zinakwenda chini ya "Kanuni za kila mradi" hapa chini.
- Weka `project:` kwenye sehemu ya taarifa ya kila noti inayohusika.
- Mradi uliokamilika unahamia `Kumbukumbu/hifadhi/{name}/` pale tu {Name} anaposema hivyo.
- Kila mradi unapaswa kusaidia lengo fulani ndani ya [[malengo]]. Wakati wa ukaguzi, onyesha malengo yasiyo na mradi na miradi isiyo na lengo.

## Kanuni za kila mradi

<!-- Kanuni za mradi mmoja tu. Ongeza mstari mradi unapohitaji kanuni yake: "**Jina-la-Mradi:** kanuni yenyewe." -->
