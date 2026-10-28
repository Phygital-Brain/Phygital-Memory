Maarifa yanayoongezeka kadiri muda unavyokwenda: maamuzi, utafiti, maombi na hifadhi ya zamani.

## Kinakwenda wapi

| Kilichomo | Kinakwenda |
|---|---|
| Uamuzi pamoja na sababu zake, au uchunguzi wa kitu cha nje (programu, tovuti, kozi, mshindani) | `maamuzi/YYYY-MM-DD-{title}.md` |
| Utafiti (soko, mwenendo, chaguo) | `utafiti/{topic}.md` |
| Maombi: kazi, ruzuku, tuzo, mialiko ya wazi (open calls) (inatengenezwa mara ya kwanza inapohitajika) | `maombi/{name}/` |
| Maelezo ya washindani (inatengenezwa mara ya kwanza inapohitajika) | `washindani/{name}.md` |
| Pesa: ankara, kodi, malipo. Ya faragha | `fedha/` |
| Maamuzi yaliyowekwa kando | `hifadhi/maamuzi/` |
| Utafiti uliokwisha au uliopitwa na wakati | `hifadhi/utafiti/` |
| Miradi iliyokamilika | `hifadhi/{name}/` |
| Noti za mikutano | `maamuzi/` kama uamuzi ulitoka humo, la sivyo noti ya `Shajara/` ya siku hiyo. Pendekeza folda ya mikutano pale tu zinapokuwa nyingi. |

## Sehemu ya taarifa (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: tarehe noti ilipoandikwa.
- `status`: tazama hapa chini kwa maamuzi na maombi. Kwa vingine vyote: `active` au `closed`.
- `tags`: aina, kisha mada.
- Si lazima: `project`, `deadline`, `description` (sentensi moja, ndani ya alama za nukuu mbili, mstari wa mwisho).

## Noti za maamuzi

Kila mara eleza kwa nini: nani alihusika, nini kilisababisha, na mlikubali kupoteza nini ili kupata nini. Tumia `> [!important]` kwa uamuzi wenyewe na `> [!warning]` kwa hatari zinazojulikana.

Maamuzi pia yana `updated:` mara baada ya `date:`. `date` ni siku ulipotengenezwa, `updated` ni mara ya mwisho ulipopitiwa au kubadilishwa.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (bado unaamuliwa au unafanyiwa kazi), `waiting` (unamsubiri mtu mwingine), `paused`, `closed`.
- Uamuzi ambao `updated` yake ina zaidi ya siku 30 unahitaji kupitiwa. Mtunzaji wa Ubongo anauonyesha hadi {Name} aubakize, aufunge au auweke kando (kila moja ya hayo inaweka `updated` kuwa siku hiyo).
- Uamuzi unahamia `hifadhi/maamuzi/` pale tu {Name} anaposema hivyo.

## Maombi

Folda moja kwa kila ombi: `maombi/{name}/`, yenye `README.md` inayoonyesha tarehe ya mwisho, kiungo, hali na kilichotumwa. Faili nyingine (majibu, barua ya maelezo) zinakaa kando yake.

- `status`: `draft`, `submitted`, `accepted`, `rejected` au `withdrawn`.
- Weka majibu kwa markdown. PDF kubwa na slaidi zinabaki nje ya ubongo: zifupishe kwenye noti.

## Kanuni

- Kwa kawaida, utafiti hauegemei upande wowote (kanuni kuu ya 23).
- Hamishia utafiti uliopitwa na utafiti mpya zaidi kwenye `hifadhi/utafiti/` badala ya kuufuta.
- `fedha/` ni ya faragha na imeorodheshwa kwenye `.claudeignore`. Ifungue pale tu {Name} anapoomba faili fulani hasa (kanuni kuu ya 8).
