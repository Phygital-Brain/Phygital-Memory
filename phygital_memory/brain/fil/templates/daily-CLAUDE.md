<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Ang pang-araw-araw na journal ni {Name}. Isang file bawat araw: `YYYY-MM-DD.md`. Nasa `gagawin.md` ang mga bukas na gawain.

## Info block (frontmatter)

Bawat note ng araw ay nagsisimula sa block na ito. Walang eksepsiyon.

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

- `type`: laging `daily`.
- `date`: ang petsa ng note, `YYYY-MM-DD`.
- `day`: araw ng linggo, sa English (Monday, Tuesday...).
- `week`: numero ng ISO week, `WNN`.
- `month`: buwan, sa English (January, February...).
- `status`: `active` habang bukas pa ang araw, `completed` kapag 2 araw o higit pa na itong luma.
- `tags`: laging `daily`, at kahit alin sa nakapirming listahang ito na nangyari sa araw na iyon. Huwag kailanman gumawa ng ibang tag.
  - `problem`: may nasira o nagkaproblema
  - `clients`: trabaho para sa kliyente o pakikipag-usap sa kliyente
  - `meeting`: isang call o meeting
  - `money`: invoice, bayad, buwis, investment
  - `research`: research na ginawa o mga natuklasan
  - `decision`: may pinagpasyahan si {Name}
  - `travel`: nasa biyahe si {Name}
  - `personal`: kalusugan, buhay, anumang labas sa trabaho

## Mga patakaran

- Sinusunod ng mga petsa ang pangunahing patakaran 30 (time zone muna ng computer, saka {Time zone}).
- Ang info block ang unang isinusulat ng gumawa ng note (ang agent mo o isang naka-schedule na task). Kapag walang info block ang isang note, lagyan ito sa itaas sa susunod na pag-edit.
- Walang `# YYYY-MM-DD` na heading. Ang pangalan ng file ang pamagat.
- Nasa note ng araw ang kasalukuyang kalagayan ng araw: isang malinis na dokumento bawat araw, ina-update ang mga bahagi sa mismong lugar nila, hindi kailanman tambak ng paulit-ulit na entry.
- Session log: bold na headline at 1 o 2 pangungusap, mga tao at project bilang `[[wikilink]]`, nasa naka-link na note ang mga detalye.
- Ang ginawa lang ngayong araw ang nasa note ngayong araw. Ang mga bukas na gawain mula sa mga nakaraang araw ay nasa `gagawin.md`. Huwag kailanman kopyahin ang mga ito pasulong.
- Kapag ginawa mo ang note ngayong araw, tingnan ang mga note mula 2, 3 at 4 na araw na ang nakalipas. Ang mga `status: active` pa ay gagawing `completed`, at lalagyan ng mga tag mula sa nakapirming listahan para sa malinaw na nangyari sa araw na iyon. Huwag nang tumingin nang mas malayo.

## tasks.md

Mga bukas na gawain na hindi kasama sa isang project. Ang mga gawain ng project ay nasa README ng project na iyon ("Status at susunod na hakbang"). Ginagawa sa unang gamit:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Bukas

- [ ] 2026-10-13: Ipadala ang invoice kay [[Ana]]

## Tapos na

- [x] 2026-10-12: Magpa-schedule sa dentista (natapos 2026-10-13)
```

- Pinakabagong bukas na gawain sa itaas, kasama ang petsa ng pagdagdag.
- Kapag tapos na ang isang gawain, i-check ito, idagdag ang petsa ng pagkatapos, at ilipat sa `## Tapos na`.
- Puwedeng tanggalin ang mga tapos nang gawain na lampas 30 araw na (magtanong muna, pangunahing patakaran 9).
