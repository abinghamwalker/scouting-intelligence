"use strict";

const main = document.getElementById("main-content");
const bootstrap = JSON.parse(main.dataset.bootstrap);
const state = {
  result: null,
  comparison: null,
  exemplar: null,
  selectedGrains: new Set(),
  searchOffset: 0,
  searchLimit: 50,
  searchTotal: 0,
};

const floatKeys = new Set(["minimum_minutes", "value", "weight"]);

class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function node(tag, text = null, className = null) {
  const element = document.createElement(tag);
  if (text !== null) element.textContent = String(text);
  if (className) element.className = className;
  return element;
}

function clear(element) {
  element.replaceChildren();
}

function labelForFeature(name) {
  return name.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function shortDigest(value) {
  return value ? `${value.slice(0, 12)}…${value.slice(-8)}` : "—";
}

function formatNumber(value, digits = 3) {
  return new Intl.NumberFormat("en-GB", { maximumFractionDigits: digits }).format(value);
}

function canonicalJson(value, key = null) {
  if (value === null) return "null";
  if (typeof value === "boolean" || typeof value === "string") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value) || Object.is(value, -0)) {
      throw new Error("Numeric inputs must be finite and cannot use negative zero.");
    }
    if (floatKeys.has(key)) return pythonFloat(value);
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return `[${value.map((item) => canonicalJson(item)).join(",")}]`;
  const keys = Object.keys(value).sort();
  return `{${keys.map((item) => `${JSON.stringify(item)}:${canonicalJson(value[item], item)}`).join(",")}}`;
}

function pythonFloat(value) {
  if (value === 0) return "0.0";
  const absolute = Math.abs(value);
  if (absolute < 1e-4 || absolute >= 1e16) {
    const [mantissa, rawExponent] = value.toExponential().split("e");
    const exponent = Number(rawExponent);
    const sign = exponent < 0 ? "-" : "+";
    return `${mantissa}e${sign}${String(Math.abs(exponent)).padStart(2, "0")}`;
  }
  const rendered = JSON.stringify(value);
  return Number.isInteger(value) ? `${rendered}.0` : rendered;
}

async function sha256Bytes(value) {
  const payload = new TextEncoder().encode(canonicalJson(value));
  return new Uint8Array(await crypto.subtle.digest("SHA-256", payload));
}

async function digest(value) {
  return Array.from(await sha256Bytes(value), (item) => item.toString(16).padStart(2, "0")).join("");
}

async function deterministicExperimentId(value) {
  const bytes = (await sha256Bytes(value)).slice(0, 16);
  bytes[6] = (bytes[6] & 0x0f) | 0x80;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = Array.from(bytes, (item) => item.toString(16).padStart(2, "0")).join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.body) headers.set("Content-Type", "application/json");
  const response = await fetch(path, {
    ...options,
    headers,
    cache: "no-store",
    credentials: "same-origin",
    redirect: "error",
  });
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      message = typeof payload.detail === "string" ? payload.detail : message;
    } catch (_) {
      // The status remains exact even when a failure body is not JSON.
    }
    throw new ApiError(response.status, message);
  }
  return response.json();
}

function setStatus(kind, message) {
  const card = document.getElementById("workbench-status");
  card.dataset.state = kind;
  document.getElementById("status-message").textContent = message;
}

function showError(error, context) {
  if (error instanceof ApiError && error.status === 422) {
    setStatus("validation-error", `${context}: validation failed — ${error.message}`);
  } else if (error instanceof ApiError && error.status === 409) {
    setStatus("conflict", `${context}: stale or incompatible authority — ${error.message}`);
  } else if (error instanceof ApiError && [404, 503].includes(error.status)) {
    setStatus("unavailable", `${context}: required governed evidence is unavailable.`);
  } else {
    setStatus("error", `${context}: ${error.message || "unexpected local error"}`);
  }
}

function metric(label, value) {
  const item = node("div", null, "metric");
  item.append(node("span", label), node("strong", value));
  return item;
}

function renderDataset(dataset) {
  const summary = document.getElementById("dataset-summary");
  clear(summary);
  summary.append(
    metric("Eligible matrix rows", formatNumber(bootstrap.matrix_row_count, 0)),
    metric("Eligible players", formatNumber(bootstrap.unique_matrix_player_count, 0)),
    metric("Source matches", formatNumber(dataset.source_match_count, 0)),
    metric("Source actions", formatNumber(dataset.source_action_count, 0)),
    metric("Source teams", formatNumber(dataset.source_team_count, 0)),
    metric("Source players", formatNumber(dataset.source_player_count, 0)),
    metric("Window", `${dataset.window_start_utc.slice(0, 10)} → ${dataset.window_end_utc.slice(0, 10)}`),
    metric("Feature cutoff", dataset.feature_cutoff_ts),
  );

  const details = document.getElementById("dataset-details");
  clear(details);
  const list = node("dl");
  const values = [
    ["Dataset version", dataset.dataset_version],
    ["Dataset manifest", dataset.dataset_manifest_digest],
    ["Matrix version", bootstrap.pins.matrix_version],
    ["Matrix digest", bootstrap.pins.matrix_digest],
    ["Index version", bootstrap.pins.index_version],
    ["Index manifest", bootstrap.pins.index_manifest_digest],
    ["Feature registry", bootstrap.pins.feature_registry_version],
    ["Eligibility policy", bootstrap.pins.eligibility_policy_version],
    ["Rights", dataset.rights_classification],
    ["Attribution", dataset.attribution],
    ["Capabilities", dataset.capabilities.join(", ")],
  ];
  for (const [term, description] of values) {
    list.append(node("dt", term), node("dd", description));
  }
  details.append(list, node("h3", "Limitations"));
  const limitations = node("ul");
  for (const limitation of dataset.limitations) limitations.append(node("li", limitation));
  details.append(limitations);
  document.getElementById("dataset-state").textContent = "Verified local authority";
}

function renderCompetitionOptions() {
  const select = document.getElementById("competition");
  const searchSelect = document.getElementById("search-competition");
  clear(select);
  clear(searchSelect);
  const anyCompetition = node("option", "Any competition");
  anyCompetition.value = "";
  searchSelect.append(anyCompetition);
  for (const competition of bootstrap.competitions) {
    const option = node("option", competition.competition_name);
    option.value = competition.competition_id;
    select.append(option);
    const searchOption = option.cloneNode(true);
    searchSelect.append(searchOption);
  }
  renderSeasonOptions();
}

function renderSeasonOptions(preferredSeasonId = null) {
  const competitionId = document.getElementById("competition").value;
  const seasonSelect = document.getElementById("season");
  clear(seasonSelect);
  const competition = bootstrap.competitions.find((item) => item.competition_id === competitionId);
  for (const seasonId of competition?.season_ids || []) {
    const option = node("option", seasonId);
    option.value = seasonId;
    seasonSelect.append(option);
  }
  if (preferredSeasonId && competition?.season_ids.includes(preferredSeasonId)) {
    seasonSelect.value = preferredSeasonId;
  }
}

function renderFeatureInputs() {
  const profiles = document.getElementById("profile-fields");
  const weights = document.getElementById("weight-fields");
  clear(profiles);
  clear(weights);
  for (const [index, featureName] of bootstrap.feature_names.entries()) {
    const profileField = node("div", null, "field");
    const profileLabel = node("label", `${labelForFeature(featureName)} target`);
    const profileInput = node("input");
    profileInput.id = `profile-${index}`;
    profileInput.dataset.feature = featureName;
    profileInput.type = "number";
    profileInput.step = "any";
    profileInput.value = "0";
    profileInput.required = true;
    profileLabel.htmlFor = profileInput.id;
    profileField.append(profileLabel, profileInput);
    profiles.append(profileField);

    const weightField = node("div", null, "field");
    const weightLabel = node("label", `${labelForFeature(featureName)} weight`);
    const weightInput = node("input");
    weightInput.id = `weight-${index}`;
    weightInput.dataset.feature = featureName;
    weightInput.type = "number";
    weightInput.min = "0";
    weightInput.step = "any";
    weightInput.value = "1";
    weightInput.required = true;
    weightLabel.htmlFor = weightInput.id;
    weightField.append(weightLabel, weightInput);
    weights.append(weightField);
  }
}

function mode() {
  return document.querySelector('input[name="query-mode"]:checked').value;
}

function updateMode() {
  const exemplar = mode() === "exemplar";
  document.getElementById("exemplar-panel").hidden = !exemplar;
  document.getElementById("profile-panel").hidden = exemplar;
}

function renderSearchResults(payload) {
  const container = document.getElementById("player-search-results");
  clear(container);
  state.searchOffset = payload.offset;
  state.searchLimit = payload.limit;
  state.searchTotal = payload.total_matches;
  const first = payload.total_matches ? payload.offset + 1 : 0;
  const last = Math.min(payload.offset + payload.players.length, payload.total_matches);
  document.getElementById("search-page-state").textContent =
    `${first}–${last} of ${payload.total_matches}`;
  document.getElementById("search-previous").disabled = payload.offset === 0;
  document.getElementById("search-next").disabled =
    payload.offset + payload.players.length >= payload.total_matches;
  if (!payload.players.length) {
    container.append(node("div", "No eligible historical player rows match this search.", "empty-card"));
    setStatus("empty", "Player search completed with no eligible matches.");
    return;
  }
  for (const player of payload.players) {
    const card = node("article", null, "search-result");
    const copy = node("div");
    copy.append(
      node("h3", player.display_name),
      node("p", `${player.position_code} · ${player.competition_name} · ${formatNumber(player.minutes, 1)} minutes`),
    );
    const button = node("button", "Use exemplar", "button secondary");
    button.type = "button";
    button.addEventListener("click", () => {
      state.exemplar = player;
      document.getElementById("selected-exemplar").textContent =
        `Selected exemplar: ${player.display_name} · ${player.competition_name} · ${player.grain_id}`;
      document.getElementById("competition").value = player.competition_id;
      renderSeasonOptions(player.season_id);
      setStatus("ready", `Exemplar selected: ${player.display_name}.`);
    });
    card.append(copy, button);
    container.append(card);
  }
  setStatus("ready", `${payload.total_matches} eligible player row(s) match the governed search.`);
}

async function searchPlayers(event = null) {
  if (event) {
    event.preventDefault();
    state.searchOffset = 0;
  }
  setStatus("loading", "Searching the governed eligible matrix…");
  const parameters = new URLSearchParams({
    limit: String(state.searchLimit),
    offset: String(state.searchOffset),
  });
  const name = document.getElementById("player-search").value.trim();
  const position = document.getElementById("search-position").value;
  const competitionId = document.getElementById("search-competition").value;
  if (name) parameters.set("name", name);
  if (position) parameters.set("position", position);
  if (competitionId) parameters.set("competition_id", competitionId);
  try {
    renderSearchResults(await api(`/api/w09/players?${parameters}`));
  } catch (error) {
    clear(document.getElementById("player-search-results"));
    showError(error, "Player search");
  }
}

function numericInput(selector, label) {
  const input = document.querySelector(selector);
  const value = Number(input.value);
  if (!input.value.trim() || !Number.isFinite(value) || Object.is(value, -0)) {
    throw new Error(`${label} must be a finite number without negative zero.`);
  }
  return value;
}

async function queryPayload() {
  const selectedMode = mode();
  if (selectedMode === "exemplar" && !state.exemplar) {
    throw new Error("Select a governed real-player exemplar first.");
  }
  const weights = bootstrap.feature_names.map((featureName, index) => ({
    feature_name: featureName,
    weight: numericInput(`#weight-${index}`, `${featureName} weight`),
  }));
  if (!weights.some((item) => item.weight > 0)) throw new Error("At least one feature weight must be positive.");
  if (weights.some((item) => item.weight < 0)) throw new Error("Feature weights cannot be negative.");
  const profile = selectedMode === "weighted_profile"
    ? bootstrap.feature_names.map((featureName, index) => ({
      feature_name: featureName,
      value: numericInput(`#profile-${index}`, `${featureName} target`),
    }))
    : [];
  const minimumText = document.getElementById("minimum-minutes").value.trim();
  const minimumMinutes = minimumText ? Number(minimumText) : null;
  if (minimumMinutes !== null && (!Number.isFinite(minimumMinutes) || minimumMinutes < 0 || Object.is(minimumMinutes, -0))) {
    throw new Error("Minimum minutes must be a non-negative finite number.");
  }
  const position = document.getElementById("filter-position").value;
  const limit = Number(document.getElementById("result-limit").value);
  if (!Number.isInteger(limit) || limit < 1 || limit > 100) throw new Error("Result limit must be an integer from 1 to 100.");
  const payload = {
    schema_version: 1,
    query_id: crypto.randomUUID(),
    requested_at: new Date().toISOString(),
    feature_cutoff_ts: bootstrap.pins.feature_cutoff_ts,
    pins: bootstrap.pins,
    mode: selectedMode,
    method: document.getElementById("method").value,
    exemplar_grain_id: selectedMode === "exemplar" ? state.exemplar.grain_id : null,
    profile,
    weights,
    filters: {
      competition_id: document.getElementById("competition").value,
      season_id: document.getElementById("season").value,
      position_codes: position ? [position] : [],
      minimum_minutes: minimumMinutes,
      excluded_player_ids: [],
    },
    limit,
    query_digest: "0".repeat(64),
    claim_boundary: "historical_resemblance_research_only",
  };
  const projection = { ...payload };
  delete projection.query_digest;
  delete projection.requested_at;
  payload.query_digest = await digest(projection);
  return payload;
}

function contributionTable(candidate) {
  const wrapper = node("div", null, "table-scroll");
  const table = node("table");
  table.append(node("caption", `Per-feature explanation for ${candidate.display_name}`));
  const head = node("thead");
  const headRow = node("tr");
  for (const heading of ["Feature", "Weight", "Query raw", "Player raw", "Scaled contrast", "Contribution"]) {
    const cell = node("th", heading);
    cell.scope = "col";
    headRow.append(cell);
  }
  head.append(headRow);
  const body = node("tbody");
  for (const item of candidate.contributions) {
    const row = node("tr");
    for (const value of [
      labelForFeature(item.feature_name),
      formatNumber(item.weight),
      formatNumber(item.query_value),
      formatNumber(item.candidate_value),
      formatNumber(item.scaled_contrast),
      formatNumber(item.contribution, 6),
    ]) row.append(node("td", value));
    body.append(row);
  }
  table.append(head, body);
  wrapper.append(table);
  return wrapper;
}

function renderPopulation(population) {
  const container = document.getElementById("population-accounting");
  clear(container);
  for (const [label, value] of [
    ["Matrix rows", population.matrix_rows],
    ["Competition rows", population.competition_rows],
    ["Filter admitted", population.filter_admitted_rows],
    ["Scored", population.scored_rows],
    ["Returned", population.returned_rows],
  ]) container.append(metric(label, formatNumber(value, 0)));
}

function methodInterpretation(method) {
  if (method === "weighted_euclidean") {
    return "Weighted Euclidean result: each contribution is weight × scaled contrast², and distance is the square root of their sum. Lower means closer only under these exact features, weights and authority pins. These values are not percentages, probabilities or calibrated match scores.";
  }
  if (method === "weighted_cosine") {
    return "Weighted cosine result: each signed contribution is the negative product of the weighted normalised query and candidate components, and distance is 1 plus their sum. Lower means closer only under these exact features, weights and authority pins. These values are not percentages, probabilities or calibrated match scores.";
  }
  throw new Error("Research result used an unsupported retrieval method.");
}

function updateCompareButton() {
  const count = state.selectedGrains.size;
  const button = document.getElementById("compare-selected");
  button.disabled = count < 2 || count > 5;
  button.textContent = count ? `Compare ${count} selected` : "Compare 2–5 selected";
}

function renderResult(result) {
  state.result = result;
  state.comparison = null;
  state.selectedGrains.clear();
  updateCompareButton();
  document.getElementById("save-experiment").disabled = false;
  const digestChip = document.getElementById("result-digest");
  digestChip.textContent = `Result ${shortDigest(result.result_digest)}`;
  digestChip.dataset.method = result.request.method;
  renderPopulation(result.population);
  document.getElementById("method-interpretation").textContent =
    methodInterpretation(result.request.method);
  const warningContainer = document.getElementById("result-warnings");
  clear(warningContainer);
  for (const warning of result.warnings) warningContainer.append(node("p", warning, "warning"));
  const container = document.getElementById("candidate-results");
  clear(container);
  if (!result.candidates.length) {
    container.append(node("div", "No governed candidates survived the submitted eligibility filters.", "empty-card"));
    setStatus("empty", "The query is valid but returned no candidates.");
    return;
  }
  for (const candidate of result.candidates) {
    const card = node("article", null, "candidate-card");
    const summary = node("div", null, "candidate-summary");
    const identity = node("div");
    identity.append(
      node("h3", `${candidate.rank}. ${candidate.display_name}`),
      node("p", `${candidate.position_code} · ${formatNumber(candidate.minutes, 1)} evidenced minutes · ${candidate.grain_id}`),
    );
    const score = node("div", null, "rank-score");
    score.append(node("span", "Distance / dissimilarity"), node("strong", formatNumber(candidate.score, 6)));
    summary.append(identity, score);
    const body = node("div", null, "candidate-body");
    const selection = node("label", null, "candidate-select");
    const checkbox = node("input");
    checkbox.type = "checkbox";
    checkbox.value = candidate.grain_id;
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) state.selectedGrains.add(candidate.grain_id);
      else state.selectedGrains.delete(candidate.grain_id);
      updateCompareButton();
    });
    selection.append(checkbox, document.createTextNode(" Select for exact comparison"));
    const details = node("details");
    details.append(node("summary", "Inspect contributions and contrasts"));
    const detailBody = node("div", null, "details-body");
    detailBody.append(
      contributionTable(candidate),
      node("h3", "Candidate limitations"),
    );
    const limitations = node("ul");
    for (const limitation of candidate.limitations) limitations.append(node("li", limitation));
    detailBody.append(limitations);
    details.append(detailBody);
    body.append(selection, details);
    card.append(summary, body);
    container.append(card);
  }
  setStatus("ready", `${result.candidates.length} ranked historical player(s) returned from ${result.population.scored_rows} scored rows.`);
}

async function runQuery(event) {
  event.preventDefault();
  setStatus("loading", "Scoring the full filter-admitted historical population…");
  try {
    const payload = await queryPayload();
    renderResult(await api("/api/w09/queries", { method: "POST", body: JSON.stringify(payload) }));
  } catch (error) {
    if (error instanceof ApiError) showError(error, "Research query");
    else setStatus("validation-error", `Research query: ${error.message}`);
  }
}

async function comparisonPayload() {
  const payload = {
    schema_version: 1,
    comparison_id: crypto.randomUUID(),
    result_id: state.result.result_id,
    result_digest: state.result.result_digest,
    query_digest: state.result.request.query_digest,
    pins: state.result.request.pins,
    grain_ids: Array.from(state.selectedGrains),
    comparison_request_digest: "0".repeat(64),
  };
  const projection = { ...payload };
  delete projection.comparison_request_digest;
  payload.comparison_request_digest = await digest(projection);
  return payload;
}

function renderComparison(comparison) {
  state.comparison = comparison;
  const container = document.getElementById("comparison-results");
  clear(container);
  for (const row of comparison.rows) {
    const card = node("article", null, "comparison-card");
    card.append(node("h3", row.display_name), node("p", `${row.position_code} · ${row.competition_name}`));
    const list = node("dl");
    const evidence = [
      ["Minutes", formatNumber(row.minutes, 1)],
      ["Minute state", row.minute_state],
      ["Matches", row.match_count],
      ["Actions", row.source_action_count],
      ["Lineup coverage", `${row.coverage.lineup_matches_observed}/${row.coverage.lineup_matches_expected}`],
      ["Action coverage", `${row.coverage.action_matches_observed}/${row.coverage.action_matches_expected}`],
      ...row.features.map((feature) => [labelForFeature(feature.feature_name), feature.value === null ? feature.state : formatNumber(feature.value)]),
    ];
    for (const [term, value] of evidence) list.append(node("dt", term), node("dd", value));
    card.append(list);
    container.append(card);
  }
  setStatus("ready", `${comparison.rows.length} exact candidate rows compared.`);
}

async function compareSelected() {
  setStatus("loading", "Loading exact matrix evidence for selected candidates…");
  try {
    const payload = await comparisonPayload();
    renderComparison(await api("/api/w09/comparisons", { method: "POST", body: JSON.stringify(payload) }));
  } catch (error) {
    showError(error, "Candidate comparison");
  }
}

function reportLink(experiment) {
  const reportFormat = experiment.report?.report_format ?? experiment.report_format;
  const link = node("a", `Open exact ${reportFormat.toUpperCase()} report`, "report-link");
  link.href = `/api/w09/experiments/${experiment.experiment_id}/report`;
  link.target = "_blank";
  link.rel = "noopener";
  return link;
}

function renderSaved(experiment) {
  const container = document.getElementById("saved-experiment");
  clear(container);
  const card = node("div", null, "saved-card");
  card.append(
    node("h3", experiment.name),
    node("p", `Experiment ${experiment.experiment_id} · digest ${shortDigest(experiment.experiment_digest)}`),
    reportLink(experiment),
  );
  const replay = node("button", "Replay exact saved pins", "button secondary");
  replay.type = "button";
  replay.addEventListener("click", () => replayExperiment(experiment.experiment_id));
  card.append(replay);
  container.append(card);
}

async function saveExperiment(event) {
  event.preventDefault();
  if (!state.result) return;
  const name = document.getElementById("experiment-name").value.trim();
  const note = document.getElementById("experiment-note").value.trim();
  if (!name) {
    setStatus("validation-error", "Experiment name is required.");
    return;
  }
  const reportFormat = document.getElementById("report-format").value;
  const semanticIdentity = {
    result_digest: state.result.result_digest,
    comparison_digest: state.comparison ? state.comparison.comparison_digest : null,
    name,
    note: note || null,
    report_format: reportFormat,
  };
  const payload = {
    experiment_id: await deterministicExperimentId(semanticIdentity),
    name,
    note: note || null,
    result_id: state.result.result_id,
    result_digest: state.result.result_digest,
    comparison_id: state.comparison ? state.comparison.request.comparison_id : null,
    comparison_digest: state.comparison ? state.comparison.comparison_digest : null,
    report_format: reportFormat,
  };
  setStatus("loading", "Rendering and saving a content-addressed local report…");
  try {
    const experiment = await api("/api/w09/experiments", { method: "POST", body: JSON.stringify(payload) });
    renderSaved(experiment);
    await loadExperiments();
    setStatus("ready", "Exact experiment and report saved locally.");
  } catch (error) {
    showError(error, "Save experiment");
  }
}

async function replayExperiment(experimentId) {
  const container = document.getElementById("replay-state");
  container.dataset.state = "loading";
  container.textContent = "Replaying the exact saved request and version pins…";
  try {
    const receipt = await api(`/api/w09/experiments/${experimentId}/replay`, { method: "POST" });
    const messages = {
      reproduced: "Replay reproduced the exact saved query, pins, result identity and digest.",
      incompatible_pins: "Replay closed safely: the loaded artifact pins differ from the saved experiment.",
      result_mismatch: "Replay completed but the deterministic result identity or digest does not match.",
    };
    const message = messages[receipt.status];
    if (!message) {
      container.dataset.state = "error";
      container.textContent = "Replay returned an unsupported closed status.";
      setStatus("error", "Replay experiment: unsupported replay status.");
      return;
    }
    container.dataset.state = receipt.status;
    container.textContent = `${message} Receipt ${shortDigest(receipt.receipt_digest)}`;
    setStatus(receipt.status === "reproduced" ? "ready" : "conflict", message);
  } catch (error) {
    showError(error, "Replay experiment");
  }
}

async function loadExperiments() {
  const container = document.getElementById("experiment-list");
  try {
    const experiments = await api("/api/w09/experiments");
    clear(container);
    if (!experiments.length) {
      container.append(node("p", "No local experiments have been saved yet."));
      return;
    }
    const list = node("ul");
    for (const experiment of experiments) {
      const item = node("li");
      item.append(document.createTextNode(`${experiment.name} · ${experiment.created_at} · `), reportLink(experiment));
      list.append(item);
    }
    container.append(list);
  } catch (error) {
    container.textContent = "Saved experiment state is unavailable.";
    showError(error, "Experiment list");
  }
}

async function initialise() {
  renderCompetitionOptions();
  renderFeatureInputs();
  updateMode();
  try {
    const datasets = await api("/api/w09/datasets");
    if (datasets.length !== 1) throw new ApiError(409, "exactly one dataset is required");
    const dataset = datasets[0];
    if (
      dataset.dataset_version !== bootstrap.dataset.dataset_version
      || dataset.dataset_manifest_digest !== bootstrap.dataset.dataset_manifest_digest
    ) throw new ApiError(409, "displayed dataset authority differs from the API authority");
    renderDataset(dataset);
    await Promise.all([searchPlayers(), loadExperiments()]);
  } catch (error) {
    showError(error, "Workbench bootstrap");
  }
}

document.querySelectorAll('input[name="query-mode"]').forEach((input) => input.addEventListener("change", updateMode));
document.getElementById("competition").addEventListener("change", () => renderSeasonOptions());
document.getElementById("player-search-form").addEventListener("submit", searchPlayers);
document.getElementById("search-previous").addEventListener("click", () => {
  state.searchOffset = Math.max(0, state.searchOffset - state.searchLimit);
  searchPlayers();
});
document.getElementById("search-next").addEventListener("click", () => {
  state.searchOffset += state.searchLimit;
  searchPlayers();
});
document.getElementById("query-form").addEventListener("submit", runQuery);
document.getElementById("compare-selected").addEventListener("click", compareSelected);
document.getElementById("save-form").addEventListener("submit", saveExperiment);

initialise();
