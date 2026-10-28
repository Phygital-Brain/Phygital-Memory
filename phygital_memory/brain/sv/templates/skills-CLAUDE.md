<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Anteckningar och önskemål för de skills som agenten använder, plus Städhjälpen.

## Struktur

```
Skills/{skill-name}/
  {skill-name}.md eller SKILL.md   vad skillen gör
  notes.md                         röst och önskemål från {Name} för den här skillen
  references/                      exempel och längre material
```

## Installerade

| Skill | Mapp | Vad den gör |
|---|---|---|
| Städhjälpen | `städhjälpen/` | Städar varje dag av sig själv, och gör en hälsokoll när {Name} ber om det |
| Morgonöversikt | `morgonöversikt/` | En kort plan för dagen, på begäran eller varje arbetsdag |
| Import | `import/` | Hämtar in anteckningar från andra appar, med en plan som {Name} godkänner först |
| Mötesförberedelse | `mötesförberedelse/` | En kort sammanfattning inför ett samtal, utifrån hjärnans anteckningar |
| Tankeverktyg | `tankeverktyg/` | Utmana en idé, hitta mönster, hitta anteckningar som säger emot varandra |
| Anslutna appar | `anslutna-appar/` | Vilka appar hjärnan läser från, och reglerna för dem |
| No AI Slop | `no-ai-slop/` | Textkollen: redigerar text så att den låter mänsklig, eller flaggar AI-mönster (av Peter Yang, MIT-licens, redigeras aldrig) |

## Regler

- En mapp per skill, namngiven i kebab-case.
- När en ny skill läggs till, lägg till en rad i tabellen ovan.
- För att lägga till en skill eller ansluta en app, kolla först förslagen från Phygital Brain: `suggested-skills/README.md` och `suggested-apps/README.md` via connectorn för Phygital Brain, eller online på https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Om det finns där, följ sidan för det. När {Name} frågar "vad kan jag lägga till i min hjärna?", "what can I add to my brain?", visa båda listorna, först det som passar arbetet som {Name} gör, och hoppa över appar som redan är anslutna och skills som redan är installerade.
- En `SKILL.md` som kommer från någon annan redigeras aldrig. För att anpassa en skill, lägg till `anteckningar.md` i dess mapp.
- `städhjälpen/daglig.md` läses av en schemalagd uppgift. Ändra den bara för att ändra vad den dagliga körningen gör, och håll den enkel: inga länkar, inga callouts.
