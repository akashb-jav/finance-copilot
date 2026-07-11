// ambient dust/orb background, shared config so it looks identical page to page
const particleConfig = {
  fullScreen: { enable: false },
  background: { color: { value: "transparent" } },
  fpsLimit: 60,
  particles: {
    number: {
      value: 70,
      density: { enable: true, area: 900 },
    },
    color: {
      value: ["#F5EDE4", "#E8D9C5", "#C2A98A"],
    },
    shape: { type: "circle" },
    opacity: {
      value: { min: 0.08, max: 0.32 },
      animation: { enable: true, speed: 0.5, sync: false },
    },
    size: {
      value: { min: 1, max: 7 },
      animation: { enable: true, speed: 1.2, sync: false },
    },
    // faint connecting lines between nearby particles - reads as a data/network feel
    links: {
      enable: true,
      distance: 140,
      color: "#E8D9C5",
      opacity: 0.12,
      width: 1,
    },
    // occasional glints in the accent gold color, sells the "premium" feel
    twinkle: {
      particles: {
        enable: true,
        frequency: 0.02,
        opacity: 0.6,
        color: { value: "#E8C39E" },
      },
    },
    move: {
      enable: true,
      speed: 0.4,
      direction: "top",
      random: true,
      straight: false,
      outModes: { default: "out" },
    },
  },
  interactivity: {
    events: {
      onHover: { enable: false },
      onClick: { enable: false },
    },
  },
  detectRetina: true,
};

function initParticleBackground() {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) return;

  if (typeof tsParticles === "undefined") {
    console.warn("tsParticles script not loaded before background.js");
    return;
  }

  tsParticles.load({ id: "particle-bg", options: particleConfig });
}

document.addEventListener("DOMContentLoaded", initParticleBackground);
