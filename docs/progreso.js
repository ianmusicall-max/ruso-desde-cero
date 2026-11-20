(function(){
var d=document,raiz=d.documentElement.getAttribute('data-raiz')||'.';
function leer(k,def){try{var v=localStorage.getItem(k);return v===null?def:JSON.parse(v)}catch(e){return def}}
function guardar(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
var b=d.getElementById('tema');
if(b){b.addEventListener('click',function(){var h=d.documentElement,a=h.getAttribute('data-tema');
  var nuevo=a==='dark'?'light':'dark';h.setAttribute('data-tema',nuevo);guardar('rdc.tema',nuevo);});}
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
// El buscador del índice. Filtra por el texto de cada lección, sin acentos
// ni mayúsculas, y abre las unidades donde queda algo. Nace oculto en el
// HTML: si no hay JavaScript, la lista entera se sigue leyendo.
var caja=d.querySelector('.buscador');
if(caja){var campo=d.getElementById('buscar'),nada=d.getElementById('buscar-nada');
  var llanas=function(s){return (s||'').toLowerCase().replace(/\u0301/g,'')
    .normalize('NFD').replace(/[\u0300-\u036f]/g,'');};
  var unidades=d.querySelectorAll('details.unidad'),secciones=d.querySelectorAll('section.nivel');
  caja.hidden=false;
  campo.addEventListener('input',function(){
    var q=llanas(campo.value).trim(),vivos=0;
    for(var i=0;i<unidades.length;i++){var u=unidades[i],lis=u.querySelectorAll('li'),deja=0;
      for(var j=0;j<lis.length;j++){var ok=!q||llanas(lis[j].textContent).indexOf(q)>=0;
        lis[j].hidden=!ok;if(ok)deja++;}
      var cabe=!q||llanas(u.querySelector('summary').textContent).indexOf(q)>=0;
      if(cabe&&q){for(var j2=0;j2<lis.length;j2++)lis[j2].hidden=false;deja=lis.length;}
      u.hidden=q&&!deja&&!cabe;if(!u.hidden)vivos+=deja||1;
      if(q&&!u.hidden)u.open=true;}
    for(var k=0;k<secciones.length;k++){var vis=secciones[k].querySelectorAll('details.unidad:not([hidden])');
      secciones[k].hidden=q&&!vis.length;}
    if(nada)nada.hidden=!(q&&!vivos);});}
})();
