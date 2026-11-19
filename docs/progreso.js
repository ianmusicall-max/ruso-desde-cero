(function(){
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
