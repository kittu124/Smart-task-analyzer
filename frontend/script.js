// Adjust this if backend runs on a different host/port
const API_BASE = "http://127.0.0.1:8000/api/tasks";

const tasks = []; // local in-browser tasks
let nextId = 1;

const form = document.getElementById("task-form");
const bulkInput = document.getElementById("bulk-input");
const strategySelect = document.getElementById("strategy");
const analyzeBtn = document.getElementById("analyze-btn");
const suggestBtn = document.getElementById("suggest-btn");
const statusEl = document.getElementById("status");
const localTasksEl = document.getElementById("local-tasks");
const resultsEl = document.getElementById("results");

function setStatus(message, type = "") {
  statusEl.textContent = message || "";
  statusEl.className = "status" + (type ? " " + type : "");
}

// Render chips with local tasks
function renderLocalTasks() {
  if (tasks.length === 0) {
    localTasksEl.innerHTML = "<em>No local tasks yet. Add some above.</em>";
    return;
  }
  localTasksEl.innerHTML = tasks
    .map(
      (t) =>
        `<span class="local-task-pill"><span>${t.id}</span>·<span>${t.title}</span></span>`
    )
    .join("");
}

// Map score -> badge class + label
function getPriority(score) {
  if (score >= 70) return { label: "High", cls: "high" };
  if (score >= 40) return { label: "Medium", cls: "medium" };
  return { label: "Low", cls: "low" };
}

// Render backend results
function renderResults(list, title = "Analyzed Tasks") {
  if (!list || !list.length) {
    resultsEl.innerHTML = "<p>No results to show.</p>";
    return;
  }

  const html = `
    <h3>${title}</h3>
    ${list
      .map((t) => {
        const pri = getPriority(t.score ?? 0);
        return `
          <article class="task-card">
            <div class="task-header">
              <div class="task-title">${t.title}</div>
              <span class="badge ${pri.cls}">${pri.label} · ${t.score}</span>
            </div>
            <div class="task-meta">
              ID: ${t.id ?? "–"} · 
              Due: ${t.due_date || "—"} · 
              Effort: ${t.estimated_hours}h · 
              Importance: ${t.importance} · 
              Dependencies: ${
                t.dependencies && t.dependencies.length
                  ? t.dependencies.join(", ")
                  : "—"
              }
            </div>
            <div class="task-explanation">
              ${t.explanation || ""}
            </div>
          </article>
        `;
      })
      .join("")}
  `;

  resultsEl.innerHTML = html;
}

// Build payload from local or bulk JSON
function buildPayload() {
  let payload = [...tasks];

  const bulk = bulkInput.value.trim();
  if (bulk) {
    try {
      const parsed = JSON.parse(bulk);
      if (Array.isArray(parsed)) {
        payload = parsed;
      } else {
        alert("Bulk JSON must be an array of tasks.");
      }
    } catch (err) {
      alert("Bulk JSON is invalid: " + err.message);
      return null;
    }
  }

  if (!payload.length) {
    alert("Add at least one task or provide bulk JSON.");
    return null;
  }

  return payload;
}

// Compute query string for strategy (weights)
function strategyQuery(strategy) {
  // default: smart balance = use backend defaults
  if (strategy === "fast") {
    return "?effort=0.6&importance=0.1&urgency=0.2&dependencies=0.1";
  }
  if (strategy === "impact") {
    return "?importance=0.7&urgency=0.1&effort=0.1&dependencies=0.1";
  }
  if (strategy === "deadline") {
    return "?urgency=0.7&importance=0.2&effort=0.05&dependencies=0.05";
  }
  return ""; // smart
}

// Handle add-task form
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const fd = new FormData(form);
  const title = (fd.get("title") || "").trim();
  if (!title) {
    alert("Title is required.");
    return;
  }

  const id = "T" + nextId++;
  const due_date = fd.get("due_date") || null;
  const estimated_hours = parseFloat(fd.get("estimated_hours")) || 1;
  const importance = parseInt(fd.get("importance")) || 5;
  const depsRaw = (fd.get("dependencies") || "").trim();

  const dependencies = depsRaw
    ? depsRaw.split(",").map((s) => s.trim()).filter(Boolean)
    : [];

  tasks.push({
    id,
    title,
    due_date,
    estimated_hours,
    importance,
    dependencies,
  });

  form.reset();
  renderLocalTasks();
  setStatus(`Added task ${id}`, "success");
});

// Analyze button
analyzeBtn.addEventListener("click", () => {
  const payload = buildPayload();
  if (!payload) return;

  const strategy = strategySelect.value;
  const qs = strategyQuery(strategy);

  setStatus("Analyzing tasks...", "");
  fetch(`${API_BASE}/analyze/${qs}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then(async (res) => {
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }
      renderResults(data.tasks, "Scored Tasks");
      setStatus("Analysis complete ✅", "success");
    })
    .catch((err) => {
      console.error(err);
      setStatus("Error: " + err.message, "error");
    });
});

// Suggest button (top 3)
suggestBtn.addEventListener("click", () => {
  const payload = buildPayload();
  if (!payload) return;

  setStatus("Fetching suggestions...", "");
  const encoded = encodeURIComponent(JSON.stringify(payload));
  const strategy = strategySelect.value;
  const qsWeights = strategyQuery(strategy);
  const sep = qsWeights ? "&" : "?";
  const url = `${API_BASE}/suggest/?tasks=${encoded}${
    qsWeights ? sep + qsWeights.slice(1) : ""
  }`;

  fetch(url)
    .then(async (res) => {
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }
      renderResults(data.suggestions, "Top 3 Suggestions");
      setStatus("Suggestions ready 💡", "success");
    })
    .catch((err) => {
      console.error(err);
      setStatus("Error: " + err.message, "error");
    });
});

// Initial render
renderLocalTasks();
setStatus("Backend must be running at http://127.0.0.1:8000", "");
