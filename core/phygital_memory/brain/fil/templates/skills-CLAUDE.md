<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Mga note at kagustuhan para sa mga skill na ginagamit ng agent, kasama ang Taga-ayos ng Utak.

## Ayos

```
Skills/{skill-name}/
  {skill-name}.md o SKILL.md    ano ang ginagawa ng skill
  notes.md                      ang boses at kagustuhan ni {Name} para sa skill na ito
  references/                   mga halimbawa at mas mahahabang materyal
```

## Naka-install

| Skill | Folder | Ano ang ginagawa |
|---|---|---|
| Taga-ayos ng Utak | `taga-ayos-ng-utak/` | Kusang nag-aayos araw-araw, at nagche-check-up kapag hiniling ni {Name} |
| Buod sa Umaga | `buod-sa-umaga/` | Maikling plano ng araw, kapag hiniling o tuwing araw ng trabaho |
| Import | `import/` | Nagpapasok ng mga note mula sa ibang apps, na may planong inaaprubahan muna ni {Name} |
| Paghahanda sa Meeting | `paghahanda-sa-meeting/` | Maikling buod bago ang isang call, mula sa mga note ng utak |
| Mga Tool sa Pag-iisip | `pag-iisip/` | Kontrahin ang isang idea, maghanap ng pattern, maghanap ng mga note na nagkakasalungat |
| Konektadong Apps | `konektadong-apps/` | Kung aling apps ang binabasa ng utak, at ang mga patakaran para sa mga ito |
| No AI Slop | `no-ai-slop/` | Ang Suri sa Pagsulat: inaayos ang sulat para tunog-tao, o itinuturo ang mga pattern ng AI (gawa ni Peter Yang, MIT License, hindi kailanman ine-edit) |

## Mga patakaran

- Isang folder bawat skill, ang pangalan ay kebab-case.
- Kapag may bagong skill na idinagdag, magdagdag ng row sa table sa itaas.
- Para magdagdag ng skill o magkonekta ng app, tingnan muna ang mga mungkahi ng Phygital Brain: ang `suggested-skills/README.md` at `suggested-apps/README.md` gamit ang Phygital Brain connector, o online sa https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Kung nandoon ito, sundin ang page nito. Kapag nagtanong si {Name} ng "ano ang puwede kong idagdag sa utak ko?", "what can I add to my brain?", ipakita ang dalawang listahan: una ang mga akma sa trabaho ni {Name}. Huwag isama ang mga app na nakakonekta na at ang mga skill na naka-install na.
- Hindi kailanman ine-edit ang `SKILL.md` na galing sa ibang tao. Para iangkop ang isang skill, magdagdag ng `notes.md` sa folder nito.
- Binabasa ng isang naka-schedule na task ang `taga-ayos-ng-utak/pang-araw-araw.md`. Baguhin lang ito para baguhin ang ginagawa ng araw-araw na takbo, at panatilihin itong simple: walang link, walang callout.
