---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Ang check-up ng Taga-ayos ng Utak: masusing pagsilip sa buong utak, kapag hiniling ni {Name}. Walang magbabago hangga't hindi pumapayag si {Name}. (Nasa `pang-araw-araw.md` ang araw-araw na pag-aayos.)

Trigger: "i-check up ang utak ko", "check up my brain", "ayusin ang utak ko", "tidy my brain", "check-up ng utak", "brain check-up", o ang katumbas sa {Language}.

## 1. Tumingin (wala munang babaguhin)

Hanapin sa buong folder at ilista ang mga problema sa mga grupong ito:

- **Sirang link**: mga `[[link]]` na tumuturo sa mga note na wala. Huwag kailanman ayusin ang mga ito sa paggawa ng blangkong note: baka nagsi-sync pa ang totoong note (pangunahing patakaran 28).
- **Ulila**: mga note na walang ibang note na nagli-link.
- **Walang laman o halos walang lamang note**, at mga naiwang placeholder (`[name]`, `TBD`).
- **Maling lugar**: mga file sa root ng folder (maliban sa `CLAUDE.md`, `.claudeignore`, `.backups/` at isang isang-linyang file ng patakaran ng ibang agent, gaya ng `AGENTS.md`), mga note na hindi tugma sa routing table ng folder nila.
- **Lumang routing table**: may `CLAUDE.md` na naglilista ng mga file o folder na wala, o hindi naglilista ng mga mayroon (ayos lang ang mga row na may markang "ginagawa sa unang gamit").
- **Info block**: wala o kulang, kumpara sa `CLAUDE.md` ng folder. Walang `status:`, kulang sa 2 `tags:`, note ng project na walang `project:`, mga tag ng araw na wala sa nakapirming listahan.
- **Natenggang project**: walang update nang 60 araw o higit pa. Magmungkahi ng update sa status, `paused`, o archive.
- **Layuning walang project**: mga layunin sa `Tungkol-sa-Akin/layunin.md` na walang aktibong project.
- **Desisyong kailangang balikan**: `updated` na lampas 30 araw na at hindi `closed` ang status.
- **Lumang ugnayan**: `status: active` pero lampas 12 buwan na ang `last-contact`. Imungkahi ang `dormant`.
- **Lumang gawain**: mga bukas na gawain sa `Araw-araw/gagawin.md` na lampas 30 araw na.
- **Doble**: parehong impormasyon sa higit sa isang note, o dalawang note para sa iisang tao o kumpanya.
- **Lumang "totoo"**: mga page sa Tungkol sa Akin o Kontak kung saan natatabunan ng mga lumang update ang kasalukuyang kalagayan (pangunahing patakaran 17).
- **Nagbabanggaang patakaran**: mga patakaran sa pangunahing `CLAUDE.md` na nagkakasalungat.
- **Privacy**: mga password, key o pribadong numero na nasa mga ordinaryong note (pangunahing patakaran 25 at 26). Iulat ang note, hindi kailanman ang value.
- **Pagsulat**: mga em dash at mga pattern ng Suri sa Pagsulat sa mga note.
- **Bagong bersyon**: ihambing ang bersyon ng utak na ito (ang unang linya ng pangunahing `CLAUDE.md`) sa pinakabagong Phygital Brain. Kung kaya mong mag-browse sa web, ang pinakabago ay ang latest release sa https://github.com/Phygital-Brain/phygital-brain/releases/latest. Kung hindi, gamitin ang bersyon ng Phygital Brain na naka-install sa agent mo, kung nakikita mo ito. Kung hindi mo matukoy, laktawan ito.

## 2. Ulat

Isang maikling listahan sa simpleng salita, nakagrupo gaya ng nasa itaas. Para sa bawat problema: ang note, ano ang mali, ang ayos na imumungkahi mo. Unahin ang mga simple at ligtas na ayos (em dash, kulang na tag, mga row sa routing table).

Kung may lumabas na mas bagong bersyon, simulan ang ulat sa isang linya. Kung mayroon na nito ang agent mo: "May bagong bersyon ng Phygital Brain. Sabihin ang 'I-upgrade ang pangalawang utak ko' o 'Upgrade my second brain' para makita kung ano ang bago." Kung wala pa: "May bagong bersyon ng Phygital Brain. I-update muna ito sa agent mo, saka sabihin ang 'I-upgrade ang pangalawang utak ko' o 'Upgrade my second brain'."

## 3. Ayusin lang ang inaprubahan

Bago ang unang ayos, i-backup ang bawat file na babaguhin mo (Backup at Undo sa pangunahing `CLAUDE.md`).

Magtanong (may mga opsyong puwedeng i-click, kung kaya): **Ayusin lahat ng ligtas**, **Isa-isahin**, **Ulat lang**.

- Huwag kailanman magbura o maglipat nang walang link check at malinaw na oo (pangunahing patakaran 21).
- I-archive sa halip na burahin kapag nag-aalinlangan.
- Magsulat ng isang linya sa note ngayong araw sa `Araw-araw/`: ano ang na-check at naayos.
