#!/usr/bin/env python3
"""El modelo del calendario: niveles, unidades, semanas y días.

    python3 scripts/plan.py              # resumen de los cuatro niveles
    python3 scripts/plan.py --nivel a1   # los 365 días del A1

Lee `programa/calendario.yaml` y reparte los 365 días de cada nivel:

- semanas 1–48: 24 unidades de dos semanas. En la primera semana de la
  unidad, días 1–5 lección, 6 repaso, 7 cultura; en la segunda, días 1–5
  lección, 6 prueba de unidad, 7 cultura con episodio;
- semanas 49–52: la fase final (simulacros del examen del nivel);
- día 365 (semana 53, día 1): reserva.

Una unidad que todavía no trae `dias` se reparte en días **genéricos**: el
tipo sale de la posición y el título es «nombre de la unidad · día N». No se
pueden escribir: `validar.py` exige que el tema de la lección sea el del
calendario, y antes de escribir una unidad se detallan sus 14 días en el YAML.
"""
from __future__ import annotations

import argparse
import dataclasses
import pathlib
import sys

import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CALENDARIO = RAIZ / "programa" / "calendario.yaml"

PISTAS = ("es", "en")
DIAS_POR_NIVEL = 365
UNIDADES = 24

SEMANA_1 = ("leccion",) * 5 + ("repaso", "cultura")
SEMANA_2 = ("leccion",) * 5 + ("prueba", "cultura")

# Las cinco pruebas de los exámenes rusos (ТЭУ, ТБУ, ТРКИ-1, ТРКИ-2): la
# forma es la misma en los cuatro niveles; cambia la dificultad.
SUBTESTS = (
    ("Ле́ксика и грамма́тика", "léxico y gramática", "vocabulary and grammar"),
    ("Чте́ние", "lectura", "reading"),
    ("Аудирова́ние", "audición", "listening"),
    ("Письмо́", "escritura", "writing"),
    ("Говоре́ние", "expresión oral", "speaking"),
)


@dataclasses.dataclass(frozen=True)
class Dia:
    nivel: str
    numero: int            # 1–365 dentro del nivel
    semana: int            # 1–53
    dia: int               # 1–7
    tipo: str
    unidad: int | None     # None en la fase final
    ru: str
    es: str
    en: str
    foco: str = ""
    detallado: bool = False

    @property
    def ruta(self) -> str:
        """La ruta de la lección dentro de una pista, sin extensión."""
        return f"{self.nivel}/semana-{self.semana:02d}/dia-{self.dia}"

    def tema(self, pista: str) -> str:
        return getattr(self, pista)


def cargar(ruta: pathlib.Path = CALENDARIO) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _fase_final(examen: str) -> list[tuple[str, str, str, str]]:
    """Los 28 días de las semanas 49–52: (tipo, ru, es, en)."""
    dias = []
    for n in (1, 2):
        sim = [("simulacro", f"Про́бный тест {n}: {ru.lower()}",
                f"Simulacro {n}: {es}", f"Mock exam {n}: {en}") for ru, es, en in SUBTESTS]
        cierre = [("repaso", "Повторе́ние: рабо́та над оши́бками",
                   "Repaso: lo que falló en el simulacro", "Review: what went wrong in the mock exam"),
                  ("cultura", "Культу́ра", "Cultura", "Culture")]
        refuerzo = [("repaso", f"Повторе́ние: {ru.lower()}", f"Refuerzo: {es}", f"Review: {en}")
                    for ru, es, en in SUBTESTS]
        dias += sim + cierre
        if n == 1:
            dias += refuerzo + cierre
    dias += [
        ("proyecto", "Прое́кт: расска́з о себе́", "Proyecto: contar tu historia", "Project: tell your story"),
        ("proyecto", "Прое́кт: запи́сываем", "Proyecto: la grabación", "Project: recording it"),
        ("repaso", "Повторе́ние: грамма́тика у́ровня", "Repaso: la gramática del nivel", "Review: the level's grammar"),
        ("repaso", "Повторе́ние: ле́ксика у́ровня", "Repaso: el vocabulario del nivel", "Review: the level's vocabulary"),
        ("repaso", "Перед экза́меном", "Antes del examen", "Before the exam"),
        ("examen", f"Экза́мен: {examen}", f"Examen final: {examen}", f"Final exam: {examen}"),
        ("cultura", "Что да́льше", "Y ahora, ¿qué?", "What comes next"),
    ]
    assert len(dias) == 28, len(dias)
    return dias


def dias_del_nivel(nivel: dict) -> list[Dia]:
    """Los 365 días de un nivel, en orden."""
    codigo = nivel["codigo"]
    unidades = nivel["unidades"]
    if len(unidades) != UNIDADES:
        raise ValueError(f"{codigo}: {len(unidades)} unidades, se esperaban {UNIDADES}")
    dias: list[Dia] = []
    numero = 0
    for u in unidades:
        n = u["numero"]
        propios = u.get("dias") or []
        if propios and len(propios) != 14:
            raise ValueError(f"{codigo} U{n}: {len(propios)} días, una unidad tiene 14")
        for k in range(14):
            semana = 2 * (n - 1) + 1 + k // 7
            dia = k % 7 + 1
            tipo_por_posicion = (SEMANA_1 if k < 7 else SEMANA_2)[dia - 1]
            numero += 1
            if propios:
                d = propios[k]
                if d["tipo"] != tipo_por_posicion:
                    raise ValueError(f"{codigo} U{n} día {k + 1}: tipo {d['tipo']!r}, "
                                     f"la posición pide {tipo_por_posicion!r}")
                dias.append(Dia(codigo, numero, semana, dia, d["tipo"], n,
                                d["ru"], d["es"], d["en"], d.get("foco", "").strip(), True))
            else:
                dias.append(Dia(codigo, numero, semana, dia, tipo_por_posicion, n,
                                u["ru"], f"{u['es']} · día {k + 1}", f"{u['en']} · day {k + 1}"))
    for k, (tipo, ru, es, en) in enumerate(_fase_final(nivel["fase_final"]["examen"])):
        numero += 1
        dias.append(Dia(codigo, numero, 49 + k // 7, k % 7 + 1, tipo, None, ru, es, en))
    numero += 1
    dias.append(Dia(codigo, numero, 53, 1, "reserva", None,
                    "Резе́рвный день", "Día de reserva", "Spare day"))
    assert len(dias) == DIAS_POR_NIVEL, (codigo, len(dias))
    return dias


def todos(cal: dict | None = None) -> list[Dia]:
    cal = cal or cargar()
    return [d for nivel in cal["niveles"] for d in dias_del_nivel(nivel)]


def por_ruta(cal: dict | None = None) -> dict[str, Dia]:
    return {d.ruta: d for d in todos(cal)}


def niveles(cal: dict | None = None) -> list[dict]:
    return (cal or cargar())["niveles"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--nivel", help="lista los días de un nivel (a1, a2, b1, b2)")
    args = ap.parse_args(argv)
    cal = cargar()
    if args.nivel:
        nivel = next((n for n in cal["niveles"] if n["codigo"] == args.nivel), None)
        if nivel is None:
            print(f"No existe el nivel {args.nivel!r}", file=sys.stderr)
            return 2
        for d in dias_del_nivel(nivel):
            marca = "*" if d.detallado else " "
            print(f"{d.numero:3d} {marca} S{d.semana:02d} D{d.dia} {d.tipo:9s} {d.es}")
        return 0
    for nivel in cal["niveles"]:
        dias = dias_del_nivel(nivel)
        detallados = sum(d.detallado for d in dias)
        print(f"{nivel['codigo']} ({nivel['examen']}): {len(dias)} días, "
              f"{sum(d.tipo == 'leccion' for d in dias)} lecciones, "
              f"{detallados} días detallados en el calendario")
    return 0


if __name__ == "__main__":
    sys.exit(main())
