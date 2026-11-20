"use strict";

const voz = window.speechSynthesis;
const botones = document.querySelectorAll("[data-escucha]");

if (voz && window.SpeechSynthesisUtterance) {
  function vozRusa() {
    return voz.getVoices().find(opcion => /^ru(?:[-_]|$)/i.test(opcion.lang));
  }

  voz.getVoices();

  botones.forEach(boton => {
    const estado = document.getElementById(boton.getAttribute("aria-describedby"));
    boton.addEventListener("click", () => {
      const rusa = vozRusa();
      if (!rusa) {
        estado.textContent = boton.dataset.sinVoz;
        return;
      }
      voz.cancel();
      const lectura = new SpeechSynthesisUtterance(boton.dataset.escucha.replace(/\u0301/g, ""));
      lectura.lang = rusa.lang;
      lectura.voice = rusa;
      lectura.rate = 0.85;
      lectura.onerror = ({error}) => {
        if (error !== "canceled" && error !== "interrupted") {
          estado.textContent = boton.dataset.sinVoz;
        }
      };
      estado.textContent = "";
      voz.speak(lectura);
    });
    boton.hidden = false;
  });
}
