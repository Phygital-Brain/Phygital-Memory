Cada projeto é uma pasta que cresce conforme a informação chega. O `README.md` é a única porta de entrada.

## Onde guardar

| Conteúdo | Vai para |
|---|---|
| Visão geral, situação, prazo, próximos passos | `Projetos/{name}/README.md` |
| Anotações de trabalho de {Name} | `Projetos/{name}/anotações/{topic}.md` |
| Pesquisa | `Projetos/{name}/pesquisa/{topic}.md` |
| Briefing, especificação, requisitos | `Projetos/{name}/briefings/{name}.md` |
| Rascunhos, roteiros, textos | `Projetos/{name}/rascunhos/{name}.md` |
| Ideias | `Projetos/{name}/ideias/{name}.md` |
| Feedback | `Projetos/{name}/feedback/{name}.md` |
| Imagens e mídia | `Projetos/{name}/mídia/` |
| Material antigo deste projeto | `Projetos/{name}/arquivados/` |

Os nomes de pastas são em minúsculas com hífens, sem números na frente (`pesquisa/`, não `01-Research/`). Um projeto pode ganhar uma pasta própria quando nenhuma destas servir.

## Estrutura do README

1. Bloco de informações (abaixo), com uma `description`.
2. `## O que é`: uma ou duas linhas, com link para [[metas]].
3. `## Situação e próximo passo`: em que pé está, o próximo passo.
4. `## Como funciona`: só se algo automático escreve aqui (uma tarefa agendada, um script).
5. `## Onde estão as coisas`: só quando já existirem subpastas. Uma tabelinha com link para cada uma.

## Bloco de informações (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (o README, que também tem `created`, `updated` e `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` ou `done`. A situação do README é a situação do projeto.
- `project`: o nome da pasta do projeto.
- `tags`: o projeto, depois o tipo.

## Regras

- Um projeto novo é só um `README.md`. Crie subpastas só quando chegar conteúdo que precise delas, e coloque um link para elas no README.
- O README é o índice. Não repita nele o conteúdo das subpastas.
- Nada de `CLAUDE.md` dentro de um projeto. As regras de um projeto vão em "Regras por projeto", abaixo.
- Inclua `project:` no bloco de informações de toda nota relacionada.
- Um projeto terminado vai para `Memória/arquivados/{name}/` só quando {Name} disser.
- Todo projeto deve servir a uma meta em [[metas]]. Num check-up, aponte metas sem projeto e projetos sem meta.

## Regras por projeto

<!-- Rules for one project only. Add a line when a project needs its own rule: "**Project-Name:** the rule." -->
