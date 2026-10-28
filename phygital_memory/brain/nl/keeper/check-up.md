---
type: skill
status: active
tags: [brain-keeper, check-up]
---

De check-up van de Opruimhulp: het hele brein grondig bekijken, als {Name} erom vraagt. Er verandert niets tot {Name} ja zegt. (Het dagelijkse opruimen staat in `dagelijks.md`.)

Wanneer: "doe een check-up van mijn brein", "check up my brain", "ruim mijn brein op", "tidy my brain", "brein-check-up", "brain check-up" of hetzelfde in het {Language}.

## 1. Kijken (nog niets veranderen)

Doorzoek de hele map en zet de problemen in deze groepen:

- **Kapotte links**: `[[links]]` naar notities die niet bestaan. Repareer ze nooit door een lege notitie te maken: de echte notitie kan nog aan het synchroniseren zijn (hoofdregel 28).
- **Losse notities**: notities waar geen enkele andere notitie naar linkt.
- **Lege of bijna lege notities**, en invulplekken die zijn blijven staan (`[name]`, `TBD`).
- **Verkeerde plek**: bestanden in de hoofdmap (behalve `CLAUDE.md`, `.claudeignore`, `.backups/` en het regelbestand van een andere agent dat maar één regel heeft, zoals `AGENTS.md`), notities die niet passen bij de tabel "Waar wat hoort" van hun map.
- **Verouderde tabellen "Waar wat hoort"**: een `CLAUDE.md` noemt bestanden of mappen die niet bestaan, of mist bestanden of mappen die er wel zijn (rijen met "wordt gemaakt bij het eerste gebruik" zijn in orde).
- **Infoblokken**: ontbrekend of onvolledig, vergeleken met de `CLAUDE.md` van de map. Geen `status:`, minder dan 2 `tags:`, een projectnotitie zonder `project:`, tags in dagnotities die niet in de vaste lijst staan.
- **Stilgevallen projecten**: 60+ dagen geen update. Stel een update van de status voor, `paused`, of archiveren.
- **Doelen zonder project**: doelen in `Profiel/doelen.md` zonder actief project.
- **Beslissingen die nagekeken moeten worden**: `updated` meer dan 30 dagen geleden en status niet `closed`.
- **Oude contacten**: `status: active` maar `last-contact` meer dan 12 maanden geleden. Stel `dormant` voor.
- **Oude taken**: open taken in `Dagboek/taken.md` die ouder zijn dan 30 dagen.
- **Dubbel**: dezelfde feiten in meer dan één notitie, of twee notities voor dezelfde persoon of hetzelfde bedrijf.
- **Verouderde stand**: pagina's in het profiel of bij de contacten waar oude updates de huidige stand ondersneeuwen (hoofdregel 17).
- **Botsende regels**: regels in de hoofd-`CLAUDE.md` die elkaar tegenspreken.
- **Privacy**: wachtwoorden, sleutels of privénummers in gewone notities (hoofdregels 25 en 26). Noem de notitie, nooit de waarde.
- **Schrijven**: gedachtestreepjes en patronen uit de Schrijfcheck in notities.
- **Nieuwe versie**: vergelijk de versie van dit brein (de eerste regel van de hoofd-`CLAUDE.md`) met de nieuwste Phygital Brain. Kun je op het web kijken, dan is de nieuwste de laatste release op https://github.com/Phygital-Brain/phygital-brain/releases/latest. Kan dat niet, gebruik dan de versie van Phygital Brain die in je agent geïnstalleerd is, als je die kunt zien. Kun je het niet zien, sla dit dan over.

## 2. Verslag

Een korte lijst in gewone woorden, in de groepen hierboven. Voor elk probleem: de notitie, wat er mis is, de oplossing die je voorstelt. Zet de simpele, veilige reparaties bovenaan (gedachtestreepjes, ontbrekende tags, rijen in de tabellen "Waar wat hoort").

Is er een nieuwere versie, begin het verslag dan met één regel. Heeft je agent hem al: "Er is een nieuwe versie van Phygital Brain. Zeg 'Werk mijn tweede brein bij' of 'Upgrade my second brain' om te zien wat er nieuw is." Zo niet: "Er is een nieuwe versie van Phygital Brain. Werk hem eerst bij in je agent, en zeg dan 'Werk mijn tweede brein bij' of 'Upgrade my second brain'."

## 3. Repareer alleen wat is goedgekeurd

Maak voor de eerste reparatie een back-up van elk bestand dat je gaat veranderen (Back-ups en ongedaan maken in de hoofd-`CLAUDE.md`).

Vraag (met klikbare keuzes als dat kan): **Alle veilige repareren**, **Een voor een**, **Alleen het verslag**.

- Verwijder of verplaats nooit iets zonder de linkcontrole en een duidelijk ja (hoofdregel 21).
- Twijfel je, archiveer dan in plaats van te verwijderen.
- Zet één regel in de `Dagboek/`-notitie van vandaag: wat er gecontroleerd en gerepareerd is.
