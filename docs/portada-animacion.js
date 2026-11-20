(() => {
  const osos = document.querySelectorAll(".oso-animado");
  const reducir = window.matchMedia("(prefers-reduced-motion: reduce)");

  if (!Element.prototype.animate || !osos.length) return;

  const parpadeo = [
    {opacity: 0, transform: "scaleY(.35)"},
    {offset: .34, opacity: 1, transform: "scaleY(1)"},
    {offset: .59, opacity: 1, transform: "scaleY(1)"},
    {opacity: 0, transform: "scaleY(.35)"}
  ];

  const pasarHoja = [
    {opacity: 0, transform: "perspective(220px) rotateY(0deg)"},
    {offset: .18, opacity: 1, transform: "perspective(220px) rotateY(-16deg) rotate(-12deg)"},
    {offset: .49, opacity: 1, transform: "perspective(220px) rotateY(-80deg) rotate(-28deg)"},
    {offset: .82, opacity: 1, transform: "perspective(220px) rotateY(-155deg) rotate(-5deg)"},
    {opacity: 0, transform: "perspective(220px) rotateY(-178deg)"}
  ];

  function mover(elemento, cuadros, duracion, espera) {
    elemento.getAnimations().forEach(animacion => animacion.cancel());
    elemento.animate(cuadros, {duration: duracion, delay: espera, easing: "ease-in-out"});
  }

  function animar(oso, espera) {
    if (reducir.matches) return;
    oso.querySelectorAll(".parpado").forEach(ojo => mover(ojo, parpadeo, 230, espera));
    const hoja = oso.querySelector(".hoja-libro");
    if (hoja) mover(hoja, pasarHoja, 940, espera + 360);
  }

  const observador = "IntersectionObserver" in window ? new IntersectionObserver(entradas => {
    for (const entrada of entradas) {
      if (!entrada.isIntersecting) continue;
      observador.unobserve(entrada.target);
      animar(entrada.target, 650);
    }
  }, {threshold: .25}) : null;

  osos.forEach(oso => {
    const zona = oso.closest(".practica, .mascota");
    zona.addEventListener("pointerenter", evento => {
      if (evento.pointerType === "mouse") animar(oso, 0);
    });
    zona.addEventListener("focus", () => animar(oso, 0));
    if (observador) observador.observe(oso);
    else animar(oso, 650);
  });

  reducir.addEventListener("change", () => {
    if (!reducir.matches) return;
    for (const oso of osos) {
      oso.querySelectorAll(".parpado, .hoja-libro").forEach(pieza => {
        pieza.getAnimations().forEach(animacion => animacion.cancel());
      });
    }
  });
})();
