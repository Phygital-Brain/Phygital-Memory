<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Clients/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Toutes les personnes avec qui {Name} travaille : une note par personne ou par organisation.

## Sous-dossiers

| Dossier | Qui va dedans |
|---|---|
| `Clients/` | Les personnes et les entreprises pour qui {Name} travaille |
| `Collaborateurs/` | Partenaires créatifs, échange réciproque, sans argent en jeu |
| `Équipe/` | Les personnes qui travaillent avec ou pour {Name} (freelances, assistants) |
| `Partenaires/` | Les organisations avec lesquelles {Name} se fait connaître (presse, lieux, plateformes) |

## Où va un nouveau prospect

- Un premier contact, sans vrai brief pour l'instant : une ligne sous `## Nouveaux` dans `Clients/_Prospects.md` (créé à la première utilisation).
- Une réponse du genre « peut-être plus tard » : une ligne sous `## À relancer` dans `Clients/_Prospects.md`.
- Un vrai brief, un appel ou un devis en cours : une note client `Clients/{client-name}.md` avec `status: prospect`.

Quand un prospect passe à l'étape suivante, déplacez-le à son nouvel endroit et retirez-le de l'ancien.

## Bloc d'infos (frontmatter)

Chaque note ici (sauf les fichiers `CLAUDE.md` et `_Prospects.md`) commence par :

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Une phrase simple sur qui ils sont et sur leur relation avec {Name}."
---
```

- `type` : `client`, `collaborator`, `team` ou `partner`.
- `status` : `active` (travail ou contact dans les 12 derniers mois), `prospect` (on discute, jamais travaillé ensemble), `dormant` (aucun contact depuis 12 mois ou plus), `closed` (terminé pour de bon).
- `last-contact` : le dernier mois avec un vrai contact ou du travail, `YYYY-MM`. Laissez vide si on ne sait pas.
- `tags` : `relationship`, puis le type, puis 2 à 5 tags de sujet (secteur, pays, type de travail), en anglais, en minuscules, avec des tirets.
- `description` : une phrase, entre guillemets droits. Toujours la dernière ligne.
- Facultatif : `aliases` (les autres noms qu'on leur donne), `project` (le projet en cours).

## Règles

- **Pas de doublons.** Avant de créer une note, cherchez le nom et ses variantes (accents, diminutifs, nom de marque ou nom de l'entreprise). Si une note existe, utilisez-la et ajoutez la nouvelle orthographe dans `aliases`. Ne créez jamais une deuxième note pour la même personne ou la même entreprise.
- **Format « vérité en haut »** (règle 17 du fichier racine) : qui ils sont et où en est la relation en haut, l'historique daté en dessous.
- **Tenez à jour.** Quand {Name} a un vrai contact avec quelqu'un (un e-mail, un appel, un travail livré), mettez `last-contact` au mois en cours, et `status` s'il a changé.
- **Les contacts** au sein d'une entreprise (un agent, un responsable, un éditeur) sont écrits en texte simple dans la note de l'entreprise, jamais en `[[liens]]`, et n'ont pas de note à eux. Pour les citer ailleurs, mettez un lien vers l'entreprise : `[[Nom de l'entreprise|Nom du contact]]`.
- **Les infos privées** (téléphones, e-mails, adresses personnelles) restent uniquement dans la note de la personne ou de l'entreprise. Ne les recopiez jamais dans les notes du jour ni dans d'autres notes.
- Faites des liens vers les personnes depuis les projets et les notes du jour, avec des `[[wikilinks]]`.
- Créez un nouveau sous-dossier seulement quand apparaît un nouveau type de relation. Demandez d'abord.
