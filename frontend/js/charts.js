function getDaysInfo() {
  const now = new Date();
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
  const currentDay = now.getDate();
  return { daysInMonth, currentDay };
}

function drawForecast(data) {
  const canvas = document.getElementById("forecast-canvas");
  const ctx = canvas.getContext("2d");

  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = 220;

  const { daysInMonth, currentDay } = getDaysInfo();
  const now = new Date();
  const spent = data.expenses.reduce((sum, e) => sum + e.amount, 0);
  const dailyAvg = spent / Math.max(currentDay, 1);
  const projectedEnd = data.budget - dailyAvg * daysInMonth;

  const w = canvas.width;
  const h = canvas.height;
  const padding = 24;

  const maxVal = data.budget;
  const minVal = Math.min(projectedEnd, 0);

  const xForDay = (day) => padding + (day / daysInMonth) * (w - padding * 2);
  const yForVal = (val) => {
    const range = maxVal - minVal || 1;
    return h - padding - ((val - minVal) / range) * (h - padding * 2);
  };

  ctx.clearRect(0, 0, w, h);

  ctx.strokeStyle = "rgba(255,255,255,0.15)";
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(padding, yForVal(0));
  ctx.lineTo(w - padding, yForVal(0));
  ctx.stroke();
  ctx.setLineDash([]);

  const expensesWithDay = data.expenses.map((e) => {
    let day = 0;
    if (e.date) {
      const d = new Date(e.date);
      const isSameMonth = d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
      day = isSameMonth ? d.getDate() : 0;
    }
    return { ...e, day };
  });

  expensesWithDay.sort((a, b) => a.day - b.day);

  const points = [{ day: 0, balance: data.budget }];
  let running = data.budget;
  expensesWithDay.forEach((e) => {
    running -= e.amount;
    points.push({ day: e.day, balance: running });
  });
  if (points[points.length - 1].day < currentDay) {
    points.push({ day: currentDay, balance: running });
  }

  ctx.strokeStyle = "#F5EDE4";
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  points.forEach((p, i) => {
    const x = xForDay(p.day);
    const y = yForVal(p.balance);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  ctx.strokeStyle = "#E8C39E";
  ctx.lineWidth = 2.5;
  ctx.setLineDash([6, 5]);
  ctx.beginPath();
  ctx.moveTo(xForDay(currentDay), yForVal(running));
  ctx.lineTo(xForDay(daysInMonth), yForVal(projectedEnd));
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = "#F5EDE4";
  ctx.beginPath();
  ctx.arc(xForDay(currentDay), yForVal(running), 4, 0, Math.PI * 2);
  ctx.fill();

  return { projectedEnd, dailyAvg, currentDay, daysInMonth };
}
// warm tones from the palette, cycled if there are more categories than colors
const PIE_COLORS = ["#E8C39E", "#C2A98A", "#997E67", "#6B5745", "#F5EDE4", "#D8CBBB"];

function drawSpendingPie(categoryTotals) {
  const canvas = document.getElementById("spending-pie");
  const ctx = canvas.getContext("2d");
  const entries = Object.entries(categoryTotals);

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (entries.length === 0) return [];

  const total = entries.reduce((sum, [, amt]) => sum + amt, 0);
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const radius = Math.min(cx, cy) - 8;

  let startAngle = -Math.PI / 2; // start at 12 o'clock

  const legendData = entries.map(([category, amount], i) => {
    const color = PIE_COLORS[i % PIE_COLORS.length];
    const sliceAngle = (amount / total) * Math.PI * 2;
    const endAngle = startAngle + sliceAngle;

    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, radius, startAngle, endAngle);
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();

    startAngle = endAngle;

    return { category, amount, color };
  });

  return legendData;
}