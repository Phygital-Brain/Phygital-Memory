<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Shajara ya kila siku ya {Name}. Faili moja kwa kila siku: `YYYY-MM-DD.md`. Kazi ambazo bado hazijafanyika zinakaa kwenye `kazi-za-kufanya.md`.

## Sehemu ya taarifa (frontmatter)

Kila noti ya siku inaanza na sehemu hii. Hakuna noti inayorukwa.

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

- `type`: kila mara `daily`.
- `date`: tarehe ya noti, `YYYY-MM-DD`.
- `day`: siku ya wiki, kwa Kiingereza (Monday, Tuesday...).
- `week`: namba ya wiki kwa ISO, `WNN`.
- `month`: mwezi, kwa Kiingereza (January, February...).
- `status`: `active` siku ikiwa bado wazi, `completed` ikishapita siku 2 au zaidi.
- `tags`: kila mara `daily`, pamoja na zile kutoka orodha hii maalum zilizotokea siku hiyo. Usibuni lebo nyingine kamwe.
  - `problem`: kitu kiliharibika au kilienda vibaya
  - `clients`: kazi ya mteja au mawasiliano na mteja
  - `meeting`: simu au mkutano
  - `money`: ankara, malipo, kodi, uwekezaji
  - `research`: utafiti uliofanywa au matokeo yake
  - `decision`: {Name} aliamua jambo
  - `travel`: {Name} alikuwa safarini
  - `personal`: afya, maisha, chochote kisicho cha kazi

## Kanuni

- Tarehe zinafuata kanuni kuu ya 30 (saa za eneo za kompyuta kwanza, kisha {Time zone}).
- Anayetengeneza noti (wakala wako au kazi iliyopangwa kwa ratiba) anaandika sehemu ya taarifa kwanza. Noti isiyo nayo inaongezewa juu kabisa wakati mwingine itakapohaririwa.
- Hakuna kichwa cha `# YYYY-MM-DD`. Jina la faili ndilo kichwa.
- Noti ya siku inaonyesha hali ya siku ilivyo sasa: hati moja nadhifu kwa kila siku, sehemu zinasasishwa palepale, si rundo la maingizo yanayojirudia.
- Kumbukumbu za kikao: kichwa kwa herufi nzito pamoja na sentensi 1 au 2, watu na miradi kama `[[wikilinks]]`, maelezo zaidi yanakwenda kwenye noti iliyounganishwa.
- Noti ya leo ina shughuli za leo tu. Kazi ambazo hazijafanyika kutoka siku zilizopita zinakwenda kwenye `kazi-za-kufanya.md`. Usizinakili kamwe kwenye noti mpya.
- Unapotengeneza noti ya leo, angalia noti za siku 2, 3 na 4 zilizopita. Yoyote ambayo bado ni `status: active` inakuwa `completed`, na inapewa lebo kutoka orodha maalum kwa yale yaliyotokea wazi siku hiyo. Usiangalie nyuma zaidi ya hapo.

## tasks.md

Kazi ambazo hazijafanyika na hazihusiani na mradi wowote. Kazi za mradi zinakwenda kwenye README ya mradi huo ("Hali na hatua inayofuata"). Inatengenezwa mara ya kwanza inapohitajika:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Hazijafanyika

- [ ] 2026-10-13: Mtumie [[Amina]] ankara

## Zimefanyika

- [x] 2026-10-12: Panga miadi na daktari wa meno (imefanyika 2026-10-13)
```

- Kazi za karibuni zaidi ziko juu, pamoja na tarehe zilipoongezwa.
- Kazi ikifanyika, iwekee tiki, ongeza tarehe ilipofanyika, na uihamishie chini ya `## Zimefanyika`.
- Kazi zilizofanyika zenye zaidi ya siku 30 zinaweza kuondolewa (uliza kwanza, kanuni kuu ya 9).
