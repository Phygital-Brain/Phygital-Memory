<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Notas y preferencias para las habilidades que usa el agente, y el Guardián del Cerebro.

## Estructura

```
Habilidades/{skill-name}/
  {skill-name}.md o SKILL.md   qué hace la habilidad
  notes.md                     la voz y las preferencias de {Name} para esta habilidad
  references/                  ejemplos y material más largo
```

## Instaladas

| Habilidad | Carpeta | Qué hace |
|---|---|---|
| Guardián del Cerebro | `guardián-del-cerebro/` | Pone orden cada día por su cuenta, y hace una revisión completa cuando {Name} la pide |
| Resumen de la mañana | `resumen-de-la-mañana/` | Un plan corto del día, cuando se pide o cada día laborable |
| Importar | `importar/` | Trae notas de otras apps, con un plan que {Name} aprueba antes |
| Preparar reuniones | `preparar-reuniones/` | Un resumen corto antes de una llamada, con las notas del cerebro |
| Herramientas para pensar | `pensar/` | Cuestionar una idea, encontrar patrones, encontrar notas que se contradicen |
| Apps conectadas | `apps-conectadas/` | De qué apps lee el cerebro y las reglas para usarlas |
| No AI Slop | `no-ai-slop/` | El Control de Escritura: corrige textos para que suenen humanos, o señala patrones de IA (de Peter Yang, licencia MIT, nunca se edita) |

## Reglas

- Una carpeta por habilidad, con el nombre en minúsculas y guiones.
- Cuando se añade una habilidad nueva, añade una fila a la tabla de arriba.
- Para añadir una habilidad o conectar una app, mira primero las sugerencias de Phygital Brain: `suggested-skills/README.md` y `suggested-apps/README.md` a través del conector de Phygital Brain, o en internet, en https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Si está ahí, sigue su página. Cuando {Name} pregunte "¿qué puedo añadir a mi cerebro?", "what can I add to my brain?", muestra las dos listas: primero lo que encaje con el trabajo de {Name}. Deja fuera las apps que ya están conectadas y las habilidades que ya están instaladas.
- Un `SKILL.md` que viene de otra persona nunca se edita. Para adaptar una habilidad, añade un `notas.md` en su carpeta.
- Una tarea programada lee `guardián-del-cerebro/rutina-diaria.md`. Cámbialo solo para cambiar lo que hace la ejecución diaria, y mantenlo sencillo: sin enlaces ni avisos destacados (callouts).
