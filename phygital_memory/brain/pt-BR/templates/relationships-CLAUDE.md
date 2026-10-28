<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Clientes/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Todo mundo com quem {Name} trabalha: uma nota por pessoa ou organização.

## Subpastas

| Pasta | Quem fica aqui |
|---|---|
| `Clientes/` | Pessoas e empresas para quem {Name} entrega trabalho |
| `Colaboradores/` | Parceiros criativos, troca mútua, sem dinheiro envolvido |
| `Equipe/` | Pessoas que trabalham com ou para {Name} (freelancers, assistentes) |
| `Parceiros/` | Organizações com quem {Name} está construindo presença (imprensa, espaços, plataformas) |

## Para onde vai um possível cliente

- Um primeiro contato, ainda sem briefing de verdade: uma linha em `## Novos` no `Clientes/_Possíveis-clientes.md` (criado no primeiro uso).
- Uma resposta do tipo "quem sabe mais para frente": uma linha em `## Manter contato` no `Clientes/_Possíveis-clientes.md`.
- Um briefing de verdade, uma conversa ou um orçamento em andamento: uma nota de cliente `Clientes/{client-name}.md` com `status: prospect`.

Quando um possível cliente sobe um degrau, mova para o próximo lugar e tire do anterior.

## Bloco de informações (frontmatter)

Toda nota aqui (menos os arquivos `CLAUDE.md` e o `_Possíveis-clientes.md`) começa com:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Uma frase simples sobre quem são e a relação com {Name}."
---
```

- `type`: `client`, `collaborator`, `team` ou `partner`.
- `status`: `active` (trabalho ou contato nos últimos 12 meses), `prospect` (conversando, nunca trabalharam juntos), `dormant` (sem contato há 12 meses ou mais), `closed` (acabou de vez).
- `last-contact`: o mês mais recente com contato ou trabalho de verdade, `YYYY-MM`. Deixe vazio se não souber.
- `tags`: `relationship`, depois o tipo, depois de 2 a 5 tags de assunto (setor, país, tipo de trabalho), em inglês, minúsculas, com hífens.
- `description`: uma frase, entre aspas duplas. Sempre a última linha.
- Opcional: `aliases` (outros nomes usados para eles), `project` (projeto atual).

## Regras

- **Nada de repetidos.** Antes de criar uma nota, procure o nome e as variações dele (acentos, apelidos, nome da marca ou da empresa). Se já existir uma nota, use essa e acrescente o novo jeito de escrever em `aliases`. Nunca faça uma segunda nota para a mesma pessoa ou empresa.
- **Formato "verdade no topo"** (regra 17 da raiz): quem são e a situação atual em cima, o histórico com datas embaixo.
- **Mantenha atualizado.** Quando {Name} tiver contato de verdade com alguém (um e-mail, uma ligação, um trabalho entregue), atualize `last-contact` para este mês, e `status` se tiver mudado.
- **Pessoas de contato** de uma empresa (um agente, um gerente, um editor) ficam como texto simples dentro da nota da empresa, nunca como `[[links]]`, e não ganham nota própria. Para citar essas pessoas em outro lugar, linke a empresa: `[[Company Name|Contact Name]]`.
- **Dados pessoais** (telefones, e-mails, endereços residenciais) ficam só na nota daquela pessoa ou empresa. Nunca copie para as notas do diário ou outras notas.
- Linke as pessoas a partir dos projetos e das notas do diário com `[[wikilinks]]`.
- Crie uma subpasta nova só quando aparecer um tipo novo de relação. Pergunte antes.
