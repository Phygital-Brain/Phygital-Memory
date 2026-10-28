<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Note și preferințe pentru abilitățile pe care le folosește agentul, plus Îngrijitorul creierului.

## Structură

```
Abilități/{skill-name}/
  {skill-name}.md sau SKILL.md   ce face abilitatea
  notes.md                       stilul și preferințele pe care le are {Name} pentru abilitatea asta
  references/                    exemple și materiale mai lungi
```

## Instalate

| Abilitate | Folder | Ce face |
|---|---|---|
| Îngrijitorul creierului | `îngrijitorul-creierului/` | Face ordine singur în fiecare zi și un check-up când îl cere {Name} |
| Rezumatul de dimineață | `rezumatul-de-dimineață/` | Un plan scurt al zilei, la cerere sau în fiecare zi lucrătoare |
| Import | `import/` | Aduce note din alte aplicații, cu un plan pe care {Name} îl aprobă mai întâi |
| Pregătirea pentru întâlniri | `pregătire-întâlniri/` | Un rezumat scurt înainte de un apel, din notele creierului |
| Instrumente de gândire | `gândire/` | Pune o idee la încercare, găsește tipare, găsește note care se contrazic |
| Aplicații conectate | `aplicații-conectate/` | Din ce aplicații citește creierul și regulile pentru ele |
| No AI Slop | `no-ai-slop/` | Verificarea textelor: corectează textele ca să sune omenește sau semnalează tiparele de inteligență artificială (de Peter Yang, licență MIT, nemodificată niciodată) |

## Reguli

- Un folder pentru fiecare abilitate, cu numele în kebab-case (litere mici, cu cratime).
- Când se adaugă o abilitate nouă, adaugă un rând în tabelul de mai sus.
- Ca să adaugi o abilitate sau să conectezi o aplicație, uită-te mai întâi la sugestiile Phygital Brain: `suggested-skills/README.md` și `suggested-apps/README.md` prin conectorul Phygital Brain, sau online la https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Dacă e acolo, urmează pagina respectivă. Când {Name} întreabă "ce pot adăuga în creierul meu?", "what can I add to my brain?", arată ambele liste, întâi ce se potrivește cu munca pe care o face {Name}, și lasă deoparte aplicațiile deja conectate și abilitățile deja instalate.
- Un `SKILL.md` venit de la altcineva nu se modifică niciodată. Ca să adaptezi o abilitate, adaugă `notițe.md` în folderul ei.
- `îngrijitorul-creierului/runda-zilnică.md` e citit de o activitate programată. Schimbă-l doar ca să schimbi ce face runda zilnică, și ține-l simplu: fără linkuri, fără casete.
