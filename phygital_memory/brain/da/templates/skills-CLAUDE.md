<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Noter og præferencer til de skills, agenten bruger, plus Oprydningshjælperen.

## Opbygning

```
Skills/{skill-name}/
  {skill-name}.md eller SKILL.md  hvad skillen gør
  notes.md                        stemme og præferencer, som {Name} har til den her skill
  references/                     eksempler og længere materiale
```

## Installeret

| Skill | Mappe | Hvad den gør |
|---|---|---|
| Oprydningshjælper | `oprydningshjælper/` | Rydder op hver dag af sig selv, og laver et tjek, når {Name} beder om det |
| Morgenoverblik | `morgenoverblik/` | En kort plan for dagen, når man beder om det, eller hver arbejdsdag |
| Import | `import/` | Henter noter ind fra andre apps, med en plan, som {Name} godkender først |
| Mødeforberedelse | `mødeforberedelse/` | Et kort overblik før et opkald, ud fra hjernens noter |
| Tænkeværktøjer | `tænkeværktøjer/` | Udfordr en idé, find mønstre, find noter, der er uenige |
| Forbundne apps | `forbundne-apps/` | Hvilke apps hjernen læser fra, og reglerne for dem |
| No AI Slop | `no-ai-slop/` | Skrivetjekket: retter tekst, så den lyder menneskelig, eller markerer AI-mønstre (af Peter Yang, MIT-licens, bliver aldrig ændret) |

## Regler

- Én mappe pr. skill, navngivet i kebab-case (små bogstaver med bindestreger).
- Når der kommer en ny skill til, så tilføj en række i tabellen ovenfor.
- Før du tilføjer en skill eller forbinder en app, så tjek først Phygital Brains forslag: `suggested-skills/README.md` og `suggested-apps/README.md` via Phygital Brain-connectoren eller online på https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Hvis den er der, så følg dens side. Når {Name} spørger "hvad kan jeg tilføje til min hjerne?", "what can I add to my brain?", så vis begge lister. Sæt dem, der passer til det arbejde, {Name} laver, først, og udelad apps, der allerede er forbundet, og skills, der allerede er installeret.
- En `SKILL.md`, der kommer fra en anden, bliver aldrig ændret. Hvis du vil tilpasse en skill, så tilføj `noter.md` i dens mappe.
- `oprydningshjælper/daglig.md` bliver læst af en planlagt opgave. Ret den kun for at ændre, hvad den daglige kørsel gør, og hold den enkel: ingen links, ingen callouts.
