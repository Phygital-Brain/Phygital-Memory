<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

O diário de {Name}. Um arquivo por dia: `YYYY-MM-DD.md`. As tarefas em aberto ficam em `tarefas.md`.

## Bloco de informações (frontmatter)

Toda nota do diário começa com este bloco. Sem exceção.

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

- `type`: sempre `daily`.
- `date`: a data da nota, `YYYY-MM-DD`.
- `day`: dia da semana, em inglês (Monday, Tuesday...).
- `week`: número da semana ISO, `WNN`.
- `month`: mês, em inglês (January, February...).
- `status`: `active` enquanto o dia está aberto, `completed` quando ele tem 2 dias ou mais.
- `tags`: sempre `daily`, mais as desta lista fixa que aconteceram naquele dia. Nunca invente outras tags.
  - `problem`: algo quebrou ou deu errado
  - `clients`: trabalho para cliente ou contato com cliente
  - `meeting`: uma ligação ou reunião
  - `money`: notas fiscais, pagamentos, impostos, investimentos
  - `research`: pesquisa feita ou descobertas
  - `decision`: {Name} decidiu alguma coisa
  - `travel`: {Name} estava viajando
  - `personal`: saúde, vida pessoal, qualquer coisa fora do trabalho

## Regras

- As datas seguem a regra 30 da raiz (primeiro o fuso horário do computador, depois {Time zone}).
- Quem cria a nota (seu agente ou uma tarefa agendada) escreve primeiro o bloco de informações. Uma nota sem ele ganha o bloco no topo na próxima vez que for editada.
- Sem título `# YYYY-MM-DD`. O nome do arquivo já é o título.
- A nota do dia guarda a situação atual do dia: um documento arrumado por dia, com as seções atualizadas no lugar, nunca uma pilha de entradas repetidas.
- Registros de sessão: título em negrito e 1 ou 2 frases, pessoas e projetos como `[[wikilinks]]`, os detalhes vão na nota linkada.
- A nota de hoje guarda só o que aconteceu hoje. Tarefas em aberto de dias anteriores vão para `tarefas.md`. Nunca copie para a frente.
- Quando criar a nota de hoje, olhe as notas de 2, 3 e 4 dias atrás. As que ainda estiverem com `status: active` viram `completed` e ganham tags da lista fixa para o que claramente aconteceu naquele dia. Não olhe mais para trás.

## tasks.md

Tarefas em aberto que não pertencem a um projeto. As tarefas de projeto vão no README daquele projeto ("Situação e próximo passo"). Criado no primeiro uso:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Em aberto

- [ ] 2026-10-13: Mandar a nota fiscal para [[Ana]]

## Feito

- [x] 2026-10-12: Marcar o dentista (feito em 2026-10-13)
```

- As tarefas em aberto mais novas ficam no topo, com a data em que foram criadas.
- Quando uma tarefa for feita, marque, coloque a data em que foi feita e mova para `## Feito`.
- Tarefas feitas há mais de 30 dias podem ser tiradas (pergunte antes, regra 9 da raiz).
