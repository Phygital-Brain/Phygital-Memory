---
type: skill
status: active
tags: [morning-brief, planning]
---

Un petit plan pour la journée. Deux modes : **Point** (à la demande) et **Programmé** (chaque jour travaillé).

## Point

Déclencheur : « point du matin », "morning brief", ou l'équivalent en {Language}.

1. Lisez `Journal/tâches.md`, la dernière note du jour, la partie « Où on en est et prochaine étape » de chaque projet en `status: active`, et les décisions en statut `open` ou `waiting`.
2. Si un agenda est connecté, lisez les événements du jour.
3. Répondez en 6 lignes courtes au maximum :
   - Les 3 choses les plus importantes du jour, chacune avec un `[[lien]]` vers sa note.
   - Ce que {Name} attend des autres.
   - Une décision à prendre, s'il y en a une.
   - Les événements du jour, si un agenda est connecté.
4. N'écrivez aucun fichier. Si {Name} répond avec une nouvelle info, enregistrez-la selon la règle 9 du fichier racine.

## Programmé

Déclencheur : « programme mon point du matin », "set up my morning brief", ou l'équivalent en {Language}.

1. Demandez l'heure (choix cliquables : 7:00, 8:00, 9:00, 10:00), pour les jours travaillés de {Name}. Ne posez pas la question si la configuration a déjà fixé l'heure.
2. Créez une tâche programmée dans l'app de l'agent, qui tourne sur ce dossier, avec ce prompt :

   > Ouvre le dossier de mon second cerveau. Lis `Compétences/point-du-matin/point-du-matin.md` et fais-moi mon point du matin.

3. Si les tâches programmées ne sont pas disponibles, dites à {Name} de dire « point du matin » au début de sa journée.
