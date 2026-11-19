# Metodología

Cómo es una lección y por qué. Las decisiones de fondo están en
`programa/plan.md`; aquí está la forma, que `scripts/validar.py` comprueba.

## Los principios

1. **Treinta minutos, con reloj.** Cada apartado lleva su franja en el
   título y suman 0 → 30 sin huecos. Quien estudia solo necesita saber
   cuánto le falta.
2. **Un punto nuevo por día.** Una forma, una regla o un grupo de letras, con
   6–10 palabras (hasta 12 en B1–B2). Lo que no cabe es otro día.
3. **El ruso se oye antes de leerse.** Cada frase rusa tiene su ▶. En el A1,
   los diálogos se aprenden de oído como bloques antes de conocer todas sus
   letras (es lo que hace Tochka Ru: «Как тебя́ зову́т?» llega antes que la
   я).
4. **Todo el ruso con acento** (U+0301), siempre, no solo en las palabras
   nuevas. En ruso la sílaba tónica no se adivina y cambia la palabra
   (за́мок «castillo» / замо́к «cerradura»).
5. **El error se nombra antes de cometerlo.** El bloque de contraste dice
   qué te va a hacer equivocarte *tu* lengua, con el ejemplo malo tachado.
   Sale de `contrastiva-ru-es.md` o `contrastiva-ru-en.md`.
6. **Nada de «trabajen en parejas».** Cada tarea de Tochka Ru pensada para el
   aula tiene aquí su versión para una persona sola (tabla de abajo).
7. **La respuesta está debajo, plegada.** Nunca al final del libro.
8. **Lo de ayer vuelve hoy.** El calentamiento repasa con tarjetas las
   palabras de los días anteriores; el sábado repasa la semana; la prueba de
   unidad, las dos semanas.
9. **La explicación, en la lengua del alumno; el ruso, en ruso.** Las
   consignas de los ejercicios van en ruso con su traducción debajo en el
   A1 (como Tochka Ru), y en ruso solo desde el A2, que es lo que pide el
   examen.

## Lo que en un aula se hace en pareja, y aquí

| En Tochka Ru | Aquí |
|---|---|
| «Слу́шайте диало́г и игра́йте в па́рах» | escuchar el diálogo; después **tu turno**: el diálogo con tu parte en blanco, la dices en voz alta, y la página te deja grabarte y compararte con el ▶ |
| entrevista al compañero | **te entrevistas a ti**: las preguntas, con su ▶, y tú contestas en voz alta o por escrito |
| «bola de nieve» en grupo | **la cadena que crece**: la frase se alarga palabra a palabra y la repites entera cada vez |
| «Что я зна́ю?» al cerrar | **«Ya puedo decir…»** / «I can now say…», con las frases del día y su ▶ |
| el recuadro del modismo | igual: literal y real, en la lengua del alumno |

## La lección (`tipo: leccion`)

| Apartado (es) | Apartado (en) | Franja | Qué lleva |
|---|---|---|---|
| 1. Calentamiento | 1. Warm-up | 0–3 | tarjetas de días anteriores; el día 1, un saludo de oído |
| 2. Fonética | 2. Pronunciation | 3–8 | un sonido, una regla de lectura o una entonación: escuchar, repetir, leer |
| 3. Nuevo | 3. New | 8–18 | el punto del día: diálogo o texto modelo, explicación, tabla y **⚠️ el contraste** |
| 4. Práctica | 4. Practice | 18–25 | ejercicios А, Б, В… con clave |
| 5. Tu turno | 5. Your turn | 25–29 | producir: tu parte del diálogo, grabarte, escribir dos frases |
| 6. Cierre | 6. Wrap-up | 29–30 | «Ya puedo decir…» / «I can now say…» |

Después, sin franja: **Vocabulario del día** / **Today's vocabulary** (tabla
de tres columnas: ruso · traducción · ejemplo) y **Respuestas** /
**Answers**.

El bloque de contraste es un `### ⚠️ Contraste con el español` /
`### ⚠️ Contrast with English` dentro de «Nuevo».

Las franjas pueden moverse si el día lo pide (un día de alfabeto puede dar
más tiempo a «Fonética»), pero tienen que seguir sumando 0 → 30.

## El repaso (`tipo: repaso`, sábado de la primera semana)

1. Calentamiento (0–3) · 2. Fonética (3–8) · 3. Mini-test (8–23) ·
4. Tu turno (23–29) · 5. Cierre (29–30). Respuestas.

## La cultura (`tipo: cultura`, domingos)

1. Antes de leer (0–5) · 2. Texto (5–18) · 3. Palabras (18–23) · 4. Tarea
(23–29) · 5. Cierre (29–30). Respuestas. El domingo de la segunda semana de
cada unidad trae el **episodio** de la historia, sin vocabulario nuevo: si se
entiende, la unidad funcionó. En el A1, el domingo de la primera semana es
«ruso de todos los días» (formularios, hotel, tienda…) cuando la unidad lo
trae.

## La prueba de unidad (`tipo: prueba`, sábado de la segunda semana)

1. Instrucciones (0–2) · 2. Prueba (2–25) · 3. Clave y puntuación (25–29) ·
4. Qué repasar (29–30). Quince preguntas en tres bloques, con la respuesta
correcta **repartida** entre las letras (la lección del proyecto hermano: un
test donde casi todas son la б se aprueba sin saber nada). Los distractores
salen de la lista de errores de la pista.

## Las consignas

En el A1 la consigna va en ruso y debajo en la lengua del alumno, en
cursiva:

> **Слу́шайте и повторя́йте.**
> *Escucha y repite.*

Así el alumno aprende las veinte consignas que se repiten todo el curso
(слу́шайте, чита́йте, пиши́те, отве́тьте, вста́вьте…) sin estudiarlas.

## Los códigos fijos de todo el curso

- **Los casos**, siempre con su número y su color: ① nominativo, ②
  genitivo, ③ dativo, ④ acusativo, ⑤ instrumental, ⑥ preposicional. El
  número es el orden escolar ruso (И Р Д В Т П).
- **El acento**: tilde combinante U+0301. La ё nunca la lleva.
- **Lo incorrecto**, tachado: ~~Я есть студе́нт~~.
- **La variante coloquial**, marcada 💬; **la formal**, 🎩.
