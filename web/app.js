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

function daysOpen(iso) {
  const then = new Date(iso + "T00:00:00Z");
  const asOf = new Date("2026-09-30T00:00:00Z");
  return Math.round((asOf - then) / 86400000);
}

function renderBrief(b) {
  const hold = b.stock.flag === "Do not push"
    || b.stock.flag === "No scan coverage"
    || b.stock.flag === "Too thin to call";
  const credits = b.pending_credits.length
    ? b.pending_credits.map((c) => `
        <li>
          <span>${esc(c.scheme)}</span>
          <b>${esc(c.amount)}</b>
          <small>accrued ${esc(c.accrued)} · ${daysOpen(c.accrued)} days</small>
        </li>`).join("")
    : `<li class="none">No unissued credits.</li>`;

  document.getElementById("brief").innerHTML = `
    <p class="eyebrow">${esc(b.distributor.distributor_id)} · ${esc(b.distributor.tier)}</p>
    <h2>${esc(b.distributor.name)}</h2>
    <p class="ask">${esc(b.collect_after_credits)} <small>left to collect once the notes are issued</small></p>
    <p class="talk">${esc(b.talking_point)}</p>
    <div class="pair">
      <div><small>Unissued credits</small><b>${esc(b.pending_total)}</b></div>
      <div><small>Held as disputed</small><b>${esc(b.disputed)}</b></div>
    </div>
    <p class="stock ${hold ? "warn" : ""}">
      <strong>${esc(b.stock.flag)}.</strong> ${esc(b.stock.line)}
      <span>${esc(b.stock.coverage)}. Scans ${Math.round(b.stock.recent_scans)} against ${Math.round(b.stock.prior_scans)} in the prior 8 weeks.</span>
    </p>
    <h3>Raise these</h3>
    <ol class="credits">${credits}</ol>
    <details>
      <summary>The other numbers</summary>
      <div class="pair quiet">
        <div><small>Overdue · ${esc(b.aging_snapshot || "no snapshot")}</small><b>${esc(b.overdue)}</b></div>
        <div><small>FY2026 sales · M01 gross</small><b>${esc(b.fy26_sales)}</b></div>
        <div><small>${esc(pct(b.fy26_vs_fy25))}</small><b>${esc(b.fy25_sales)}</b></div>
      </div>
      <p class="meta">
        Sales is M01: gross sell-in, order date, ${esc(b.distributor.currency)} only.
        Overdue is the latest aging snapshot, not live ERP.
        Orders through ${esc(b.freshness.orders_as_of)}. Aging through ${esc(b.freshness.aging_as_of)}.
        Cancelled credits are excluded. Nothing is converted to USD.
      </p>
    </details>
  `;
}

function addRow(list, item, quiet) {
  const btn = document.createElement("button");
  btn.className = "row" + (item.rank === 0 ? " dispute" : "");
  btn.innerHTML = quiet
    ? `<strong>${esc(item.name)}</strong><span>Nothing to raise</span>`
    : `<strong>${esc(item.name)}</strong><span>${esc(item.pending)} · ${item.credit_count} ${item.credit_count === 1 ? "credit" : "credits"}</span>`;
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
  const first = list.querySelector("button.row");
  if (first) first.click();
}

main().catch((err) => {
  document.getElementById("brief").textContent = err.message;
});
