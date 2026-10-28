Cada proyecto es una carpeta que crece a medida que llega información. `README.md` es la única puerta de entrada.

## Dónde va cada cosa

| Contenido | Adónde va |
|---|---|
| Resumen, estado, plazo, siguientes pasos | `Proyectos/{name}/README.md` |
| Notas de trabajo de {Name} | `Proyectos/{name}/notas/{topic}.md` |
| Investigación | `Proyectos/{name}/investigación/{topic}.md` |
| Encargo, especificaciones, requisitos | `Proyectos/{name}/encargos/{name}.md` |
| Borradores, guiones, textos | `Proyectos/{name}/borradores/{name}.md` |
| Ideas | `Proyectos/{name}/ideas/{name}.md` |
| Comentarios y opiniones recibidas | `Proyectos/{name}/comentarios/{name}.md` |
| Imágenes y multimedia | `Proyectos/{name}/multimedia/` |
| Material antiguo de este proyecto | `Proyectos/{name}/archivo/` |

Los nombres de carpeta van en minúsculas y con guiones, sin números delante (`investigación/`, no `01-Research/`). Un proyecto puede añadir su propia carpeta cuando ninguna de estas encaje.

## Estructura del README

1. Bloque de información (más abajo), con una `description`.
2. `## Qué es`: una o dos líneas, enlazado a [[objetivos]].
3. `## Estado y siguiente paso`: cómo va y cuál es el siguiente paso.
4. `## Cómo funciona`: solo si algo automático escribe aquí (una tarea programada, un script).
5. `## Dónde está cada cosa`: solo cuando ya existan subcarpetas. Una tabla pequeña que enlaza cada una.

## Bloque de información (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (el README, que además lleva `created`, `updated` y `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` o `done`. El estado del README es el estado del proyecto.
- `project`: el nombre de la carpeta del proyecto.
- `tags`: el proyecto y luego el tipo.

## Reglas

- Un proyecto nuevo es solo un `README.md`. Crea subcarpetas solo cuando llegue contenido que las necesite, y enlázalas desde el README.
- El README es el índice. No repitas en él lo que hay en las subcarpetas.
- Nada de `CLAUDE.md` dentro de un proyecto. Las reglas de un solo proyecto van en "Reglas por proyecto", más abajo.
- Pon `project:` en el bloque de información de cada nota relacionada.
- Un proyecto terminado pasa a `Memoria/archivo/{name}/` solo cuando {Name} lo diga.
- Cada proyecto debería servir a un objetivo de [[objetivos]]. En una revisión completa, avisa de los objetivos sin proyecto y de los proyectos sin objetivo.

## Reglas por proyecto

<!-- Reglas para un solo proyecto. Añade una línea cuando un proyecto necesite su propia regla: "**Nombre-del-proyecto:** la regla." -->
