<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Esta carpeta guarda los datos básicos sobre {Name}. Estas notas son la fuente de verdad para todo lo demás.

## Archivos

| Archivo | Para qué | Etiqueta de categoría |
|---|---|---|
| `yo.md` | Quién es {Name}, cómo trabaja y cómo quiere que trabaje su agente | `identity` |
| `biografía.md` | La historia de {Name} | `identity` |
| `objetivos.md` | Objetivos y prioridades | `goals` |
| `negocio.md` | El negocio | `business` |
| `servicios.md` | Servicios, productos, ofertas | `business` |
| `clientela.md` | Quién compra y cómo encuentra a {Name} | `customers` |
| `problemas.md` | Problemas que resolver | `customers` (o `goals` si {Name} no vende) |
| `marca.md` | Voz, tono, palabras que usar y que evitar | `brand` |
| `herramientas.md` | Herramientas y dónde vive cada tipo de cosa | `tools` |
| `cv.md` | Trayectoria, estudios, prensa, premios | `career` |

## Bloque de información (frontmatter)

Cada archivo de aquí (menos este) empieza con:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Quién es {Name} y cómo quiere que trabaje su agente."
---
```

- `type`: siempre `about`.
- `status`: `active`, o `outdated` cuando se sabe que un dato ya no está al día.
- `updated`: la fecha en que cambiaron los datos por última vez. No se toca por erratas ni cambios de estilo.
- `tags`: `about`, luego la etiqueta de categoría del archivo (de la tabla de arriba) y luego etiquetas de tema que digan de qué trata el archivo (en inglés, minúsculas, con guiones). Actualiza las etiquetas de tema cuando se añada o se quite una sección.
- `description`: una frase, entre comillas dobles, que diga qué guarda este archivo. Siempre es la última línea.

## Reglas

- Estos archivos son la fuente de verdad. No copies su contenido en otro sitio: enlázalos.
- Formato de verdad actual (regla principal 17): lo que es verdad hoy arriba, el historial con fechas debajo.
- La fecha de nacimiento completa de {Name} vive solo en `yo.md`. Nunca la copies ni la menciones en una respuesta. El año de nacimiento sí se puede usar.
- Crea un archivo nuevo solo cuando un tema nuevo lo necesite. Pregunta antes (regla principal 9).
- En una revisión completa, avisa de los objetivos de `objetivos.md` que no tengan ningún proyecto activo.
