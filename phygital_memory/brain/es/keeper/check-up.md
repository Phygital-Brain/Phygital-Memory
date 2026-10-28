---
type: skill
status: active
tags: [brain-keeper, check-up]
---

La revisión completa del Guardián del Cerebro: un repaso de todo el cerebro, cuando {Name} lo pide. No cambia nada hasta que {Name} diga que sí. (El orden diario está en `rutina-diaria.md`.)

Cuándo: "revisa mi cerebro", "check up my brain", "ordena mi cerebro", "tidy my brain", "revisión del cerebro", "brain check-up", o lo mismo en {Language}.

## 1. Mira (todavía no cambies nada)

Busca en toda la carpeta y haz una lista de problemas en estos grupos:

- **Enlaces rotos**: `[[enlaces]]` que apuntan a notas que no existen. Nunca los arregles creando una nota en blanco: puede que la nota de verdad todavía se esté sincronizando (regla principal 28).
- **Notas huérfanas**: notas a las que no enlaza ninguna otra.
- **Notas vacías o casi vacías**, y marcadores que se quedaron sin rellenar (`[name]`, `TBD`).
- **Fuera de sitio**: archivos en la raíz de la carpeta (menos `CLAUDE.md`, `.claudeignore`, `.backups/` y el archivo de reglas de una línea de otro agente, como `AGENTS.md`), y notas que no cuadran con la tabla de su carpeta.
- **Tablas de rutas desactualizadas**: un `CLAUDE.md` que menciona archivos o carpetas que no existen, o que no menciona algunos que sí existen (las filas marcadas "se crea la primera vez que hace falta" están bien).
- **Bloques de información**: que faltan o están incompletos, comparados con el `CLAUDE.md` de la carpeta. Sin `status:`, con menos de 2 `tags:`, una nota de proyecto sin `project:`, etiquetas del día que no están en la lista fija.
- **Proyectos parados**: sin actualizar en 60 días o más. Sugiere actualizar el estado, ponerlo en `paused` o archivarlo.
- **Objetivos a la deriva**: objetivos de `Perfil/objetivos.md` sin ningún proyecto activo.
- **Decisiones que hay que revisar**: `updated` de hace más de 30 días y un estado que no es `closed`.
- **Relaciones antiguas**: `status: active` pero un `last-contact` de hace más de 12 meses. Sugiere `dormant`.
- **Tareas antiguas**: tareas abiertas de `Diario/tareas.md` de hace más de 30 días.
- **Duplicados**: los mismos datos en más de una nota, o dos notas para la misma persona o empresa.
- **Verdad desactualizada**: páginas del Perfil o de Contactos donde las actualizaciones viejas tapan el estado actual (regla principal 17).
- **Reglas que chocan**: reglas del `CLAUDE.md` principal que se contradicen entre sí.
- **Privacidad**: contraseñas, claves o números privados metidos en notas normales (reglas principales 25 y 26). Di en qué nota están, nunca el dato.
- **Escritura**: rayas largas y patrones del Control de Escritura en las notas.
- **Versión nueva**: compara la versión de este cerebro (la primera línea del `CLAUDE.md` principal) con la versión más nueva de Phygital Brain. Si puedes navegar por la web, la más nueva es la última versión publicada en https://github.com/Phygital-Brain/phygital-brain/releases/latest. Si no puedes, usa la versión de Phygital Brain instalada en tu agente, si la puedes ver. Si no hay forma de saberlo, sáltate esto.

## 2. Informe

Una lista corta con palabras sencillas, agrupada como arriba. Para cada problema: la nota, qué falla y el arreglo que sugieres. Pon primero los arreglos sencillos y seguros (rayas largas, etiquetas que faltan, filas de las tablas de rutas).

Si hay una versión más nueva, empieza el informe con una línea. Si tu agente ya la tiene: "Hay una versión nueva de Phygital Brain. Di 'actualiza mi segundo cerebro' ('Upgrade my second brain') para ver qué hay de nuevo." Si no: "Hay una versión nueva de Phygital Brain. Primero actualízala en tu agente y luego di 'actualiza mi segundo cerebro'."

## 3. Arregla solo lo aprobado

Antes del primer arreglo, haz una copia de seguridad de cada archivo que vayas a cambiar (Copias de seguridad y deshacer, en el `CLAUDE.md` principal).

Pregunta (con opciones para hacer clic cuando se pueda): **Arreglar las seguras**, **Ir una por una**, **Solo el informe**.

- Nunca borres ni muevas nada sin revisar los enlaces y sin un sí claro (regla principal 21).
- Si tienes dudas, archiva en vez de borrar.
- Escribe una línea en la nota de hoy de `Diario/`: qué se revisó y qué se arregló.
