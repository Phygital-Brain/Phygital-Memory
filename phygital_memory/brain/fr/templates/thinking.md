---
type: skill
status: active
tags: [thinking, review]
---

Outils de réflexion : votre agent se sert des propres notes de {Name} pour mettre une idée à l'épreuve, repérer des tendances et trouver les notes qui se contredisent. Aucun de ces outils ne modifie une note, sauf si {Name} le demande.

## Challenge mon idée

Déclencheur : « challenge mon idée », « contredis-moi là-dessus », « qu'est-ce qui m'échappe ? », "challenge my idea", "push back on this", "what am I missing?", ou l'équivalent en {Language}.

1. Reformulez l'idée en une ligne, et posez une seule question si elle n'est pas claire.
2. Cherchez des éléments dans le cerveau : les décisions passées dans `Mémoire/décisions/` (avec leurs raisons et leurs résultats), les recherches dans `Mémoire/recherches/`, ce que les clients et les partenaires ont dit dans `Relations/`, les objectifs dans `Profil/objectifs.md`, les difficultés dans `Profil/difficultés.md`, et les notes du jour des 60 derniers jours.
3. Répondez en trois petites parties :
   - **Pour :** jusqu'à 3 points tirés des notes, chacun avec son `[[lien]]`.
   - **Contre :** jusqu'à 3 points tirés des notes, chacun avec son `[[lien]]`. Ajoutez une décision passée qui est allée dans l'autre sens, s'il y en a une.
   - **Questions à régler d'abord :** jusqu'à 3.
4. Utilisez seulement ce qu'il y a dans les notes, plus un raisonnement simple. Dites « rien dans vos notes » quand il n'y a rien. Ne décidez pas à la place de {Name}.
5. Si {Name} prend une décision, proposez d'écrire une note de décision.

## Quelles tendances tu vois ?

Déclencheur : « quelles tendances tu vois ? », « qu'est-ce qui revient souvent ? », « passe en revue mon dernier mois », "what patterns do you see?", "what keeps coming up?", "review my last month", ou l'équivalent en {Language}.

1. Lisez les notes du jour des 30 derniers jours (ou de la période que {Name} indique), et `Journal/tâches.md`.
2. Comptez ce qui se répète : personnes, projets, tags (`problem`, `money`, `meeting`...), blocages, tâches qui glissent d'un jour à l'autre, et tout ce que {Name} a mentionné plus de trois fois.
3. Répondez avec 5 tendances au maximum, chacune avec le nombre de fois où elle est apparue, deux ou trois `[[liens]]` vers les jours concernés, et une question simple (« Trois appels avec l'imprimeur ont été repoussés. Vous voulez un créneau fixe pour eux ? »).
4. Notez ce qui n'est pas apparu mais qui compte : les objectifs de `Profil/objectifs.md` qui n'apparaissent nulle part sur la période.

## Trouver les contradictions

Déclencheur : « trouve les contradictions », « qu'est-ce qui se contredit dans mon cerveau ? », "find contradictions", "what disagrees in my brain?", ou l'équivalent en {Language}.

1. Comparez les faits qui devraient concorder : les pages Profil face aux décisions plus récentes, les prix dans `Profil/offres.md` face aux devis récents dans les notes du jour et les projets, les infos sur les personnes d'une note à l'autre, le statut des projets face aux dernières mentions dans les notes du jour.
2. Pour chaque contradiction : les deux notes en `[[liens]]`, les deux lignes qui ne concordent pas, et celle qui semble la plus récente.
3. Proposez une correction pour chacune, et demandez (avec des choix cliquables si possible) : `Les corriger une par une` · `Juste la liste`. Les corrections suivent la règle 9 du fichier racine, avec une sauvegarde d'abord.
