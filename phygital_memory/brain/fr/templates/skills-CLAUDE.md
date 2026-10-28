<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Les notes et préférences pour les compétences qu'utilise l'agent, plus le Gardien du cerveau.

## Structure

```
Compétences/{skill-name}/
  {skill-name}.md ou SKILL.md   ce que fait la compétence
  notes.md                      le style et les préférences de {Name} pour cette compétence
  references/                   exemples et documents plus longs
```

## Installées

| Compétence | Dossier | Ce qu'elle fait |
|---|---|---|
| Gardien du cerveau | `gardien-du-cerveau/` | Range le cerveau chaque jour tout seul, et fait un bilan quand {Name} le demande |
| Point du matin | `point-du-matin/` | Un petit plan de la journée, à la demande ou chaque jour travaillé |
| Import | `import/` | Importe des notes venant d'autres apps, avec un plan que {Name} valide d'abord |
| Préparation de réunion | `préparation-réunion/` | Un petit brief avant un appel, à partir des notes du cerveau |
| Outils de réflexion | `réflexion/` | Challenger une idée, repérer des tendances, trouver les notes qui se contredisent |
| Apps connectées | `apps-connectées/` | Les apps que le cerveau consulte, et les règles qui vont avec |
| No AI Slop | `no-ai-slop/` | Le Contrôle d'écriture : retouche un texte pour qu'il sonne humain, ou signale les tics d'IA (par Peter Yang, licence MIT, jamais modifié) |

## Règles

- Un dossier par compétence, nommé en kebab-case (minuscules et tirets).
- Quand une nouvelle compétence est ajoutée, ajoutez une ligne au tableau ci-dessus.
- Pour ajouter une compétence ou connecter une app, regardez d'abord les suggestions de Phygital Brain : `suggested-skills/README.md` et `suggested-apps/README.md` via le connecteur Phygital Brain, ou en ligne sur https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Si l'élément y est, suivez sa page. Quand {Name} demande « qu'est-ce que je peux ajouter à mon cerveau ? », "what can I add to my brain?", montrez les deux listes, d'abord ce qui correspond au travail de {Name}, sans les apps déjà connectées ni les compétences déjà installées.
- Un `SKILL.md` venu de quelqu'un d'autre n'est jamais modifié. Pour adapter une compétence, ajoutez un `notes.md` dans son dossier.
- `gardien-du-cerveau/quotidien.md` est lu par une tâche programmée. Modifiez-le seulement pour changer ce que fait le passage quotidien, et gardez-le simple : pas de liens, pas d'encadrés.
