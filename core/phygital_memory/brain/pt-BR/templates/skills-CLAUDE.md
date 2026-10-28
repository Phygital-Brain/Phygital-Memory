<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Notas e preferências para as skills que o agente usa, mais o Guardião do Cérebro.

## Estrutura

```
Skills/{skill-name}/
  {skill-name}.md ou SKILL.md   o que a skill faz
  notes.md                      a voz e as preferências de {Name} para esta skill
  references/                   exemplos e material mais longo
```

## Instaladas

| Skill | Pasta | O que faz |
|---|---|---|
| Guardião do Cérebro | `guardião-do-cérebro/` | Arrumação diária sozinho, e um check-up quando {Name} pede |
| Resumo da manhã | `resumo-da-manhã/` | Um plano curto do dia, quando pedido ou todo dia de trabalho |
| Importar | `importar/` | Traz notas de outros apps, com um plano que {Name} aprova antes |
| Preparo de reunião | `preparo-de-reunião/` | Um resumo curto antes de uma ligação, com as notas do cérebro |
| Ferramentas de pensamento | `pensamento/` | Questionar uma ideia, achar padrões, achar notas que se contradizem |
| Apps conectados | `apps-conectados/` | Quais apps o cérebro lê, e as regras para eles |
| No AI Slop | `no-ai-slop/` | A Revisão de Texto: edita textos para soarem humanos, ou aponta padrões de IA (de Peter Yang, licença MIT, nunca editada) |

## Regras

- Uma pasta por skill, com nome em kebab-case (minúsculas com hífens).
- Quando uma skill nova for adicionada, acrescente uma linha na tabela acima.
- Para adicionar uma skill ou conectar um app, veja primeiro as sugestões do Phygital Brain: `suggested-skills/README.md` e `suggested-apps/README.md` pelo conector do Phygital Brain, ou online em https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Se estiver lá, siga a página. Quando {Name} perguntar "o que eu posso adicionar ao meu cérebro?", "what can I add to my brain?", mostre as duas listas, primeiro o que combina com o trabalho de {Name}, e deixe de fora os apps já conectados e as skills já instaladas.
- Um `SKILL.md` que veio de outra pessoa nunca é editado. Para personalizar uma skill, crie um `anotações.md` na pasta dela.
- `guardião-do-cérebro/rotina-diária.md` é lido por uma tarefa agendada. Mude esse arquivo só para mudar o que a execução diária faz, e mantenha simples: sem links, sem callouts.
