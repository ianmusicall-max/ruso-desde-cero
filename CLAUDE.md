# Ruso desde cero · contexto para Claude Code

Curso de ruso **desde cero hasta B2** para hispanohablantes y angloparlantes,
30 minutos al día, en una web nueva con publicidad. Proyecto hermano de
`espanol-desde-ruso` (que enseña español a rusohablantes): mismo método,
dirección inversa. **Leer `programa/plan.md` antes de tocar nada**: ahí están
las decisiones y su porqué.

## Dónde está cada cosa

- `programa/plan.md` — qué es el curso, el tamaño (4 niveles × 365 días), la
  base (Tochka Ru), la línea de los derechos de autor y qué se mejora.
- `programa/calendario.yaml` — **la única fuente de verdad** de niveles,
  unidades, semanas, días y temas. Cualquier cuenta sale de aquí.
- `programa/metodologia.md` — la lección de 30 minutos y sus apartados.
- `programa/contrastiva-ru-es.md`, `programa/contrastiva-ru-en.md` — los
  errores predecibles de cada lengua de partida: alimentan el bloque de
  contraste y los distractores de las pruebas.
- `referencias/` — análisis de los libros (estructura y secuencia, nunca su
  contenido). Los PDF no se versionan: viven en el repositorio privado y
  temporal `libros-ruso-temp`.
- `curso/es/<nivel>/semana-NN/dia-N.md` y `curso/en/...` — las lecciones.
  **Las dos pistas comparten el ruso** (textos, diálogos, ejemplos, audio) y
  cambian la explicación y el contraste.
- `scripts/` — `plan.py` (lee el calendario), `validar.py` (forma de las
  lecciones), `construir_sitio.py` (Markdown → `docs/`).
- `tests/` — `python3 -m unittest discover -s tests`.

## Reglas

1. **Una lección = 30 minutos exactos.** Los apartados llevan su franja
   («## 3. Nuevo (8–18 min)» / «## 3. New (8–18 min)»); `validar.py` exige
   0 → 30 contiguo.
2. **Una lección = un punto nuevo y 6–10 palabras** (en B1–B2 hasta 12). Si no
   cabe, son dos días y se cambia el calendario, no la duración.
3. **Toda lección de tipo `leccion` lleva el bloque de contraste** («⚠️
   Contraste con el español» / «⚠️ Contrast with English») con el error
   predecible de esa lengua. Es lo que hace que el curso sea «desde el
   español» o «desde el inglés».
4. **El tema de la lección es el del calendario**, carácter por carácter. Si
   hay que cambiarlo, se cambia primero el YAML.
5. **Las claves son obligatorias** si hay ejercicios.
6. **Nada se publica sin revisión.** Todo nace con `revisado: false`. El autor
   del curso no es nativo de ruso: su revisión certifica el método; la
   corrección del ruso la sostienen las fuentes y, antes de publicar en
   serio, la mirada de un nativo.
7. **No se inventan datos** (precios, fechas, cifras, ni errores de
   interferencia): si no se sabe, `[VERIFICAR]`.
8. **Todo el ruso lleva acento** (tilde combinante U+0301 sobre la vocal
   tónica: молоко́). La ё no lo lleva: siempre es tónica. Para el audio y para
   corregir respuestas, el acento se quita.
9. **Ni un texto, diálogo, ejercicio ni dibujo de los libros.** De Tochka Ru y
   compañía se toma el orden, los temas y la forma de la lección; el
   contenido se escribe para este curso. Ver `programa/plan.md`.
10. **Nada de política ni de guerra** en la cultura ni en la historia.

## Estado (2026-11-19)

- Leídos los índices y la anatomía de lección de los siete libros, incluido
  **Tochka Ru A1** (subido por el usuario en tres partes al chat; no está en
  `libros-ruso-temp` y hay que subirlo ahí para las sesiones siguientes).
- Escritos `programa/plan.md` y los análisis de `referencias/`.
- En curso: calendario, metodología, listas de contraste, el motor del
  sitio y la semana piloto del A1 en las dos pistas.
- Pendiente del usuario: **nombre y dominio** de la web (no se puede crear el
  repositorio de GitHub desde esta sesión: lo crea él, vacío, y se conecta).

## El A1 sigue a Tochka Ru A1, lección por lección

Tochka Ru A1 tiene 22 lecciones en 6 unidades más seis de «Русский на каждый
день». En este curso cada lección suya es **una unidad de dos semanas**, salvo
la 1.1 (todo el alfabeto), que se abre en dos: la unidad 1 son las letras y la
2 los sonidos y las reglas de lectura. La unidad 24 cierra con el repaso. Las
«Русский на каждый день» (tarjeta migratoria, intercambiar contactos, hotel,
tienda de ropa, postal, cita) van en los domingos de la primera semana de la
unidad donde encajan. El detalle está en `programa/calendario.yaml`.

Lo que Tochka Ru A1 no trae y se completa con «Русский язык сегодня A1+»: la
**fonética** de cada lección y la **entonación** (ИК-1 a ИК-5).
