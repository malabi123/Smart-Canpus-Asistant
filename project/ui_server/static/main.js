// ════════════════════════════════════════
//  Ask (main flow)
// ════════════════════════════════════════

function showStatus(msg) {
  document.getElementById("divider").style.display = "";
  const bar = document.getElementById("status-bar");
  bar.classList.add("visible");
  document.getElementById("status-text").textContent = msg;
  document.getElementById("answer-block").classList.remove("visible");
  document.getElementById("error-block").classList.remove("visible");
}

function showError(msg) {
  document.getElementById("divider").style.display = "";
  document.getElementById("status-bar").classList.remove("visible");
  const el = document.getElementById("error-block");
  el.textContent = "⚠ " + msg;
  el.classList.add("visible");
}

function showAnswer(data) {
  document.getElementById("status-bar").classList.remove("visible");
  const block = document.getElementById("answer-block");
  document.getElementById("tag-category").textContent = data.category || "general";
  document.getElementById("answer-title").textContent = data.title || "";
  document.getElementById("answer-body").textContent = data.answer || "";

  const saveBtn = document.getElementById("save-btn");
  if (data.save !== 0 && data.answer) {
    saveBtn.style.display = "";
    saveBtn.dataset.ready = "true";
  } else {
    saveBtn.style.display = "none";
    saveBtn.dataset.ready = "false";
  }

  block.classList.add("visible");
}

let _currentToken = null;
let _currentTaskId = null;

async function saveQuestion() {
  const saveBtn = document.getElementById("save-btn");
  if (!_currentToken || !_currentTaskId) return;

  saveBtn.disabled = true;
  saveBtn.textContent = "Saving…";

  try {
    const res = await fetch(`/ask/${_currentTaskId}/save`, {
      method: "POST",
      headers: { "user-token": _currentToken }
    });
    const data = await res.json();
    if (data.status === "saved successfully") {
      saveBtn.textContent = "✓ Saved";
      saveBtn.classList.add("saved");
      // Refresh the Ask Again list to include the newly saved question
      loadTitles();
    } else {
      saveBtn.textContent = "Save failed";
      saveBtn.disabled = false;
    }
  } catch {
    saveBtn.textContent = "Save failed";
    saveBtn.disabled = false;
  }
}

async function submitQuestion() {
  const question = document.getElementById("question-input").value.trim();
  if (!question) return;

  const btn = document.getElementById("ask-btn");
  btn.disabled = true;

  // Reset save button state
  const saveBtn = document.getElementById("save-btn");
  saveBtn.style.display = "none";
  saveBtn.disabled = false;
  saveBtn.textContent = "Save answer";
  saveBtn.classList.remove("saved");

  try {
    // 1. Get token
    showStatus("Fetching token…");
    const tokenRes = await fetch("/get_token");
    if (!tokenRes.ok) throw new Error("Failed to get token");
    const { user_token } = await tokenRes.json();
    _currentToken = user_token;

    // 2. Submit question
    showStatus("Submitting question…");
    const askRes = await fetch("/ask", {
      method: "POST",
      headers: { "user-token": user_token, "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    if (!askRes.ok) throw new Error("Failed to submit question");
    const { task_id } = await askRes.json();
    _currentTaskId = task_id;

    // 3. Poll for answer
    let status = "processing";
    let data = {};
    while (status === "processing") {
      showStatus("Processing… (this may take a moment)");
      await new Promise(r => setTimeout(r, 1000));
      const pollRes = await fetch(`/ask/${_currentTaskId}`, {
        headers: { "user-token": _currentToken }
      });
      if (!pollRes.ok) throw new Error("Polling failed");
      data = await pollRes.json();
      status = data.status;
    }

    showAnswer(data);
  } catch (err) {
    showError(err.message || "Something went wrong.");
  } finally {
    btn.disabled = false;
  }
}

// Ctrl+Enter / Cmd+Enter to submit
document.getElementById("question-input").addEventListener("keydown", e => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) submitQuestion();
});


// ════════════════════════════════════════
//  Ask Again section
// ════════════════════════════════════════

let _activeItemEl = null;

async function loadTitles() {
  const loadingEl = document.getElementById("again-loading");
  const emptyEl   = document.getElementById("again-empty");
  const errorEl   = document.getElementById("again-error");
  const listEl    = document.getElementById("titles-list");

  // Reset state
  loadingEl.style.display = "flex";
  emptyEl.style.display   = "none";
  errorEl.style.display   = "none";
  listEl.style.display    = "none";
  listEl.innerHTML        = "";
  closeAgainPanel();

  try {
    const res = await fetch("/ask/again/titles");
    if (!res.ok) throw new Error("Request failed");
    const titles = await res.json(); // { q_id: title, ... }

    loadingEl.style.display = "none";

    const entries = Object.entries(titles);
    if (entries.length === 0) {
      emptyEl.style.display = "block";
      return;
    }

    entries.forEach(([qId, title]) => {
      const li = document.createElement("li");
      li.className = "title-item";
      li.dataset.qid = qId;
      li.innerHTML = `
        <span class="title-text">${escapeHtml(title)}</span>
        <span class="title-arrow">→</span>
      `;
      li.addEventListener("click", () => openAgainAnswer(qId, li));
      listEl.appendChild(li);
    });

    listEl.style.display = "flex";
  } catch {
    loadingEl.style.display = "none";
    errorEl.style.display   = "block";
  }
}

async function openAgainAnswer(qId, itemEl) {
  // Highlight selected item
  if (_activeItemEl) _activeItemEl.classList.remove("active");
  _activeItemEl = itemEl;
  itemEl.classList.add("active");

  const panel       = document.getElementById("again-answer-panel");
  const loadingEl   = document.getElementById("again-answer-loading");
  const contentEl   = document.getElementById("again-answer-content");
  const errorEl     = document.getElementById("again-answer-error");

  // Show panel in loading state
  panel.style.display   = "block";
  loadingEl.style.display = "flex";
  contentEl.style.display = "none";
  errorEl.style.display   = "none";

  // Scroll panel into view smoothly
  panel.scrollIntoView({ behavior: "smooth", block: "nearest" });

  try {
    const res = await fetch(`/ask/again/questions/${qId}`);
    if (!res.ok) throw new Error("Request failed");
    const data = await res.json(); // { title, category, answer }

    document.getElementById("again-tag-category").textContent = data.category || "general";
    document.getElementById("again-answer-title").textContent  = data.title    || "";
    document.getElementById("again-answer-body").textContent   = data.answer   || "";

    loadingEl.style.display = "none";
    contentEl.style.display = "block";
  } catch {
    loadingEl.style.display = "none";
    errorEl.style.display   = "block";
  }
}

function closeAgainPanel() {
  document.getElementById("again-answer-panel").style.display = "none";
  if (_activeItemEl) {
    _activeItemEl.classList.remove("active");
    _activeItemEl = null;
  }
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// Load titles on page load
document.addEventListener("DOMContentLoaded", loadTitles);