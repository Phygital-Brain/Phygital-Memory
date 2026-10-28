---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Check-up-ul Îngrijitorului creierului: o privire completă peste tot creierul, când o cere {Name}. Nu se schimbă nimic până nu spune {Name} da. (Curățenia de zi cu zi e în `runda-zilnică.md`.)

Când se folosește: "fă un check-up creierului meu", "check up my brain", "fă ordine în creierul meu", "tidy my brain", "check-up la creier", "brain check-up", sau același lucru în {Language}.

## 1. Uită-te (încă nu schimba nimic)

Caută în tot folderul și fă lista problemelor, pe grupele astea:

- **Linkuri stricate**: `[[linkuri]]` spre note care nu există. Nu le repara niciodată creând o notă goală: nota adevărată poate fi încă în sincronizare (regula principală 28).
- **Note orfane**: note spre care nu duce niciun link din altă notă.
- **Note goale sau aproape goale**, și locuri de completat rămase (`[name]`, `TBD`).
- **La locul greșit**: fișiere în rădăcina folderului (în afară de `CLAUDE.md`, `.claudeignore`, `.backups/` și fișierul de reguli de un rând al altui agent, cum e `AGENTS.md`), note care nu se potrivesc cu tabelul "unde merge fiecare lucru" din folderul lor.
- **Tabele "unde merge fiecare lucru" neactualizate**: un `CLAUDE.md` pomenește fișiere sau foldere care nu există, sau le lasă pe dinafară pe unele care există (rândurile marcate "se creează prima dată când e nevoie" sunt în regulă).
- **Blocuri de informații**: lipsă sau incomplete, față de `CLAUDE.md`-ul folderului. Fără `status:`, mai puțin de 2 `tags:`, o notă de proiect fără `project:`, etichete în notele zilei care nu sunt în lista fixă.
- **Proiecte uitate**: nicio actualizare de 60 de zile sau mai mult. Propune o actualizare a stadiului, `paused` sau arhivare.
- **Obiective rămase fără proiect**: obiective din `Profil/obiective.md` fără niciun proiect activ.
- **Decizii de revăzut**: `updated` acum mai mult de 30 de zile și stadiul nu e `closed`.
- **Relații vechi**: `status: active`, dar `last-contact` acum mai mult de 12 luni. Propune `dormant`.
- **Lucruri de făcut vechi**: lucruri deschise în `Jurnal/de-făcut.md`, mai vechi de 30 de zile.
- **Dubluri**: aceleași informații în mai multe note, sau două note pentru aceeași persoană sau firmă.
- **Adevăr învechit**: pagini din Profil sau din Contacte unde actualizările vechi îngroapă situația de acum (regula principală 17).
- **Reguli care se bat cap în cap**: reguli din `CLAUDE.md`-ul principal care se contrazic.
- **Date private**: parole, chei sau numere private lăsate în note obișnuite (regulile principale 25 și 26). Spune care e nota, niciodată valoarea.
- **Scris**: linii lungi (em dash) și tipare din Verificarea textelor în note.
- **Versiune nouă**: compară versiunea creierului ăstuia (primul rând din `CLAUDE.md`-ul principal) cu cea mai nouă versiune Phygital Brain. Dacă poți căuta pe web, cea mai nouă e ultima versiune publicată la https://github.com/Phygital-Brain/phygital-brain/releases/latest. Dacă nu poți, folosește versiunea de Phygital Brain instalată în agentul tău, dacă o vezi. Dacă nu-ți dai seama, sari peste pasul ăsta.

## 2. Raportul

O listă scurtă, în cuvinte simple, pe grupele de mai sus. Pentru fiecare problemă: nota, ce nu e în regulă, reparația pe care o propui. Pune întâi reparațiile simple și sigure (linii lungi, etichete lipsă, rânduri din tabelele "unde merge fiecare lucru").

Dacă a apărut o versiune nouă, începe raportul cu un rând. Dacă agentul tău o are deja: "A apărut o versiune nouă de Phygital Brain. Spune «Actualizează-mi al doilea creier» ('Upgrade my second brain') ca să vezi ce e nou." Dacă nu: "A apărut o versiune nouă de Phygital Brain. Actualizeaz-o întâi în agentul tău, apoi spune «Actualizează-mi al doilea creier» ('Upgrade my second brain')."

## 3. Repară doar ce e aprobat

Înainte de prima reparație, fă o copie de siguranță pentru fiecare fișier pe care îl vei schimba (Copii de siguranță și anulare, în `CLAUDE.md`-ul principal).

Întreabă (dacă se poate, cu opțiuni pe care le alege dintr-un clic): **Repară tot ce e sigur**, **Una câte una**, **Doar raportul**.

- Nu șterge și nu muta niciodată nimic fără verificarea linkurilor și un da clar (regula principală 21).
- Când ai dubii, arhivează în loc să ștergi.
- Scrie un rând în nota de azi din `Jurnal/`: ce s-a verificat și ce s-a reparat.
