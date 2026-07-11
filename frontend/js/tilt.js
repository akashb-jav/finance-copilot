// subtle tilt on hover, tracks cursor position within each card
const TILT_MAX_DEG = 6;

function attachTilt(card) {
  card.style.perspective = "800px";

  card.addEventListener("mousemove", (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateY = ((x - centerX) / centerX) * TILT_MAX_DEG;
    const rotateX = -((y - centerY) / centerY) * TILT_MAX_DEG;

    card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
  });

  card.addEventListener("mouseleave", () => {
    card.style.transform = "";
  });
}

function initTilt() {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) return;

  document.querySelectorAll(".glass-card").forEach(attachTilt);
}

document.addEventListener("DOMContentLoaded", initTilt);