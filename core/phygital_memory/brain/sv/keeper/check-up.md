---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Städhjälpens hälsokoll: en ordentlig genomgång av hela hjärnan, när {Name} ber om det. Inget ändras förrän {Name} säger ja. (Den dagliga städningen finns i `daglig.md`.)

Utlösare: "gör en hälsokoll av min hjärna", "check up my brain", "städa min hjärna", "tidy my brain", "hälsokoll", "brain check-up" eller samma sak på {Language}.

## 1. Titta (ändra inget än)

Sök igenom hela mappen och lista problemen i de här grupperna:

- **Trasiga länkar**: `[[länkar]]` som pekar på anteckningar som inte finns. Laga dem aldrig genom att skapa en tom anteckning: den riktiga anteckningen kanske fortfarande synkas (huvudregel 28).
- **Föräldralösa anteckningar**: anteckningar som ingen annan anteckning länkar till.
- **Tomma eller nästan tomma anteckningar**, och platshållare som blivit kvar (`[name]`, `TBD`).
- **Fel ställe**: filer direkt i huvudmappen (utom `CLAUDE.md`, `.claudeignore`, `.backups/` och en annan agents regelfil på en rad, som `AGENTS.md`), anteckningar som inte stämmer med mappens tabell "Var allt hamnar".
- **Inaktuella tabeller "Var allt hamnar"**: en `CLAUDE.md` listar filer eller mappar som inte finns, eller saknar sådana som finns (rader märkta "skapas första gången de behövs" är okej).
- **Infoblock**: saknas eller är ofullständiga, jämfört med mappens `CLAUDE.md`. Ingen `status:`, färre än 2 `tags:`, en projektanteckning utan `project:`, dagstaggar utanför den fasta listan.
- **Projekt som står still**: ingen uppdatering på 60 dagar eller mer. Föreslå en uppdatering av läget, `paused` eller arkivering.
- **Mål utan projekt**: mål i `Profil/mål.md` som inte har något aktivt projekt.
- **Beslut som behöver ses över**: `updated` för mer än 30 dagar sedan och status som inte är `closed`.
- **Gamla relationer**: `status: active` men `last-contact` för mer än 12 månader sedan. Föreslå `dormant`.
- **Gamla uppgifter**: öppna uppgifter i `Dagbok/uppgifter.md` som är äldre än 30 dagar.
- **Dubbletter**: samma fakta i mer än en anteckning, eller två anteckningar om samma person eller företag.
- **Inaktuellt läge**: sidor i `Profil` eller `Kontakter` där gamla uppdateringar gömmer det som gäller nu (huvudregel 17).
- **Regler som krockar**: regler i huvud-`CLAUDE.md` som säger emot varandra.
- **Integritet**: lösenord, nycklar eller privata nummer i vanliga anteckningar (huvudregel 25 och 26). Nämn anteckningen, aldrig själva uppgiften.
- **Text**: tankstreck och mönster från Textkollen i anteckningar.
- **Ny version**: jämför den här hjärnans version (första raden i huvud-`CLAUDE.md`) med den nyaste versionen av Phygital Brain. Om du kan surfa på webben är den nyaste den senaste releasen på https://github.com/Phygital-Brain/phygital-brain/releases/latest. Om du inte kan det, använd versionen av Phygital Brain som är installerad i din agent, om du kan se den. Om du inte kan avgöra det, hoppa över det här.

## 2. Rapport

En kort lista med enkla ord, grupperad som ovan. För varje problem: anteckningen, vad som är fel, rättelsen du föreslår. Lägg de enkla, säkra rättningarna först (tankstreck, taggar som saknas, rader i tabellerna "Var allt hamnar").

Om det finns en nyare version, börja rapporten med en rad. Om din agent redan har den: "Det finns en ny version av Phygital Brain. Säg 'Uppgradera min andra hjärna' för att se vad som är nytt." Om inte: "Det finns en ny version av Phygital Brain. Uppdatera den i din agent först, och säg sedan 'Uppgradera min andra hjärna'."

## 3. Rätta bara det som är godkänt

Före första rättningen: gör en säkerhetskopia av varje fil du kommer att ändra (Säkerhetskopior och ångra i huvud-`CLAUDE.md`).

Fråga (med klickbara val om det går): **Rätta allt som är säkert**, **En i taget**, **Bara rapporten**.

- Radera eller flytta aldrig något utan länkkontrollen och ett tydligt ja (huvudregel 21).
- Arkivera hellre än radera när du är osäker.
- Skriv en rad i dagens anteckning i `Dagbok/`: vad som kontrollerades och rättades.
