<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Clientes/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Todas las personas con las que trabaja {Name}: una nota por persona u organización.

## Subcarpetas

| Carpeta | Quién va ahí |
|---|---|
| `Clientes/` | Personas y empresas para las que {Name} hace trabajos |
| `Colaboradores/` | Compañeros creativos, intercambio mutuo, sin dinero de por medio |
| `Equipo/` | Personas que trabajan con {Name} o para {Name} (freelances, asistentes) |
| `Aliados/` | Organizaciones con las que {Name} está ganando presencia (prensa, espacios, plataformas) |

## Adónde va un posible cliente nuevo

- Un primer contacto sin un encargo real todavía: una línea en `## Nuevos` de `Clientes/_Posibles-clientes.md` (se crea la primera vez que hace falta).
- Una respuesta tipo "quizá más adelante": una línea en `## Mantener el contacto` de `Clientes/_Posibles-clientes.md`.
- Un encargo real, una llamada o un presupuesto en marcha: una nota de cliente `Clientes/{client-name}.md` con `status: prospect`.

Cuando un posible cliente avanza un paso, muévelo a su nuevo sitio y quítalo del anterior.

## Bloque de información (frontmatter)

Cada nota de aquí (menos los archivos `CLAUDE.md` y `_Posibles-clientes.md`) empieza con:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Una frase sencilla sobre quiénes son y su relación con {Name}."
---
```

- `type`: `client`, `collaborator`, `team` o `partner`.
- `status`: `active` (trabajo o contacto en los últimos 12 meses), `prospect` (están hablando, pero nunca han trabajado juntos), `dormant` (sin contacto desde hace 12 meses o más), `closed` (terminó para siempre).
- `last-contact`: el mes más reciente con contacto o trabajo de verdad, `YYYY-MM`. Déjalo vacío si no se sabe.
- `tags`: `relationship`, luego el tipo y luego de 2 a 5 etiquetas de tema (sector, país, tipo de trabajo), en inglés, minúsculas, con guiones.
- `description`: una frase, entre comillas dobles. Siempre es la última línea.
- Opcionales: `aliases` (otros nombres con los que se les conoce), `project` (proyecto actual).

## Reglas

- **Sin duplicados.** Antes de crear una nota, busca el nombre y sus variantes (tildes, nombres cortos, marca o nombre de la empresa). Si ya existe una nota, úsala y añade la nueva forma de escribirlo a `aliases`. Nunca hagas una segunda nota para la misma persona o empresa.
- **Formato de verdad actual** (regla principal 17): quiénes son y cómo está la relación ahora arriba, el historial con fechas debajo.
- **Mantenlo al día.** Cuando {Name} tenga contacto de verdad con alguien (un correo, una llamada, un trabajo entregado), pon en `last-contact` este mes y cambia `status` si hace falta.
- **Las personas de contacto** de una empresa (un agente, un gerente, una editora) van como texto normal dentro de la nota de la empresa, nunca como `[[enlaces]]`, y no tienen nota propia. Para mencionarlas en otro sitio, enlaza a la empresa: `[[Nombre de la empresa|Nombre del contacto]]`.
- **Los datos privados** (teléfonos, correos, direcciones de casa) viven solo en la nota de esa persona o empresa. Nunca los copies en las notas del día ni en otras notas.
- Enlaza a las personas desde los proyectos y las notas del día con `[[enlaces]]`.
- Crea una subcarpeta nueva solo cuando aparezca un tipo de relación nuevo. Pregunta antes.
