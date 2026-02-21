/* ─── app.js  ─── Shared JS logic for CTF Platform ─── */

const API = {
  login: (data) => post("/login", data),
  logout: () => post("/logout", {}),
  me: () => get("/me"),

  // Admin
  createChallenge: (formData) => postForm("/admin/challenges", formData),
  adminChallenges: () => get("/admin/challenges"),
  deleteChallenge: (id) => del(`/admin/challenges/${id}`),
  adminSubmissions: () => get("/admin/submissions"),
  adminLeaderboard: () => get("/admin/leaderboard"),

  // Participant
  challenges: () => get("/challenges"),
  submitFlag: (data) => post("/submit-flag", data),
  leaderboard: () => get("/leaderboard"),
};

async function get(url) {
  const r = await fetch(url, { credentials: "same-origin" });
  if (!r.ok) {
    if (r.status === 401) { window.location.href = "/login"; return; }
    throw await r.json();
  }
  return r.json();
}

async function post(url, data) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
    credentials: "same-origin",
  });
  return r.json();
}

async function postForm(url, formData) {
  const r = await fetch(url, {
    method: "POST",
    body: formData,
    credentials: "same-origin",
  });
  return r.json();
}

async function del(url) {
  const r = await fetch(url, { method: "DELETE", credentials: "same-origin" });
  return r.json();
}

function toast(msg, type = "info") {
  const t = document.createElement("div");
  t.className = `alert alert-${type}`;
  t.style.cssText = "position:fixed;top:1.5rem;right:1.5rem;z-index:9999;min-width:280px;animation:fadeIn 0.3s ease;";
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

function categoryBadge(cat) {
  const map = { welcome: "👋", web: "🌐", forensic: "🔬", osint: "🕵️", steg: "🖼️", crypto: "🔐" };
  return `<span class="badge badge-${cat}">${(map[cat] || "🏁")} ${cat.toUpperCase()}</span>`;
}

function categoryColor(cat) {
  const map = { welcome: "var(--accent-green)", web: "var(--cat-web)", forensic: "var(--cat-forensic)", osint: "var(--cat-osint)", steg: "var(--cat-steg)", crypto: "var(--cat-crypto)" };
  return map[cat] || "var(--accent-green)";
}

function categoryIcon(cat) {
  const map = { welcome: "👋", web: "🌐", forensic: "🔬", osint: "🕵️", steg: "🖼️", crypto: "🔐" };
  return map[cat] || "🏁";
}

function escHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// Tabs
function initTabs(tabsContainer) {
  const btns = tabsContainer.querySelectorAll(".tab-btn");
  btns.forEach(btn => {
    btn.addEventListener("click", () => {
      const panel = btn.dataset.tab;
      btns.forEach(b => b.classList.remove("active"));
      tabsContainer.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(panel).classList.add("active");
    });
  });
}

// Logout
function setupLogout() {
  const btn = document.getElementById("logout-btn");
  if (btn) {
    btn.addEventListener("click", async () => {
      await API.logout();
      window.location.href = "/login";
    });
  }
}
