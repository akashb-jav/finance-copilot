async function getCombinedFinanceData() {
  const modes = ["student", "working", "personal"];
  let budget = 0;
  let spent = 0;
  let remaining = 0;
  let expenses = [];
  let predictions = [];
  let categoryWarnings = [];
  let found = false;

  for (const mode of modes) {
    const dashboard = await fetchDashboard(mode);
    const modeExpenses = await fetchExpenses(mode);
    if (!dashboard) continue;

    budget += dashboard.total_budget;
    spent += dashboard.total_spent;
    remaining += dashboard.remaining;
    expenses = expenses.concat(modeExpenses);

    // only keep predictions that actually say something useful -
    // skip empty-state ones so we don't show 3 copies of "no expenses yet"
    if (dashboard.prediction && dashboard.total_spent > 0) {
      predictions.push(dashboard.prediction);
    }

    Object.entries(dashboard.categories || {}).forEach(([name, info]) => {
      if (info.warning) categoryWarnings.push(normalizeCategory(name));
    });

    found = true;
  }

  return found ? { budget, spent, remaining, expenses, predictions, categoryWarnings } : null;
}

function renderAlerts(data) {
  const container = document.getElementById("alerts-list");
  const alerts = [];

  if (data.remaining < 0) {
    alerts.push({
      critical: true,
      text: `You're ${formatAmount(Math.abs(data.remaining))} over budget this month.`,
    });
  } else if (data.budget > 0 && data.remaining < data.budget * 0.15) {
    alerts.push({
      critical: false,
      text: `You're down to less than 15% of your budget remaining.`,
    });
  }

  data.categoryWarnings.forEach((cat) => {
    alerts.push({ critical: false, text: `${cat} is flagged as running high this month.` });
  });

  if (alerts.length === 0) {
    container.innerHTML = `
      <div class="alert-item">
        <span class="alert-dot"></span>
        <span>Nothing concerning right now — you're on track.</span>
      </div>`;
    return;
  }

  container.innerHTML = alerts
    .map(
      (a) => `
      <div class="alert-item ${a.critical ? "is-critical" : ""}">
        <span class="alert-dot"></span>
        <span>${a.text}</span>
      </div>`
    )
    .join("");
}

function renderTips(data) {
  const container = document.getElementById("tips-list");
  const tips = [...data.predictions]; // real predictions from the backend, deduped/filtered already

  tips.push(`Setting aside a fixed amount right after payday tends to stick better than saving "whatever's left."`);

  container.innerHTML = tips.map((t) => `<div class="tip-item">${t}</div>`).join("");
}

function renderSpendingPie(data) {
  const legendContainer = document.getElementById("pie-legend");
  const totals = {};

  data.expenses.forEach((e) => {
    const cat = normalizeCategory(e.category);
    totals[cat] = (totals[cat] || 0) + e.amount;
  });

  const legendData = drawSpendingPie(totals); // from charts.js

  if (legendData.length === 0) {
    legendContainer.innerHTML = `<p class="comparison-empty">No spending data yet.</p>`;
    return;
  }

  legendContainer.innerHTML = legendData
    .map(
      (item) => `
      <div class="pie-legend-item">
        <span class="pie-legend-swatch" style="background: ${item.color};"></span>
        <span class="pie-legend-label">${item.category}</span>
        <span class="pie-legend-value">${formatAmount(item.amount)}</span>
      </div>`
    )
    .join("");
}

async function initPredictor() {
  const data = await getCombinedFinanceData();
  const caption = document.getElementById("forecast-caption");

  if (!data || data.expenses.length === 0) {
    return; // leave the empty-state placeholders already in the HTML
  }

  caption.textContent =
    data.remaining >= 0
      ? `Projected to end the month with ${formatAmount(data.remaining)} remaining.`
      : `Projected to go ${formatAmount(Math.abs(data.remaining))} over budget by month end.`;

  renderAlerts(data);
  renderTips(data);
  renderSpendingPie(data);
}

document.addEventListener("DOMContentLoaded", initPredictor);