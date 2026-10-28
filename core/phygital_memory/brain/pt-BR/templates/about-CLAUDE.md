<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Esta pasta guarda os fatos principais sobre {Name}. Estas notas são a fonte da verdade para todo o resto do trabalho.

## Arquivos

| Arquivo | Para quê | Tag de categoria |
|---|---|---|
| `eu.md` | Quem {Name} é, como trabalha, como quer que o agente trabalhe | `identity` |
| `biografia.md` | A história de {Name} | `identity` |
| `metas.md` | Metas e prioridades | `goals` |
| `negócio.md` | O negócio | `business` |
| `serviços.md` | Serviços, produtos, ofertas | `business` |
| `público.md` | Quem compra e como chega até {Name} | `customers` |
| `problemas.md` | Problemas a resolver | `customers` (ou `goals` se {Name} não vende nada) |
| `marca.md` | Voz, tom, palavras para usar e para evitar | `brand` |
| `ferramentas.md` | Ferramentas e onde cada tipo de coisa fica | `tools` |
| `currículo.md` | Trajetória profissional, formação, imprensa, prêmios | `career` |

## Bloco de informações (frontmatter)

Todo arquivo aqui (menos este) começa com:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Quem {Name} é e como quer que o agente trabalhe."
---
```

- `type`: sempre `about`.
- `status`: `active`, ou `outdated` quando se sabe que um fato está velho.
- `updated`: a data em que os fatos mudaram pela última vez. Não muda por correção de digitação ou de estilo.
- `tags`: `about`, depois a tag de categoria do arquivo (da tabela acima), depois tags de assunto dizendo o que o arquivo cobre (em inglês, minúsculas, com hífens). Atualize as tags de assunto quando uma seção for criada ou tirada.
- `description`: uma frase, entre aspas duplas, dizendo o que o arquivo guarda. Sempre a última linha.

## Regras

- Estes arquivos são a fonte da verdade. Não copie o conteúdo deles para outro lugar: coloque um link.
- Formato "verdade no topo" (regra 17 da raiz): a verdade atual em cima, o histórico com datas embaixo.
- A data de nascimento completa de {Name} fica só no `eu.md`. Nunca copie nem cite numa resposta. O ano de nascimento pode.
- Crie um arquivo novo só quando um assunto novo precisar. Pergunte antes (regra 9 da raiz).
- Num check-up, aponte as metas do `metas.md` que não têm nenhum projeto ativo.
