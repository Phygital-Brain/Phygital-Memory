Le savoir qui s'accumule avec le temps : décisions, recherches, candidatures et archives.

## Où ranger quoi

| Contenu | À ranger dans |
|---|---|
| Une décision avec ses raisons, ou l'étude d'une chose extérieure (app, site, formation, concurrent) | `décisions/YYYY-MM-DD-{title}.md` |
| Recherches (marché, tendances, options) | `recherches/{topic}.md` |
| Candidatures : emplois, bourses, prix, appels à projets (créé à la première utilisation) | `candidatures/{name}/` |
| Fiches concurrents (créé à la première utilisation) | `concurrents/{name}.md` |
| Argent : factures, impôts, paiements. Privé | `finances/` |
| Décisions archivées | `archives/décisions/` |
| Recherches terminées ou dépassées | `archives/recherches/` |
| Projets terminés | `archives/{name}/` |
| Notes de réunion | `décisions/` si une décision en est sortie, sinon la note `Journal/` de ce jour-là. Proposez un dossier réunions seulement quand il y en a beaucoup. |

## Bloc d'infos (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type` : `decision`, `research`, `application`, `competitor`.
- `date` : la date à laquelle la note a été écrite.
- `status` : voir plus bas pour les décisions et les candidatures. Pour tout le reste : `active` ou `closed`.
- `tags` : le type, puis le sujet.
- Facultatif : `project`, `deadline`, `description` (une phrase, entre guillemets droits, en dernière ligne).

## Notes de décision

Toujours avec le pourquoi : qui était impliqué, ce qui a déclenché la décision, quel compromis a été fait. Utilisez `> [!important]` pour la décision elle-même et `> [!warning]` pour les risques connus.

Les décisions ont aussi un `updated:` juste après `date:`. `date` est la date de création, `updated` la dernière fois que la décision a été revue ou modifiée.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status` : `open` (encore en réflexion ou en cours), `waiting` (on attend quelqu'un d'autre), `paused`, `closed`.
- Une décision dont le `updated` date de plus de 30 jours est à revoir. Le Gardien du cerveau la signale jusqu'à ce que {Name} la garde, la clôture ou l'archive (chacun de ces choix met `updated` à la date du jour).
- Une décision va dans `archives/décisions/` seulement quand {Name} le dit.

## Candidatures

Un dossier par candidature : `candidatures/{name}/`, avec un `README.md` qui contient la date limite, le lien, le statut et ce qui a été envoyé. Les autres fichiers (réponses, lettre de motivation) sont à côté.

- `status` : `draft`, `submitted`, `accepted`, `rejected` ou `withdrawn`.
- Gardez les réponses en Markdown. Les gros PDF et les présentations restent en dehors du cerveau : résumez-les dans une note.

## Règles

- Les recherches sont neutres par défaut (règle 23 du fichier racine).
- Déplacez les recherches dépassées dans `archives/recherches/` au lieu de les supprimer.
- `finances/` est privé et listé dans `.claudeignore`. Ouvrez-le seulement quand {Name} demande un fichier précis (règle 8 du fichier racine).
