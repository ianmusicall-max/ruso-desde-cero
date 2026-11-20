"""Pruebas del curso: calendario, validador, las dos pistas y el sitio.

    python3 -m unittest discover -s tests
"""
from __future__ import annotations

import html.parser
import json
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
import pruebas  # noqa: E402
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

    def test_el_calendario_no_mezcla_alfabetos(self):
        texto = (RAIZ / "programa" / "calendario.yaml").read_text(encoding="utf-8")
        self.assertEqual(validar.alfabetos_mezclados(texto), [])

    def test_el_ruso_del_calendario_lleva_acento(self):
        """Regla 8 también para los títulos: salen en la web."""
        malas = []
        for n in plan.niveles(self.cal):
            malas += validar.sin_acento(n["ru"])
            for u in n["unidades"]:
                malas += validar.sin_acento(u["ru"])
                for d in u.get("dias") or []:
                    malas += validar.sin_acento(d["ru"])
                if u.get("episodio"):
                    malas += validar.sin_acento(u["episodio"]["ru"])
        self.assertEqual(malas, [])


class TestLaHistoria(unittest.TestCase):
    """Los episodios viven en el calendario y se explican en historia.md: si
    uno de los dos se queda viejo, el otro miente sin que nada falle."""

    def setUp(self):
        self.a1 = plan.niveles(plan.cargar())[0]
        self.historia = (RAIZ / "programa" / "historia.md").read_text(encoding="utf-8")

    def test_cada_unidad_del_a1_tiene_su_episodio(self):
        for u in self.a1["unidades"]:
            ep = u.get("episodio") or {}
            for campo in ("ru", "es", "en", "sinopsis"):
                self.assertTrue(ep.get(campo), f"unidad {u['numero']}: falta episodio.{campo}")

    def test_historia_nombra_los_mismos_episodios(self):
        faltan = [u["episodio"]["ru"] for u in self.a1["unidades"]
                  if u["episodio"]["ru"] not in self.historia]
        self.assertEqual(faltan, [])

    def test_el_dia_14_de_cada_unidad_es_su_episodio(self):
        for u in self.a1["unidades"]:
            dias = u.get("dias") or []
            if dias:
                self.assertEqual(dias[13]["ru"], u["episodio"]["ru"], f"unidad {u['numero']}")


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

    def test_una_vocal_latina_con_tilde_dentro_de_una_palabra_rusa(self):
        # «Óльга» con la Ó latina: pasó al calendario sin que nada avisara.
        self.assertEqual(validar.alfabetos_mezclados("Óльга"), ["Óльга"])
        self.assertEqual(validar.alfabetos_mezclados("О́льга, habitación, mi-ÑA"), [])

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


class TestLasPruebasSeContestan(unittest.TestCase):
    """pruebas.py lee las preguntas y su clave del propio Markdown. Lo que no
    puede pasar es que diga «correcta» de una opción que la clave no marca."""

    def _tests(self):
        return [r for r in validar.lecciones() if validar.leer(r)[0].get("tipo") in pruebas.TIPOS]

    def test_todas_las_pruebas_y_minitests_se_leen(self):
        for ruta in self._tests():
            test = pruebas.leer(ruta)
            self.assertIsNotNone(test, ruta)
            self.assertEqual(len(test["preguntas"]), 15, ruta)

    def test_la_correcta_es_la_de_la_clave(self):
        """Se vuelve a leer la clave con una expresión propia y se compara:
        es la relación lo que importa, no una secuencia copiada aquí."""
        for ruta in self._tests():
            _, cuerpo = validar.leer(ruta)
            clave = cuerpo.split(validar.RESPUESTAS[validar.pista_de(ruta)], 1)[1]
            letras = dict(re.findall(r"(\d+) ([абвгд]) \(", re.sub(r"\s+", " ", clave)))
            for p in pruebas.leer(ruta)["preguntas"]:
                self.assertEqual(p["correcta"], letras[str(p["n"])], f"{ruta.name} {p['n']}")

    def test_cada_respuesta_manda_a_un_dia_del_calendario(self):
        dias = plan.por_ruta()
        for ruta in self._tests():
            for p in pruebas.leer(ruta)["preguntas"]:
                self.assertIn(p["leccion"], dias, f"{ruta} pregunta {p['n']}")

    def test_una_clave_que_no_cuadra_deja_la_pagina_en_papel(self):
        ruta = RAIZ / "curso" / "es" / "a1" / "semana-02" / "dia-6.md"
        meta, cuerpo = validar.leer(ruta)
        self.assertIsNotNone(pruebas.de_texto(meta, cuerpo, "es"))
        texto, clave = cuerpo.split("## Respuestas", 1)
        # Falta una respuesta: la última de la clave, sacada del propio archivo.
        ultima = re.findall(r"\d+ [абвг] \([^)]*\)", re.sub(r"\s+", " ", clave))[-1]
        roto = texto + "## Respuestas" + re.sub(r"\s+", " ", clave).replace(ultima, "")
        self.assertNotEqual(roto, cuerpo)
        self.assertIsNone(pruebas.de_texto(meta, roto, "es"))
        # Una letra que no está entre las opciones.
        primera = re.findall(r"\d+ [абвг] \(", re.sub(r"\s+", " ", clave))[0]
        mal = re.sub(r"\s+", " ", clave).replace(primera, primera[:-3] + "д (", 1)
        self.assertIsNone(pruebas.de_texto(meta, texto + "## Respuestas" + mal, "es"))


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

    def test_la_prueba_se_contesta_y_el_papel_sigue_ahi(self):
        texto = (self.tmp / "es" / "a1" / "semana-02" / "dia-6.html").read_text(encoding="utf-8")
        self.assertIn('<div class="test-papel">', texto)
        self.assertIn('<div class="test-vivo" hidden', texto)
        self.assertIn('test.js" defer', texto)
        self.assertTrue((self.tmp / "test.js").exists())
        m = re.search(r'<script type="application/json" class="test-datos">(.*?)</script>', texto, re.S)
        datos = json.loads(m.group(1))
        self.assertEqual(len(datos["preguntas"]), 15)
        # Los enlaces «para repasar» viven en el JSON: el revisor de enlaces
        # no los ve, así que se comprueban aquí uno a uno.
        base = self.tmp / "es" / "a1" / "semana-02"
        for p in datos["preguntas"]:
            if "url" in p:
                self.assertTrue((base / p["url"]).resolve().exists(), p["url"])

    def test_una_leccion_normal_no_carga_el_test(self):
        texto = (self.tmp / "es" / "a1" / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertNotIn("test.js", texto)
        self.assertNotIn('class="test-datos"', texto)

    def test_el_tachado_se_ve_tachado(self):
        self.assertIn("<del>mal</del>", construir_sitio.md("esto está ~~mal~~"))

    def test_la_pagina_sale_siempre_de_dia(self):
        """El modo oscuro del aparato no decide: lo decide el lector.

        Si alguien vuelve a meter una regla de paleta dentro de un
        `prefers-color-scheme: dark`, el sitio saldría oscuro de entrada en
        un móvil puesto en oscuro, que es justo lo que no se quiere.
        """
        hojas = [construir_sitio.CSS,
                 (construir_sitio.WEB / "portada.css").read_text(encoding="utf-8")]
        for hoja in hojas:
            for bloque in re.findall(r"prefers-color-scheme:\s*dark[^{]*\{(.*?)\}\s*\}",
                                     hoja, re.S):
                self.assertNotIn("--papel", bloque,
                                 "la paleta no puede colgar de prefers-color-scheme")

    def test_el_boton_del_tema_no_consulta_el_aparato(self):
        """Si lo consultara, el primer clic en un móvil oscuro no haría nada.

        La página nace clara; si el botón creyera que está oscura porque el
        aparato lo está, guardaría «light» y el lector no vería ningún
        cambio.
        """
        guion = construir_sitio.PROGRESO_JS
        tema = guion[guion.index("getElementById('tema')"):][:400]
        self.assertNotIn("prefers-color-scheme", tema)

    def test_la_portada_tambien_tiene_noche(self):
        """La portada fija su propia paleta, así que necesita su override.

        Sin él el botón guarda la elección y en la portada no se ve nada:
        el sitio solo sale oscuro al abrir una lección.
        """
        css = (construir_sitio.WEB / "portada.css").read_text(encoding="utf-8")
        self.assertIn('[data-tema="dark"] .portada', css)
        oscuro = css[css.index('[data-tema="dark"] .portada'):]
        self.assertIn("--papel", oscuro)


class TestLasPruebasDeLaPortada(unittest.TestCase):
    """Las cuatro pruebas de dos minutos a las que lleva la portada.

    Nacieron de un defecto: los cuatro accesos apuntaban a un ancla DENTRO
    de una lección de treinta minutos, así que «Escucha» dejaba al visitante
    en el minuto 25 del día 5, con el ejercicio fuera de contexto y media
    página por encima y por debajo.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp())
        cfg = dict(construir_sitio.cargar_config(), adsense={"cliente": ""}, dominio="")
        construir_sitio.construir(cls.tmp, cfg=cfg)
        cls.textos = construir_sitio.cargar_textos()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def _html(self, pista, clave):
        pagina = self.textos[pista]["pruebas"]["paginas"][clave]
        return (self.tmp / pista / pagina).read_text(encoding="utf-8")

    def test_la_portada_lleva_a_las_pruebas_y_no_a_un_ancla(self):
        """Una tarjeta que promete «graba tu voz» tiene que abrir eso.

        Apuntando a `dia-5.html#parte-5` abría una lección entera y la
        dejaba en su minuto 25, que es lo que se leía como un salto al
        fondo de una página cualquiera.
        """
        for pista in plan.PISTAS:
            texto = (self.tmp / pista / "index.html").read_text(encoding="utf-8")
            destinos = re.findall(r'<a class="practica" href="([^"]+)"', texto)
            paginas = self.textos[pista]["pruebas"]["paginas"]
            self.assertEqual(destinos, [paginas[c] for c in construir_sitio._PRACTICAS], pista)
            for d in destinos:
                self.assertNotIn("#", d, "una tarjeta no puede llevar a media lección")

    def test_las_ocho_paginas_existen_y_no_comparten_nombre(self):
        rutas = set()
        for pista in plan.PISTAS:
            for clave in construir_sitio._PRUEBAS:
                pagina = self.textos[pista]["pruebas"]["paginas"][clave]
                self.assertTrue((self.tmp / pista / pagina).exists(), f"{pista}/{pagina}")
                rutas.add(f"{pista}/{pagina}")
        self.assertEqual(len(rutas), 8)

    def test_las_dos_pistas_ensenan_el_mismo_ruso(self):
        """Lo que cambia es la explicación, nunca el ruso.

        El ruso vive una sola vez en el generador justamente para esto; si
        alguien lo copiara a textos.yaml, las dos pistas podrían separarse
        sin que nada fallara. La ÚNICA excepción es el ejemplo de la prueba
        de escritura: transliterar «José» para un angloparlante no enseña
        nada, así que ahí cada pista pone un nombre de su lengua, y esta
        prueba exige que la diferencia esté solo ahí.
        """
        cirilico = re.compile(r"[\u0400-\u04FF\u0301]+")
        for clave in construir_sitio._PRUEBAS:
            a, b = (set(cirilico.findall(self._html(p, clave))) for p in plan.PISTAS)
            if a == b:
                continue
            self.assertEqual(clave, "escritura", f"{clave} no comparte el ruso")
            for pista, propias in zip(plan.PISTAS, (a - b, b - a)):
                intro = self.textos[pista]["pruebas"]["escritura"]["intro"]
                for palabra in propias:
                    self.assertIn(palabra, intro,
                                  f"{pista}: «{palabra}» no está en el ejemplo del nombre")

    def test_cada_lista_de_textos_acompana_al_ruso(self):
        """Una lista corta dejaría filas sin su traducción, en silencio: zip
        se para en la más corta y la tabla saldría incompleta."""
        largos = {"letras": len(construir_sitio._PRUEBA_LETRAS),
                  "palabras": len(construir_sitio._PRUEBA_PALABRAS),
                  "puerta": len(construir_sitio._PRUEBA_PUERTA),
                  "alfabeto": len(construir_sitio._PRUEBA_ALFABETO),
                  "pares": len(construir_sitio._PRUEBA_VOZ),
                  "lineas": len(construir_sitio._PRUEBA_DIALOGO),
                  "frases": len(construir_sitio._PRUEBA_FRASES)}
        for pista in plan.PISTAS:
            for clave in construir_sitio._PRUEBAS:
                bloque = self.textos[pista]["pruebas"][clave]
                for nombre, largo in largos.items():
                    if nombre in bloque:
                        self.assertEqual(len(bloque[nombre]), largo, f"{pista}/{clave}/{nombre}")

    def test_la_voz_sube_sobre_su_silaba_y_no_al_lado(self):
        """La curva y la fila de sílabas comparten caja y columnas iguales.

        El vértice se calcula de la sílaba tónica, así que tiene que caer en
        el centro de su columna. Dibujado con un número a ojo señalaría a
        otra sílaba y la página enseñaría lo contrario de lo que dice.
        """
        for silabas, tonica, _, _ in construir_sitio._PRUEBA_VOZ:
            n = len(silabas)
            for sube in (False, True):
                svg = construir_sitio._voz(silabas, tonica, sube)
                ancho = float(re.search(r'viewBox="0 0 (\d+)', svg).group(1))
                puntos = [p.split(",") for p in
                          re.search(r'points="([^"]+)"', svg).group(1).split()]
                x = float(puntos[2][0]) / ancho
                self.assertAlmostEqual(x, (tonica + 0.5) / n, places=2,
                                       msg=f"{''.join(silabas)} sube={sube}")

    def test_las_palabras_se_abren_sin_javascript(self):
        """Un <details> y no un botón: la página tiene que enseñar seis
        palabras aunque el guion no cargue."""
        texto = self._html("es", "lectura")
        self.assertEqual(texto.count('<details class="palabra">'),
                         len(construir_sitio._PRUEBA_PALABRAS))
        self.assertNotIn('class="quiere" hidden', texto)

    def test_la_grabadora_nace_oculta(self):
        """Sin micrófono o sin MediaRecorder, un botón de grabar pediría
        permiso para nada y no haría nada."""
        for pista in plan.PISTAS:
            texto = self._html(pista, "escucha")
            self.assertIn('id="grabadora" class="grabadora" hidden', texto)
        self.assertIn("zona.hidden=false", construir_sitio.PRUEBA_JS)
        self.assertIn("MediaRecorder", construir_sitio.PRUEBA_JS)
        # El micrófono se apaga de verdad al parar: si no, el punto rojo de
        # la pestaña se queda encendido y se lee como que el sitio escucha.
        self.assertIn("getTracks()", construir_sitio.PRUEBA_JS)

    def test_el_hueco_del_nombre_no_deja_dos_puntos_seguidos(self):
        """Con «…» salía «Меня́ зову́т …. А тебя́?»."""
        hueco = construir_sitio._PRUEBA_HUECO
        for pista in plan.PISTAS:
            lineas = list(construir_sitio._PRUEBA_DIALOGO)
            lineas += self.textos[pista]["pruebas"]["habla"]["lineas"]
            for linea in lineas:
                puesto = linea.replace("{nombre}", hueco)
                self.assertNotIn("..", puesto, puesto)
            texto = self._html(pista, "habla")
            self.assertIn(f"data-plantilla=", texto)
            self.assertIn("{nombre}", texto, "el guion necesita la plantilla")
        self.assertIn(f"'{hueco}'", construir_sitio.PRUEBA_JS,
                      "el guion y el HTML tienen que usar el mismo hueco")

    def test_cada_prueba_vuelve_al_curso(self):
        """Dos minutos sin puerta al día 1 son dos minutos perdidos."""
        for pista in plan.PISTAS:
            dia1 = f"a1/semana-01/dia-1.html"
            for clave in construir_sitio._PRUEBAS:
                texto = self._html(pista, clave)
                self.assertIn(f'<a class="boton" href="{dia1}"', texto, f"{pista}/{clave}")
                self.assertIn('class="otras"', texto, f"{pista}/{clave}")
                # El enlace a la lección de la que sale, salvo en lectura,
                # que viene del día 1 y tendría los dos botones iguales.
                dia = construir_sitio._PRUEBA_DIA[clave]
                if dia != 1:
                    self.assertIn(f'a1/semana-01/dia-{dia}.html', texto, f"{pista}/{clave}")


if __name__ == "__main__":
    unittest.main()
