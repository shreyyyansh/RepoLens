const API_URL = "http://127.0.0.1:5000/analyze";

const orgInput = document.getElementById("orgName");
const analyzeButton = document.getElementById("analyzeButton");
const loaderContainer = document.getElementById("loader-container");
const resultsHeaderBar = document.getElementById("results-header-bar");
const resultsHeader = document.getElementById("results-header");
const resultsGrid = document.getElementById("results-grid");
const sortContainer = document.getElementById("sort-container");
const sortSelect = document.getElementById("sortSelect");

if (analyzeButton) {
  analyzeButton.addEventListener("click", startAnalysis);
}
if (orgInput) {
  orgInput.addEventListener("keyup", (event) => {
    if (event.key === "Enter") startAnalysis();
  });
}

async function startAnalysis() {
  const orgName = orgInput.value.trim();

  if (!orgName) {
    alert("Please enter a GitHub organization name.");
    return;
  }

  loaderContainer.style.display = "block";
  resultsHeaderBar.style.display = "none";
  resultsGrid.innerHTML = "";
  analyzeButton.disabled = true;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ org: orgName }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Server error occurred");

    const report = Array.isArray(data.report) ? data.report : [];
    displayResults(report, orgName);
  } catch (error) {
    console.error("Error:", error);
    resultsGrid.innerHTML = `<div class="error">An error occurred: ${error.message}</div>`;
  } finally {
    loaderContainer.style.display = "none";
    analyzeButton.disabled = false;
  }
}

function displayResults(report, orgName) {
  if (!report.length) {
    resultsHeader.innerText = `No repositories found for "${orgName}"`;
    resultsHeaderBar.style.display = "flex";
    return;
  }

  resultsHeader.innerText = `Analysis Report (${report.length} Repos)`;
  resultsHeaderBar.style.display = "flex";
  sortContainer.style.display = "flex";

  report.sort((a, b) => (b.stars || 0) - (a.stars || 0));
  renderCards(report);

  sortSelect.addEventListener("change", () => {
    const val = sortSelect.value;
    if (val === "stars") report.sort((a, b) => (b.stars || 0) - (a.stars || 0));
    if (val === "name") report.sort((a, b) => (a.repo_name || "").localeCompare(b.repo_name || ""));
    if (val === "updated") report.sort((a, b) => new Date(b.last_push || 0) - new Date(a.last_push || 0));
    renderCards(report);
  });
}

function renderCards(repos) {
  resultsGrid.innerHTML = "";
  repos.forEach((repo) => {
    const repoName = repo.repo_name || "Unnamed Repository";
    const repoURL = repo.github_url || "#";
    const description = repo.description || "No description available.";
    const aiSummary = repo.ai_summary || "No AI summary available.";
    const activityStatus = repo.activity_status || "Unknown";
    const statusClass = activityStatus.toLowerCase().includes("active") ? "active" : "inactive";
    const stars = repo.stars || 0;
    const language = repo.language || "N/A";
    const lastPush = repo.last_push ? new Date(repo.last_push).toLocaleDateString() : "Unknown";

    const card = document.createElement("div");
    card.className = "repo-card";
    card.innerHTML = `
      <div class="card-header">
        <h3><a href="${repoURL}" target="_blank">${repoName}</a></h3>
        <div class="stat status ${statusClass}">
          <span class="status-dot"></span>${activityStatus}
        </div>
      </div>
      <p class="description">${description}</p>
      <div class="ai-summary"><strong>AI Summary:</strong><p>${aiSummary}</p></div>
      <div class="card-footer">
        <div class="stat">⭐ ${stars} Stars</div>
        <div class="stat">${language}</div>
        <div class="stat">Last push: ${lastPush}</div>
      </div>
    `;
    resultsGrid.appendChild(card);
  });
}
