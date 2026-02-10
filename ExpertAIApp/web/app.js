/* global fetch */

// Translations
const translations = {
  de: {
    subtitle: 'Experten: Geben Sie Ihren Namen und Ihre Antworten ein und klicken Sie auf "Absenden".',
    formTitle: "Experten-Eingaben",
    formDesc: "Bitte geben Sie Ihren Namen ein und beantworten Sie die folgenden Fragen.",
    nameLabel: "Ihr Name",
    namePlaceholder: "Vor- und Nachname eingeben...",
    nameError: "Bitte geben Sie Ihren Namen ein.",
    answerPlaceholder: "Ihre Antwort hier eingeben...",
    answerError: "Bitte geben Sie eine Antwort ein.",
    submit: "Absenden",
    reset: "Zurücksetzen",
    successTitle: "Vielen Dank!",
    successMessage: "Ihre Antworten wurden erfolgreich gespeichert.",
    submittedAs: "Eingereicht als:",
    submissionCount: "{count} Antworten eingereicht",
    loadError: "Fehler beim Laden der Fragen vom Server.",
    saveError: "Fehler beim Speichern der Antworten",
    langButton: "EN",
    dayMode: "Tagmodus",
    nightMode: "Nachtmodus",
  },
  en: {
    subtitle: 'Experts: Enter your name and answers, then click "Submit".',
    formTitle: "Expert Input",
    formDesc: "Please enter your name and answer the following questions.",
    nameLabel: "Your Name",
    namePlaceholder: "Enter first and last name...",
    nameError: "Please enter your name.",
    answerPlaceholder: "Enter your answer here...",
    answerError: "Please enter an answer.",
    submit: "Submit",
    reset: "Reset",
    successTitle: "Thank you!",
    successMessage: "Your answers have been saved successfully.",
    submittedAs: "Submitted as:",
    submissionCount: "{count} answers submitted",
    loadError: "Error loading questions from server.",
    saveError: "Error saving answers",
    langButton: "DE",
    dayMode: "Day mode",
    nightMode: "Night mode",
  },
};

const state = {
  questions: [],
  name: "",
  textResponses: {},
  isSubmitting: false,
  error: "",
  submitted: false,
  submissionCount: 0,
  lang: "de",
};

const els = {
  formSection: document.getElementById("formSection"),
  successSection: document.getElementById("successSection"),
  questionsRoot: document.getElementById("questionsRoot"),
  nameInput: document.getElementById("nameInput"),
  nameError: document.getElementById("nameError"),
  nameLabel: document.getElementById("nameLabel"),
  btnSubmit: document.getElementById("btnSubmit"),
  btnSubmitText: document.getElementById("btnSubmitText"),
  btnReset: document.getElementById("btnReset"),
  btnTheme: document.getElementById("btnTheme"),
  btnLang: document.getElementById("btnLang"),
  errorBox: document.getElementById("errorBox"),
  subtitle: document.getElementById("subtitle"),
  submissionCount: document.getElementById("submissionCount"),
  successDetails: document.getElementById("successDetails"),
  formTitle: document.getElementById("formTitle"),
  formDesc: document.getElementById("formDesc"),
  successTitle: document.getElementById("successTitle"),
  successMessage: document.getElementById("successMessage"),
};

function t(key) {
  return translations[state.lang][key] || translations.de[key] || key;
}

function getPreferredLang() {
  const saved = localStorage.getItem("lang");
  if (saved === "de" || saved === "en") return saved;
  // German default unless user explicitly chose otherwise.
  return "de";
}

function applyLang(lang) {
  state.lang = lang === "en" ? "en" : "de";
  document.documentElement.lang = state.lang;
  
  // Update all static text elements
  if (els.subtitle) els.subtitle.textContent = t("subtitle");
  if (els.formTitle) els.formTitle.textContent = t("formTitle");
  if (els.formDesc) els.formDesc.textContent = t("formDesc");
  if (els.nameLabel) els.nameLabel.textContent = t("nameLabel");
  if (els.nameInput) els.nameInput.placeholder = t("namePlaceholder");
  if (els.nameError) els.nameError.textContent = t("nameError");
  if (els.btnSubmitText) els.btnSubmitText.textContent = t("submit");
  if (els.btnReset) els.btnReset.textContent = t("reset");
  if (els.successTitle) els.successTitle.textContent = t("successTitle");
  if (els.successMessage) els.successMessage.textContent = t("successMessage");
  if (els.btnLang) els.btnLang.textContent = t("langButton");
  
  // Update theme button text
  const currentTheme = document.documentElement.dataset.theme;
  if (els.btnTheme) {
    els.btnTheme.textContent = currentTheme === "light" ? t("nightMode") : t("dayMode");
  }
  
  // Re-render dynamic content
  updateSubmissionCountDisplay();
  if (!els.formSection.hidden) {
    render();
  }
}

function toggleLang() {
  const next = state.lang === "de" ? "en" : "de";
  localStorage.setItem("lang", next);
  applyLang(next);
}

function getPreferredTheme() {
  const saved = localStorage.getItem("theme");
  if (saved === "light" || saved === "dark") return saved;
  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
    return "light";
  }
  return "dark";
}

function applyTheme(theme) {
  const themeVal = theme === "light" ? "light" : "dark";
  document.documentElement.dataset.theme = themeVal;
  if (els.btnTheme) {
    els.btnTheme.textContent = themeVal === "light" ? t("nightMode") : t("dayMode");
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
  textarea.placeholder = t("answerPlaceholder");
  textarea.value = response;
  textarea.rows = 4;
  textarea.addEventListener("input", (e) => updateTextResponse(q.id, e.target.value));
  root.appendChild(textarea);

  if (isEmpty) {
    const helper = document.createElement("div");
    helper.className = "qHelper error";
    helper.textContent = t("answerError");
    root.appendChild(helper);
  }

  return root;
}

function updateSubmissionCountDisplay() {
  if (els.submissionCount) {
    if (state.submissionCount > 0) {
      els.submissionCount.textContent = t("submissionCount").replace("{count}", state.submissionCount);
    } else {
      els.submissionCount.textContent = "";
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

  // Update name error visibility
  const nameIsEmpty = !state.name.trim();
  els.nameError.hidden = !nameIsEmpty;

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
      els.successDetails.textContent = `${t("submittedAs")} ${state.name.trim()}`;
    }
    
    showSection("success");
  } catch (e) {
    setError(e instanceof Error ? e.message : t("saveError"));
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
  
  render();
}

async function init() {
  setError("");
  applyTheme(getPreferredTheme());
  applyLang(getPreferredLang());
  
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
    setError(t("loadError"));
  }

  // Setup event listeners
  els.btnSubmit.addEventListener("click", handleSubmit);
  els.btnReset.addEventListener("click", handleReset);
  if (els.btnTheme) els.btnTheme.addEventListener("click", toggleTheme);
  if (els.btnLang) els.btnLang.addEventListener("click", toggleLang);
  if (els.nameInput) {
    els.nameInput.addEventListener("input", (e) => updateName(e.target.value));
  }

  showSection("form");
  render();
}

init();
