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

## Estado (2026-11-20)

- Leídos los índices y la anatomía de lección de los siete libros, incluido
  **Tochka Ru A1** (subido por el usuario en tres partes al chat; **no está
  en `libros-ruso-temp`** y hay que subirlo ahí para las sesiones
  siguientes). Su secuencia está en `referencias/tochka-ru.md`.
- Hechos: `programa/plan.md`, calendario A1–B2, metodología, las dos listas
  de contraste, el motor (`plan.py`, `validar.py`, `construir_sitio.py`) y
  38 pruebas.
- **Escrita la unidad 1 del A1 entera en las dos pistas** (28 lecciones,
  semanas 1 y 2): las 33 letras en diez tandas, la о átona, presentarse,
  la entonación de la pregunta, Как дела́, спаси́бо / пожа́луйста, ты / вы,
  las despedidas, el repaso con mini-test, el día de cultura del alfabeto,
  la prueba de la unidad y el **episodio 1** de la historia.
- **La historia está escrita** (`programa/historia.md`): Camila (Lima) y Tom
  (Toronto), su vecina Kira, médica, su hijo Misha y el gato Bársik. Los 24
  episodios del A1 viven en el calendario (campo `episodio`).
- **Escrita la unidad 2 entera en las dos pistas** (28 lecciones más,
  semanas 3 y 4): no…, sino… (не…, а…), las reglas de lectura (la е y la я
  átonas, duras y blandas, el final que se apaga, las palabras con trampa),
  ИК-2 e ИК-4, la escala de Как дела́?, pedir en un café, las palabras
  internacionales y su acento, las respuestas cortas, el repaso, el día de
  los préstamos y los falsos amigos, la prueba y el **episodio 2**. Probadas
  en Chromium la prueba y el mini-test: 15/15, 0/15, enlaces vivos y sin
  JavaScript en papel.
- **Escrita la unidad 3 entera en las dos pistas** (semanas 5 y 6):
  saludar según la hora y de usted, los países con из como bloque, он /
  она́ / они́, las nacionalidades en -ец / -ка, las lenguas con по-,
  немно́го y чуть-чу́ть, говори́ть entero, ты o вы, el kit de supervivencia
  (Как по-ру́сски…? Повтори́те…), la presentación entera, el repaso, el día
  del patronímico y la анке́та (РнкД 1), la prueba y el **episodio 3**.
  84 lecciones en total.
- **Escrita la unidad 4 entera en las dos pistas** (semanas 7 y 8): dónde
  está algo y cómo se pregunta, он / она́ / оно́ por la terminación, почему́
  y потому́ что con las dos trampas del género (la -ь y los hombres en -а),
  спра́ва / сле́ва / в це́нтре, los números hasta 20, el repaso, el metro de
  Moscú, меня́ / тебя́ / его́ / её con зову́т, la conversación entera en la
  calle, la asimilación dentro de la palabra, mi ciudad, la prueba y el
  **episodio 4**. **112 lecciones en total.**
- Siguiente: la unidad 5. Antes, detallar sus 14 días en el calendario con
  la ficha de Tochka Ru A1.
- **Las pruebas y los mini-tests se contestan pulsando** (`scripts/pruebas.py`
  + `test.js`): el lector saca preguntas y clave del propio Markdown y, ante
  cualquier duda, devuelve None y la página se queda en papel. Al terminar,
  el resultado manda a la lección de cada fallo. Probado en Chromium:
  acertando todo, fallando todo y sin JavaScript.
- **Los libros están leídos enteros** (2026-11-19): los cinco escaneos
  pasaron por Tesseract (el texto, solo en `libros-ruso-temp/ocr`), y cada
  tramo lo fichó un lector en `referencias/lecciones/`: Tochka Ru A1, A2
  (libro y cuaderno) y B1.1, Русский язык сегодня, Я пишу по-русски,
  Дорога в Россию 2 y Russian in Exercises. Las fichas señalan desajustes
  del calendario A2–B1 que hay que corregir antes de detallar esas unidades.
- **El ritmo lo elige el alumno** (`programa/plan.md`): la lección es de 30
  minutos y una hora al día son dos lecciones. Con una hora, de cero a A2 en
  un año y a B2 en dos; «Ruso en un año» es ese plan.
- **El repositorio existe y el curso está subido**:
  `ianmusicall-max/ruso-desde-cero`, público, rama **`main`** (2026-11-20).
  Al cerrar cada unidad: `construir_sitio.py`, pruebas, commit y `git push`.
- **GitHub Pages está APAGADO a propósito** (2026-11-20) — ver más abajo.
  Mientras tanto el sitio se mira en local (`python3 -m http.server 8000
  --directory docs`) o en el artifact privado que se republica al cerrar
  cada unidad.
- Pendiente del usuario: **nombre y dominio** propios. Con el dominio se
  vuelve a encender Pages, se pone en Custom domain y se escribe en
  `web/sitio.yaml`, que ya genera el `CNAME` y el sitemap solos. Eso es
  además lo que hace falta para pedir AdSense.
- Sin audio todavía: no hay `OPENAI_API_KEY` en el entorno.

## Cómo se escribe una lección (lo aprendido en la semana 1)

- **Dentro de una cita (`>`) cada línea del Markdown es una línea en
  pantalla.** La prosa de una cita va en una sola línea; los diálogos y las
  opciones de un ejercicio que van en varias líneas, dentro de una cita
  (fuera de ella, Markdown junta las líneas en un párrafo). `validar.py`
  caza la frase partida.
- **La negrita puede marcar una letra dentro de una palabra**
  («М**о**сква́»): el validador quita los asteriscos antes de leer. Lo que
  no se puede es citar un trozo de palabra («мната»): sale como ruso sin
  acento. Se dice «el resto de la palabra».
- **Letras latinas dentro de palabras rusas**: se colaron cuatro veces
  escribiendo («до́ktор», «Алекса́ndр», y una «Ó» latina en «О́льга» del
  calendario). A ojo no se ven. `validar.py` las caza —las letras con tilde
  también desde que la «Ó» pasó sin aviso— y una prueba recorre el
  calendario, así que se valida cada lección al salir.
- **La pronunciación aproximada** («Se lee» / «Say it») va en letras
  latinas y con la sílaba tónica en mayúsculas, con la ortografía de cada
  lengua: «niet», «mi-ÑA» en la pista española; «nyet», «mi-NYA» en la
  inglesa. Solo en las primeras semanas: es una muleta.
- **Nada de días de la semana** («el miércoles»): el alumno empieza cuando
  quiere. Se dice «mañana», «el día 7», «la lección 5».
- **El mini-test**: «N. ítem → а) … · б) … · в) …», tres bloques de cinco, y
  la clave como «N б (día N)» para que el resultado mande a su lección. La
  letra correcta 5/5/5, sin tres iguales seguidas ni escaleras (абв, вба):
  se genera con un script, a mano siempre sale un patrón.
- **Transcripciones comprobadas**: Москва́ es [масква́] (la в no se
  ensordece delante de vocal); el calendario y la lista de contraste decían
  [маскфа́] y se corrigió.

## Lo aprendido en la unidad 2

- **Antes de usar una palabra en un diálogo, comprobar que se enseñó.**
  **Здра́вствуйте** se dio por sabida en los días 8 y 9 y no estaba en la
  unidad 1: ahora entra en el día 8. El vocabulario enseñado hasta una
  semana se lista leyendo las tablas «Vocabulario del día» y «3. Palabras»
  de las lecciones anteriores; hay que mirarlo antes de escribir.
- **Hasta el acusativo (unidad 8), nada de complementos que cambien.** Al
  pedir, **Мне вода́** está mal (es **Мне во́ду**): el día 9 pide solo
  bebidas que no cambian y enseña a señalar (**Мне э́то**). Lo mismo con
  cualquier frase con complemento directo.
- **Las terminaciones y los trozos de palabra, entre comillas invertidas**
  (`-ого`): fuera de ellas el validador los lee como palabras rusas sin
  acento, y tiene razón en avisar.
- **Las letras latinas se siguen colando**: «пожа́luйста», «пробле́ma» y
  «пра́вda» en esta unidad. Se valida cada lección al salir, sin
  excepción.
- **El episodio**: el error de cada personaje sale de un bloque de contraste
  ya enseñado (Camila, **Нет зна́ю**; Tom, **вы** a un niño), y lo corrige
  Misha con la construcción de la propia unidad: «Не «нет зна́ю», а «не
  зна́ю»!».
- **Una palabra del calendario se cambia si la lección no puede enseñarla
  bien**, y se cambia primero en el YAML: salieron **минера́льная вода́**
  (pide acusativo) y **ноутбу́к** (su pronunciación depende de la
  asimilación de la unidad 4).

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

## Por qué el curso salía en saludymetabolismo.com (2026-11-20)

El profesor lo encontró abriendo
`https://saludymetabolismo.com/ruso-desde-cero/es/index.html`: el curso de
ruso estaba publicado dentro del dominio del proyecto de salud.

**No lo copió nadie, y el sitio servido era byte a byte el nuestro** (25.263
bytes, con el `dima.png` subido diez minutos antes). Es cómo funciona
GitHub Pages: el repositorio de usuario (`ianmusicall-max.github.io`) tiene
el dominio `saludymetabolismo.com`, y GitHub cuelga de ese dominio **todos
los demás Pages de la cuenta**, en `/<nombre-del-repo>/`. No lo decide
ningún archivo de este repositorio y le pasaría igual a cualquier proyecto
de la misma cuenta.

**Se apagó Pages** (Settings → Pages → Branch: None), que es lo único que lo
separa sin dominio propio. Lo hizo el profesor: **la API de Pages está
bloqueada por el proxy de este contenedor** (403) y no hay ninguna
herramienta de GitHub que la alcance, así que desde aquí no se puede ni leer
el estado ni cambiarlo. Comprobado después: la dirección da 404.

Importa más de lo que parece porque `saludymetabolismo.com` está en revisión
de AdSense, y un curso de ruso a medias colgando del mismo dominio es justo
lo que enturbia una revisión.

**Mientras no haya dominio**, el sitio se mira de dos maneras: en local con
`python3 -m http.server 8000 --directory docs`, o en un **artifact privado**
de claude.ai con los 137 archivos de `docs/` dentro (se republica al cerrar
cada unidad; es una foto, no se actualiza sola).

## Lo aprendido en la unidad 4

- **Las semanas 1 a 4 enseñan el alfabeto con palabras fáciles, y esas
  palabras vuelven.** метро́, музе́й, футбо́л, авто́бус, слова́рь, день y
  дверь se habían enseñado como práctica de lectura y las unidades 3 y 4 las
  presentaban otra vez como nuevas en su «Vocabulario del día»: diez entradas
  repetidas, y вокза́л dos veces en la misma semana. **Se queda la PRIMERA
  enseñanza** y la lección de después las usa como material conocido, que
  además es mejor didáctica: el día del género ya no presenta слова́рь, день
  y дверь como nuevas sino que dice «estas seis ya las conoces; lo que no
  sabías es su género». Antes de escribir una tabla de vocabulario hay que
  volcar lo ya enseñado y comprobar entrada por entrada.
- **Un día de integración no tiene palabras nuevas, y la tabla tiene que
  decirlo.** El día 5 de la semana 6 reúne las seis frases de la unidad 3 y
  su apartado 3 ya avisaba («hoy no hay palabras nuevas: hay un orden»); la
  tabla no, y parecía que las enseñaba. Ahora lleva la nota. Es la única
  repetición que queda a propósito.
- **El episodio puede salir con cero palabras nuevas** si se comprueba antes:
  el 4 usa solo unidades 1 a 4, журна́л incluido, que ya estaba en la semana
  2. Se comprueba volcando el léxico, no de memoria.
- **El error de cada personaje sale de un contraste ya enseñado.** Camila
  dice **Вот он, река́** porque «el río» es masculino en español (error nº 9
  de la lista negra, el de esta unidad) y se corrige sola con la regla del
  día 8; Tom pregunta si en un **магази́н** hay **журна́лы**, que es el falso
  amigo del día 12.
- **Un token con los dos alfabetos se cuela también en la prosa inglesa**:
  «both unstressed **а**'s weaken», con а cirílica y apóstrofo inglés. El
  barrido hay que hacerlo en las dos pistas.
- **La letra correcta de la prueba se reparte con un script** (4/4/4/3, sin
  tres iguales seguidas y sin escalera, con semilla del nombre del fichero);
  a mano siempre sale un patrón. Y se comprueba **contestándola en Chromium
  por el TEXTO de la opción**, no por su letra: por la letra sería repetir la
  cuenta del generador. 15/15 y 0/15 en las dos pistas.
