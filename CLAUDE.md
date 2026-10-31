# CLAUDE.md — clude_skills

Repositorio de skills del equipo. Cada skill es una carpeta plana `skills/<nombre>/` con su `SKILL.md`.

## Cómo se usa en un proyecto
- Copia (o enlaza) la carpeta de la skill a `.claude/skills/<nombre>/` del proyecto. Claude Code la carga por su `name` y su `description`.
- Consulta `skills/README.md` para ver el índice por categoría. Las skills marcadas «solo si la invocas» hay que pedirlas por su nombre.

## Mantenimiento
- **Carpetas planas.** No anides skills en subcarpetas de categoría: la carpeta y el `name` deben coincidir.
- **Categorías en `skills/categorias.json`.** Una skill nueva se añade ahí, en la categoría que corresponda.
- **Índice generado.** Tras cambiar un `SKILL.md` o `categorias.json`, ejecuta `python3 scripts/skills.py indice` y no edites `skills/README.md` a mano.
- **Antes de hacer commit** ejecuta `python3 scripts/skills.py validar`. Comprueba que el YAML se lee, que `name` coincide con la carpeta, que la descripción tiene como máximo 1024 caracteres y que la skill está en una categoría.
- Al entrecomillar descripciones: si la descripción contiene `: `, va entre comillas dobles.
- **Procedencia.** Cada skill tiene su origen en `SOURCES.md`. Si añades una skill, añade también su fila.
- **Referencias que faltan.** `python3 scripts/skills.py faltas` genera `FALTAN.md`. Ejecútalo tras cambiar cualquier skill.
