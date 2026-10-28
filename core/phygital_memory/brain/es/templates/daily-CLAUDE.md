<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

El diario de {Name}. Un archivo por día: `YYYY-MM-DD.md`. Las tareas abiertas viven en `tareas.md`.

## Bloque de información (frontmatter)

Cada nota del día empieza con este bloque. Sin excepciones.

```yaml
---
type: daily
date: 2026-10-13
day: Tuesday
week: W42
month: October
status: active
tags: [daily, meeting]
---
```

- `type`: siempre `daily`.
- `date`: la fecha de la nota, `YYYY-MM-DD`.
- `day`: el día de la semana, en inglés (Monday, Tuesday...).
- `week`: el número de semana ISO, `WNN`.
- `month`: el mes, en inglés (January, February...).
- `status`: `active` mientras el día está abierto, `completed` cuando tiene 2 días o más.
- `tags`: siempre `daily`, más las de esta lista fija que correspondan a lo que pasó ese día. Nunca te inventes otras.
  - `problem`: algo se rompió o salió mal
  - `clients`: trabajo o contacto con clientes
  - `meeting`: una llamada o una reunión
  - `money`: facturas, pagos, impuestos, inversiones
  - `research`: investigación hecha o hallazgos
  - `decision`: {Name} decidió algo
  - `travel`: {Name} estaba de viaje
  - `personal`: salud, vida, cualquier cosa fuera del trabajo

## Reglas

- Las fechas siguen la regla principal 30 (primero la zona horaria del dispositivo, después {Time zone}).
- Quien crea la nota (tu agente o una tarea programada) escribe primero el bloque de información. A una nota que no lo tenga se le añade arriba la próxima vez que se edite.
- Sin título `# YYYY-MM-DD`. El nombre del archivo ya es el título.
- La nota del día muestra cómo está el día ahora: un solo documento ordenado por día, con las secciones actualizadas en su sitio, nunca un montón de entradas repetidas.
- Registros de sesión: un titular en negrita y 1 o 2 frases, con personas y proyectos como `[[enlaces]]`. Los detalles van en la nota enlazada.
- La nota de hoy guarda solo lo que pasó hoy. Las tareas abiertas de días anteriores van a `tareas.md`. Nunca las copies de un día a otro.
- Cuando crees la nota de hoy, mira las notas de hace 2, 3 y 4 días. Las que sigan en `status: active` pasan a `completed` y reciben las etiquetas de la lista fija que correspondan a lo que claramente pasó ese día. No mires más atrás.

## tasks.md

Tareas abiertas que no son de ningún proyecto. Las tareas de un proyecto van en el README de ese proyecto ("Estado y siguiente paso"). Se crea la primera vez que hace falta:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Abiertas

- [ ] 2026-10-13: Enviar la factura a [[Ana]]

## Hechas

- [x] 2026-10-12: Pedir cita con el dentista (hecha el 2026-10-13)
```

- Las tareas abiertas más nuevas van arriba, con la fecha en que se añadieron.
- Cuando una tarea está hecha, márcala, añade la fecha en que se hizo y muévela a `## Hechas`.
- Las tareas hechas de hace más de 30 días se pueden quitar (pregunta antes, regla principal 9).
