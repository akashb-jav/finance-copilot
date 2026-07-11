function getMode() {
  return document.body.dataset.financeMode;
}

async function loadDashboard(mode) {
  const dashboard = await fetchDashboard(mode);
  const expenses = await fetchExpenses(mode);
  const savings = getLocalSavings(mode);

  return { dashboard, expenses, savings };
}

function renderSummary({ dashboard, savings }) {
  const budget = dashboard ? dashboard.total_budget : 0;
  const spent = dashboard ? dashboard.total_spent : 0;
  const remaining = dashboard ? dashboard.remaining : 0;

  document.getElementById("budget-value").textContent = formatAmount(budget);
  document.getElementById("spent-value").textContent = formatAmount(spent);
  document.getElementById("remaining-value").textContent = formatAmount(remaining);
  document.getElementById("savings-value").textContent = formatAmount(savings);
}

function renderExpenseList(expenses) {
  const container = document.getElementById("expense-list-items");
  container.innerHTML = "";

  if (!expenses || expenses.length === 0) {
    container.innerHTML = `<p style="color: var(--cream-dim); font-size: 0.9rem;">No expenses logged yet.</p>`;
    return;
  }

  [...expenses].reverse().forEach((expense) => {
    const category = normalizeCategory(expense.category);
    const row = document.createElement("div");
    row.className = "expense-item";
    row.innerHTML = `
      <span>${expense.description || category} <span class="category">· ${category}</span></span>
      <span>${formatAmount(expense.amount)}</span>
    `;
    container.appendChild(row);
  });
}

function initBudgetEdit(mode, state) {
  const editBtn = document.getElementById("edit-budget-btn");
  const budgetEl = document.getElementById("budget-value");

  editBtn.addEventListener("click", () => {
    const currentBudget = state.dashboard ? state.dashboard.total_budget : 0;

    const input = document.createElement("input");
    input.type = "number";
    input.value = currentBudget;
    input.style.width = "100%";
    input.style.textAlign = "center";
    input.style.fontSize = "1.4rem";
    input.style.background = "rgba(255,255,255,0.08)";
    input.style.border = "1px solid var(--glass-border)";
    input.style.borderRadius = "10px";
    input.style.color = "var(--cream)";
    input.style.padding = "0.3rem";

    budgetEl.replaceWith(input);
    input.focus();

    const commit = async () => {
      const newBudget = Number(input.value) || currentBudget;

      // backend now properly replaces the budget for this category+month,
      // so we just send the target amount directly
      await setBudget(mode, "Overall", newBudget);

      const refreshed = await loadDashboard(mode);
      Object.assign(state, refreshed);

      input.replaceWith(budgetEl);
      renderSummary(state);
    };

    input.addEventListener("blur", commit);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") input.blur();
    });
  });
}

function initExpenseForm(mode, state) {
  const addBtn = document.getElementById("add-expense-btn");
  const amountInput = document.getElementById("amount");
  const categorySelect = document.getElementById("category");

  addBtn.addEventListener("click", async () => {
    const amount = Number(amountInput.value);
    if (!amount || amount <= 0) {
      amountInput.focus();
      return;
    }

    const category = categorySelect.value;
    await addExpense(mode, category, amount, `${category} expense`);

    const refreshed = await loadDashboard(mode);
    Object.assign(state, refreshed);

    renderSummary(state);
    renderExpenseList(state.expenses);

    amountInput.value = "";
  });
}

async function initFinanceDashboard() {
  const mode = getMode();
  if (!mode) return;

  const state = await loadDashboard(mode);

  renderSummary(state);
  renderExpenseList(state.expenses);
  initBudgetEdit(mode, state);
  initExpenseForm(mode, state);
}

document.addEventListener("DOMContentLoaded", initFinanceDashboard);