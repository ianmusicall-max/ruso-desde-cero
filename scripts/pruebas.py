#!/usr/bin/env python3
"""Lee las preguntas de opción múltiple de una lección y su clave.

    python3 scripts/pruebas.py            # qué pruebas y mini-tests se pueden contestar

Las preguntas se escriben así (programa/metodologia.md):

    ### 1. Чте́ние
    1. сок → а) [kok] · б) [sok] · в) [sak]

y la clave, en «## Respuestas» / «## Answers», así:

    **Mini-test:** 1 б (día 2) · 2 б (día 2) …
    **1. Чте́ние:** 1 а (sem. 2, día 1) · …

Lo que se lee de la lección y no de otro sitio, para que una corrección del
profesor en el Markdown llegue sola a la web.

**Falla de forma segura**: si algo no cuadra —menos respuestas que
preguntas, una letra que no está entre las opciones, números que saltan—
`leer` devuelve None y la página se queda como está, en papel. Decirle a
alguien que acertó cuando falló es peor que no ofrecerle el test.
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import plan  # noqa: E402
import validar  # noqa: E402

TIPOS = ("prueba", "repaso")
LETRAS = "абвгд"
PREGUNTA = re.compile(r"^(\d+)\. (.+?) → (.+)$")
OPCION = re.compile(rf"([{LETRAS}])\) (.+?)(?= · [{LETRAS}]\) |$)")
CLAVE = re.compile(rf"(?<![\d.])(\d+) ([{LETRAS}]) \(([^)]*)\)")
REF_SEMANA = re.compile(r"(?:sem\.|wk)\s*(\d+),\s*(?:día|day)\s*(\d+)")
REF_DIA = re.compile(r"(?:día|day)\s*(\d+)")


def _referencia(texto: str, nivel: str, semana: int) -> str | None:
    """«sem. 2, día 1» → «a1/semana-02/dia-1». Un «día 3» suelto es de la
    misma semana que la prueba."""
    m = REF_SEMANA.search(texto)
    if m:
        return f"{nivel}/semana-{int(m.group(1)):02d}/dia-{int(m.group(2))}"
    m = REF_DIA.search(texto)
    if m:
        return f"{nivel}/semana-{semana:02d}/dia-{int(m.group(1))}"
    return None


def leer(ruta: pathlib.Path) -> dict | None:
    """Las preguntas de la lección, con su respuesta y el día que la enseña.
    None si la lección no tiene test o si algo no cuadra."""
    try:
        meta, cuerpo = validar.leer(ruta)
        pista = validar.pista_de(ruta)
    except Exception:  # noqa: BLE001
        return None
    return de_texto(meta, cuerpo, pista)


def de_texto(meta: dict, cuerpo: str, pista: str) -> dict | None:
    """Lo mismo que `leer`, con la lección ya leída (el generador la tiene)."""
    if meta.get("tipo") not in TIPOS or pista not in validar.RESPUESTAS:
        return None
    titulo_clave = validar.RESPUESTAS[pista]
    if titulo_clave not in cuerpo:
        return None
    texto, clave = cuerpo.split(titulo_clave, 1)

    preguntas, bloque = [], ""
    for linea in texto.splitlines():
        if linea.startswith("### "):
            bloque = linea[4:].strip()
            continue
        m = PREGUNTA.match(linea.strip())
        if not m:
            continue
        opciones = OPCION.findall(m.group(3))
        letras = [o[0] for o in opciones]
        if len(opciones) < 2 or letras != list(LETRAS[:len(letras)]):
            return None
        preguntas.append({"n": int(m.group(1)), "bloque": bloque, "pregunta": m.group(2).strip(),
                          "opciones": [[l, t.strip()] for l, t in opciones]})
    if not preguntas or [p["n"] for p in preguntas] != list(range(1, len(preguntas) + 1)):
        return None

    respuestas = {int(n): (letra, ref) for n, letra, ref in CLAVE.findall(re.sub(r"\s+", " ", clave))}
    if sorted(respuestas) != [p["n"] for p in preguntas]:
        return None
    nivel, semana = str(meta["nivel"]), int(meta["semana"])
    for p in preguntas:
        letra, ref = respuestas[p["n"]]
        if letra not in [l for l, _ in p["opciones"]]:
            return None
        p["correcta"] = letra
        p["leccion"] = _referencia(ref, nivel, semana)
    return {"pista": pista, "preguntas": preguntas}


def main() -> int:
    dias = plan.por_ruta()
    for ruta in validar.lecciones():
        meta, _ = validar.leer(ruta)
        if meta.get("tipo") not in TIPOS:
            continue
        test = leer(ruta)
        estado = f"{len(test['preguntas'])} preguntas" if test else "NO se puede leer: se queda en papel"
        print(f"{ruta.relative_to(validar.CURSO)}: {estado}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
