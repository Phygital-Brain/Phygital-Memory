<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Noti na mapendeleo ya ujuzi (skills) anaotumia wakala, pamoja na Mtunzaji wa Ubongo.

## Muundo

```
Ujuzi/{skill-name}/
  {skill-name}.md au SKILL.md   ujuzi huu unafanya nini
  noti.md                       sauti na mapendeleo ya {Name} kwa ujuzi huu
  references/                   mifano na maelezo marefu zaidi
```

## Vilivyowekwa

| Ujuzi | Folda | Unafanya nini |
|---|---|---|
| Mtunzaji wa Ubongo | `mtunzaji-wa-ubongo/` | Hupanga kila siku peke yake, na hufanya ukaguzi {Name} anapoomba |
| Muhtasari wa Asubuhi | `muhtasari-wa-asubuhi/` | Mpango mfupi wa siku, ukiombwa au kila siku ya kazi |
| Kuingiza | `kuingiza/` | Huleta noti kutoka programu nyingine, kwa mpango ambao {Name} anaukubali kwanza |
| Maandalizi ya Mkutano | `maandalizi-ya-mkutano/` | Maelezo mafupi kabla ya simu, kutoka kwenye noti za ubongo |
| Zana za Kufikiri | `zana-za-kufikiri/` | Kupinga wazo, kutafuta mwenendo, kutafuta noti zisizokubaliana |
| Programu Zilizounganishwa | `programu-zilizounganishwa/` | Ubongo unasoma programu zipi, na kanuni zake |
| No AI Slop | `no-ai-slop/` | Ukaguzi wa Maandishi: hurekebisha maandishi yasikike kama ya binadamu, au huonyesha mitindo ya AI (na Peter Yang, leseni ya MIT, haibadilishwi kamwe) |

## Kanuni

- Folda moja kwa kila ujuzi, yenye jina kwa mtindo wa kebab-case.
- Ujuzi mpya ukiongezwa, ongeza mstari kwenye jedwali hapo juu.
- Ili kuongeza ujuzi au kuunganisha programu, angalia kwanza mapendekezo ya Phygital Brain: `suggested-skills/README.md` na `suggested-apps/README.md` kupitia kiunganishi (connector) cha Phygital Brain, au mtandaoni kwenye https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Kikiwa hapo, fuata ukurasa wake. {Name} akiuliza "naweza kuongeza nini kwenye ubongo wangu?", "what can I add to my brain?", mwonyeshe orodha zote mbili, zile zinazofaa kazi ya {Name} kwanza, na uache programu ambazo tayari zimeunganishwa na ujuzi ambao tayari umewekwa.
- `SKILL.md` iliyotoka kwa mtu mwingine haibadilishwi kamwe. Ili kubadilisha ujuzi upendavyo, ongeza `noti.md` ndani ya folda yake.
- `mtunzaji-wa-ubongo/kila-siku.md` inasomwa na kazi iliyopangwa kwa ratiba. Ibadilishe tu kama unataka kubadilisha kile kinachofanyika kila siku, na iwe rahisi: bila viungo, bila callouts.
