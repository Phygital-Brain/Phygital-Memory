---
type: skill
status: active
tags: [brain-keeper, check-up]
---

O check-up do Guardião do Cérebro: uma olhada completa no cérebro inteiro, quando {Name} pedir. Nada muda até {Name} dizer sim. (A arrumação diária está em `rotina-diária.md`.)

Quando usar: "faz um check-up no meu cérebro", "arruma meu cérebro", "check-up do cérebro", "check up my brain", "tidy my brain", "brain check-up" ou o mesmo em {Language}.

## 1. Olhe (sem mudar nada ainda)

Procure na pasta inteira e liste os problemas nestes grupos:

- **Links quebrados**: `[[links]]` apontando para notas que não existem. Nunca conserte criando uma nota em branco: a nota de verdade pode ainda estar sincronizando (regra 28 da raiz).
- **Órfãs**: notas que não recebem link de nenhuma outra nota.
- **Notas vazias ou quase vazias**, e marcadores esquecidos (`[name]`, `TBD`).
- **Fora do lugar**: arquivos na raiz da pasta (menos `CLAUDE.md`, `.claudeignore`, `.backups/` e o arquivo de regras de uma linha de outro agente, como `AGENTS.md`), notas que não batem com a tabela de onde guardar da pasta delas.
- **Tabelas de onde guardar desatualizadas**: um `CLAUDE.md` lista arquivos ou pastas que não existem, ou deixa de fora alguns que existem (linhas marcadas "criado no primeiro uso" estão certas).
- **Blocos de informações**: faltando ou incompletos, comparando com o `CLAUDE.md` da pasta. Sem `status:`, menos de 2 `tags:`, uma nota de projeto sem `project:`, tags do diário fora da lista fixa.
- **Projetos parados**: sem atualização há 60 dias ou mais. Sugira atualizar a situação, `paused` ou arquivar.
- **Metas soltas**: metas em `Sobre/metas.md` sem nenhum projeto ativo.
- **Decisões que precisam de revisão**: `updated` de mais de 30 dias atrás e status diferente de `closed`.
- **Relações antigas**: `status: active` mas `last-contact` de mais de 12 meses atrás. Sugira `dormant`.
- **Tarefas antigas**: tarefas em aberto em `Diário/tarefas.md` com mais de 30 dias.
- **Repetidos**: os mesmos fatos em mais de uma nota, ou duas notas para a mesma pessoa ou empresa.
- **Verdade desatualizada**: páginas do Sobre ou dos Contatos onde atualizações antigas enterram a situação atual (regra 17 da raiz).
- **Regras em conflito**: regras do `CLAUDE.md` da raiz que se contradizem.
- **Privacidade**: senhas, chaves ou números privados em notas comuns (regras 25 e 26 da raiz). Diga qual é a nota, nunca o valor.
- **Escrita**: travessões longos e padrões da Revisão de Texto nas notas.
- **Versão nova**: compare a versão deste cérebro (a primeira linha do `CLAUDE.md` da raiz) com a versão mais nova do Phygital Brain. Se você puder navegar na web, a mais nova é a última versão publicada em https://github.com/Phygital-Brain/phygital-brain/releases/latest. Se não puder, use a versão do Phygital Brain instalada no seu agente, se der para ver. Se não der para saber, pule esta parte.

## 2. Relatório

Uma lista curta em palavras simples, agrupada como acima. Para cada problema: a nota, o que está errado, a correção que você sugere. Coloque primeiro as correções simples e seguras (travessões, tags faltando, linhas das tabelas de onde guardar).

Se tiver uma versão mais nova, comece o relatório com uma linha. Se o seu agente já tem essa versão: "Saiu uma versão nova do Phygital Brain. Diga 'atualize meu segundo cérebro' ('Upgrade my second brain') para ver o que mudou." Se não tem: "Saiu uma versão nova do Phygital Brain. Atualize primeiro no seu agente, depois diga 'atualize meu segundo cérebro'."

## 3. Corrija só o que for aprovado

Antes da primeira correção, faça backup de cada arquivo que vai mudar (Backup e desfazer no `CLAUDE.md` da raiz).

Pergunte (com opções para clicar, quando der): **Corrigir todas as seguras**, **Ir uma por uma**, **Só o relatório**.

- Nunca apague nem mova sem checar os links e sem um sim claro (regra 21 da raiz).
- Na dúvida, arquive em vez de apagar.
- Registre uma linha na nota de hoje em `Diário/`: o que foi checado e corrigido.
