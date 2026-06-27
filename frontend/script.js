const API_BASE = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
  ? "http://127.0.0.1:5050"
  : window.location.origin;

const form = document.querySelector("#analyzeForm");
const fileInput = document.querySelector("#resumeFile");
const fileLabel = document.querySelector("#fileLabel");
const statusText = document.querySelector("#statusText");
const scoreValue = document.querySelector("#scoreValue");
const scoreOrb = document.querySelector("#scoreOrb");
const metricsGrid = document.querySelector("#metricsGrid");
const skillGroups = document.querySelector("#skillGroups");
const recommendations = document.querySelector("#recommendations");
const roleLabel = document.querySelector("#roleLabel");
const levelLabel = document.querySelector("#levelLabel");
const wordCount = document.querySelector("#wordCount");
const signalsGrid = document.querySelector("#signalsGrid");
const improveButton = document.querySelector("#improveButton");
const voiceButton = document.querySelector("#voiceButton");
const improvementList = document.querySelector("#improvementList");
const keywordGap = document.querySelector("#keywordGap");
const skillChart = document.querySelector("#skillChart");
const matchLabel = document.querySelector("#matchLabel");
const themeToggle = document.querySelector("#themeToggle");
const themeIcon = document.querySelector("#themeIcon");
const targetRole = document.querySelector("#targetRole");
const customRoleField = document.querySelector("#customRoleField");

let latestAnalysis = null;

initTheme();

fileInput.addEventListener("change", () => {
  fileLabel.textContent = fileInput.files[0]?.name || "Upload resume";
});

targetRole.addEventListener("change", updateCustomRoleVisibility);
updateCustomRoleVisibility();

themeToggle.addEventListener("click", () => {
  const nextTheme = getActiveTheme() === "dark" ? "light" : "dark";
  applyTheme(nextTheme, true);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = form.querySelector(".primary-button");
  statusText.textContent = "Analyzing resume...";
  submitButton.disabled = true;

  try {
    const formData = new FormData(form);
    const response = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Resume analysis failed.");
    }
    latestAnalysis = data;
    renderResults(data);
    statusText.textContent = "Analysis complete.";
  } catch (error) {
    statusText.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

improveButton.addEventListener("click", async () => {
  statusText.textContent = "Generating improved bullets...";
  try {
    const formData = new FormData(form);
    const response = await fetch(`${API_BASE}/api/improve`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Could not improve resume bullets.");
    }
    renderImprovements(data.improvements);
    statusText.textContent = "Improved bullets generated.";
  } catch (error) {
    statusText.textContent = error.message;
  }
});

voiceButton.addEventListener("click", () => {
  if (!latestAnalysis) {
    statusText.textContent = "Analyze a resume first, then I can read the feedback.";
    return;
  }
  const message = new SpeechSynthesisUtterance(latestAnalysis.voiceSummary);
  message.rate = 0.95;
  message.pitch = 1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(message);
  statusText.textContent = "Reading feedback aloud.";
});

function renderResults(data) {
  scoreValue.textContent = data.overallScore;
  scoreOrb.style.background = `conic-gradient(${scoreColor(data.overallScore)} ${data.overallScore * 3.6}deg, var(--track) 0deg)`;
  roleLabel.textContent = data.targetRole;
  levelLabel.textContent = data.level;
  wordCount.textContent = `${data.wordCount} words`;

  metricsGrid.innerHTML = Object.entries(data.sectionScores)
    .map(([label, value]) => metricCard(label, value))
    .join("");

  skillGroups.classList.remove("empty-state");
  skillGroups.innerHTML = [
    chipGroup("Matched required", data.skills.matchedRequired, "good"),
    chipGroup("Missing required", data.skills.missingRequired, "bad"),
    chipGroup("High priority", data.skills.highPriority, "priority"),
    chipGroup("Advanced to learn", data.skills.suggestedAdvanced, "warn"),
    chipGroup("Smart extracted skills", data.skills.found, ""),
  ].join("");

  matchLabel.textContent = `${data.sectionScores["Job Match"]}% match`;
  keywordGap.classList.remove("empty-state");
  keywordGap.innerHTML = [
    chipGroup("Present skills", data.skills.found, "good"),
    chipGroup("Missing skills", data.skills.missingRequired, "bad"),
    chipGroup("Job keywords missing", data.jobMatch.missing, "warn"),
    chipGroup("High priority skills", data.skills.highPriority, "priority"),
  ].join("");

  renderSkillChart(data.charts.skillDistribution);

  recommendations.classList.remove("empty-state");
  recommendations.innerHTML = data.recommendations.map((item) => `<li>${escapeHtml(item)}</li>`).join("");

  signalsGrid.innerHTML = [
    signalBox("Quantified impact", `${data.signals.metricsCount} measurable result signals found.`),
    signalBox("Action language", `${data.signals.actionVerbCount} strong action verbs detected.`),
    signalBox("ATS compatibility", data.signals.atsWarnings.length ? data.signals.atsWarnings.join(" ") : "No major ATS warnings detected."),
    signalBox("Keyword density", `${data.signals.keywordDensity}% skill keyword density.`),
    signalBox("Job keywords matched", listSentence(data.jobMatch.matched)),
    signalBox("Detected sections", sectionSentence(data.sections)),
  ].join("");

  renderImprovements(data.improvements);
}

function metricCard(label, value) {
  return `
    <article class="panel metric">
      <div class="metric-top">
        <strong style="color:${scoreColor(value)}">${value}%</strong>
        <span>${escapeHtml(label)}</span>
      </div>
      <div class="progress-track" aria-label="${escapeHtml(label)}">
        <div class="progress-fill" style="width:${value}%;background:${scoreColor(value)}"></div>
      </div>
    </article>
  `;
}

function chipGroup(title, items, type) {
  const chips = items.length
    ? items.map((item) => `<span class="chip ${type}">${escapeHtml(item)}</span>`).join("")
    : `<span class="chip">None yet</span>`;
  return `
    <div>
      <strong>${escapeHtml(title)}</strong>
      <div class="chip-row">${chips}</div>
    </div>
  `;
}

function renderSkillChart(distribution) {
  const max = Math.max(1, ...Object.values(distribution));
  skillChart.classList.remove("empty-state");
  skillChart.innerHTML = Object.entries(distribution)
    .map(([label, value]) => {
      const height = Math.max(8, (value / max) * 100);
      return `
        <div class="bar-item">
          <div class="bar-column" style="height:${height}%"></div>
          <strong>${value}</strong>
          <span>${escapeHtml(label)}</span>
        </div>
      `;
    })
    .join("");
}

function renderImprovements(items) {
  improvementList.classList.remove("empty-state");
  improvementList.innerHTML = items.length
    ? items.map((item) => `
        <article class="improvement-card">
          <small>Before</small>
          <p>${escapeHtml(item.before)}</p>
          <small>After</small>
          <strong>${escapeHtml(item.after)}</strong>
        </article>
      `).join("")
    : "No bullet points found to improve yet.";
}

function signalBox(title, text) {
  return `
    <article class="signal-box">
      <strong>${escapeHtml(title)}</strong>
      <p>${escapeHtml(text)}</p>
    </article>
  `;
}

function sectionSentence(sections) {
  const present = Object.entries(sections)
    .filter(([, value]) => value)
    .map(([name]) => name);
  return present.length ? present.join(", ") : "No standard section headings detected.";
}

function listSentence(items) {
  return items.length ? items.join(", ") : "No items in this category.";
}

function scoreColor(score) {
  if (score >= 75) return "#52d273";
  if (score >= 55) return "#f7bc45";
  return "#ff5c7c";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function initTheme() {
  const savedTheme = localStorage.getItem("resumeAnalyzerTheme");
  if (savedTheme === "light" || savedTheme === "dark") {
    applyTheme(savedTheme, false);
  } else {
    document.documentElement.removeAttribute("data-theme");
    updateThemeButton(getActiveTheme(), true);
  }

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (!localStorage.getItem("resumeAnalyzerTheme")) {
      updateThemeButton(getActiveTheme(), true);
    }
  });
}

function applyTheme(theme, persist) {
  document.documentElement.dataset.theme = theme;
  if (persist) {
    localStorage.setItem("resumeAnalyzerTheme", theme);
  }
  updateThemeButton(theme, false);
}

function getActiveTheme() {
  const explicitTheme = document.documentElement.dataset.theme;
  if (explicitTheme) {
    return explicitTheme;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function updateThemeButton(theme, isSystem) {
  themeIcon.textContent = theme === "dark" ? "D" : "L";
  themeToggle.title = isSystem ? `Using system ${theme} theme` : `Using ${theme} theme`;
  themeToggle.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} theme`);
}

function updateCustomRoleVisibility() {
  customRoleField.hidden = targetRole.value !== "custom-role";
}
