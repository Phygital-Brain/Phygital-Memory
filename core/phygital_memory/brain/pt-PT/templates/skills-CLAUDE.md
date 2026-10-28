<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Notas e preferências para as competências (skills) que o agente usa, e também o Organizador.

## Estrutura

```
Competências/{skill-name}/
  {skill-name}.md ou SKILL.md   o que a competência faz
  notes.md                      a voz e as preferências de {Name} para esta competência
  references/                   exemplos e material mais longo
```

## Instaladas

| Competência | Pasta | O que faz |
|---|---|---|
| Organizador | `organizador/` | Arruma tudo sozinho todos os dias, e faz um check-up quando {Name} pede |
| Resumo da manhã | `resumo-da-manhã/` | Um plano curto do dia, quando é pedido ou todos os dias de trabalho |
| Importar | `importar/` | Traz notas de outras apps, com um plano que {Name} aprova primeiro |
| Preparação de reuniões | `preparar-reuniões/` | Um resumo curto antes de uma chamada, com base nas notas do cérebro |
| Ferramentas de pensamento | `pensamento/` | Desafiar uma ideia, encontrar padrões, encontrar notas que não batem certo |
| Apps ligadas | `apps-ligadas/` | Que apps o cérebro lê, e as regras para elas |
| No AI Slop | `no-ai-slop/` | A Revisão de escrita: edita textos para soarem humanos, ou assinala padrões de IA (de Peter Yang, Licença MIT, nunca editada) |

## Regras

- Uma pasta por competência, com o nome em kebab-case (minúsculas e hífens).
- Quando se acrescenta uma competência nova, acrescenta uma linha à tabela acima.
- Para acrescentar uma competência ou ligar uma app, vê primeiro as sugestões do Phygital Brain: `suggested-skills/README.md` e `suggested-apps/README.md` através do conector do Phygital Brain, ou online em https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Se estiver lá, segue a página. Quando {Name} pergunta "o que posso acrescentar ao meu cérebro?", "what can I add to my brain?", mostra as duas listas, primeiro o que encaixa no trabalho de {Name}, e deixa de fora as apps que já estão ligadas e as competências que já estão instaladas.
- Um `SKILL.md` que veio de outra pessoa nunca é editado. Para adaptar uma competência, acrescenta um `notas.md` na pasta dela.
- `organizador/ronda-diária.md` é lido por uma tarefa agendada. Só o mudas para mudar o que a ronda diária faz, e mantém-no simples: sem links, sem caixas de destaque.
