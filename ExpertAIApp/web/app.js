/* global fetch */

const state = {
  questions: [],
  name: "",
  textResponses: {},
  isSubmitting: false,
  error: "",
  submitted: false,
  submissionCount: 0,
  maxSubmissions: 25,
};

const els = {
  formSection: document.getElementById("formSection"),
  successSection: document.getElementById("successSection"),
  questionsRoot: document.getElementById("questionsRoot"),
  nameInput: document.getElementById("nameInput"),
  nameError: document.getElementById("nameError"),
  btnSubmit: document.getElementById("btnSubmit"),
  btnReset: document.getElementById("btnReset"),
  btnTheme: document.getElementById("btnTheme"),
  errorBox: document.getElementById("errorBox"),
  subtitle: document.getElementById("subtitle"),
  submissionCount: document.getElementById("submissionCount"),
  successDetails: document.getElementById("successDetails"),
};

function getPreferredTheme() {
  const saved = localStorage.getItem("theme");
  if (saved === "light" || saved === "dark") return saved;
  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
    return "light";
  }
  return "dark";
}

function applyTheme(theme) {
  const t = theme === "light" ? "light" : "dark";
  document.documentElement.dataset.theme = t;
  if (els.btnTheme) {
    els.btnTheme.textContent = t === "light" ? "Night mode" : "Day mode";
  }
}

function toggleTheme() {
  const current = document.documentElement.dataset.theme === "light" ? "light" : "dark";
  const next = current === "light" ? "dark" : "light";
  localStorage.setItem("theme", next);
  applyTheme(next);
}

function emptyTextResponses(questions) {
  const out = {};
  for (const q of questions) out[q.id] = "";
  return out;
}

function setError(message) {
  state.error = message || "";
  if (!state.error) {
    els.errorBox.hidden = true;
    els.errorBox.textContent = "";
    return;
  }
  els.errorBox.hidden = false;
  els.errorBox.textContent = state.error;
}

function canSubmit() {
  if (!state.name.trim()) return false;
  return state.questions.every((q) => {
    const response = state.textResponses[q.id] || "";
    return response.trim().length > 0;
  });
}

function updateName(value) {
  state.name = value;
  els.nameError.hidden = value.trim().length > 0;
  updateButtonState();
}

function updateTextResponse(questionId, value) {
  state.textResponses[questionId] = value;
  updateButtonState();
}

function updateButtonState() {
  els.btnSubmit.disabled = !canSubmit() || state.isSubmitting;
  setButtonLoading(els.btnSubmit, state.isSubmitting);
}

function setButtonLoading(btn, isLoading) {
  const spinner = btn.querySelector(".spinner");
  if (spinner) {
    spinner.hidden = !isLoading;
  }
  if (isLoading) {
    btn.classList.add("loading");
  } else {
    btn.classList.remove("loading");
  }
}

function renderQuestion(q) {
  const response = state.textResponses[q.id] || "";
  const isEmpty = response.trim().length === 0;

  const root = document.createElement("section");
  root.className = "question";

  const title = document.createElement("p");
  title.className = "qTitle";
  title.textContent = q.text;
  root.appendChild(title);

  const textarea = document.createElement("textarea");
  textarea.className = "qTextarea";
  textarea.placeholder = "Ihre Antwort hier eingeben...";
  textarea.value = response;
  textarea.rows = 4;
  textarea.addEventListener("input", (e) => updateTextResponse(q.id, e.target.value));
  root.appendChild(textarea);

  if (isEmpty) {
    const helper = document.createElement("div");
    helper.className = "qHelper error";
    helper.textContent = "Bitte geben Sie eine Antwort ein.";
    root.appendChild(helper);
  }

  return root;
}

function updateSubmissionCountDisplay() {
  if (els.submissionCount) {
    const remaining = state.maxSubmissions - state.submissionCount;
    if (state.submissionCount >= state.maxSubmissions) {
      els.submissionCount.textContent = `Alle ${state.maxSubmissions} Plätze sind belegt.`;
      els.submissionCount.classList.add("error");
    } else {
      els.submissionCount.textContent = `${state.submissionCount}/${state.maxSubmissions} Antworten eingereicht (${remaining} Plätze frei)`;
      els.submissionCount.classList.remove("error");
    }
  }
}

function showSection(section) {
  els.formSection.hidden = section !== "form";
  els.successSection.hidden = section !== "success";
}

function render() {
  updateButtonState();
  updateSubmissionCountDisplay();

  // Only render questions if we're on the form section
  if (!els.formSection.hidden) {
    els.questionsRoot.innerHTML = "";
    for (const q of state.questions) {
      els.questionsRoot.appendChild(renderQuestion(q));
    }
  }
}

async function postJson(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const details =
      data && data.error && data.message ? `${data.error}: ${data.message}` : data.error || data.message;
    throw new Error(details || `Request failed (${res.status})`);
  }
  return data;
}

async function fetchSubmissionCount() {
  try {
    const res = await fetch("/api/submissions/count");
    const data = await res.json();
    state.submissionCount = data.count || 0;
    state.maxSubmissions = data.max || 25;
    updateSubmissionCountDisplay();
  } catch {
    // Ignore errors
  }
}

async function handleSubmit() {
  setError("");
  state.isSubmitting = true;
  render();
  
  try {
    const data = await postJson("/api/submit", {
      name: state.name.trim(),
      textResponses: state.textResponses,
    });
    
    state.submitted = true;
    state.submissionCount = data.submission_count || state.submissionCount + 1;
    
    // Show success message
    if (els.successDetails) {
      els.successDetails.textContent = `Eingereicht als: ${state.name.trim()}`;
    }
    
    showSection("success");
  } catch (e) {
    setError(e instanceof Error ? e.message : "Fehler beim Speichern der Antworten");
  } finally {
    state.isSubmitting = false;
    render();
  }
}

function handleReset() {
  setError("");
  state.name = "";
  state.textResponses = emptyTextResponses(state.questions);
  state.isSubmitting = false;
  
  if (els.nameInput) {
    els.nameInput.value = "";
  }
  els.nameError.hidden = true;
  
  render();
}

async function init() {
  setError("");
  applyTheme(getPreferredTheme());
  
  try {
    // Fetch questions and submission count in parallel
    const [questionsRes] = await Promise.all([
      fetch("/api/questions"),
      fetchSubmissionCount(),
    ]);
    
    const questionsData = await questionsRes.json();
    state.questions = questionsData.questions || [];
    state.textResponses = emptyTextResponses(state.questions);
  } catch {
    setError("Fehler beim Laden der Fragen vom Server.");
  }

  // Setup event listeners
  els.btnSubmit.addEventListener("click", handleSubmit);
  els.btnReset.addEventListener("click", handleReset);
  if (els.btnTheme) els.btnTheme.addEventListener("click", toggleTheme);
  if (els.nameInput) {
    els.nameInput.addEventListener("input", (e) => updateName(e.target.value));
  }

  showSection("form");
  render();
}

init();
