(function(){
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
