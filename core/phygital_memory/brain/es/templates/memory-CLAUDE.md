Lo que se va acumulando con el tiempo: decisiones, investigación, solicitudes y el archivo.

## Dónde va cada cosa

| Contenido | Adónde va |
|---|---|
| Una decisión con sus motivos, o el análisis de algo de fuera (una app, una web, un curso, un competidor) | `decisiones/YYYY-MM-DD-{title}.md` |
| Investigación (mercado, tendencias, opciones) | `investigación/{topic}.md` |
| Solicitudes: empleos, becas, premios, convocatorias (se crea la primera vez que hace falta) | `solicitudes/{name}/` |
| Fichas de la competencia (se crea la primera vez que hace falta) | `competencia/{name}.md` |
| Dinero: facturas, impuestos, pagos. Privado | `finanzas/` |
| Decisiones archivadas | `archivo/decisiones/` |
| Investigación terminada o que ya no está al día | `archivo/investigación/` |
| Proyectos terminados | `archivo/{name}/` |
| Notas de reuniones | `decisiones/` si de ahí salió una decisión; si no, la nota de ese día en `Diario/`. Sugiere una carpeta de reuniones solo cuando haya muchas. |

## Bloque de información (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: la fecha en que se escribió la nota.
- `status`: más abajo se explica para decisiones y solicitudes. Para todo lo demás: `active` o `closed`.
- `tags`: el tipo y luego el tema.
- Opcionales: `project`, `deadline`, `description` (una frase, entre comillas dobles, en la última línea).

## Notas de decisión

Incluye siempre el porqué: quién participó, qué la provocó y qué se sacrificó a cambio. Usa `> [!important]` para la decisión en sí y `> [!warning]` para los riesgos conocidos.

Las decisiones también llevan `updated:` justo después de `date:`. `date` es cuándo se creó y `updated`, la última vez que se revisó o cambió.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (todavía se está decidiendo o trabajando), `waiting` (se espera a otra persona), `paused`, `closed`.
- Una decisión con un `updated` de hace más de 30 días hay que revisarla. El Guardián del Cerebro avisa de ella hasta que {Name} la mantenga, la cierre o la archive (cada opción pone `updated` con la fecha de ese día).
- Una decisión pasa a `archivo/decisiones/` solo cuando {Name} lo diga.

## Solicitudes

Una carpeta por solicitud: `solicitudes/{name}/`, con un `README.md` que guarda el plazo, el enlace, el estado y lo que se envió. Los demás archivos (respuestas, carta de presentación) van al lado.

- `status`: `draft`, `submitted`, `accepted`, `rejected` o `withdrawn`.
- Guarda las respuestas en markdown. Los PDF y las presentaciones grandes se quedan fuera del cerebro: resúmelos en una nota.

## Reglas

- La investigación es neutral por defecto (regla principal 23).
- La investigación que ya no vale se mueve a `archivo/investigación/` en vez de borrarse.
- `finanzas/` es privada y está en `.claudeignore`. Ábrela solo cuando {Name} pida un archivo concreto (regla principal 8).
