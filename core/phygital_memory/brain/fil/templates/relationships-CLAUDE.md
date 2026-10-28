<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Kliyente/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Lahat ng nakakatrabaho ni {Name}: isang note bawat tao o organisasyon.

## Mga subfolder

| Folder | Sino ang nandito |
|---|---|
| `Kliyente/` | Mga tao at kumpanyang ginagawan ni {Name} ng trabaho |
| `Katuwang/` | Mga creative partner, palitan ng tulong, walang bayaran |
| `Team/` | Mga taong katrabaho ni {Name} o nagtatrabaho para kay {Name} (freelancer, assistant) |
| `Partner/` | Mga organisasyong tumutulong para mas makilala si {Name} (media, venue, platform) |

## Saan ilalagay ang bagong posibleng kliyente

- Unang kontak na wala pang totoong brief: isang linya sa ilalim ng `## Bago` sa `Kliyente/_Posibleng-kliyente.md` (ginagawa sa unang gamit).
- Sagot na "baka sa susunod": isang linya sa ilalim ng `## Balikan sa susunod` sa `Kliyente/_Posibleng-kliyente.md`.
- Totoong brief, call o quotation na inaayos na: isang note ng kliyente `Kliyente/{client-name}.md` na may `status: prospect`.

Kapag umakyat ng isang hakbang ang posibleng kliyente, ilipat ito sa susunod na lugar at tanggalin sa dati.

## Info block (frontmatter)

Bawat note dito (maliban sa mga `CLAUDE.md` file at `_Posibleng-kliyente.md`) ay nagsisimula sa:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Isang simpleng pangungusap kung sino sila at ang ugnayan nila kay {Name}."
---
```

- `type`: `client`, `collaborator`, `team` o `partner`.
- `status`: `active` (may trabaho o pag-uusap sa huling 12 buwan), `prospect` (nag-uusap, hindi pa nagkakatrabaho), `dormant` (walang pag-uusap nang 12 buwan o higit pa), `closed` (tapos na nang tuluyan).
- `last-contact`: ang pinakahuling buwan na may totoong pag-uusap o trabaho, `YYYY-MM`. Iwanang blangko kung hindi alam.
- `tags`: `relationship`, saka ang uri, saka 2 hanggang 5 topic tag (industriya, bansa, uri ng trabaho), English, maliliit na titik, may gitling.
- `description`: isang pangungusap, nasa double quotes. Laging ang huling linya.
- Opsyonal: `aliases` (ibang pangalang ginagamit para sa kanila), `project` (kasalukuyang project).

## Mga patakaran

- **Walang doble.** Bago gumawa ng note, hanapin ang pangalan at ang mga bersyon nito (may accent, palayaw, pangalan ng brand kumpara sa pangalan ng kumpanya). Kung may note na, gamitin iyon at idagdag ang bagong baybay sa `aliases`. Huwag kailanman gumawa ng pangalawang note para sa iisang tao o kumpanya.
- **Format na "kasalukuyang totoo"** (pangunahing patakaran 17): sino sila at ang kasalukuyang kalagayan sa itaas, ang may-petsang kasaysayan sa ibaba.
- **Panatilihing bago.** Kapag may totoong pag-uusap si {Name} sa isang tao (email, call, naipasang trabaho), gawing buwang ito ang `last-contact`, at ang `status` kung nagbago.
- **Mga contact person** sa isang kumpanya (agent, manager, editor) ay plain text sa loob ng note ng kumpanya, hindi kailanman `[[link]]`, at walang sariling note. Para banggitin sila sa ibang lugar, i-link ang kumpanya: `[[Pangalan ng Kumpanya|Pangalan ng Contact]]`.
- **Mga pribadong detalye** (numero ng phone, email, address ng bahay) ay nasa note lang ng taong iyon o kumpanyang iyon. Huwag kailanman kopyahin ang mga ito sa mga note ng araw o ibang note.
- I-link ang mga tao mula sa mga project at note ng araw gamit ang `[[wikilink]]`.
- Gumawa lang ng bagong subfolder kapag may lumitaw na bagong uri ng ugnayan. Magtanong muna.
