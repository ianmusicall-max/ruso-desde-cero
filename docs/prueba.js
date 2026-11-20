(function(){
// Las cuatro pruebas de dos minutos de la portada. Lo que de verdad enseña
// cada página está en el HTML: el alfabeto, las frases, el dibujo de la voz
// y las palabras —que se abren con <details>, sin guion—. Aquí solo van las
// tres cosas que un navegador puede hacer y una página estática no.
var d=document;

// El teclado cirílico de la prueba de escritura. La mayúscula se pone sola
// al principio y después de un espacio, que es la regla de un nombre.
var caja=d.getElementById('nombre-ru');
if(caja){
  d.querySelectorAll('.tecla').forEach(function(k){
    k.addEventListener('click',function(){
      var l=k.getAttribute('data-letra')||'';
      if(!caja.value||/\s$/.test(caja.value))l=l.toUpperCase();
      caja.value+=l;caja.focus();
    });
  });
  var una=d.getElementById('borra-letra');
  if(una)una.addEventListener('click',function(){caja.value=caja.value.slice(0,-1);caja.focus()});
  var todo=d.getElementById('borra-todo');
  if(todo)todo.addEventListener('click',function(){caja.value='';caja.focus()});
}

// El nombre entra en el diálogo mientras se escribe. Sin guion, las líneas
// ya se leen con un «…» en su sitio.
var mio=d.getElementById('mi-nombre'),dialogo=d.getElementById('dialogo');
if(mio&&dialogo){
  var huecos=[];
  dialogo.querySelectorAll('[data-plantilla]').forEach(function(s){
    var p=s.getAttribute('data-plantilla');
    if(p&&p.indexOf('{nombre}')>=0)huecos.push([s,p]);
  });
  var poner=function(){
    var n=mio.value.trim()||'___';
    huecos.forEach(function(h){h[0].textContent=h[1].replace('{nombre}',n)});
  };
  mio.addEventListener('input',poner);
  poner();
}

// Grabarse y oírse. Nace oculto y lo enciende el navegador: un botón de
// grabar que no puede grabar es peor que ninguno, y además pediría permiso
// para nada. La grabación vive en memoria, no se sube a ninguna parte y
// muere con la pestaña.
var zona=d.getElementById('grabadora'),boton=d.getElementById('graba'),
    audio=d.getElementById('mi-voz'),aviso=d.getElementById('sin-micro');
if(zona&&boton&&audio&&window.MediaRecorder&&navigator.mediaDevices&&
   navigator.mediaDevices.getUserMedia){
  zona.hidden=false;
  var rec=null,trozos=[],url=null;
  boton.addEventListener('click',function(){
    if(rec&&rec.state==='recording'){rec.stop();return}
    navigator.mediaDevices.getUserMedia({audio:true}).then(function(flujo){
      trozos=[];rec=new MediaRecorder(flujo);
      rec.addEventListener('dataavailable',function(ev){if(ev.data&&ev.data.size)trozos.push(ev.data)});
      rec.addEventListener('stop',function(){
        // El micrófono se apaga de verdad: si no, el punto rojo de la
        // pestaña se queda encendido y se lee como que el sitio escucha.
        flujo.getTracks().forEach(function(p){p.stop()});
        if(url)URL.revokeObjectURL(url);
        url=URL.createObjectURL(new Blob(trozos,{type:rec.mimeType||''}));
        audio.src=url;audio.hidden=false;
        boton.textContent=boton.getAttribute('data-graba');
        boton.setAttribute('aria-pressed','false');
      });
      rec.start();
      boton.textContent=boton.getAttribute('data-para');
      boton.setAttribute('aria-pressed','true');
    }).catch(function(){
      // Permiso denegado o micrófono ocupado: se dice, y la prueba sigue.
      boton.hidden=true;
      if(aviso)aviso.hidden=false;
    });
  });
}
})();
