---
type: skill
status: active
tags: [morning-brief, planning]
---

Um plano curto para o dia. Dois modos: **Resumo** (quando é pedido) e **Agendado** (todos os dias de trabalho).

## Resumo

Frase de ativação: "resumo da manhã", "morning brief", ou o mesmo em {Language}.

1. Lê `Diário/tarefas.md`, a nota do dia mais recente, o "Estado e próximo passo" de cada projeto com `status: active`, e as decisões com estado `open` ou `waiting`.
2. Se houver um calendário ligado, lê os eventos de hoje.
3. Responde em 6 linhas curtas, no máximo:
   - As 3 coisas mais importantes de hoje, cada uma com um `[[link]]` para a sua nota.
   - Aquilo de que {Name} está à espera de outras pessoas.
   - Uma decisão a tomar, se houver.
   - Os eventos de hoje, se houver um calendário ligado.
4. Não escrevas nenhum ficheiro. Se {Name} responder com informação nova, guarda-a segundo a regra geral 9.

## Agendado

Frase de ativação: "configura o meu resumo da manhã", "set up my morning brief", ou o mesmo em {Language}.

1. Pergunta a hora (opções para clicar: 7:00, 8:00, 9:00, 10:00), nos dias de trabalho de {Name}. Salta a pergunta se a configuração já tiver definido a hora.
2. Cria uma tarefa agendada na app do agente, a correr nesta pasta, com este prompt:

   > Abre a pasta do meu segundo cérebro. Lê `Competências/resumo-da-manhã/resumo-da-manhã.md` e dá-me o meu resumo da manhã.

3. Se não houver tarefas agendadas, pede a {Name} que diga "resumo da manhã" quando começar o dia.
