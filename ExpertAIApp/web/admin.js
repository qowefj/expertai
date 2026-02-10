/* global fetch */

// Translations
const translations = {
  de: {
    subtitle: "Moderator-Ansicht: Hier können Sie alle Experten-Einreichungen einsehen und zusammenfassen.",
    authErrorTitle: "Zugriff verweigert",
    authErrorText: "Sie benötigen einen gültigen Admin-Schlüssel, um diese Seite aufzurufen.",
    authErrorHint: "Beispiel: /admin.html?key=IhrSchlüssel",
    statsLabelSubmissions: "Einreichungen",
    refresh: "Aktualisieren",
    clearAll: "Alle löschen",
    clearConfirm: "Sind Sie sicher, dass Sie alle Einreichungen löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.",
    summaryTitle: "KI-Zusammenfassung",
    summaryDesc: "Fassen Sie alle Experten-Antworten mit KI zusammen.",
    summarize: "Expertenantworten zusammenfassen",
    expertSummaryTitle: "Experten-Zusammenfassung",
    expertSummaryDesc: "Zusammenfassung aller Expertenantworten (max. 2000 Zeichen).",
    expertSummaryEmpty: "Keine Experten-Zusammenfassung vorhanden.",
    aiInsightTitle: "KI-Einsicht",
    aiInsightDesc: "KI-Antwort nur auf Basis der Fragen, ohne Expertenkontext (max. 2000 Zeichen).",
    aiInsightEmpty: "Keine KI-Einsicht vorhanden.",
    comparisonInsightTitle: "Finale Einsicht (Vergleich)",
    comparisonInsightDesc: "Vergleicht Experten- und KI-Einsichten und hebt die wichtigsten Unterschiede hervor.",
    comparisonInsightEmpty: 'Kein Vergleich vorhanden. Klicken Sie auf "Vergleichen".',
    compare: "Vergleichen",
    finalInsightTitle: "Finale Einsicht (Zusammenführung)",
    finalInsightDesc: "Kombiniert Experten- und KI-Einsichten zu einer diskussionsbereiten Zusammenfassung (max. 2000 Zeichen).",
    finalInsightEmpty: 'Keine finale Einsicht vorhanden. Klicken Sie auf "KI und Experten zusammenführen".',
    merge: "KI und Experten zusammenführen",
    individualAnswersTitle: "Einzelne Experten-Antworten",
    submissionsEmpty: "Noch keine Einreichungen vorhanden.",
    submissionsCount: "{count} Einreichungen im Original.",
    noAnswer: "(keine Antwort)",
    loadQuestionsError: "Fehler beim Laden der Fragen.",
    summarizeError: "Fehler beim Generieren der Zusammenfassung",
    mergeError: "Fehler beim Zusammenführen der Einsichten",
    compareError: "Fehler beim Vergleichen der Einsichten",
    clearError: "Fehler beim Löschen der Einreichungen",
    langButton: "EN",
    dayMode: "Day mode",
    nightMode: "Night mode",
    questionsConfigTitle: "Fragen-Konfiguration",
    questionsConfigDesc: "Bearbeiten Sie die Fragen, die den Experten gestellt werden.",
    saveQuestions: "Speichern",
    resetQuestions: "Zurücksetzen",
    addQuestion: "+ Frage hinzufügen",
    questionPlaceholder: "Geben Sie hier die Frage ein...",
    deleteQuestion: "Löschen",
    saveQuestionsSuccess: "Fragen erfolgreich gespeichert.",
    saveQuestionsError: "Fehler beim Speichern der Fragen.",
    resetQuestionsSuccess: "Fragen auf Standardwerte zurückgesetzt.",
    resetQuestionsError: "Fehler beim Zurücksetzen der Fragen.",
    resetQuestionsConfirm: "Sind Sie sicher, dass Sie die Fragen auf die Standardwerte zurücksetzen möchten?",
  },
  en: {
    subtitle: "Moderator view: View all expert submissions and generate summaries.",
    authErrorTitle: "Access Denied",
    authErrorText: "You need a valid admin key to access this page.",
    authErrorHint: "Example: /admin.html?key=YourKey",
    statsLabelSubmissions: "Submissions",
    refresh: "Refresh",
    clearAll: "Clear all",
    clearConfirm: "Are you sure you want to delete all submissions? This action cannot be undone.",
    summaryTitle: "AI Summary",
    summaryDesc: "Summarize all expert answers with AI.",
    summarize: "Summarize expert answers",
    expertSummaryTitle: "Expert Summary",
    expertSummaryDesc: "Summary of all expert answers (max. 2000 characters).",
    expertSummaryEmpty: "No expert summary available.",
    aiInsightTitle: "AI Insight",
    aiInsightDesc: "AI response based on questions only, without expert context (max. 2000 characters).",
    aiInsightEmpty: "No AI insight available.",
    comparisonInsightTitle: "Final Insight (Comparison)",
    comparisonInsightDesc: "Compares expert and AI insights and highlights the main differences.",
    comparisonInsightEmpty: 'No comparison available. Click "Compare".',
    compare: "Compare",
    finalInsightTitle: "Final Insight (Merged)",
    finalInsightDesc: "Combines expert and AI insights into a discussion-ready summary (max. 2000 characters).",
    finalInsightEmpty: 'No final insight available. Click "Merge AI and Experts".',
    merge: "Merge AI and Experts",
    individualAnswersTitle: "Individual Expert Answers",
    submissionsEmpty: "No submissions yet.",
    submissionsCount: "{count} submissions in original form.",
    noAnswer: "(no answer)",
    loadQuestionsError: "Error loading questions.",
    summarizeError: "Error generating summary",
    mergeError: "Error merging insights",
    compareError: "Error comparing insights",
    clearError: "Error deleting submissions",
    langButton: "DE",
    dayMode: "Day mode",
    nightMode: "Night mode",
    questionsConfigTitle: "Questions Configuration",
    questionsConfigDesc: "Edit the questions that will be asked to the experts.",
    saveQuestions: "Save",
    resetQuestions: "Reset",
    addQuestion: "+ Add Question",
    questionPlaceholder: "Enter the question here...",
    deleteQuestion: "Delete",
    saveQuestionsSuccess: "Questions saved successfully.",
    saveQuestionsError: "Error saving questions.",
    resetQuestionsSuccess: "Questions reset to defaults.",
    resetQuestionsError: "Error resetting questions.",
    resetQuestionsConfirm: "Are you sure you want to reset questions to default values?",
  },
};

const state = {
  adminKey: "",
  questions: [],
  editableQuestions: [],
  submissions: [],
  expertInsight: "",
  aiInsight: "",
  comparisonInsight: "",
  finalInsight: "",
  isLoading: false,
  isSummarizing: false,
  isComparing: false,
  isMerging: false,
  isSavingQuestions: false,
  error: "",
  questionsError: "",
  lang: "de",
};

const els = {
  authError: document.getElementById("authError"),
  authErrorTitle: document.getElementById("authErrorTitle"),
  authErrorText: document.getElementById("authErrorText"),
  authErrorHint: document.getElementById("authErrorHint"),
  adminSection: document.getElementById("adminSection"),
  resultsSection: document.getElementById("resultsSection"),
  submissionCount: document.getElementById("submissionCount"),
  statsLabelSubmissions: document.getElementById("statsLabelSubmissions"),
  submissionsRoot: document.getElementById("submissionsRoot"),
  submissionsSubtitle: document.getElementById("submissionsSubtitle"),
  btnSummarize: document.getElementById("btnSummarize"),
  btnSummarizeText: document.getElementById("btnSummarizeText"),
  btnCompare: document.getElementById("btnCompare"),
  btnCompareText: document.getElementById("btnCompareText"),
  btnMerge: document.getElementById("btnMerge"),
  btnMergeText: document.getElementById("btnMergeText"),
  btnRefresh: document.getElementById("btnRefresh"),
  btnClear: document.getElementById("btnClear"),
  btnTheme: document.getElementById("btnTheme"),
  btnLang: document.getElementById("btnLang"),
  subtitle: document.getElementById("subtitle"),
  summaryTitle: document.getElementById("summaryTitle"),
  summaryDesc: document.getElementById("summaryDesc"),
  expertSummaryTitle: document.getElementById("expertSummaryTitle"),
  expertSummaryDesc: document.getElementById("expertSummaryDesc"),
  expertInsight: document.getElementById("expertInsight"),
  aiInsightTitle: document.getElementById("aiInsightTitle"),
  aiInsightDesc: document.getElementById("aiInsightDesc"),
  aiInsight: document.getElementById("aiInsight"),
  comparisonInsightTitle: document.getElementById("comparisonInsightTitle"),
  comparisonInsightDesc: document.getElementById("comparisonInsightDesc"),
  comparisonInsight: document.getElementById("comparisonInsight"),
  finalInsightTitle: document.getElementById("finalInsightTitle"),
  finalInsightDesc: document.getElementById("finalInsightDesc"),
  finalInsight: document.getElementById("finalInsight"),
  individualAnswersTitle: document.getElementById("individualAnswersTitle"),
  errorBox: document.getElementById("errorBox"),
  // Questions editor elements
  questionsConfigTitle: document.getElementById("questionsConfigTitle"),
  questionsConfigDesc: document.getElementById("questionsConfigDesc"),
  questionsEditor: document.getElementById("questionsEditor"),
  questionsErrorBox: document.getElementById("questionsErrorBox"),
  btnSaveQuestions: document.getElementById("btnSaveQuestions"),
  btnSaveQuestionsText: document.getElementById("btnSaveQuestionsText"),
  btnResetQuestions: document.getElementById("btnResetQuestions"),
  btnResetQuestionsText: document.getElementById("btnResetQuestionsText"),
  btnAddQuestion: document.getElementById("btnAddQuestion"),
  btnAddQuestionText: document.getElementById("btnAddQuestionText"),
};

function t(key) {
  return translations[state.lang][key] || translations.de[key] || key;
}

function getPreferredLang() {
  const saved = localStorage.getItem("lang");
  if (saved === "de" || saved === "en") return saved;
  const browserLang = navigator.language || navigator.userLanguage;
  if (browserLang && browserLang.startsWith("en")) return "en";
  return "de";
}

function applyLang(lang) {
  state.lang = lang === "en" ? "en" : "de";
  document.documentElement.lang = state.lang;
  
  // Update all static text elements
  if (els.subtitle) els.subtitle.textContent = t("subtitle");
  if (els.authErrorTitle) els.authErrorTitle.textContent = t("authErrorTitle");
  if (els.authErrorText) els.authErrorText.textContent = t("authErrorText");
  if (els.authErrorHint) els.authErrorHint.textContent = t("authErrorHint");
  if (els.statsLabelSubmissions) els.statsLabelSubmissions.textContent = t("statsLabelSubmissions");
  if (els.btnRefresh) els.btnRefresh.textContent = t("refresh");
  if (els.btnClear) els.btnClear.textContent = t("clearAll");
  if (els.summaryTitle) els.summaryTitle.textContent = t("summaryTitle");
  if (els.summaryDesc) els.summaryDesc.textContent = t("summaryDesc");
  if (els.btnSummarizeText) els.btnSummarizeText.textContent = t("summarize");
  if (els.expertSummaryTitle) els.expertSummaryTitle.textContent = t("expertSummaryTitle");
  if (els.expertSummaryDesc) els.expertSummaryDesc.textContent = t("expertSummaryDesc");
  if (els.aiInsightTitle) els.aiInsightTitle.textContent = t("aiInsightTitle");
  if (els.aiInsightDesc) els.aiInsightDesc.textContent = t("aiInsightDesc");
  if (els.comparisonInsightTitle) els.comparisonInsightTitle.textContent = t("comparisonInsightTitle");
  if (els.comparisonInsightDesc) els.comparisonInsightDesc.textContent = t("comparisonInsightDesc");
  if (els.btnCompareText) els.btnCompareText.textContent = t("compare");
  if (els.finalInsightTitle) els.finalInsightTitle.textContent = t("finalInsightTitle");
  if (els.finalInsightDesc) els.finalInsightDesc.textContent = t("finalInsightDesc");
  if (els.btnMergeText) els.btnMergeText.textContent = t("merge");
  if (els.individualAnswersTitle) els.individualAnswersTitle.textContent = t("individualAnswersTitle");
  if (els.btnLang) els.btnLang.textContent = t("langButton");
  
  // Questions configuration
  if (els.questionsConfigTitle) els.questionsConfigTitle.textContent = t("questionsConfigTitle");
  if (els.questionsConfigDesc) els.questionsConfigDesc.textContent = t("questionsConfigDesc");
  if (els.btnSaveQuestionsText) els.btnSaveQuestionsText.textContent = t("saveQuestions");
  if (els.btnResetQuestionsText) els.btnResetQuestionsText.textContent = t("resetQuestions");
  if (els.btnAddQuestionText) els.btnAddQuestionText.textContent = t("addQuestion");
  
  // Update theme button text
  const currentTheme = document.documentElement.dataset.theme;
  if (els.btnTheme) {
    els.btnTheme.textContent = currentTheme === "light" ? t("nightMode") : t("dayMode");
  }
  
  // Re-render dynamic content
  render();
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

function getAdminKey() {
  const params = new URLSearchParams(window.location.search);
  return params.get("key") || "";
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

function setInsight(el, text, emptyKey) {
  if (text) {
    el.classList.remove("muted");
    el.textContent = text;
  } else {
    el.classList.add("muted");
    el.textContent = t(emptyKey);
  }
}

function canSummarize() {
  return state.submissions.length > 0 && !state.isSummarizing;
}

function canCompare() {
  return Boolean(state.expertInsight && state.aiInsight) && !state.isComparing;
}

function canMerge() {
  return Boolean(state.expertInsight && state.aiInsight) && !state.isMerging;
}

function updateButtonState() {
  els.btnSummarize.disabled = !canSummarize();
  els.btnCompare.disabled = !canCompare();
  els.btnMerge.disabled = !canMerge();
  els.btnSaveQuestions.disabled = state.isSavingQuestions;
  setButtonLoading(els.btnSummarize, state.isSummarizing);
  setButtonLoading(els.btnCompare, state.isComparing);
  setButtonLoading(els.btnMerge, state.isMerging);
  setButtonLoading(els.btnSaveQuestions, state.isSavingQuestions);
}

function formatDate(isoString) {
  try {
    const date = new Date(isoString);
    const locale = state.lang === "en" ? "en-US" : "de-DE";
    return date.toLocaleString(locale, {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoString;
  }
}

function renderSubmission(submission, index) {
  const root = document.createElement("div");
  root.className = "submissionItem";

  // Header with name and timestamp
  const header = document.createElement("div");
  header.className = "submissionHeader";
  
  const nameSpan = document.createElement("span");
  nameSpan.className = "submissionName";
  nameSpan.textContent = `${index + 1}. ${submission.name}`;
  header.appendChild(nameSpan);

  const timeSpan = document.createElement("span");
  timeSpan.className = "submissionTime muted";
  timeSpan.textContent = formatDate(submission.timestamp);
  header.appendChild(timeSpan);

  root.appendChild(header);

  // Responses
  const responses = document.createElement("div");
  responses.className = "submissionResponses";

  for (const q of state.questions) {
    const response = submission.responses[q.id] || t("noAnswer");
    
    const qBlock = document.createElement("div");
    qBlock.className = "submissionQuestion";
    
    const qTitle = document.createElement("p");
    qTitle.className = "submissionQTitle";
    qTitle.textContent = q.text;
    qBlock.appendChild(qTitle);

    const qAnswer = document.createElement("p");
    qAnswer.className = "submissionQAnswer";
    qAnswer.textContent = response;
    qBlock.appendChild(qAnswer);

    responses.appendChild(qBlock);
  }

  root.appendChild(responses);
  return root;
}

function renderSubmissions() {
  els.submissionsRoot.innerHTML = "";
  
  if (state.submissions.length === 0) {
    const empty = document.createElement("p");
    empty.className = "muted";
    empty.textContent = t("submissionsEmpty");
    els.submissionsRoot.appendChild(empty);
    return;
  }

  for (let i = 0; i < state.submissions.length; i++) {
    els.submissionsRoot.appendChild(renderSubmission(state.submissions[i], i));
  }
}

function setQuestionsError(message) {
  state.questionsError = message || "";
  if (!state.questionsError) {
    els.questionsErrorBox.hidden = true;
    els.questionsErrorBox.textContent = "";
    return;
  }
  els.questionsErrorBox.hidden = false;
  els.questionsErrorBox.textContent = state.questionsError;
}

function renderQuestionsEditor() {
  els.questionsEditor.innerHTML = "";
  
  for (let i = 0; i < state.editableQuestions.length; i++) {
    const q = state.editableQuestions[i];
    
    const item = document.createElement("div");
    item.className = "questionEditItem";
    
    const label = document.createElement("span");
    label.className = "questionNumber";
    label.textContent = `${i + 1}.`;
    item.appendChild(label);
    
    const textarea = document.createElement("textarea");
    textarea.className = "questionTextarea";
    textarea.value = q.text || "";
    textarea.placeholder = t("questionPlaceholder");
    textarea.rows = 2;
    textarea.dataset.index = i;
    textarea.addEventListener("input", (e) => {
      const idx = parseInt(e.target.dataset.index, 10);
      state.editableQuestions[idx].text = e.target.value;
    });
    item.appendChild(textarea);
    
    const deleteBtn = document.createElement("button");
    deleteBtn.className = "btn btnOutline btnSmall btnDanger";
    deleteBtn.textContent = t("deleteQuestion");
    deleteBtn.dataset.index = i;
    deleteBtn.addEventListener("click", (e) => {
      const idx = parseInt(e.target.dataset.index, 10);
      state.editableQuestions.splice(idx, 1);
      renderQuestionsEditor();
    });
    item.appendChild(deleteBtn);
    
    els.questionsEditor.appendChild(item);
  }
}

function render() {
  // Update counts
  els.submissionCount.textContent = state.submissions.length;
  
  // Update subtitle
  if (state.submissions.length === 0) {
    els.submissionsSubtitle.textContent = t("submissionsEmpty");
  } else {
    els.submissionsSubtitle.textContent = t("submissionsCount").replace("{count}", state.submissions.length);
  }

  // Update button states
  updateButtonState();

  // Render submissions list
  renderSubmissions();

  // Update insights display
  setInsight(els.expertInsight, state.expertInsight, "expertSummaryEmpty");
  setInsight(els.aiInsight, state.aiInsight, "aiInsightEmpty");
  setInsight(els.comparisonInsight, state.comparisonInsight, "comparisonInsightEmpty");
  setInsight(els.finalInsight, state.finalInsight, "finalInsightEmpty");
}

// Default fetch timeout (3 minutes); LLM endpoints get a longer timeout via options
const DEFAULT_FETCH_TIMEOUT_MS = 180_000;

function _parseError(res, data) {
  const details =
    data && data.error && data.message ? `${data.error}: ${data.message}` : data.error || data.message;
  return details || `Request failed (${res.status})`;
}

async function fetchJson(url, { timeoutMs } = {}) {
  const controller = new AbortController();
  const timeout = timeoutMs || DEFAULT_FETCH_TIMEOUT_MS;
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(url, { signal: controller.signal });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(_parseError(res, data));
    return data;
  } catch (e) {
    if (e.name === "AbortError") {
      throw new Error(`Request timed out after ${Math.round(timeout / 1000)}s. The server may still be processing — please wait and try again.`);
    }
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

async function postJson(url, body, { timeoutMs } = {}) {
  const controller = new AbortController();
  const timeout = timeoutMs || DEFAULT_FETCH_TIMEOUT_MS;
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(_parseError(res, data));
    return data;
  } catch (e) {
    if (e.name === "AbortError") {
      throw new Error(`Request timed out after ${Math.round(timeout / 1000)}s. The server may still be processing — please wait and try again.`);
    }
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

async function loadSubmissions() {
  try {
    const data = await fetchJson(`/api/admin/submissions?key=${encodeURIComponent(state.adminKey)}`);
    state.submissions = data.submissions || [];
    render();
  } catch (e) {
    if (e.message.includes("Unauthorized")) {
      showAuthError();
    } else {
      setError(e.message);
    }
  }
}

async function loadQuestions() {
  try {
    const data = await fetchJson("/api/questions");
    state.questions = data.questions || [];
  } catch (e) {
    setError(t("loadQuestionsError"));
  }
}

async function loadAdminQuestions() {
  try {
    const data = await fetchJson(`/api/admin/questions?key=${encodeURIComponent(state.adminKey)}`);
    state.editableQuestions = (data.questions || []).map(q => ({ ...q }));
    renderQuestionsEditor();
  } catch (e) {
    if (e.message.includes("Unauthorized")) {
      showAuthError();
    } else {
      setQuestionsError(t("loadQuestionsError"));
    }
  }
}

async function handleSaveQuestions() {
  setQuestionsError("");
  state.isSavingQuestions = true;
  updateButtonState();
  
  try {
    const questions = state.editableQuestions.map((q, i) => ({
      id: q.id || `q${i + 1}`,
      type: q.type || "text",
      text: (q.text || "").trim(),
    })).filter(q => q.text);
    
    const data = await postJson(`/api/admin/questions?key=${encodeURIComponent(state.adminKey)}`, {
      questions: questions,
    });
    
    // Reload questions to sync state
    await loadQuestions();
    await loadAdminQuestions();
    setQuestionsError("");
  } catch (e) {
    setQuestionsError(e instanceof Error ? e.message : t("saveQuestionsError"));
  } finally {
    state.isSavingQuestions = false;
    updateButtonState();
  }
}

async function handleResetQuestions() {
  if (!confirm(t("resetQuestionsConfirm"))) {
    return;
  }
  
  setQuestionsError("");
  state.isSavingQuestions = true;
  updateButtonState();
  
  try {
    await postJson(`/api/admin/questions/reset?key=${encodeURIComponent(state.adminKey)}`, {});
    
    // Reload questions to sync state
    await loadQuestions();
    await loadAdminQuestions();
    setQuestionsError("");
  } catch (e) {
    setQuestionsError(e instanceof Error ? e.message : t("resetQuestionsError"));
  } finally {
    state.isSavingQuestions = false;
    updateButtonState();
  }
}

function handleAddQuestion() {
  const newId = `q${state.editableQuestions.length + 1}_${Date.now()}`;
  state.editableQuestions.push({
    id: newId,
    type: "text",
    text: "",
  });
  renderQuestionsEditor();
}

async function handleSummarize() {
  setError("");
  state.isSummarizing = true;
  state.comparisonInsight = "";
  state.finalInsight = "";
  updateButtonState();
  
  try {
    const data = await postJson(`/api/admin/summarize?key=${encodeURIComponent(state.adminKey)}`, {}, { timeoutMs: 180_000 });
    state.expertInsight = data.expertInsight || "";
    state.aiInsight = data.aiInsight || "";
    els.resultsSection.hidden = false;
  } catch (e) {
    setError(e instanceof Error ? e.message : t("summarizeError"));
  } finally {
    state.isSummarizing = false;
    render();
  }
}

async function handleCompare() {
  setError("");
  state.isComparing = true;
  updateButtonState();
  
  try {
    const data = await postJson(`/api/admin/compare?key=${encodeURIComponent(state.adminKey)}`, {
      expertInsight: state.expertInsight,
      aiInsight: state.aiInsight,
    }, { timeoutMs: 180_000 });
    state.comparisonInsight = data.comparisonInsight || "";
  } catch (e) {
    setError(e instanceof Error ? e.message : t("compareError"));
  } finally {
    state.isComparing = false;
    render();
  }
}

async function handleMerge() {
  setError("");
  state.isMerging = true;
  updateButtonState();
  
  try {
    const data = await postJson(`/api/admin/merge?key=${encodeURIComponent(state.adminKey)}`, {
      expertInsight: state.expertInsight,
      aiInsight: state.aiInsight,
    }, { timeoutMs: 180_000 });
    state.finalInsight = data.finalInsight || "";
  } catch (e) {
    setError(e instanceof Error ? e.message : t("mergeError"));
  } finally {
    state.isMerging = false;
    render();
  }
}

async function handleRefresh() {
  setError("");
  await loadSubmissions();
}

async function handleClear() {
  if (!confirm(t("clearConfirm"))) {
    return;
  }
  
  setError("");
  try {
    await fetchJson(`/api/admin/clear?key=${encodeURIComponent(state.adminKey)}`);
    state.submissions = [];
    state.expertInsight = "";
    state.aiInsight = "";
    state.comparisonInsight = "";
    state.finalInsight = "";
    els.resultsSection.hidden = true;
    render();
  } catch (e) {
    setError(e instanceof Error ? e.message : t("clearError"));
  }
}

function showAuthError() {
  els.authError.hidden = false;
  els.adminSection.hidden = true;
}

function showAdminSection() {
  els.authError.hidden = true;
  els.adminSection.hidden = false;
}

async function init() {
  applyTheme(getPreferredTheme());
  applyLang(getPreferredLang());
  
  // Get admin key from URL
  state.adminKey = getAdminKey();
  
  if (!state.adminKey) {
    showAuthError();
    return;
  }

  // Load data
  await loadQuestions();
  await loadAdminQuestions();
  await loadSubmissions();
  
  // If auth was successful, show admin section
  if (els.authError.hidden) {
    showAdminSection();
  }

  // Setup event listeners
  els.btnSummarize.addEventListener("click", handleSummarize);
  els.btnCompare.addEventListener("click", handleCompare);
  els.btnMerge.addEventListener("click", handleMerge);
  els.btnRefresh.addEventListener("click", handleRefresh);
  els.btnClear.addEventListener("click", handleClear);
  if (els.btnTheme) els.btnTheme.addEventListener("click", toggleTheme);
  if (els.btnLang) els.btnLang.addEventListener("click", toggleLang);
  
  // Questions editor listeners
  if (els.btnSaveQuestions) els.btnSaveQuestions.addEventListener("click", handleSaveQuestions);
  if (els.btnResetQuestions) els.btnResetQuestions.addEventListener("click", handleResetQuestions);
  if (els.btnAddQuestion) els.btnAddQuestion.addEventListener("click", handleAddQuestion);

  render();
}

init();
