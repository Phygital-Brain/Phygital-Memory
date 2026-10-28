<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Notater og ønsker for ferdighetene agenten bruker, pluss Ryddehjelperen.

## Oppbygning

```
Ferdigheter/{skill-name}/
  {skill-name}.md eller SKILL.md   hva ferdigheten gjør
  notes.md                         stemmen og ønskene til {Name} for denne ferdigheten
  references/                      eksempler og lengre stoff
```

## Installert

| Ferdighet | Mappe | Hva den gjør |
|---|---|---|
| Ryddehjelperen | `ryddehjelper/` | Rydder litt hver dag av seg selv, og tar en helsesjekk når {Name} ber om det |
| Morgenoversikt | `morgenoversikt/` | En kort plan for dagen, på forespørsel eller hver arbeidsdag |
| Import | `import/` | Henter inn notater fra andre apper, med en plan {Name} godkjenner først |
| Møteforberedelse | `møteforberedelse/` | En kort oppsummering før en samtale, ut fra notatene i hjernen |
| Tenkeverktøy | `tenkeverktøy/` | Utfordrer en idé, finner mønstre, finner notater som sier hverandre imot |
| Tilkoblede apper | `tilkoblede-apper/` | Hvilke apper hjernen leser fra, og reglene for dem |
| No AI Slop | `no-ai-slop/` | Skrivesjekken: retter tekst så den høres menneskelig ut, eller peker ut KI-mønstre (av Peter Yang, MIT-lisens, redigeres aldri) |

## Regler

- Én mappe per ferdighet, med navn i kebab-case (små bokstaver og bindestreker).
- Når en ny ferdighet legges til, legg til en rad i tabellen over.
- For å legge til en ferdighet eller koble til en app, sjekk først forslagene fra Phygital Brain: `suggested-skills/README.md` og `suggested-apps/README.md` gjennom koblingen til Phygital Brain, eller på nett på https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Hvis det er der, følg siden for det. Når {Name} spør «hva kan jeg legge til i hjernen min?», «what can I add to my brain?», vis begge listene, først det som passer til arbeidet til {Name}, og hopp over apper som allerede er koblet til og ferdigheter som allerede er installert.
- En `SKILL.md` som kommer fra noen andre, redigeres aldri. For å tilpasse en ferdighet, legg til `notater.md` i mappen dens.
- `ryddehjelper/daglig.md` leses av en planlagt oppgave. Endre den bare for å endre hva den daglige kjøringen gjør, og hold den enkel: ingen lenker, ingen callouts.
