<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Esta pasta guarda os factos essenciais sobre {Name}. Estas notas são a fonte de verdade para todo o resto do trabalho.

## Ficheiros

| Ficheiro | Para que serve | Etiqueta de categoria |
|---|---|---|
| `eu.md` | Quem é {Name}, como trabalha, como quer que o agente trabalhe | `identity` |
| `biografia.md` | A história de {Name} | `identity` |
| `objetivos.md` | Objetivos e prioridades | `goals` |
| `negócio.md` | O negócio | `business` |
| `serviços.md` | Serviços, produtos, ofertas | `business` |
| `público-alvo.md` | Quem compra e como chega até {Name} | `customers` |
| `dificuldades.md` | Problemas a resolver | `customers` (ou `goals` se {Name} não vender nada) |
| `marca.md` | Voz, tom, palavras a usar e a evitar | `brand` |
| `ferramentas.md` | Ferramentas e onde fica cada tipo de coisa | `tools` |
| `cv.md` | Percurso profissional, formação, imprensa, prémios | `career` |

## Bloco de informação (frontmatter)

Todos os ficheiros desta pasta (menos este) começam com:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Quem é {Name} e como quer que o agente trabalhe."
---
```

- `type`: sempre `about`.
- `status`: `active`, ou `outdated` quando se sabe que um facto já não é atual.
- `updated`: a data em que os factos mudaram pela última vez. Não muda quando só se corrige uma gralha ou o estilo.
- `tags`: `about`, depois a etiqueta de categoria do ficheiro (da tabela acima), depois etiquetas de tema que dizem do que trata o ficheiro (em inglês, minúsculas, com hífens). Atualiza as etiquetas de tema quando se acrescenta ou tira uma secção.
- `description`: uma frase, entre aspas, a dizer o que este ficheiro tem. É sempre a última linha.

## Regras

- Estes ficheiros são a fonte de verdade. Não copies o conteúdo deles para outro lado: põe um link.
- Formato "estado atual em cima, registo em baixo" (regra geral 17): o que é verdade hoje no topo, as entradas com data por baixo.
- A data de nascimento completa de {Name} só existe em `eu.md`. Nunca a copies nem a repitas numa resposta. O ano de nascimento pode ser usado.
- Só crias um ficheiro novo quando um tema novo precisar dele. Pergunta primeiro (regra geral 9).
- Num check-up, assinala os objetivos de `objetivos.md` que não têm nenhum projeto ativo.
