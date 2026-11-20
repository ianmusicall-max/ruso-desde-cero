#!/usr/bin/env python3
"""Convierte el curso en el sitio público de docs/, en sus dos pistas.

    python3 scripts/construir_sitio.py
    python3 scripts/construir_sitio.py --destino /tmp/sitio

Estructura:

    index.html                        portada bilingüe: las dos puertas
    es/index.html  en/index.html      portada de cada pista
    es/curso.html  en/course.html     índice: niveles, unidades y días
    es/a1/semana-01/dia-1.html        las lecciones (y en/… la misma ruta)
    es/sobre.html … en/privacy.html   páginas fijas
    fonts/  progreso.js  robots.txt   (y CNAME, sitemap.xml, ads.txt si toca)

Solo se publican las lecciones **escritas**: el índice enseña el resto del
calendario como «próximamente», sin enlace. Una lección que no pasa
`validar.py` no se publica, y el script lo dice.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET

import markdown
import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import plan  # noqa: E402
import pruebas  # noqa: E402
import validar  # noqa: E402

RAIZ = plan.RAIZ
DOCS = RAIZ / "docs"
WEB = RAIZ / "web"
CURSO = RAIZ / "curso"
PISTAS = plan.PISTAS


# ── Markdown ────────────────────────────────────────────────────────────

class _Tachado(markdown.inlinepatterns.InlineProcessor):
    def handleMatch(self, m, data):  # noqa: N802 (API de markdown)
        el = ET.Element("del")
        el.text = m.group(1)
        return el, m.start(0), m.end(0)


class Tachado(markdown.extensions.Extension):
    """~~así~~ → <del>: Python-Markdown no trae tachado y el curso tacha lo
    incorrecto (~~Я есть студе́нт~~). Sin esto saldrían las tildes a la vista."""

    def extendMarkdown(self, md):  # noqa: N802
        md.inlinePatterns.register(_Tachado(r"~~(.+?)~~", md), "tachado", 175)


def md(texto: str) -> str:
    return markdown.markdown(texto, extensions=["tables", "sane_lists", "attr_list", Tachado()])


# ── Estilo ──────────────────────────────────────────────────────────────

_CIRILICO = "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116"
_LATINO = ("U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, "
           "U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD")
_CARAS = [("Literata", "normal", 400, "literata-{a}-400"), ("Literata", "italic", 400, "literata-{a}-400i"),
          ("Literata", "normal", 700, "literata-{a}-700"), ("Onest", "normal", 400, "onest-{a}-400"),
          ("Onest", "normal", 700, "onest-{a}-700")]


def caras(raiz: str) -> str:
    """Las @font-face, con la ruta de la profundidad de la página. Cada cara
    lleva su unicode-range: una página solo descarga los alfabetos que usa."""
    out = []
    for familia, estilo, peso, archivo in _CARAS:
        for alfabeto, rango in (("cyrillic", _CIRILICO), ("latin", _LATINO)):
            out.append(f"@font-face{{font-family:'{familia}';font-style:{estilo};font-weight:{peso};"
                       f"font-display:swap;src:url({raiz}/fonts/{archivo.format(a=alfabeto)}.woff2) "
                       f"format('woff2');unicode-range:{rango}}}")
    return "\n".join(out)


CSS = """
:root{color-scheme:light;
  --papel:#ffffff;--tinta:#111317;--tenue:#626873;--linea:#dfe2e7;--tarjeta:#f4f6f9;
  --acento:#1f56a6;--acento-suave:#eaf1fb;--aviso:#b4461b;--aviso-suave:#fdf1ea;
  --bien:#1f7a4d;--ancho:44rem}
@media(prefers-color-scheme:dark){:root:not([data-tema="light"]){color-scheme:dark;
  --papel:#121418;--tinta:#e6e8eb;--tenue:#9aa1ab;--linea:#2d3138;--tarjeta:#1b1e23;
  --acento:#8db4f2;--acento-suave:#1a2433;--aviso:#f09a72;--aviso-suave:#2a1d17;--bien:#6fcf9c}}
:root[data-tema="dark"]{color-scheme:dark;
  --papel:#121418;--tinta:#e6e8eb;--tenue:#9aa1ab;--linea:#2d3138;--tarjeta:#1b1e23;
  --acento:#8db4f2;--acento-suave:#1a2433;--aviso:#f09a72;--aviso-suave:#2a1d17;--bien:#6fcf9c}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--papel);color:var(--tinta);
  font:400 17px/1.65 Literata,ui-serif,Georgia,serif;-webkit-font-smoothing:antialiased;overflow-wrap:break-word}
.envoltorio{max-width:var(--ancho);margin:0 auto;padding:0 18px}
a{color:var(--acento)}
h1,h2,h3,.sans,header.sitio,footer.sitio,.boton,.migas,summary{font-family:Onest,ui-sans-serif,system-ui,sans-serif}
h1{font-size:1.9rem;line-height:1.2;margin:.4rem 0 .3rem;letter-spacing:-.01em}
h2{font-size:1.3rem;line-height:1.3;margin:2.2rem 0 .7rem}
h3{font-size:1.06rem;margin:1.6rem 0 .5rem}
header.sitio{border-bottom:1px solid var(--linea)}
header.sitio .envoltorio{max-width:60rem;display:flex;flex-wrap:wrap;align-items:center;gap:.4rem 1rem;padding-block:.6rem;font-size:.9rem}
header.sitio a{color:var(--tenue);text-decoration:none}
header.sitio a:hover,header.sitio a[aria-current]{color:var(--acento)}
header.sitio .marca{font-weight:700;color:var(--tinta);font-size:1rem;margin-right:auto}
header.sitio nav{display:flex;gap:.9rem}
header.sitio .idiomas a{font-weight:700}
.tema{background:none;border:1px solid var(--linea);border-radius:99px;color:var(--tenue);cursor:pointer;
  padding:.3rem .45rem;line-height:0;display:inline-flex;align-items:center}
.tema:hover{color:var(--acento);border-color:var(--acento)}
footer.sitio{border-top:1px solid var(--linea);margin-top:4rem;color:var(--tenue);font-size:.85rem}
footer.sitio .envoltorio{padding-block:1.4rem;display:flex;flex-wrap:wrap;gap:.5rem 1.2rem}
footer.sitio a{color:var(--tenue)}
main{padding-bottom:1rem}
.migas{color:var(--tenue);font-size:.85rem;margin-top:1.6rem}
.ru-tema{font-size:1.15rem;color:var(--tenue);margin:0 0 1rem}
.borrador{background:var(--aviso-suave);border-left:4px solid var(--aviso);padding:.6rem .9rem;border-radius:6px;font-size:.92rem}
blockquote{margin:1rem 0;padding:.75rem 1rem;background:var(--tarjeta);border-radius:10px;border-left:4px solid var(--acento)}
blockquote p{margin:.35rem 0}
blockquote ul{margin:.3rem 0;padding-left:1.2rem}
.tabla{overflow-x:auto;margin:1rem 0}
table{border-collapse:collapse;width:100%;font-size:.95rem}
th,td{border-bottom:1px solid var(--linea);padding:.45rem .6rem;text-align:left;vertical-align:top}
th{font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.85rem;color:var(--tenue);font-weight:700}
h2.parte{display:flex;align-items:baseline;gap:.6rem;flex-wrap:wrap}
h2.parte .num{display:inline-flex;align-items:center;justify-content:center;width:1.8rem;height:1.8rem;border-radius:50%;
  background:var(--acento);color:var(--papel);font-size:.95rem;flex:none}
h2.parte .franja{margin-left:auto;font-size:.8rem;font-weight:400;color:var(--tenue);border:1px solid var(--linea);border-radius:99px;padding:.05rem .55rem}
aside.contraste{background:var(--aviso-suave);border-left:4px solid var(--aviso);border-radius:10px;padding:.2rem 1rem .4rem;margin:1.4rem 0}
aside.contraste h3{color:var(--aviso);margin-top:.8rem}
del{text-decoration-thickness:2px;text-decoration-color:var(--aviso);color:var(--tenue)}
details.clave{margin-top:2.2rem;border:1px solid var(--linea);border-radius:10px;padding:.2rem 1rem}
details.clave summary{cursor:pointer;font-weight:700;color:var(--acento);padding:.6rem 0}
.boton{display:inline-block;background:var(--acento);color:var(--papel);text-decoration:none;border:0;border-radius:99px;
  padding:.6rem 1.15rem;font-size:.95rem;font-weight:700;cursor:pointer}
.boton.secundario{background:var(--acento-suave);color:var(--acento)}
.botones{display:flex;flex-wrap:wrap;gap:.6rem;margin:1.2rem 0}
.final{display:flex;flex-wrap:wrap;align-items:center;gap:.8rem;margin:2.6rem 0 1rem;padding-top:1.2rem;border-top:1px solid var(--linea)}
#marcar[aria-pressed="true"]{background:var(--bien)}
.vecinos{display:flex;justify-content:space-between;gap:1rem;font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.9rem}
.nota{color:var(--tenue);font-size:.88rem}
.test-vivo .pregunta{margin:0 0 1.2rem}
.test-vivo .enunciado{margin:.2rem 0 .5rem;font-weight:600}
.test-vivo .opciones{display:grid;gap:.4rem}
.test-vivo .opcion{display:block;width:100%;text-align:left;font:inherit;color:inherit;background:var(--tarjeta);
  border:1px solid var(--linea);border-radius:10px;padding:.6rem .85rem;cursor:pointer}
.test-vivo .opcion:hover:not(:disabled){border-color:var(--acento)}
.test-vivo .opcion:disabled{cursor:default}
.test-vivo .opcion.bien{border-color:var(--bien);box-shadow:inset 5px 0 0 var(--bien)}
.test-vivo .opcion.bien::after{content:" ✓";color:var(--bien);font-weight:700}
.test-vivo .opcion.mal{border-color:var(--aviso);box-shadow:inset 5px 0 0 var(--aviso)}
.test-vivo .opcion.mal::after{content:" ✗";color:var(--aviso);font-weight:700}
.test-vivo .resultado{border:1px solid var(--linea);border-radius:12px;padding:1rem 1.1rem;background:var(--acento-suave)}
.test-vivo .nota-final{font-size:1.2rem;font-weight:700;margin:.2rem 0 .6rem}
.heroe{padding:2.2rem 0 .6rem}
.heroe h1{font-size:2.2rem}
.lema{font-size:1.15rem;color:var(--tenue);margin:.2rem 0 0}
.puertas{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:1rem;margin:1.6rem 0}
.puerta{display:block;border:1px solid var(--linea);border-radius:14px;padding:1.1rem 1.2rem;text-decoration:none;color:var(--tinta);background:var(--tarjeta)}
.puerta:hover{border-color:var(--acento)}
.puerta strong{display:block;font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:1.15rem;color:var(--acento);margin-bottom:.3rem}
.nivel{margin-top:2.4rem}
details.unidad{border:1px solid var(--linea);border-radius:10px;margin:.5rem 0;padding:.1rem .9rem}
details.unidad summary{cursor:pointer;padding:.55rem 0;font-weight:700}
details.unidad summary .ru{font-weight:400;color:var(--tenue);margin-left:.4rem}
details.unidad ol{margin:.2rem 0 .8rem;padding-left:1.4rem}
details.unidad li{margin:.15rem 0}
li.pronto{color:var(--tenue)}
li.hecha>a::after{content:" ✓";color:var(--bien);font-weight:700}
.tipo{font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.75rem;color:var(--tenue);border:1px solid var(--linea);border-radius:99px;padding:0 .45rem;margin-right:.3rem}
"""

ICONO_TEMA = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
              '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/>'
              '<path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg>')

TEMA_CABEZA = ("<script>try{var t=localStorage.getItem('rdc.tema');"
               "if(t)document.documentElement.setAttribute('data-tema',JSON.parse(t))}catch(e){}</script>")

PROGRESO_JS = r"""(function(){
var d=document,raiz=d.documentElement.getAttribute('data-raiz')||'.';
function leer(k,def){try{var v=localStorage.getItem(k);return v===null?def:JSON.parse(v)}catch(e){return def}}
function guardar(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
var b=d.getElementById('tema');
if(b){b.addEventListener('click',function(){var h=d.documentElement,a=h.getAttribute('data-tema');
  var oscuro=a==='dark'||(a!=='light'&&window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches);
  var nuevo=oscuro?'light':'dark';h.setAttribute('data-tema',nuevo);guardar('rdc.tema',nuevo);});}
var hechas=leer('rdc.hechas',[]);if(!Array.isArray(hechas))hechas=[];
var lec=d.querySelector('main[data-leccion]');
if(lec){var id=lec.getAttribute('data-leccion'),pista=id.split('/')[0];
  guardar('rdc.ultima.'+pista,{id:id,url:lec.getAttribute('data-url'),titulo:lec.getAttribute('data-titulo')});
  var m=d.getElementById('marcar');
  if(m){var pinta=function(){var h=hechas.indexOf(id)>=0;m.textContent=m.getAttribute(h?'data-hecha':'data-marcar');
      m.setAttribute('aria-pressed',h?'true':'false');};
    pinta();m.hidden=false;
    m.addEventListener('click',function(){var i=hechas.indexOf(id);if(i>=0)hechas.splice(i,1);else hechas.push(id);
      guardar('rdc.hechas',hechas);pinta();});}}
var items=d.querySelectorAll('[data-leccion-item]');
for(var i=0;i<items.length;i++){if(hechas.indexOf(items[i].getAttribute('data-leccion-item'))>=0)items[i].className+=' hecha';}
var c=d.getElementById('continuar');
if(c){var u=leer('rdc.ultima.'+c.getAttribute('data-pista'),null);
  if(u&&u.url){c.href=raiz+'/'+u.url;c.hidden=false;var s=c.querySelector('.donde');if(s)s.textContent=u.titulo||'';}}
})();
"""


# ── Datos ───────────────────────────────────────────────────────────────

TEST_JS = r"""(function(){
// Las pruebas y los mini-tests, contestables. Sin JavaScript queda la
// versión en papel (div.test-papel) con su clave plegada: el guion la
// esconde solo cuando puede ofrecer algo mejor.
function el(tag,cls,txt){var x=document.createElement(tag);if(cls)x.className=cls;if(txt!=null)x.textContent=txt;return x}
document.querySelectorAll('.test-vivo').forEach(function(caja){
  var datos,t;
  try{datos=JSON.parse(caja.nextElementSibling.textContent);t=JSON.parse(caja.getAttribute('data-textos'))}catch(e){return}
  var papel=caja.previousElementSibling;
  function montar(){
    caja.textContent='';
    var bien=0,hechas=0,fallos=[],bloque=null,total=datos.preguntas.length;
    var res=el('div','resultado');res.hidden=true;
    datos.preguntas.forEach(function(p){
      if(p.bloque&&p.bloque!==bloque){bloque=p.bloque;caja.appendChild(el('h3',null,bloque))}
      var item=el('div','pregunta');
      item.appendChild(el('p','enunciado',p.n+'. '+p.pregunta));
      var ops=el('div','opciones');
      p.opciones.forEach(function(o){
        var b=el('button','opcion',o[0]+') '+o[1]);b.type='button';
        b.addEventListener('click',function(){
          if(item.getAttribute('data-hecha'))return;
          item.setAttribute('data-hecha','1');hechas++;
          var bs=ops.querySelectorAll('button');
          for(var i=0;i<bs.length;i++){bs[i].disabled=true;if(p.opciones[i][0]===p.correcta)bs[i].classList.add('bien')}
          if(o[0]===p.correcta){bien++}else{b.classList.add('mal');fallos.push(p)}
          if(hechas===total)resultado();
        });
        ops.appendChild(b);
      });
      item.appendChild(ops);caja.appendChild(item);
    });
    caja.appendChild(res);
    function resultado(){
      res.hidden=false;res.textContent='';
      res.appendChild(el('p','nota-final',t.resultado.replace('{bien}',bien).replace('{total}',total)));
      var vistos={},lista=el('ul');
      fallos.forEach(function(p){if(p.url&&!vistos[p.url]){vistos[p.url]=1;var li=el('li'),a=el('a',null,p.tema);a.href=p.url;li.appendChild(a);lista.appendChild(li)}});
      if(lista.children.length){res.appendChild(el('p',null,t.repasa));res.appendChild(lista)}
      var acc=el('p','botones');
      var otra=el('button','boton',t.otra_vez);otra.type='button';
      otra.addEventListener('click',function(){montar();caja.scrollIntoView({behavior:'smooth'})});
      var clave=el('button','boton secundario',t.ver_clave);clave.type='button';
      clave.addEventListener('click',function(){var d=document.getElementById('respuestas');if(d){d.open=true;d.scrollIntoView({behavior:'smooth'})}});
      acc.appendChild(otra);acc.appendChild(clave);res.appendChild(acc);
    }
  }
  montar();
  if(papel&&papel.classList.contains('test-papel'))papel.hidden=true;
  caja.hidden=false;
});
})();
"""


def cargar_config(ruta: pathlib.Path = WEB / "sitio.yaml") -> dict:
    return yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}


def cargar_textos(ruta: pathlib.Path = WEB / "textos.yaml") -> dict:
    return yaml.safe_load(ruta.read_text(encoding="utf-8"))


def escritas(cal: dict, curso: pathlib.Path = CURSO) -> dict[str, list[tuple[plan.Dia, dict, str]]]:
    """Por pista, las lecciones escritas en el orden del curso: (día, meta, cuerpo).
    Una lección que no pasa validar.py no entra, y se avisa."""
    dias = plan.todos(cal)
    por_ruta = {d.ruta: d for d in dias}
    orden = {d.ruta: i for i, d in enumerate(dias)}
    salida: dict[str, list] = {p: [] for p in PISTAS}
    for pista in PISTAS:
        for ruta in sorted((curso / pista).glob("*/semana-*/dia-*.md")):
            problemas = validar.validar(ruta, por_ruta)
            if problemas:
                print(f"✗ no se publica {ruta.relative_to(RAIZ)}: {problemas[0]}", file=sys.stderr)
                continue
            meta, cuerpo = validar.leer(ruta)
            clave = ruta.relative_to(curso / pista).with_suffix("").as_posix()
            salida[pista].append((por_ruta[clave], meta, cuerpo))
        salida[pista].sort(key=lambda x: orden[x[0].ruta])
    return salida


# ── Páginas ─────────────────────────────────────────────────────────────

def e(texto) -> str:
    return html.escape(str(texto), quote=True)


def absoluta(cfg: dict, ruta: str) -> str:
    return f"{cfg['dominio'].rstrip('/')}/{ruta}" if cfg.get("dominio") else ""


def pagina(cfg, textos, idioma, titulo, cuerpo, *, ruta, raiz, descripcion="",
           alternas=None, actual="", principal="") -> str:
    """Una página completa. `ruta` es la de esta página desde la raíz del sitio;
    `alternas` = {idioma: ruta} de sus versiones en las otras lenguas."""
    sitio = cfg["nombre"].get(idioma) or cfg["nombre"]["es"]
    t = textos.get(idioma) or textos["es"]
    alternas = alternas or {}
    cabeza = [f'<title>{e(titulo)} · {e(sitio)}</title>' if titulo != sitio else f"<title>{e(sitio)}</title>",
              f'<meta name="description" content="{e(descripcion or t["descripcion"])}">']
    if cfg.get("dominio"):
        cabeza.append(f'<link rel="canonical" href="{e(absoluta(cfg, ruta))}">')
        for otra, r in alternas.items():
            cabeza.append(f'<link rel="alternate" hreflang="{otra}" href="{e(absoluta(cfg, r))}">')
    if (cfg.get("adsense") or {}).get("cliente"):
        cabeza.append('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
                      f'?client={e(cfg["adsense"]["cliente"])}" crossorigin="anonymous"></script>')

    if idioma in textos:
        inicio = f"{raiz}/{idioma}/index.html"
        menu = "".join(
            f'<a href="{raiz}/{idioma}/{t["paginas"][k]}"{" aria-current=page" if actual == k else ""}>{e(t["menu"][k])}</a>'
            for k in ("curso", "sobre"))
        idiomas = "".join(
            f'<a lang="{p}" hreflang="{p}" href="{raiz}/{alternas.get(p, f"{p}/index.html")}"'
            f'{" aria-current=true" if p == idioma else ""}>{p.upper()}</a>' for p in PISTAS)
        nav = f'<nav class="menu">{menu}</nav><nav class="idiomas" aria-label="Language">{idiomas}</nav>'
        pie_links = "".join(f'<a href="{raiz}/{idioma}/{t["paginas"][k]}">{e(t["menu"][k])}</a>'
                            for k in ("sobre", "contacto", "privacidad"))
        pie = f'<span>{e(t["pie"])}</span>{pie_links}'
    else:  # la portada bilingüe de la raíz
        inicio = f"{raiz}/index.html"
        nav = ""
        pie = " · ".join(f'<a href="{raiz}/{p}/{textos[p]["paginas"]["privacidad"]}">{e(textos[p]["menu"]["privacidad"])}</a>'
                         for p in PISTAS)
    boton_tema = e(t["botones"]["tema"])
    return f"""<!doctype html>
<html lang="{idioma if idioma in textos else 'en'}" data-raiz="{raiz}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{chr(10).join(cabeza)}
<style>{caras(raiz)}{CSS}</style>
{TEMA_CABEZA}
</head>
<body>
<header class="sitio"><div class="envoltorio">
<a class="marca" href="{inicio}">{e(sitio)}</a>{nav}
<button id="tema" class="tema" type="button" aria-label="{boton_tema}" title="{boton_tema}">{ICONO_TEMA}</button>
</div></header>
<main class="envoltorio"{principal}>
{cuerpo}
</main>
<footer class="sitio"><div class="envoltorio">{pie}</div></footer>
<script src="{raiz}/progreso.js" defer></script>
</body>
</html>
"""


# ── La lección ──────────────────────────────────────────────────────────

APARTADO_HTML = re.compile(r"<h2>(\d+)\. (.+?) \((\d+)[–-](\d+) min\)</h2>")


def _cerrar_en_parrafos_de_citas(cuerpo_html: str) -> str:
    """Dentro de una cita (>) cada línea del Markdown es una línea: así se
    escriben los diálogos y su traducción debajo, sin espacios invisibles."""
    def citas(m):
        return re.sub(r"<p>(.*?)</p>", lambda p: "<p>" + p.group(1).replace("\n", "<br>\n") + "</p>",
                      m.group(0), flags=re.S)
    return re.sub(r"<blockquote>.*?</blockquote>", citas, cuerpo_html, flags=re.S)


def html_de_leccion(cuerpo_md: str, pista: str, textos: dict) -> str:
    h = md(cuerpo_md)
    h = _cerrar_en_parrafos_de_citas(h)
    h = APARTADO_HTML.sub(
        lambda m: (f'<h2 id="parte-{m.group(1)}" class="parte"><span class="num">{m.group(1)}</span>'
                   f'<span class="nombre">{m.group(2)}</span>'
                   f'<span class="franja">{m.group(3)}–{m.group(4)} min</span></h2>'), h)
    # El contraste: desde su <h3> hasta el siguiente <h2> o <h3>.
    marca = validar.CONTRASTE[pista][4:]
    h = re.sub(rf"(<h3>{re.escape(marca)}</h3>.*?)(?=<h2|<h3|\Z)",
               lambda m: f'<aside class="contraste">{m.group(1)}</aside>\n', h, flags=re.S)
    h = re.sub(r"<table>", '<div class="tabla"><table>', h)
    h = re.sub(r"</table>", "</table></div>", h)
    # Las respuestas, plegadas: son lo último de la lección.
    titulo = validar.RESPUESTAS[pista][3:]
    partes = h.split(f"<h2>{titulo}</h2>", 1)
    if len(partes) == 2:
        h = (partes[0] + f'<details class="clave" id="respuestas"><summary>'
             f'{e(textos[pista]["botones"]["ver_respuestas"])}</summary>\n{partes[1]}</details>\n')
    return h


def envolver_test(h: str, test: dict, pista: str, textos: dict, raiz: str,
                  publicadas: set[str], dias: dict) -> str:
    """La versión en papel del test va dentro de div.test-papel y, detrás, el
    hueco que llena test.js con las preguntas pulsables. Desde el primer
    título de bloque hasta el siguiente apartado (<h2>). Si no se encuentra
    ese título, la página se queda como estaba."""
    primero = next((p["bloque"] for p in test["preguntas"] if p["bloque"]), "")
    marca = f"<h3>{e(primero)}</h3>" if primero else ""
    ini = h.find(marca) if marca else -1
    if ini < 0:
        return h
    fin = h.find("<h2", ini)
    clave = h.find('<details class="clave"', ini)
    fin = min(x for x in (fin, clave, len(h)) if x >= 0)
    datos = []
    for p in test["preguntas"]:
        q = {k: p[k] for k in ("n", "bloque", "pregunta", "opciones", "correcta")}
        if p.get("leccion") and p["leccion"] in publicadas:
            q["url"] = f"{raiz}/{pista}/{p['leccion']}.html"
            q["tema"] = dias[p["leccion"]].tema(pista)
        datos.append(q)
    letrero = json.dumps(textos[pista]["test"], ensure_ascii=False)
    carga = json.dumps({"preguntas": datos}, ensure_ascii=False).replace("</", "<\\/")
    vivo = (f'<div class="test-vivo" hidden data-textos="{e(letrero)}"></div>\n'
            f'<script type="application/json" class="test-datos">{carga}</script>\n')
    return h[:ini] + '<div class="test-papel">' + h[ini:fin] + "</div>\n" + vivo + h[fin:]


def ruta_leccion(pista: str, dia: plan.Dia) -> str:
    return f"{pista}/{dia.ruta}.html"


def construir_lecciones(cfg, textos, cal, destino, publicadas) -> list[str]:
    rutas = []
    hay = {p: {d.ruta for d, _, _ in publicadas[p]} for p in PISTAS}
    dias = plan.por_ruta(cal)
    for pista in PISTAS:
        t = textos[pista]
        lista = publicadas[pista]
        for i, (dia, meta, cuerpo) in enumerate(lista):
            ruta = ruta_leccion(pista, dia)
            raiz = "../../.."
            alternas = {p: ruta_leccion(p, dia) for p in PISTAS if dia.ruta in hay[p]}
            unidad = f' · {t["etiquetas"]["unidad"]} {dia.unidad}' if dia.unidad else ""
            migas = (f'{dia.nivel.upper()}{unidad} · {t["etiquetas"]["semana"]} {dia.semana} · '
                     f'{t["etiquetas"]["dia"]} {dia.dia} · {t["tipos"].get(dia.tipo, dia.tipo)}')
            aviso = "" if meta.get("revisado") else f'<p class="borrador">{e(t["borrador"])}</p>'
            anterior = (f'<a href="{raiz}/{ruta_leccion(pista, lista[i - 1][0])}">← {e(t["botones"]["anterior"])}</a>'
                        if i > 0 else "<span></span>")
            siguiente = (f'<a href="{raiz}/{ruta_leccion(pista, lista[i + 1][0])}">{e(t["botones"]["siguiente"])} →</a>'
                         if i + 1 < len(lista) else "<span></span>")
            indice = f'<a href="{raiz}/{pista}/{t["paginas"]["curso"]}">{e(t["botones"]["indice"])}</a>'
            articulo = html_de_leccion(cuerpo, pista, textos)
            test = pruebas.de_texto(meta, cuerpo, pista) if dia.tipo in pruebas.TIPOS else None
            if test:
                nuevo = envolver_test(articulo, test, pista, textos, raiz, hay[pista], dias)
                if nuevo != articulo:
                    articulo = nuevo + f'\n<script src="{raiz}/test.js" defer></script>'
            cuerpo_html = f"""<p class="migas">{e(migas)}</p>
<h1>{e(dia.tema(pista))}</h1>
<p class="ru-tema" lang="ru">{e(dia.ru)}</p>
{aviso}
<article>
{articulo}
</article>
<div class="final"><button id="marcar" class="boton" type="button" hidden aria-pressed="false"
 data-marcar="{e(t["botones"]["marcar"])}" data-hecha="{e(t["botones"]["hecha"])}">{e(t["botones"]["marcar"])}</button>
<span class="nota">{e(t["progreso"])}</span></div>
<nav class="vecinos">{anterior}{indice}{siguiente}</nav>"""
            principal = (f' data-leccion="{pista}/{dia.ruta}" data-url="{ruta}"'
                         f' data-titulo="{e(dia.tema(pista))}"')
            descripcion = f'{dia.nivel.upper()} · {t["etiquetas"]["semana"]} {dia.semana} · {dia.tema(pista)}. {t["lema"]}'
            texto = pagina(cfg, textos, pista, dia.tema(pista), cuerpo_html, ruta=ruta, raiz=raiz,
                           descripcion=descripcion, alternas=alternas, principal=principal)
            escribir(destino / ruta, texto)
            rutas.append(ruta)
    return rutas


# ── Índice del curso, portadas y páginas fijas ─────────────────────────

def construir_indice(cfg, textos, cal, destino, publicadas) -> list[str]:
    rutas = []
    for pista in PISTAS:
        t = textos[pista]
        hay = {d.ruta for d, _, _ in publicadas[pista]}
        bloques = [f"<h1>{e(t['menu']['curso'])}</h1>",
                   f'<p class="nota">{len(hay)} {e(t["etiquetas"]["disponibles"])}. {e(t["progreso"])}</p>']
        for nivel in plan.niveles(cal):
            dias = plan.dias_del_nivel(nivel)
            n_hay = sum(d.ruta in hay for d in dias)
            bloques.append(f'<section class="nivel"><h2>{e(nivel[pista])} '
                           f'<span class="tipo">{e(nivel["examen"])}</span></h2>'
                           f'<p class="nota">{n_hay} {e(t["etiquetas"]["de"])} {len(dias)}</p>')
            for u in nivel["unidades"]:
                propios = [d for d in dias if d.unidad == u["numero"]]
                abiertos = any(d.ruta in hay for d in propios)
                cabeza = (f'<summary>{e(t["etiquetas"]["unidad"])} {u["numero"]} · {e(u[pista])}'
                          f'<span class="ru" lang="ru">{e(u["ru"])}</span></summary>')
                if not any(d.detallado for d in propios):
                    bloques.append(f'<details class="unidad">{cabeza}<p class="nota">'
                                   f'{e(t["etiquetas"]["proximamente"])}</p></details>')
                    continue
                items = []
                for d in propios:
                    etiqueta = (f'<span class="tipo">{e(t["etiquetas"]["semana"][:1])}{d.semana}·'
                                f'{e(t["etiquetas"]["dia"][:1])}{d.dia}</span>')
                    if d.ruta in hay:
                        items.append(f'<li data-leccion-item="{pista}/{d.ruta}">{etiqueta}'
                                     f'<a href="{d.ruta}.html">{e(d.tema(pista))}</a></li>')
                    else:
                        items.append(f'<li class="pronto">{etiqueta}{e(d.tema(pista))} — '
                                     f'{e(t["etiquetas"]["proximamente"])}</li>')
                bloques.append(f'<details class="unidad"{" open" if abiertos else ""}>{cabeza}'
                               f'<ol>{"".join(items)}</ol></details>')
            bloques.append("</section>")
        ruta = f"{pista}/{t['paginas']['curso']}"
        otras = {p: f"{p}/{textos[p]['paginas']['curso']}" for p in PISTAS}
        escribir(destino / ruta, pagina(cfg, textos, pista, t["menu"]["curso"], "\n".join(bloques),
                                        ruta=ruta, raiz="..", alternas=otras, actual="curso"))
        rutas.append(ruta)
    return rutas


def construir_portadas(cfg, textos, cal, destino, publicadas) -> list[str]:
    rutas = []
    for pista in PISTAS:
        t = textos[pista]
        lista = publicadas[pista]
        sitio = cfg["nombre"][pista]
        empezar = (f'<a class="boton" href="{lista[0][0].ruta}.html">{e(t["botones"]["empezar"])}</a>'
                   if lista else "")
        continuar = (f'<a id="continuar" class="boton secundario" data-pista="{pista}" href="#" hidden>'
                     f'{e(t["botones"]["continuar"])}: <span class="donde"></span></a>')
        cuerpo = f"""<section class="heroe">
<h1>{e(sitio)}</h1>
<p class="lema">{e(t["lema"])}</p>
<div class="botones">{empezar}{continuar}</div>
<p class="nota">{e(t["progreso"])}</p>
</section>
{md(t["portada"].replace("{lecciones}", str(len(lista))))}"""
        ruta = f"{pista}/index.html"
        escribir(destino / ruta, pagina(cfg, textos, pista, sitio, cuerpo, ruta=ruta, raiz="..",
                                        alternas={p: f"{p}/index.html" for p in PISTAS}))
        rutas.append(ruta)
    # La raíz: las dos puertas, cada una en su lengua.
    puertas = "".join(
        f'<a class="puerta" lang="{p}" href="{p}/index.html"><strong>{e(cfg["nombre"][p])}</strong>'
        f'{e(textos[p]["lema"])}</a>' for p in PISTAS)
    cuerpo = (f'<section class="heroe"><h1 lang="ru">Ру́сский язы́к</h1>'
              f'<p class="lema">{e(textos["es"]["lema"])}<br><span lang="en">{e(textos["en"]["lema"])}</span></p>'
              f'</section><div class="puertas">{puertas}</div>'
              f'<p lang="es">{e(textos["es"]["descripcion"])}</p><p lang="en">{e(textos["en"]["descripcion"])}</p>')
    raiz_cfg = dict(cfg, nombre=dict(cfg["nombre"], raiz="Ruso · Russian"))
    escribir(destino / "index.html",
             pagina(raiz_cfg, textos, "raiz", "Ruso · Russian", cuerpo, ruta="index.html", raiz=".",
                    descripcion=textos["en"]["descripcion"],
                    alternas={"es": "es/index.html", "en": "en/index.html", "x-default": "index.html"}))
    rutas.append("index.html")
    return rutas


def construir_estaticas(cfg, textos, destino) -> list[str]:
    rutas = []
    for clave in ("sobre", "contacto", "privacidad"):
        for pista in PISTAS:
            t = textos[pista]
            texto = t[clave]
            if clave == "contacto":
                correo = cfg.get("contacto")
                texto = texto.replace("{correo}", f"[{correo}](mailto:{correo})" if correo else t["sin_correo"])
            ruta = f"{pista}/{t['paginas'][clave]}"
            otras = {p: f"{p}/{textos[p]['paginas'][clave]}" for p in PISTAS}
            escribir(destino / ruta, pagina(cfg, textos, pista, t["menu"][clave], md(texto), ruta=ruta,
                                            raiz="..", alternas=otras, actual=clave))
            rutas.append(ruta)
    return rutas


def construir_extras(cfg, destino, rutas) -> None:
    fuentes = destino / "fonts"
    fuentes.mkdir(parents=True, exist_ok=True)
    for f in (WEB / "fonts").glob("*.woff2"):
        shutil.copy2(f, fuentes / f.name)
    escribir(destino / "progreso.js", PROGRESO_JS)
    escribir(destino / "test.js", TEST_JS)
    dominio = (cfg.get("dominio") or "").rstrip("/")
    robots = "User-agent: *\nAllow: /\n"
    if dominio:
        robots += f"Sitemap: {dominio}/sitemap.xml\n"
        urls = "".join(f"<url><loc>{e(dominio + '/' + r)}</loc></url>" for r in sorted(rutas))
        escribir(destino / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
                 f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
        host = re.sub(r"^https?://", "", dominio)
        if not host.endswith("github.io"):
            escribir(destino / "CNAME", host + "\n")
    escribir(destino / "robots.txt", robots)
    # GitHub Pages pasa el sitio por Jekyll, que se salta las carpetas que
    # empiezan por «_» y puede romper rutas: este archivo lo apaga.
    escribir(destino / ".nojekyll", "")
    cliente = (cfg.get("adsense") or {}).get("cliente", "")
    if cliente:
        pub = cliente.replace("ca-", "")
        escribir(destino / "ads.txt", f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")


def escribir(ruta: pathlib.Path, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


def construir(destino: pathlib.Path = DOCS, cfg=None, textos=None, cal=None, curso: pathlib.Path = CURSO) -> dict:
    cfg = cfg or cargar_config()
    textos = textos or cargar_textos()
    cal = cal or plan.cargar()
    publicadas = escritas(cal, curso)
    rutas = []
    rutas += construir_lecciones(cfg, textos, cal, destino, publicadas)
    rutas += construir_indice(cfg, textos, cal, destino, publicadas)
    rutas += construir_portadas(cfg, textos, cal, destino, publicadas)
    rutas += construir_estaticas(cfg, textos, destino)
    construir_extras(cfg, destino, rutas)
    return {"paginas": rutas, "lecciones": {p: len(publicadas[p]) for p in PISTAS}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--destino", type=pathlib.Path, default=DOCS)
    args = ap.parse_args(argv)
    resumen = construir(args.destino)
    print(f"{len(resumen['paginas'])} páginas en {args.destino} · lecciones: "
          + ", ".join(f"{p} {n}" for p, n in resumen["lecciones"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
