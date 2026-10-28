<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

O diário de {Name}. Um ficheiro por dia: `YYYY-MM-DD.md`. As tarefas em aberto ficam em `tarefas.md`.

## Bloco de informação (frontmatter)

Todas as notas do dia começam com este bloco. Sem exceções.

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
- `day`: o dia da semana, em inglês (Monday, Tuesday...).
- `week`: o número da semana ISO, `WNN`.
- `month`: o mês, em inglês (January, February...).
- `status`: `active` enquanto o dia está aberto, `completed` quando já tem 2 ou mais dias.
- `tags`: sempre `daily`, mais as desta lista fixa que se aplicam a esse dia. Nunca inventes outras.
  - `problem`: alguma coisa avariou ou correu mal
  - `clients`: trabalho para clientes ou contacto com clientes
  - `meeting`: uma chamada ou reunião
  - `money`: faturas, pagamentos, impostos, investimentos
  - `research`: pesquisa feita ou descobertas
  - `decision`: {Name} decidiu alguma coisa
  - `travel`: {Name} estava em viagem
  - `personal`: saúde, vida pessoal, tudo o que não é trabalho

## Regras

- As datas seguem a regra geral 30 (primeiro o fuso horário do computador, depois {Time zone}).
- Quem cria a nota (o teu agente ou uma tarefa agendada) escreve primeiro o bloco de informação. Uma nota sem bloco ganha um no topo da próxima vez que for editada.
- Nada de título `# YYYY-MM-DD`. O nome do ficheiro é o título.
- A nota do dia mostra como está o dia agora: um documento arrumado por dia, com as secções atualizadas no sítio, nunca uma pilha de entradas repetidas.
- Registos da sessão: título a negrito e 1 ou 2 frases, pessoas e projetos como `[[wikilinks]]`, os pormenores vão para a nota ligada.
- A nota de hoje só tem o que se passou hoje. As tarefas em aberto de dias anteriores vão para `tarefas.md`. Nunca as copies para a frente.
- Quando criares a nota de hoje, olha para as notas de há 2, 3 e 4 dias. As que ainda estiverem com `status: active` passam a `completed`, e recebem etiquetas da lista fixa para o que claramente aconteceu nesse dia. Não olhes mais para trás.

## tasks.md

Tarefas em aberto que não pertencem a nenhum projeto. As tarefas de um projeto vão para o README desse projeto ("Estado e próximo passo"). É criado na primeira vez que for preciso:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Em aberto

- [ ] 2026-10-13: Enviar a fatura à [[Ana]]

## Feito

- [x] 2026-10-12: Marcar o dentista (feito a 2026-10-13)
```

- As tarefas em aberto mais recentes ficam no topo, com a data em que foram acrescentadas.
- Quando uma tarefa está feita, marca-a, acrescenta a data em que foi feita e passa-a para `## Feito`.
- As tarefas feitas há mais de 30 dias podem ser retiradas (pergunta primeiro, regra geral 9).
