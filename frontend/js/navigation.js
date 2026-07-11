// where each card's "Get Started" takes you by default (used on index.html).
// a page can override this by defining window.PAGE_ROUTES before this script loads.
const DEFAULT_ROUTES = {
  finance: "pages/finance/finance.html",
  shopping: "pages/shopping/shopping.html",
  predictor: "pages/predictor/predictor.html",
};

const ROUTES = window.PAGE_ROUTES || DEFAULT_ROUTES;

const TRANSITION_DELAY_MS = 450; // should roughly match --med in style.css

function collapseAllCards(cards) {
  cards.forEach((c) => {
    c.classList.remove("is-expanding");
    c.classList.remove("scene-blur");
  });
}

function expandCard(card, allCards) {
  // kill any inline tilt transform so the class-based expand transform applies cleanly
  card.style.transform = "";

  card.classList.add("is-expanding");
  allCards.forEach((c) => {
    if (c !== card) c.classList.add("scene-blur");
  });
}

function goTo(route) {
  const overlay = document.querySelector(".transition-overlay");
  if (overlay) overlay.classList.add("is-active");

  setTimeout(() => {
    window.location.href = route;
  }, TRANSITION_DELAY_MS);
}

function initNavigation() {
  const cards = Array.from(document.querySelectorAll(".glass-card"));
  if (!cards.length) return;

  cards.forEach((card) => {
    card.addEventListener("click", (e) => {
      const alreadyExpanded = card.classList.contains("is-expanding");

      if (!alreadyExpanded) {
        collapseAllCards(cards);
        expandCard(card, cards);
        return;
      }
    });

    const btn = card.querySelector(".get-started-btn");
    if (btn) {
      btn.addEventListener("click", (e) => {
        e.stopPropagation(); // don't let this also trigger the card's own click handler
        const mode = card.dataset.mode;
        const route = ROUTES[mode];
        if (route) goTo(route);
      });
    }
  });

  // clicking outside any card collapses whatever's expanded
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".glass-card")) {
      collapseAllCards(cards);
    }
  });
}

document.addEventListener("DOMContentLoaded", initNavigation);