---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Oprydningshjælperens tjek: et grundigt kig på hele hjernen, når {Name} beder om det. Intet bliver ændret, før {Name} siger ja. (Den daglige oprydning står i `daglig.md`.)

Udløser: "tjek min hjerne", "check up my brain", "ryd op i min hjerne", "tidy my brain", "hjernetjek", "brain check-up" eller det samme på {Language}.

## 1. Kig (lav ikke noget om endnu)

Søg i hele mappen, og list problemerne i de her grupper:

- **Døde links**: `[[links]]`, der peger på noter, som ikke findes. Ret dem aldrig ved at oprette en tom note: den rigtige note er måske stadig ved at blive synkroniseret (hovedregel 28).
- **Forældreløse noter**: noter, som ingen anden note linker til.
- **Tomme eller næsten tomme noter**, og pladsholdere, der er blevet stående (`[name]`, `TBD`).
- **Forkert sted**: filer i roden af mappen (undtagen `CLAUDE.md`, `.claudeignore`, `.backups/` og en anden agents regelfil på én linje, som `AGENTS.md`), noter, der ikke passer til deres mappes tabel over, hvor hvad hører hjemme.
- **Forældede tabeller**: en `CLAUDE.md` nævner filer eller mapper, der ikke findes, eller mangler nogle, der gør (rækker markeret "oprettes første gang, den skal bruges" er fine).
- **Infoblokke**: mangler eller er ufuldstændige i forhold til mappens `CLAUDE.md`. Ingen `status:`, færre end 2 `tags:`, en projektnote uden `project:`, dags-tags uden for den faste liste.
- **Projekter, der står stille**: ingen opdatering i 60 dage eller mere. Foreslå en opdatering af status, `paused` eller arkivering.
- **Mål uden projekt**: mål i `Profil/mål.md` uden et aktivt projekt.
- **Beslutninger, der skal gennemgås**: `updated` for mere end 30 dage siden, og status er ikke `closed`.
- **Gamle forbindelser**: `status: active`, men `last-contact` for mere end 12 måneder siden. Foreslå `dormant`.
- **Gamle opgaver**: åbne opgaver i `Dagbog/opgaver.md`, der er mere end 30 dage gamle.
- **Dubletter**: de samme fakta i mere end én note, eller to noter om den samme person eller det samme firma.
- **Forældet status**: sider i Profil eller Kontakter, hvor gamle opdateringer begraver det, der gælder nu (hovedregel 17).
- **Regler, der strider mod hinanden**: regler i hoved-`CLAUDE.md`, der siger hinanden imod.
- **Privatliv**: adgangskoder, nøgler eller private numre i almindelige noter (hovedregel 25 og 26). Nævn noten, aldrig værdien.
- **Skrivning**: tankestreger og Skrivetjek-mønstre i noterne.
- **Ny version**: sammenlign hjernens version (første linje i hoved-`CLAUDE.md`) med den nyeste udgave af Phygital Brain. Hvis du kan gå på nettet, er den nyeste den seneste udgivelse på https://github.com/Phygital-Brain/phygital-brain/releases/latest. Hvis du ikke kan, så brug den version af Phygital Brain, der er installeret i din agent, hvis du kan se den. Hvis du ikke kan se det, så spring det over.

## 2. Rapport

En kort liste med almindelige ord, delt op i grupperne ovenfor. For hvert problem: noten, hvad der er galt, og den rettelse, du foreslår. Sæt de enkle, sikre rettelser først (tankestreger, manglende tags, rækker i tabellerne).

Hvis der er kommet en nyere version, så start rapporten med én linje. Hvis din agent allerede har den: "Der er kommet en ny version af Phygital Brain. Sig 'opgradér min anden hjerne' ('Upgrade my second brain') for at se, hvad der er nyt." Hvis ikke: "Der er kommet en ny version af Phygital Brain. Opdater den i din agent først, og sig så 'opgradér min anden hjerne'."

## 3. Ret kun det, der er godkendt

Før den første rettelse tager du en sikkerhedskopi af hver fil, du vil ændre (Sikkerhedskopier og fortryd i hoved-`CLAUDE.md`).

Spørg (med knapper, når det er muligt): **Ret alle de sikre**, **Én ad gangen**, **Kun rapporten**.

- Slet eller flyt aldrig noget uden linktjekket og et klart ja (hovedregel 21).
- Arkivér hellere end at slette, når du er i tvivl.
- Skriv én linje i dagens note i `Dagbog/`: hvad der blev tjekket og rettet.
