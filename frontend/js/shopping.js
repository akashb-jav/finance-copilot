let latestRecommendation = null;
const API = "https://finance-copilot-production-ca23.up.railway.app";

function initSearch() {
  const input = document.getElementById("search-input");
  const btn = document.getElementById("search-btn");

  async function search() {

    const product = input.value.trim();

    if (!product) return;

    const res = await fetch(
      `${API}/shopping?product=${encodeURIComponent(product)}`
    );

    const data = await res.json();
    latestRecommendation = data;

    displayProducts(data);

  }

  btn.addEventListener("click", search);

  input.addEventListener("keydown", e => {
    if(e.key==="Enter") search();
  });

}
function displayProducts(data){

    const grid=document.getElementById("product-grid");

    grid.innerHTML="";

    data.all_products.forEach(product=>{

        grid.innerHTML+=`

        <div class="glass-card product-card"
             data-price="${product.price.replace(/[^\d]/g,'')}">

            <img src="${product.thumbnail}" alt="${product.title}">

            <div class="product-name">
                ${product.title}
            </div>

            <div class="product-price">
                ${product.price}
            </div>

            <div class="product-meta">
                ${product.source}
            </div>

            <button class="compare-btn">
                Add to Compare
            </button>

        </div>

        `;

    });

    initCompare();
    updateRecommendation();

    document.getElementById("verdict-text").textContent =
        data.recommendation;

    document.getElementById("verdict-reason").textContent =
        data.reason;

}

function renderComparison(selected) {
  const table = document.getElementById("comparison-table");

  if (selected.length === 0) {
    table.innerHTML = `<p class="comparison-empty">Add a couple of products above to compare them side by side.</p>`;
    return;
  }

  table.innerHTML = selected
    .map((card) => {
      const name = card.querySelector(".product-name").textContent;
      const price = card.querySelector(".product-price").textContent;
      const meta = card.querySelector(".product-meta").textContent;
      return `
        <div class="glass-card">
          <div class="product-name">${name}</div>
          <div class="product-price">${price}</div>
          <div class="product-meta">${meta}</div>
        </div>
      `;
    })
    .join("");
}



function updateRecommendation() {

    const verdictEl = document.getElementById("verdict-text");
    const reasonEl = document.getElementById("verdict-reason");

    if (!latestRecommendation) {
        verdictEl.textContent = "Search a product";
        verdictEl.className = "verdict";

        reasonEl.textContent =
            "Search a product to get AI recommendation.";

        return;
    }

    const recommendation = latestRecommendation.recommendation;

    if (recommendation === "buy_now") {
        verdictEl.textContent = "Buy Now";
        verdictEl.className = "verdict buy";
    }

    else if (recommendation === "wait") {
        verdictEl.textContent = "Wait";
        verdictEl.className = "verdict wait";
    }

    else if (recommendation === "compare_more") {
        verdictEl.textContent = "Compare More";
        verdictEl.className = "verdict";
    }

    else {
        verdictEl.textContent = recommendation;
        verdictEl.className = "verdict";
    }

    reasonEl.textContent = latestRecommendation.reason;
}

function initCompare() {
  const selected = [];
  const MAX_COMPARE = 3;

  document.querySelectorAll(".product-card").forEach((card) => {
    const btn = card.querySelector(".compare-btn");

    btn.addEventListener("click", async () => {
      const index = selected.indexOf(card);

      if (index > -1) {
        // Remove from comparison
        selected.splice(index, 1);
        btn.classList.remove("is-selected");
        btn.textContent = "Add to Compare";
      } else {
        if (selected.length >= MAX_COMPARE) {
          alert("You can compare up to 3 products only.");
          return;
        }

        // Add to comparison
        selected.push(card);
        btn.classList.add("is-selected");
        btn.textContent = "Selected";
      }

      renderComparison(selected);

      // Optional: Keep this if you want budget comparison
     updateRecommendation();
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initSearch();
  initCompare();
});