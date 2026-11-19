# Ruso desde cero · contexto para Claude Code

Dos cursos de ruso desde cero, en paralelo, para dos públicos distintos: uno
para angloparlantes (`curso/en/`) y otro para hispanohablantes (`curso/es/`).
Un año, 30 minutos al día — la misma forma que `espanol-desde-ruso`, el
proyecto hermano, pero con el ruso como lengua META en vez de como lengua
base.

## Por qué existe este repo, y qué decisión reemplaza

El 2026-10-30, trabajando en `espanol-desde-ruso`, se planteó esta misma idea
(«¿hacemos el curso al revés, para enseñar ruso?») y se descartó. La razón
que quedó escrita en `espanol-desde-ruso/CLAUDE.md` fue esta:

> «el código sirve casi entero y las 365 lecciones no [...] ese curso lo
> firmaría alguien que no es nativo de ruso —sería el alumno y no el
> profesor—»

El profesor de `espanol-desde-ruso` es nativo de español, con inglés como
segunda lengua: puede firmar un curso que enseñe CUALQUIERA de esas dos, pero
no puede firmar como experto un curso que enseñe ruso, porque el ruso es la
lengua que él mismo está aprendiendo.

**El 2026-11-19 se retomó la idea con esa objeción resuelta de otra forma**:
en vez de un profesor nativo de ruso, el contraste va a salir de **libros de
referencia** que el usuario va a mandar — el mismo método que ya usa
`espanol-desde-ruso` con Nuzhdin y compañía (`referencias/`, análisis
estructural, nunca copia del contenido ajeno). La diferencia es que ahí los
libros confirman o corrigen decisiones de alguien que YA domina las dos
lenguas; acá los libros son la fuente primaria de qué le cuesta a un
angloparlante o a un hispanohablante en ruso, porque el autor no lo sabe de
primera mano.

**Esto es el eje de todo el proyecto, no un detalle**: sin los libros no hay
manera honesta de escribir el bloque de contraste (lo que en
`espanol-desde-ruso` es «⚠️ Контраст с русским», la pieza que hace que un
curso sea «desde el inglés» o «desde el español» y no un curso de ruso
genérico con la portada cambiada). Regla 7 del proyecto hermano — no se
inventan datos — aplica acá con más fuerza todavía: inventar un error típico
del angloparlante en ruso sin haberlo leído en ninguna parte sería peor que
no tener esa lección.

## Estado: ESPERANDO LOS LIBROS

Al día de hoy (2026-11-19) este repo es solo el esqueleto. No hay
`calendario.yaml`, no hay una sola lección escrita, no hay lista de errores
por lengua base. Lo que sigue, apenas lleguen los libros:

1. Leerlos y escribir `referencias/<libro>.md` con el análisis estructural de
   cada uno — qué orden de gramática usa, qué dice de interferencias, qué se
   toma y qué no. Es el mismo formato que `espanol-desde-ruso/referencias/`.
2. De ahí sacar DOS listas negras de errores — una para el angloparlante
   aprendiendo ruso, otra para el hispanohablante — porque el alfabeto
   cirílico, el aspecto verbal, los seis casos y el orden de palabras le
   pegan distinto a cada uno. No son la misma lista traducida.
3. Recién con eso armar `programa/calendario-en.yaml` y
   `programa/calendario-es.yaml`.

**No se escribe ninguna lección de prueba ni ningún calendario de muestra
mientras tanto**: un calendario inventado hoy se tiraría entero en cuanto
lleguen los libros, y el precio de ese error ya está documentado en
`espanol-desde-ruso` (la unidad 5, los 72 tiempos verbales usados antes de su
lección) — ahí el defecto era de progresión interna; acá sería peor, sería
el eje entero del curso construido sin su fuente.

## Por qué DOS pistas y no una con selector de idioma

`espanol-desde-ruso` tiene un selector de ru/es/en en la interfaz, pero las
**lecciones** están escritas una sola vez, en ruso, porque el ruso es la
lengua base de ESE curso (la instrucción) y el español la meta. Acá no hay
un «idioma de interfaz»: hay dos lenguas base distintas (inglés, español) que
enseñan la MISMA lengua meta (ruso), y lo que un angloparlante necesita que
se le explique no es lo que necesita un hispanohablante — ni el vocabulario
de apoyo, ni el orden de los casos, ni los falsos amigos. Son dos cursos que
comparten método y quizá infraestructura, no un curso con interfaz traducida.

Qué se puede compartir entre las dos pistas, probablemente (a decidir cuando
haya contenido):

- El armazón del calendario (24 unidades, fase final, día de reserva) —
  **la progresión gramatical del ruso** puede ser casi igual para las dos,
  porque el ruso es el mismo ruso; lo que cambia es el contraste, no el
  temario.
- Los scripts de construcción del sitio, audio, dibujos, tests — todo lo que
  en `espanol-desde-ruso` no depende del idioma, adaptado.
- La metodología de 30 minutos, los principios, la estructura de lección.

Qué NO se comparte:

- El bloque de contraste, palabra por palabra.
- Probablemente buena parte del vocabulario de apoyo y los ejemplos.

## Dónde está cada cosa (cuando haya algo)

- `referencias/` — análisis de los libros que mande el usuario. No se copia
  contenido ajeno; los PDF no se versionan (misma regla que el proyecto
  hermano).
- `programa/` — calendario y documentación del programa, uno por pista una
  vez que el contraste esté claro.
- `curso/en/`, `curso/es/` — las lecciones, cuando existan.
- `scripts/` — se van a portar y adaptar desde
  `../espanol-desde-ruso/scripts/` a medida que haga falta cada uno
  (`construir_sitio.py`, `validar.py`, `generar_audio.py`...), no todos de
  entrada: ese repo tiene más de medio año de ajustes específicos a SU
  dirección (ru→es) que acá no aplican tal cual.
- `tests/` — vacío. La convención del proyecto hermano es escribir la prueba
  cuando aparece el primer caso real que puede fallar, no antes.

## Reglas heredadas de `espanol-desde-ruso` (se mantienen acá)

1. No se inventan datos (precios, fechas, cifras, y aquí además: errores de
   interferencia) — si no está en un libro o no se puede verificar, se marca
   `[VERIFICAR]` o no se escribe.
2. Una lección = 30 minutos, un punto nuevo, 6-10 palabras.
3. Nada generado se publica sin revisión. Acá la revisión tiene un peso
   extra: el usuario no es nativo de ruso, así que su revisión certifica la
   FORMA y el método, no la corrección del ruso en sí — eso lo sostienen los
   libros y, en algún punto, convendría sumar una revisión humana nativa
   antes de publicar de verdad (a decidir más adelante, no bloqueante para
   armar el esqueleto).
4. Variación regional: el español de España/América ya tiene su regla en el
   proyecto hermano (🌎); acá habría que decidir si el ruso de Rusia alcanza
   o si hace falta avisar de variantes (no es un problema hoy, con cero
   contenido escrito).

## Pendiente inmediato

- **Recibir los libros de referencia** del usuario (mencionó que los va a
  mandar). Sin esto no se avanza con contenido.
- Decidir si este repo se conecta a GitHub ahora (vacío) o cuando ya tenga
  algo. Hoy es un repo local sin remoto.
- Nombre de dominio / plataforma de publicación: no se decide todavía, es
  prematuro con cero lecciones.
