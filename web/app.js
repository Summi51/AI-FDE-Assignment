const USER = "U042";

async function get(path) {
  const res = await fetch(path);
  const body = await res.json();
  if (!res.ok) throw new Error(body.error || "Request failed");
  return body;
}

function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function pct(value) {
  if (value == null) return "no prior year";
  const n = Math.round(value * 100);
  return (n > 0 ? "+" : "") + n + "% vs FY2025";
}

function renderBrief(b) {
  const credits = b.pending_credits.length
    ? `<table>
        <thead><tr><th>Accrued</th><th>Scheme</th><th>Amount</th></tr></thead>
        <tbody>
          ${b.pending_credits.map((c) => `
            <tr><td>${esc(c.accrued)}</td><td>${esc(c.scheme)}</td><td>${esc(c.amount)}</td></tr>
          `).join("")}
        </tbody>
      </table>`
    : `<p class="empty">No unissued credits.</p>`;

  document.getElementById("brief").innerHTML = `
    <p class="eyebrow">${esc(b.distributor.distributor_id)} · ${esc(b.distributor.tier)}</p>
    <h2>${esc(b.distributor.name)}</h2>
    <p class="talk">${esc(b.talking_point)}</p>
    <p class="stock ${b.stock.flag === "Do not push" || b.stock.flag === "No scan coverage" || b.stock.flag === "Too thin to call" ? "warn" : ""}">
      <strong>${esc(b.stock.flag)}.</strong> ${esc(b.stock.line)}
      <span>${b.stock.coverage}. Scans ${Math.round(b.stock.recent_scans)} vs ${Math.round(b.stock.prior_scans)} prior 8 weeks.</span>
    </p>
    <div class="nums">
      <div><small>Unissued credits</small><b>${b.pending_total}</b></div>
      <div><small>Overdue · snapshot ${b.aging_snapshot || "—"}</small><b>${b.overdue}</b></div>
      <div><small>Of which disputed</small><b>${b.disputed}</b></div>
      <div><small>Collect after credits issue</small><b>${b.collect_after_credits}</b></div>
      <div><small>FY2026 sales (M01, gross)</small><b>${b.fy26_sales}</b></div>
      <div><small>${pct(b.fy26_vs_fy25)}</small><b>${b.fy25_sales}</b></div>
    </div>
    <h3>Credits still accrued, not issued</h3>
    ${credits}
    <p class="meta">
      Sales is M01: gross sell-in, order date, ${b.distributor.currency} only.
      Overdue is the latest aging snapshot, not live ERP.
      Orders loaded through ${b.freshness.orders_as_of}. Aging through ${b.freshness.aging_as_of}.
      Cancelled credits are excluded. Amounts are not converted to USD.
    </p>
  `;
}

function addRow(list, item, quiet) {
  const btn = document.createElement("button");
  btn.className = "row";
  btn.innerHTML = quiet
    ? `<strong>${esc(item.name)}</strong><span>No action</span>`
    : `<strong>${esc(item.name)}</strong><span>${esc(item.action)} · ${esc(item.pending)}</span>`;
  btn.onclick = async () => {
    document.querySelectorAll("button.row").forEach((el) => el.classList.remove("active"));
    btn.classList.add("active");
    try {
      renderBrief(await get(`/api/brief?user=${USER}&distributor=${encodeURIComponent(item.distributor_id)}`));
    } catch (err) {
      document.getElementById("brief").textContent = err.message;
    }
  };
  list.appendChild(btn);
}

async function main() {
  const monday = await get(`/api/monday?user=${USER}`);
  document.getElementById("who").textContent =
    `${monday.user.user_id} · ${monday.territory_code} · orders through ${monday.freshness.orders_as_of}`;
  document.getElementById("eyebrow").textContent =
    `${monday.call_first.length} to raise before 9:30 · aging through ${monday.freshness.aging_as_of}`;
  const list = document.getElementById("list");
  monday.call_first.forEach((item) => addRow(list, item, false));
  monday.quiet.forEach((item) => addRow(list, item, true));
}

main().catch((err) => {
  document.getElementById("brief").textContent = err.message;
});
