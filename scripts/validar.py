#!/usr/bin/env python3
"""Comprueba la forma de las lecciones.

    python3 scripts/validar.py                       # todas
    python3 scripts/validar.py curso/es/a1/semana-01/dia-1.md

Lo que exige (programa/metodologia.md, reglas de CLAUDE.md):

- el frontmatter completo, y que el día exista en el calendario con el mismo
  tipo y **el mismo tema, carácter por carácter** (regla 4);
- los apartados del tipo de día, en orden, con sus franjas de 0 a 30
  minutos sin huecos (regla 1);
- en una lección: el bloque de contraste (regla 3) y el vocabulario del día
  con 6–10 filas (12 en B1–B2) (regla 2);
- la clave, si hay ejercicios (regla 5);
- **todo el ruso con acento** (regla 8): una palabra cirílica de dos o más
  vocales sin U+0301 ni ё es un error. Las siglas en mayúsculas no cuentan;
- ninguna letra latina dentro de una palabra cirílica: una «о» latina en
  «кот» no se ve a ojo, rompe el audio y la búsqueda;
- `revisado: true` solo sin [VERIFICAR] pendiente (regla 6).
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import plan  # noqa: E402

RAIZ = plan.RAIZ
CURSO = RAIZ / "curso"

APARTADOS = {
    "es": {
        "leccion": ["Calentamiento", "Fonética", "Nuevo", "Práctica", "Tu turno", "Cierre"],
        "repaso": ["Calentamiento", "Fonética", "Mini-test", "Tu turno", "Cierre"],
        "cultura": ["Antes de leer", "Texto", "Palabras", "Tarea", "Cierre"],
        "prueba": ["Instrucciones", "Prueba", "Clave y puntuación", "Qué repasar"],
    },
    "en": {
        "leccion": ["Warm-up", "Pronunciation", "New", "Practice", "Your turn", "Wrap-up"],
        "repaso": ["Warm-up", "Pronunciation", "Mini-test", "Your turn", "Wrap-up"],
        "cultura": ["Before you read", "Text", "Words", "Task", "Wrap-up"],
        "prueba": ["Instructions", "Test", "Key and score", "What to review"],
    },
}
CONTRASTE = {"es": "### ⚠️ Contraste con el español", "en": "### ⚠️ Contrast with English"}
VOCABULARIO = {"es": "## Vocabulario del día", "en": "## Today's vocabulary"}
RESPUESTAS = {"es": "## Respuestas", "en": "## Answers"}
CON_CLAVE = ("leccion", "repaso", "cultura", "prueba")
FILAS_VOCABULARIO = {"a1": (6, 10), "a2": (6, 10), "b1": (6, 12), "b2": (6, 12)}

CAMPOS = ("nivel", "semana", "dia", "tipo", "tema", "revisado")
APARTADO = re.compile(r"^## (\d+)\. (.+?) \((\d+)[–-](\d+) min\)\s*$")

ACENTO = "́"
VOCALES = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")
PALABRA = re.compile(r"[A-Za-zА-Яа-яЁё́]+(?:-[A-Za-zА-Яа-яЁё́]+)*")
CIRILICO = re.compile(r"[А-Яа-яЁё]")
LATINO = re.compile(r"[A-Za-z]")
# Palabras rusas de dos o más vocales que de verdad son átonas.
SIN_ACENTO = {"из-за", "из-под"}


def leer(ruta: pathlib.Path) -> tuple[dict, str]:
    """El frontmatter y el cuerpo de una lección."""
    texto = ruta.read_text(encoding="utf-8")
    if not texto.startswith("---\n"):
        raise ValueError("falta el frontmatter (--- al principio)")
    _, cabeza, cuerpo = texto.split("---\n", 2)
    meta = yaml.safe_load(cabeza) or {}
    return meta, cuerpo


def pista_de(ruta: pathlib.Path) -> str:
    partes = ruta.resolve().relative_to(CURSO).parts
    return partes[0]


def _sin_codigo(texto: str) -> str:
    """El texto sin código y sin asteriscos. Los asteriscos fuera porque la
    negrita también marca una letra dentro de una palabra («М**о**сква́», para
    señalar qué о se reduce), y sin quitarlos la palabra se lee en trozos:
    «мната» sin acento, cuando la palabra entera es «ко́мната»."""
    texto = re.sub(r"```.*?```", "", texto, flags=re.S)
    return re.sub(r"`[^`]*`", "", texto).replace("*", "")


def sin_acento(texto: str) -> list[str]:
    """Las palabras rusas de dos o más vocales que no llevan acento."""
    malas = []
    for palabra in PALABRA.findall(_sin_codigo(texto)):
        if not CIRILICO.search(palabra) or LATINO.search(palabra):
            continue
        limpia = palabra.replace(ACENTO, "")
        if len(limpia) > 1 and limpia.isupper():
            continue  # siglas: ТЭУ, ТРКИ
        if sum(c in VOCALES for c in limpia) < 2:
            continue
        if ACENTO in palabra or "ё" in limpia.lower() or limpia.lower() in SIN_ACENTO:
            continue
        malas.append(palabra)
    return malas


def alfabetos_mezclados(texto: str) -> list[str]:
    """Palabras con letras cirílicas y latinas a la vez."""
    return [p for p in PALABRA.findall(_sin_codigo(texto))
            if CIRILICO.search(p) and LATINO.search(p)]


def frases_partidas_en_citas(cuerpo: str) -> list[str]:
    """Dentro de una cita (>) cada línea del Markdown es una línea en pantalla
    (así se escriben los diálogos con su traducción debajo), de modo que una
    frase partida en dos líneas sale partida. Se detecta: una línea que acaba
    en letra o coma seguida de otra que empieza en minúscula."""
    lineas = cuerpo.splitlines()
    malas = []
    for a, b in zip(lineas, lineas[1:]):
        if not (a.startswith("> ") and b.startswith("> ")):
            continue
        ta, tb = a[2:].rstrip(), b[2:].lstrip()
        if not ta or not tb or re.match(r"[-*+] |\d+\. ", ta) or re.match(r"[-*+] |\d+\. ", tb):
            continue
        # Solo prosa en la lengua del alumno: dos líneas de ruso (sílabas,
        # réplicas) van separadas a propósito.
        if (re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü],?$", ta) and re.match(r"[a-záéíóúñü]", tb)):
            malas.append(ta[-30:] + " / " + tb[:30])
    return malas


def filas_de_tabla(cuerpo: str, titulo: str) -> list[list[str]]:
    """Las filas de la primera tabla debajo de un `## titulo`."""
    if titulo not in cuerpo:
        return []
    resto = cuerpo.split(titulo, 1)[1]
    resto = resto.split("\n## ", 1)[0]
    filas = [ln for ln in resto.splitlines() if ln.strip().startswith("|")]
    datos = [f for f in filas[2:]]  # fuera la cabecera y el separador
    return [[c.strip() for c in f.strip().strip("|").split("|")] for f in datos]


def validar(ruta: pathlib.Path, dias: dict[str, plan.Dia] | None = None) -> list[str]:
    """Los problemas de una lección; lista vacía si está bien."""
    dias = dias if dias is not None else plan.por_ruta()
    problemas: list[str] = []
    try:
        meta, cuerpo = leer(ruta)
    except Exception as e:  # noqa: BLE001
        return [f"no se puede leer: {e}"]
    pista = pista_de(ruta)
    if pista not in plan.PISTAS:
        return [f"pista desconocida: {pista}"]

    faltan = [c for c in CAMPOS if c not in meta]
    if faltan:
        return [f"faltan en el frontmatter: {', '.join(faltan)}"]
    clave = f"{meta['nivel']}/semana-{int(meta['semana']):02d}/dia-{int(meta['dia'])}"
    esperada = ruta.resolve().relative_to(CURSO / pista).with_suffix("").as_posix()
    if clave != esperada:
        problemas.append(f"el frontmatter dice {clave} y el archivo está en {esperada}")
    dia = dias.get(clave)
    if dia is None:
        return problemas + [f"{clave} no existe en el calendario"]
    if not dia.detallado:
        problemas.append(f"{clave} no está detallado en el calendario: se detalla antes de escribir")
    if meta["tipo"] != dia.tipo:
        problemas.append(f"tipo {meta['tipo']!r}, el calendario dice {dia.tipo!r}")
    if meta["tema"] != dia.tema(pista):
        problemas.append(f"tema distinto del calendario:\n    lección:    {meta['tema']}\n"
                         f"    calendario: {dia.tema(pista)}")
    if dia.unidad is not None and meta.get("unidad") != dia.unidad:
        problemas.append(f"unidad {meta.get('unidad')!r}, el calendario dice {dia.unidad}")
    if not isinstance(meta["revisado"], bool):
        problemas.append("revisado tiene que ser true o false")
    if re.search(r"^# ", cuerpo, flags=re.M):
        problemas.append("el título (#) lo pone el sitio a partir del frontmatter: no va en el cuerpo")

    esperados = APARTADOS[pista].get(dia.tipo)
    if esperados:
        encontrados = [APARTADO.match(ln) for ln in cuerpo.splitlines()]
        encontrados = [m for m in encontrados if m]
        nombres = [m.group(2) for m in encontrados]
        if nombres != esperados:
            problemas.append(f"apartados {nombres}, se esperaban {esperados}")
        for i, m in enumerate(encontrados, 1):
            if int(m.group(1)) != i:
                problemas.append(f"el apartado «{m.group(2)}» lleva el número {m.group(1)}, le toca {i}")
        minuto = 0
        for m in encontrados:
            ini, fin = int(m.group(3)), int(m.group(4))
            if ini != minuto:
                problemas.append(f"«{m.group(2)}» empieza en el minuto {ini}, el anterior acabó en {minuto}")
            if fin <= ini:
                problemas.append(f"«{m.group(2)}» acaba antes de empezar ({ini}–{fin})")
            minuto = fin
        if encontrados and minuto != 30:
            problemas.append(f"la lección acaba en el minuto {minuto}, no en el 30")

    if dia.tipo == "leccion":
        if CONTRASTE[pista] not in cuerpo:
            problemas.append(f"falta el bloque «{CONTRASTE[pista]}»")
        filas = filas_de_tabla(cuerpo, VOCABULARIO[pista])
        minimo, maximo = FILAS_VOCABULARIO[dia.nivel]
        if not filas:
            problemas.append(f"falta «{VOCABULARIO[pista]}» con su tabla")
        elif not minimo <= len(filas) <= maximo:
            problemas.append(f"el vocabulario del día tiene {len(filas)} palabras: van de {minimo} a {maximo}")
    if dia.tipo in CON_CLAVE and RESPUESTAS[pista] not in cuerpo:
        problemas.append(f"falta «{RESPUESTAS[pista]}»")

    malas = sin_acento(cuerpo) + sin_acento(meta["tema"])
    if malas:
        problemas.append("palabras rusas sin acento: " + ", ".join(sorted(set(malas))))
    mezcladas = alfabetos_mezclados(cuerpo) + alfabetos_mezclados(meta["tema"])
    if mezcladas:
        problemas.append("letras latinas dentro de palabras rusas: " + ", ".join(sorted(set(mezcladas))))
    for partida in frases_partidas_en_citas(cuerpo):
        problemas.append(f"frase partida dentro de una cita (en pantalla sale cortada): «{partida}»")
    if meta["revisado"] is True and "[VERIFICAR" in cuerpo:
        problemas.append("está marcada como revisada pero tiene un [VERIFICAR] pendiente")
    return problemas


def lecciones() -> list[pathlib.Path]:
    return sorted(p for pista in plan.PISTAS for p in (CURSO / pista).glob("*/semana-*/dia-*.md"))


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    rutas = [pathlib.Path(a) for a in argv] or lecciones()
    dias = plan.por_ruta()
    errores = 0
    for ruta in rutas:
        problemas = validar(ruta, dias)
        if problemas:
            errores += 1
            print(f"✗ {ruta}")
            for p in problemas:
                print(f"    {p}")
    print(f"{len(rutas)} lecciones, {errores} con problemas")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
