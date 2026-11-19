# Ruso desde cero

Un curso de ruso de A0 a B2, 30 minutos al día, en dos pistas que comparten
el mismo ruso:

- **Español → ruso**, en `curso/es/`
- **Inglés → ruso**, en `curso/en/`

Cuatro niveles (A1, A2, B1, B2) de 365 días cada uno, con la salida de cada
nivel puesta en su examen oficial (ТЭУ, ТБУ, ТРКИ-1, ТРКИ-2). La columna
vertebral es la secuencia de Tochka Ru; el contenido se escribe entero para
este curso.

Proyecto hermano de `espanol-desde-ruso` (mismo método, dirección inversa).
`CLAUDE.md` tiene el estado y las reglas; `programa/plan.md`, las decisiones y
su porqué.

## Uso

```bash
python3 scripts/plan.py --nivel a1        # el calendario de un nivel
python3 scripts/validar.py                # la forma de todas las lecciones
python3 scripts/construir_sitio.py        # Markdown → docs/
python3 -m unittest discover -s tests     # las pruebas
```

Hace falta Python 3 con `markdown` y `PyYAML`.

## Estado

La semana 1 del A1 está escrita en las dos pistas (14 lecciones) y el sitio
se construye en `docs/`. Todo está en borrador (`revisado: false`) hasta que
lo revise el profesor y, antes de publicar en serio, un nativo de ruso.
