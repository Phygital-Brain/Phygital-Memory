---
type: skill
status: active
tags: [brain-keeper, check-up]
---

O check-up do Organizador: uma volta completa a todo o cérebro, quando {Name} pede. Nada muda até {Name} dizer que sim. (A arrumação diária está em `ronda-diária.md`.)

Frase de ativação: "faz um check-up ao meu cérebro", "check up my brain", "arruma o meu cérebro", "tidy my brain", "check-up ao cérebro", "brain check-up", ou o mesmo em {Language}.

## 1. Olhar (ainda sem mudar nada)

Pesquisa a pasta toda e faz uma lista dos problemas, nestes grupos:

- **Links partidos**: `[[links]]` que apontam para notas que não existem. Nunca os resolvas com uma nota em branco nova: a nota verdadeira pode ainda estar a sincronizar (regra geral 28).
- **Notas órfãs**: notas para as quais nenhuma outra nota tem link.
- **Notas vazias ou quase vazias**, e textos de exemplo esquecidos (`[name]`, `TBD`).
- **Fora do sítio**: ficheiros na raiz da pasta (menos `CLAUDE.md`, `.claudeignore`, `.backups/` e o ficheiro de regras de uma linha de outro agente, como `AGENTS.md`), notas que não correspondem à tabela de arrumação da sua pasta.
- **Tabelas de arrumação desatualizadas**: um `CLAUDE.md` refere ficheiros ou pastas que não existem, ou não refere outros que existem (as linhas marcadas "criado na primeira vez que for preciso" estão bem).
- **Blocos de informação**: em falta ou incompletos, comparados com o `CLAUDE.md` da pasta. Sem `status:`, menos de 2 `tags:`, uma nota de projeto sem `project:`, etiquetas do diário que não estão na lista fixa.
- **Projetos parados**: sem atualizações há 60 dias ou mais. Sugere atualizar o estado, `paused`, ou arquivar.
- **Objetivos sem projeto**: objetivos em `Perfil/objetivos.md` sem nenhum projeto ativo.
- **Decisões a precisar de revisão**: `updated` há mais de 30 dias e estado diferente de `closed`.
- **Relações antigas**: `status: active` mas `last-contact` há mais de 12 meses. Sugere `dormant`.
- **Tarefas antigas**: tarefas em aberto em `Diário/tarefas.md` com mais de 30 dias.
- **Repetidos**: os mesmos factos em mais de uma nota, ou duas notas para a mesma pessoa ou empresa.
- **Estado atual desatualizado**: páginas do perfil ou dos contactos onde as atualizações antigas escondem o estado atual (regra geral 17).
- **Regras em conflito**: regras do `CLAUDE.md` principal que se contradizem.
- **Privacidade**: palavras-passe, chaves ou números privados em notas normais (regras gerais 25 e 26). Indica a nota, nunca o valor.
- **Escrita**: travessões e padrões da Revisão de escrita nas notas.
- **Versão nova**: compara a versão deste cérebro (a primeira linha do `CLAUDE.md` principal) com o Phygital Brain mais recente. Se conseguires navegar na web, a mais recente é a última versão publicada em https://github.com/Phygital-Brain/phygital-brain/releases/latest. Se não conseguires, usa a versão do Phygital Brain instalada no teu agente, se a conseguires ver. Se não der para saber, salta este ponto.

## 2. Relatório

Uma lista curta, por palavras simples, agrupada como acima. Para cada problema: a nota, o que está mal, a correção que sugeres. Põe primeiro as correções simples e seguras (travessões, etiquetas em falta, linhas das tabelas de arrumação).

Se houver uma versão nova, começa o relatório com uma linha. Se o teu agente já a tiver: "Já saiu uma versão nova do Phygital Brain. Diz 'Atualiza o meu segundo cérebro' ('Upgrade my second brain') para veres o que há de novo." Se não tiver: "Já saiu uma versão nova do Phygital Brain. Atualiza-o primeiro no teu agente e depois diz 'Atualiza o meu segundo cérebro' ('Upgrade my second brain')."

## 3. Corrigir só o que foi aprovado

Antes da primeira correção, faz uma cópia de segurança de cada ficheiro que vais alterar (Cópias de segurança e desfazer, no `CLAUDE.md` principal).

Pergunta (com opções para clicar, quando der): **Corrigir todas as seguras**, **Uma a uma**, **Só o relatório**.

- Nunca apagues nem movas nada sem verificar os links e sem um sim claro (regra geral 21).
- Na dúvida, arquiva em vez de apagar.
- Escreve uma linha na nota de hoje em `Diário/`: o que foi verificado e corrigido.
