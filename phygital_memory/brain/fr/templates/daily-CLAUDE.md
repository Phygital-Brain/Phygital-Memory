<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Le journal quotidien de {Name}. Un fichier par jour : `YYYY-MM-DD.md`. Les tâches en cours sont dans `tâches.md`.

## Bloc d'infos (frontmatter)

Chaque note du jour commence par ce bloc. Sans exception.

```yaml
---
type: daily
date: 2026-10-13
day: Tuesday
week: W42
month: October
status: active
tags: [daily, meeting]
---
```

- `type` : toujours `daily`.
- `date` : la date de la note, `YYYY-MM-DD`.
- `day` : le jour de la semaine, en anglais (Monday, Tuesday...).
- `week` : le numéro de semaine ISO, `WNN`.
- `month` : le mois, en anglais (January, February...).
- `status` : `active` tant que la journée est ouverte, `completed` dès qu'elle date de 2 jours ou plus.
- `tags` : toujours `daily`, plus ceux de cette liste fixe qui correspondent à ce qui s'est passé ce jour-là. N'inventez jamais d'autres tags.
  - `problem` : quelque chose a cassé ou s'est mal passé
  - `clients` : travail ou échange avec un client
  - `meeting` : un appel ou une réunion
  - `money` : factures, paiements, impôts, placements
  - `research` : recherches faites ou résultats
  - `decision` : {Name} a pris une décision
  - `travel` : {Name} était en déplacement
  - `personal` : santé, vie perso, tout ce qui sort du travail

## Règles

- Les dates suivent la règle 30 du fichier racine (d'abord le fuseau horaire de l'ordinateur, sinon {Time zone}).
- Celui qui crée la note (votre agent ou une tâche programmée) écrit d'abord le bloc d'infos. Une note qui n'en a pas le reçoit en haut la prochaine fois qu'elle est modifiée.
- Pas de titre `# YYYY-MM-DD`. Le nom du fichier sert de titre.
- La note du jour montre l'état actuel de la journée : un seul document bien rangé par jour, avec des sections mises à jour sur place, jamais une pile d'entrées répétées.
- Journal de session : un titre en gras plus 1 ou 2 phrases, les personnes et les projets en `[[wikilinks]]`, les détails dans la note liée.
- La note d'aujourd'hui ne contient que l'activité d'aujourd'hui. Les tâches en cours des jours précédents vont dans `tâches.md`. Ne les recopiez jamais d'un jour à l'autre.
- Quand vous créez la note d'aujourd'hui, regardez les notes d'il y a 2, 3 et 4 jours. Celles qui sont encore en `status: active` passent en `completed`, et reçoivent les tags de la liste fixe pour ce qui s'est clairement passé ce jour-là. Ne remontez pas plus loin.

## tasks.md

Les tâches en cours qui ne font partie d'aucun projet. Les tâches d'un projet vont dans le README de ce projet (« Où on en est et prochaine étape »). Créé à la première utilisation :

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## En cours

- [ ] 2026-10-13 : Envoyer la facture à [[Léa]]

## Fait

- [x] 2026-10-12 : Prendre rendez-vous chez le dentiste (fait le 2026-10-13)
```

- Les tâches en cours les plus récentes en haut, avec leur date d'ajout.
- Quand une tâche est faite, cochez-la, ajoutez la date où elle a été faite, et déplacez-la sous `## Fait`.
- Les tâches faites depuis plus de 30 jours peuvent être supprimées (demandez d'abord, règle 9 du fichier racine).
