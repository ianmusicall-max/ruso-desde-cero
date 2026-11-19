"""Pruebas del curso: calendario, validador, las dos pistas y el sitio.

    python3 -m unittest discover -s tests
"""
from __future__ import annotations

import html.parser
import pathlib
import re
import shutil
import sys
import tempfile
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import construir_sitio  # noqa: E402
import plan  # noqa: E402
import validar  # noqa: E402


class TestElCalendario(unittest.TestCase):
    def setUp(self):
        self.cal = plan.cargar()

    def test_cuatro_niveles_de_365_dias(self):
        niveles = plan.niveles(self.cal)
        self.assertEqual([n["codigo"] for n in niveles], ["a1", "a2", "b1", "b2"])
        for n in niveles:
            self.assertEqual(len(plan.dias_del_nivel(n)), 365, n["codigo"])

    def test_cada_nivel_tiene_240_lecciones_y_su_examen(self):
        for n in plan.niveles(self.cal):
            dias = plan.dias_del_nivel(n)
            self.assertEqual(sum(d.tipo == "leccion" for d in dias), 240)
            self.assertEqual(sum(d.tipo == "examen" for d in dias), 1)
            self.assertEqual(dias[-1].tipo, "reserva")

    def test_las_rutas_no_se_repiten(self):
        rutas = [d.ruta for d in plan.todos(self.cal)]
        self.assertEqual(len(rutas), len(set(rutas)))

    def test_un_dia_detallado_trae_su_tema_en_tres_lenguas(self):
        for d in plan.todos(self.cal):
            if d.detallado:
                self.assertTrue(d.ru and d.es and d.en and d.foco, d.ruta)

    def test_el_ruso_del_calendario_lleva_acento(self):
        """Regla 8 también para los títulos: salen en la web."""
        malas = []
        for n in plan.niveles(self.cal):
            malas += validar.sin_acento(n["ru"])
            for u in n["unidades"]:
                malas += validar.sin_acento(u["ru"])
                for d in u.get("dias") or []:
                    malas += validar.sin_acento(d["ru"])
        self.assertEqual(malas, [])


class TestElValidador(unittest.TestCase):
    """Cada regla tiene que saltar con su error. Se arma una copia de una
    lección buena y se le rompe una cosa cada vez."""

    BUENA = RAIZ / "curso" / "es" / "a1" / "semana-01" / "dia-1.md"

    def _con(self, cambio):
        tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        destino = tmp / "curso" / "es" / "a1" / "semana-01" / "dia-1.md"
        destino.parent.mkdir(parents=True)
        destino.write_text(cambio(self.BUENA.read_text(encoding="utf-8")), encoding="utf-8")
        viejo = validar.CURSO
        validar.CURSO = tmp / "curso"
        self.addCleanup(setattr, validar, "CURSO", viejo)
        return validar.validar(destino)

    def test_la_leccion_buena_pasa(self):
        self.assertEqual(self._con(lambda t: t), [])

    def test_una_palabra_sin_acento(self):
        p = self._con(lambda t: t.replace("| ма́ма | mamá | Там ма́ма. |", "| мама | mamá | Там ма́ма. |"))
        self.assertTrue(any("sin acento" in x and "мама" in x for x in p), p)

    def test_una_letra_latina_dentro_de_una_palabra_rusa(self):
        # «кот» con una o latina: no se ve a ojo.
        p = self._con(lambda t: t.replace("| кот | gato |", "| кoт | gato |"))
        self.assertTrue(any("letras latinas" in x for x in p), p)

    def test_un_hueco_en_el_reloj(self):
        p = self._con(lambda t: t.replace("## 4. Práctica (18–25 min)", "## 4. Práctica (19–25 min)"))
        self.assertTrue(any("empieza en el minuto 19" in x for x in p), p)

    def test_sin_contraste(self):
        p = self._con(lambda t: t.replace("### ⚠️ Contraste con el español", "### Nota"))
        self.assertTrue(any("Contraste" in x for x in p), p)

    def test_el_tema_tiene_que_ser_el_del_calendario(self):
        p = self._con(lambda t: t.replace("las letras que ya conoces", "letras conocidas"))
        self.assertTrue(any("tema distinto" in x for x in p), p)

    def test_sin_respuestas(self):
        p = self._con(lambda t: t.split("## Respuestas")[0])
        self.assertTrue(any("Respuestas" in x for x in p), p)

    def test_revisada_con_un_verificar_pendiente(self):
        p = self._con(lambda t: t.replace("revisado: false", "revisado: true") + "\n[VERIFICAR] algo\n")
        self.assertTrue(any("VERIFICAR" in x for x in p), p)

    def test_las_siglas_no_necesitan_acento(self):
        self.assertEqual(validar.sin_acento("ТЭУ, ТРКИ-2 y ТБУ"), [])

    def test_la_negrita_dentro_de_una_palabra_no_la_parte(self):
        """La negrita marca a veces una letra («к**о́**мната», para señalar qué
        о se reduce): la palabra sigue siendo una y lleva su acento."""
        self.assertEqual(validar.sin_acento("к**о́**мната · М**о**сква́"), [])
        self.assertEqual(validar.sin_acento("к**о**мната"), ["комната"])

    def test_la_frase_partida_en_una_cita(self):
        self.assertTrue(validar.frases_partidas_en_citas("> una frase que se parte y\n> sigue aquí\n"))
        self.assertFalse(validar.frases_partidas_en_citas("> ма — мо — ка\n> ам — ом — ак\n"))
        self.assertFalse(validar.frases_partidas_en_citas("> — **Кто там?**\n> *¿Quién es?*\n"))


class TestLasDosPistas(unittest.TestCase):
    def test_todas_las_lecciones_pasan(self):
        dias = plan.por_ruta()
        malas = {str(r): validar.validar(r, dias) for r in validar.lecciones()}
        self.assertEqual({k: v for k, v in malas.items() if v}, {})

    def test_las_dos_pistas_ensenan_las_mismas_palabras_rusas(self):
        """El ruso es uno: lo que cambia entre pistas es la explicación. Si un
        día enseñara palabras distintas en cada pista, el audio, las tarjetas
        y la historia dejarían de poder compartirse."""
        for es in (RAIZ / "curso" / "es").glob("*/semana-*/dia-*.md"):
            en = RAIZ / "curso" / "en" / es.relative_to(RAIZ / "curso" / "es")
            if not en.exists():
                continue
            _, cuerpo_es = validar.leer(es)
            _, cuerpo_en = validar.leer(en)
            rusas_es = [f[0] for f in validar.filas_de_tabla(cuerpo_es, validar.VOCABULARIO["es"])]
            rusas_en = [f[0] for f in validar.filas_de_tabla(cuerpo_en, validar.VOCABULARIO["en"])]
            self.assertEqual(rusas_es, rusas_en, es.name)


class _Enlaces(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.enlaces = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.enlaces.append(a["href"])
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        if tag == "link" and a.get("href") and a.get("rel") == "stylesheet":
            self.scripts.append(a["href"])


class TestElSitio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp())
        cfg = construir_sitio.cargar_config()
        cfg = dict(cfg, adsense={"cliente": ""}, dominio="")
        cls.resumen = construir_sitio.construir(cls.tmp, cfg=cfg)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def _paginas(self):
        return sorted(self.tmp.rglob("*.html"))

    def test_cada_leccion_escrita_tiene_su_pagina(self):
        for pista in plan.PISTAS:
            for md in (RAIZ / "curso" / pista).glob("*/semana-*/dia-*.md"):
                rel = md.relative_to(RAIZ / "curso").with_suffix(".html")
                self.assertTrue((self.tmp / rel).exists(), rel)

    def test_ningun_enlace_interno_roto(self):
        rotos = []
        for p in self._paginas():
            lector = _Enlaces()
            lector.feed(p.read_text(encoding="utf-8"))
            for href in lector.enlaces + lector.scripts:
                if re.match(r"^(https?:|mailto:|#)", href):
                    continue
                destino = (p.parent / href.split("#")[0]).resolve()
                if not destino.exists():
                    rotos.append(f"{p.relative_to(self.tmp)} → {href}")
        self.assertEqual(rotos, [])

    def test_nada_de_terceros_sin_anuncios(self):
        """La política de privacidad dice que no se carga nada de fuera: tiene
        que seguir siendo verdad en todas las páginas."""
        for p in self._paginas():
            texto = p.read_text(encoding="utf-8")
            self.assertNotIn("googlesyndication", texto, p.name)
            lector = _Enlaces()
            lector.feed(texto)
            externos = [s for s in lector.scripts if re.match(r"^https?:", s)]
            self.assertEqual(externos, [], p.name)

    def test_no_se_escapa_ninguna_llave_sin_rellenar(self):
        for p in self._paginas():
            texto = p.read_text(encoding="utf-8")
            for llave in ("{raiz}", "{lecciones}", "{correo}", "{ICONO_TEMA}"):
                self.assertNotIn(llave, texto, p.name)

    def test_la_leccion_lleva_contraste_reloj_respuestas_y_aviso(self):
        texto = (self.tmp / "es" / "a1" / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertIn('<aside class="contraste">', texto)
        self.assertEqual(texto.count('class="parte"'), 6)
        self.assertIn('<details class="clave"', texto)
        self.assertIn('class="borrador"', texto)
        self.assertIn('data-leccion="es/a1/semana-01/dia-1"', texto)

    def test_el_cambio_de_idioma_lleva_a_la_misma_leccion(self):
        texto = (self.tmp / "es" / "a1" / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertIn('href="../../../en/a1/semana-01/dia-1.html"', texto)

    def test_las_fuentes_y_el_guion_estan(self):
        self.assertTrue((self.tmp / "progreso.js").exists())
        self.assertEqual(len(list((self.tmp / "fonts").glob("*.woff2"))), 10)

    def test_sin_dominio_no_hay_cname_ni_sitemap(self):
        self.assertFalse((self.tmp / "CNAME").exists())
        self.assertFalse((self.tmp / "sitemap.xml").exists())

    def test_el_tachado_se_ve_tachado(self):
        self.assertIn("<del>mal</del>", construir_sitio.md("esto está ~~mal~~"))


if __name__ == "__main__":
    unittest.main()
