<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Clientes/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Todas as pessoas e organizações com quem {Name} trabalha: uma nota por pessoa ou organização.

## Subpastas

| Pasta | Quem vai para lá |
|---|---|
| `Clientes/` | Pessoas e empresas para quem {Name} faz trabalho |
| `Colaboradores/` | Parceiros criativos, troca mútua, sem dinheiro envolvido |
| `Equipa/` | Pessoas que trabalham com {Name} ou para {Name} (freelancers, assistentes) |
| `Parceiros/` | Organizações onde {Name} quer ganhar presença (imprensa, espaços, plataformas) |

## Para onde vai um novo interessado

- Um primeiro contacto ainda sem um pedido concreto: uma linha em `## Novos` no ficheiro `Clientes/_Interessados.md` (criado na primeira vez que for preciso).
- Uma resposta do tipo "talvez mais tarde": uma linha em `## Manter o contacto` no ficheiro `Clientes/_Interessados.md`.
- Um pedido concreto, uma chamada ou um orçamento em curso: uma nota de cliente `Clientes/{client-name}.md` com `status: prospect`.

Quando um interessado avança um passo, passa-o para o sítio seguinte e tira-o do anterior.

## Bloco de informação (frontmatter)

Todas as notas desta pasta (menos os ficheiros `CLAUDE.md` e o `_Interessados.md`) começam com:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Uma frase simples sobre quem é e a relação com {Name}."
---
```

- `type`: `client`, `collaborator`, `team` ou `partner`.
- `status`: `active` (trabalho ou contacto nos últimos 12 meses), `prospect` (em conversa, nunca trabalharam juntos), `dormant` (sem contacto há 12 meses ou mais), `closed` (acabou de vez).
- `last-contact`: o mês mais recente com contacto ou trabalho a sério, `YYYY-MM`. Deixa vazio se não se souber.
- `tags`: `relationship`, depois o tipo, depois 2 a 5 etiquetas de tema (setor, país, tipo de trabalho), em inglês, minúsculas, com hífens.
- `description`: uma frase, entre aspas. É sempre a última linha.
- Opcional: `aliases` (outros nomes usados para essa pessoa ou empresa), `project` (o projeto atual).

## Regras

- **Nada de notas repetidas.** Antes de criares uma nota, procura o nome e as suas variantes (acentos, nomes curtos, marca ou nome da empresa). Se já existir uma nota, usa-a e acrescenta a nova grafia em `aliases`. Nunca faças uma segunda nota para a mesma pessoa ou empresa.
- **Formato "estado atual em cima, registo em baixo"** (regra geral 17): quem é e como estão as coisas agora no topo, a história com datas por baixo.
- **Mantém tudo em dia.** Quando {Name} tem um contacto a sério com alguém (um email, uma chamada, um trabalho entregue), atualiza `last-contact` para este mês, e o `status` se tiver mudado.
- **As pessoas de contacto** numa empresa (um agente, um gestor, um editor) ficam como texto simples dentro da nota da empresa, nunca como `[[links]]`, e não têm nota própria. Para as referir noutro sítio, põe um link para a empresa: `[[Nome da Empresa|Nome do Contacto]]`.
- **Os dados privados** (telefones, emails, moradas) só existem na nota dessa pessoa ou empresa. Nunca os copies para as notas do dia nem para outras notas.
- Liga as pessoas a partir dos projetos e das notas do dia com `[[wikilinks]]`.
- Só crias uma subpasta nova quando aparecer um tipo novo de relação. Pergunta primeiro.
