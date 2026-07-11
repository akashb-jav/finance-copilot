const API_BASE_URL = "https://finance-copilot-production-ca23.up.railway.app";

const USER_ID_MAP = {
  student: 1,
  working: 2,
  personal: 3,
};

async function fetchDashboard(mode) {
  const userId = USER_ID_MAP[mode];
  try {
    const res = await fetch(`${API_BASE_URL}/dashboard/${userId}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.warn("couldn't reach backend for dashboard", e);
    return null;
  }
}

async function fetchExpenses(mode) {
  const userId = USER_ID_MAP[mode];
  try {
    const res = await fetch(`${API_BASE_URL}/expenses/${userId}`);
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data) ? data : data.expenses || [];
  } catch (e) {
    console.warn("couldn't reach backend for expenses", e);
    return [];
  }
}

async function setBudget(mode, category, amount) {
  const userId = USER_ID_MAP[mode];
  const month = new Date().toISOString().slice(0, 7);

  try {
    const res = await fetch(`${API_BASE_URL}/budget`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, category, amount, month }),
    });
    return res.ok;
  } catch (e) {
    console.warn("failed to set budget", e);
    return false;
  }
}

async function addExpense(mode, category, amount, description) {
  const userId = USER_ID_MAP[mode];
  const date = new Date().toISOString().split("T")[0];

  try {
    const res = await fetch(`${API_BASE_URL}/expenses`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, category, amount, description, date }),
    });
    return res.ok;
  } catch (e) {
    console.warn("failed to add expense", e);
    return false;
  }
}

function getLocalSavings(mode) {
  return Number(localStorage.getItem(`financeai:${mode}:savings`)) || 0;
}

function setLocalSavings(mode, amount) {
  localStorage.setItem(`financeai:${mode}:savings`, amount);
}

// backend doesn't enforce category casing ("food" vs "Food" both exist in test data),
// so anywhere we group/match by category, run it through this first
function normalizeCategory(category) {
  if (!category) return "Miscellaneous";
  return category.charAt(0).toUpperCase() + category.slice(1).toLowerCase();
}

function formatAmount(n) {
  return "₹" + Math.round(n).toLocaleString("en-IN");
}

function parseAmount(text) {
  return Number(text.replace(/[^\d.]/g, "")) || 0;
}