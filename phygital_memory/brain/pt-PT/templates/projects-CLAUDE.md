Cada projeto é uma pasta que vai crescendo à medida que chega informação. O `README.md` é a única porta de entrada.

## Onde guardar

| Conteúdo | Vai para |
|---|---|
| Visão geral, estado, prazo, próximos passos | `Projetos/{name}/README.md` |
| Notas de trabalho de {Name} | `Projetos/{name}/notas/{topic}.md` |
| Pesquisa | `Projetos/{name}/pesquisa/{topic}.md` |
| Briefing, especificações, requisitos | `Projetos/{name}/briefings/{name}.md` |
| Rascunhos, guiões, textos | `Projetos/{name}/rascunhos/{name}.md` |
| Ideias | `Projetos/{name}/ideias/{name}.md` |
| Feedback | `Projetos/{name}/feedback/{name}.md` |
| Imagens e outros materiais | `Projetos/{name}/materiais/` |
| Material antigo deste projeto | `Projetos/{name}/arquivo/` |

Os nomes das pastas vão em minúsculas, com hífens, sem números à frente (`pesquisa/`, e não `01-Research/`). Um projeto pode ter uma pasta própria quando nenhuma destas servir.

## Como se organiza o README

1. Bloco de informação (abaixo), com uma `description`.
2. `## O que é`: uma ou duas linhas, com link para [[objetivos]].
3. `## Estado e próximo passo`: em que ponto está, o próximo passo.
4. `## Como funciona`: só se alguma coisa automática escrever aqui (uma tarefa agendada, um script).
5. `## Onde está cada coisa`: só quando já houver subpastas. Uma tabela pequena com um link para cada uma.

## Bloco de informação (frontmatter)

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
- `status`: `active`, `paused` ou `done`. O estado do README é o estado do projeto.
- `project`: o nome da pasta do projeto.
- `tags`: o projeto, depois o tipo.

## Regras

- Um projeto novo é só um `README.md`. Só crias subpastas quando chegar conteúdo que precise delas, e pões um link para elas no README.
- O README é o índice. Não repitas lá o conteúdo das subpastas.
- Nada de `CLAUDE.md` dentro de um projeto. As regras de um só projeto vão para "Regras por projeto", abaixo.
- Põe `project:` no bloco de informação de todas as notas ligadas ao projeto.
- Um projeto acabado só passa para `Memória/arquivo/{name}/` quando {Name} disser.
- Cada projeto deve servir um objetivo de [[objetivos]]. Num check-up, assinala objetivos sem projeto e projetos sem objetivo.

## Regras por projeto

<!-- Rules for one project only. Add a line when a project needs its own rule: "**Project-Name:** the rule." -->
