<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Notities en voorkeuren voor de skills die de agent gebruikt, plus de Opruimhulp.

## Opbouw

```
Skills/{skill-name}/
  {skill-name}.md of SKILL.md   wat de skill doet
  notes.md                      de stem en voorkeuren van {Name} voor deze skill
  references/                   voorbeelden en langer materiaal
```

## Geïnstalleerd

| Skill | Map | Wat het doet |
|---|---|---|
| Opruimhulp | `opruimhulp/` | Ruimt elke dag vanzelf op, en doet een check-up als {Name} erom vraagt |
| Ochtendoverzicht | `ochtendoverzicht/` | Een kort plan voor de dag, op verzoek of elke werkdag |
| Import | `import/` | Haalt notities uit andere apps binnen, met een plan dat {Name} eerst goedkeurt |
| Meetingvoorbereiding | `meetingvoorbereiding/` | Een korte voorbereiding voor een call, uit de notities van het brein |
| Denktools | `denktools/` | Een idee op de proef stellen, patronen vinden, notities vinden die elkaar tegenspreken |
| Gekoppelde apps | `gekoppelde-apps/` | Uit welke apps het brein leest, en de regels daarvoor |
| No AI Slop | `no-ai-slop/` | De Schrijfcheck: past tekst aan zodat hij menselijk klinkt, of wijst AI-patronen aan (van Peter Yang, MIT-licentie, nooit bewerkt) |

## Regels

- Eén map per skill, in kebab-case (kleine letters met koppeltekens).
- Komt er een nieuwe skill bij, voeg dan een rij toe aan de tabel hierboven.
- Wil je een skill toevoegen of een app koppelen, kijk dan eerst bij de suggesties van Phygital Brain: `suggested-skills/README.md` en `suggested-apps/README.md` via de connector van Phygital Brain, of online op https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Staat het daar, volg dan de pagina ervan. Als {Name} vraagt "wat kan ik aan mijn brein toevoegen?", "what can I add to my brain?", laat dan beide lijsten zien, eerst wat past bij het werk van {Name}, en laat apps die al gekoppeld zijn en skills die al geïnstalleerd zijn weg.
- Een `SKILL.md` die van iemand anders komt, wordt nooit bewerkt. Wil je een skill aanpassen, zet dan een `notities.md` in de map.
- `opruimhulp/dagelijks.md` wordt gelezen door een geplande taak. Pas het alleen aan als de dagelijkse ronde iets anders moet doen, en houd het eenvoudig: geen links, geen callouts.
