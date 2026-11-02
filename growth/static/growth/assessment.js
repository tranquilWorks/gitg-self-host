(function () {
  "use strict";

  const app = document.getElementById("assessment-app");
  if (!app || !window.GroundedGrowthAssessment) return;

  const spec = JSON.parse(document.getElementById("assessment-spec").textContent);
  const model = JSON.parse(document.getElementById("assessment-model").textContent);
  const display = JSON.parse(document.getElementById("assessment-display").textContent);
  const assessment = spec.assessment;
  const engine = window.GroundedGrowthAssessment;
  const storageKey = app.dataset.storageKey;
  const saveUrl = app.dataset.saveUrl;
  const coreItems = assessment.core_items;
  const coreIds = coreItems.map((item) => item.id);
  const allItems = [
    ...coreItems,
    ...assessment.adaptive_capability_clarifiers,
    ...assessment.adaptive_orientation_clarifiers,
  ];
  const itemMap = Object.fromEntries(allItems.map((item) => [item.id, item]));

  const byId = (id) => document.getElementById(id);
  const stages = {
    intro: byId("assessment-intro"),
    quiz: byId("assessment-quiz"),
    results: byId("assessment-results"),
  };
  const importPanel = app.querySelector(".assessment-import");
  const csrfToken = app.querySelector("[name=csrfmiddlewaretoken]").value;
  const startButton = byId("assessment-start");
  const resetButton = byId("assessment-reset");
  const importButton = byId("assessment-import-submit");
  const count = byId("assessment-count");
  const autosave = byId("assessment-autosave");
  const progressFill = byId("assessment-progress-fill");
  const prompt = byId("assessment-prompt");
  const scale = byId("assessment-scale");
  const backButton = byId("assessment-back");
  const nextButton = byId("assessment-next");
  const saveStatus = byId("assessment-save-status");
  const saveError = byId("assessment-save-error");
  const profileLink = byId("assessment-profile-link");
  const retrySaveButton = byId("assessment-retry-save");

  function newSubmissionId() {
    if (window.crypto && window.crypto.randomUUID) return window.crypto.randomUUID();
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (character) => {
      const random = Math.floor(Math.random() * 16);
      const value = character === "x" ? random : (random & 3) | 8;
      return value.toString(16);
    });
  }

  function freshState() {
    return {
      assessment_version: assessment.version,
      responses: {},
      timings_seconds: {},
      index: 0,
      phase: "core",
      source: "application",
      submission_id: newSubmissionId(),
    };
  }

  function loadState() {
    try {
      const stored = JSON.parse(localStorage.getItem(storageKey));
      if (
        stored &&
        stored.assessment_version === assessment.version &&
        typeof stored.responses === "object"
      ) {
        return stored;
      }
    } catch (_error) {
      localStorage.removeItem(storageKey);
    }
    return freshState();
  }

  let state = loadState();
  let order =
    state.phase === "clarifier" && Array.isArray(state.clarifier_order)
      ? state.clarifier_order
      : assessment.display_order;
  let itemStartedAt = performance.now();
  let currentTimedItem = null;

  function saveLocal() {
    localStorage.setItem(storageKey, JSON.stringify(state));
    autosave.textContent = "Saved on this device";
  }

  function show(stageName, moveFocus = true) {
    Object.entries(stages).forEach(([name, element]) => {
      element.classList.toggle("hidden", name !== stageName);
    });
    importPanel.classList.toggle("hidden", stageName === "quiz");
    importPanel.open = false;
    if (moveFocus && stageName !== "quiz") {
      const heading = stages[stageName].querySelector("h2");
      if (heading) { heading.tabIndex = -1; heading.focus(); }
    }
  }

  function responseScale(item) {
    if (item.type.startsWith("orientation")) return display.scales.orientation;
    if (item.type === "response_quality") return display.scales.response_quality;
    return display.scales.capability;
  }

  function selectAnswer(itemId, value) {
    state.responses[itemId] = value;
    saveLocal();
    scale.querySelectorAll(".assessment-answer").forEach((button) => {
      const selected = button.dataset.value === String(value);
      button.classList.toggle("selected", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
    nextButton.disabled = false;
  }

  function answerButton(item, value, label) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "assessment-answer";
    if (state.responses[item.id] === value) button.classList.add("selected");
    button.dataset.value = String(value);
    button.setAttribute("aria-pressed", String(state.responses[item.id] === value));

    const strong = document.createElement("strong");
    strong.textContent = value === "NA" ? "N/A" : String(value);
    button.append(strong, document.createTextNode(` — ${label}`));
    button.addEventListener("click", () => selectAnswer(item.id, value));
    return button;
  }

  function renderQuestion(resetClock) {
    const itemId = order[state.index];
    const item = itemMap[itemId];
    if (!item) {
      showResults();
      return;
    }

    count.textContent = `${state.phase === "clarifier" ? "Follow-up" : "Question"} ${state.index + 1} of ${order.length}`;
    progressFill.style.width = `${(100 * (state.index + 1)) / order.length}%`;
    prompt.textContent = display.prompts[itemId] || item.prompt;
    prompt.focus();
    scale.replaceChildren();
    const labels = responseScale(item);
    for (let value = 1; value <= 5; value += 1) {
      scale.append(answerButton(item, value, labels[String(value)]));
    }
    if (item.allow_not_applicable) {
      scale.append(
        answerButton(item, "NA", "Not applicable; I do not have enough experience to answer"),
      );
    }

    backButton.disabled = state.index === 0 && state.phase !== "clarifier";
    nextButton.disabled = state.responses[itemId] == null;
    nextButton.textContent = state.index === order.length - 1 ? "Finish" : "Next";
    if (resetClock || currentTimedItem !== itemId) {
      itemStartedAt = performance.now();
      currentTimedItem = itemId;
    }
  }

  function captureTiming() {
    const itemId = order[state.index];
    if (currentTimedItem !== itemId) return;
    const elapsed = Math.max(0, (performance.now() - itemStartedAt) / 1000);
    state.timings_seconds[itemId] =
      Number(state.timings_seconds[itemId] || 0) + elapsed;
    currentTimedItem = null;
  }

  function beginOrResume() {
    if (state.phase === "complete" && state.last_result) {
      renderResults(state.last_result, state.display_share_code);
      show("results");
      persistResult();
      return;
    }
    if (state.phase === "core_complete") {
      startClarifiers();
      return;
    }
    order =
      state.phase === "clarifier" && Array.isArray(state.clarifier_order)
        ? state.clarifier_order
        : assessment.display_order;
    state.index = Math.min(Number(state.index || 0), order.length - 1);
    show("quiz");
    renderQuestion(true);
  }

  function clearSavedAssessment() {
    if (
      Object.keys(state.responses || {}).length > 0 &&
      !window.confirm("Clear the saved assessment on this device?")
    ) {
      return;
    }
    localStorage.removeItem(storageKey);
    state = freshState();
    state.retake_started = app.dataset.completed === "true";
    order = assessment.display_order;
    startButton.textContent = "Begin assessment";
    show("intro");
  }

  function startClarifiers() {
    // Re-select from the frozen core answers, never from stale follow-ups left
    // by a backwards edit. IDs, selection limits and scorer are unchanged.
    const coreResponses = Object.fromEntries(coreIds.map((id) => [id, state.responses[id]]));
    const coreTimings = Object.fromEntries(Object.entries(state.timings_seconds || {}).filter(([id]) => coreIds.includes(id)));
    const preliminary = engine.scoreAssessment(spec, model, {
      ...state, responses: coreResponses, timings_seconds: coreTimings, total_seconds: undefined,
    });
    const selected = [
      ...preliminary.suggested_capability_clarifiers.map(
        (item) => item.clarifier_id,
      ),
      ...preliminary.suggested_orientation_clarifiers.map(
        (item) => item.clarifier_id,
      ),
    ];
    const included = new Set([...coreIds, ...selected]);
    state.responses = Object.fromEntries(Object.entries(state.responses).filter(([id]) => included.has(id)));
    state.timings_seconds = Object.fromEntries(Object.entries(state.timings_seconds || {}).filter(([id]) => included.has(id)));
    if (selected.length === 0) {
      showResults();
      return;
    }
    state.phase = "clarifier";
    state.clarifier_order = selected;
    state.index = 0;
    order = selected;
    saveLocal();
    show("quiz");
    renderQuestion(true);
  }

  function renderResults(result, shareCode) {
    byId("assessment-share-code").value = shareCode;
    byId("assessment-share").classList.remove("hidden");
  }

  function payloadShareCode() {
    return state.source === "share_code"
      ? state.original_share_code
      : state.display_share_code;
  }

  async function persistResult() {
    if (!state.last_result) return;
    saveStatus.textContent = "Saving…";
    saveStatus.classList.remove("status-pill-ready");
    saveError.classList.add("hidden");
    retrySaveButton.classList.add("hidden");
    try {
      const response = await fetch(saveUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          submission_id: state.submission_id,
          source: state.source || "application",
          assessment_version: assessment.version,
          responses: state.responses,
          timings_seconds: state.timings_seconds || {},
          total_seconds: state.total_seconds ?? null,
          result: state.last_result,
          share_code: payloadShareCode(),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "The assessment could not be saved.");
      state.saved_run_id = data.run_id;
      state.saved_profile_url = data.profile_url;
      state.retake_started = false;
      app.dataset.completed = "true";
      app.dataset.runId = data.run_id;
      saveLocal();
      saveStatus.textContent = data.created ? "Saved" : "Already saved";
      saveStatus.classList.add("status-pill-ready");
      byId("assessment-complete-message").textContent = "Your answers are saved. See your results and choose a practice when you are ready.";
      profileLink.href = data.profile_url;
      profileLink.classList.remove("hidden");
    } catch (error) {
      saveStatus.textContent = "Save failed";
      byId("assessment-complete-message").textContent = "Your answers are still on this device. Retry saving before leaving.";
      saveError.textContent = error.message;
      saveError.classList.remove("hidden");
      retrySaveButton.classList.remove("hidden");
    }
  }

  function showResults() {
    if (Object.keys(state.timings_seconds || {}).length) {
      state.total_seconds = Object.values(state.timings_seconds).reduce(
        (total, value) => total + Number(value || 0),
        0,
      );
    }
    const result = engine.scoreAssessment(spec, model, state);
    const displayShareCode = engine.encodeShareCode(spec, state);
    state.phase = "complete";
    state.last_result = result;
    state.display_share_code = displayShareCode;
    saveLocal();
    renderResults(result, displayShareCode);
    byId("assessment-complete-message").textContent = "Saving your answers…";
    profileLink.classList.add("hidden");
    show("results");
    persistResult();
  }

  function importShareCode() {
    const importCode = byId("assessment-import-code").value.trim();
    const importError = byId("assessment-import-error");
    importError.classList.add("hidden");
    try {
      const decoded = engine.decodeShareCode(spec, importCode);
      const missingCore = coreIds.filter((itemId) => decoded.responses[itemId] == null);
      if (missingCore.length) {
        throw new Error("The share code does not contain all 50 required core answers.");
      }
      state = freshState();
      state.source = "share_code";
      state.original_share_code = importCode;
      state.responses = decoded.responses;
      state.timings_seconds = {};
      state.total_seconds = decoded.total_seconds ?? null;
      showResults();
    } catch (error) {
      importError.textContent = `This share code could not be imported: ${error.message}`;
      importError.classList.remove("hidden");
    }
  }

  startButton.addEventListener("click", beginOrResume);
  resetButton.addEventListener("click", clearSavedAssessment);
  backButton.addEventListener("click", () => {
    captureTiming();
    if (state.index > 0) state.index -= 1;
    else if (state.phase === "clarifier") {
      state.phase = "core";
      order = assessment.display_order;
      state.index = order.length - 1;
    }
    saveLocal();
    renderQuestion(true);
  });
  nextButton.addEventListener("click", () => {
    captureTiming();
    if (state.index < order.length - 1) {
      state.index += 1;
      saveLocal();
      renderQuestion(true);
      return;
    }
    if (state.phase === "core") {
      state.phase = "core_complete";
      state.index = 0;
      saveLocal();
      startClarifiers();
      return;
    }
    showResults();
  });
  importButton.addEventListener("click", importShareCode);
  retrySaveButton.addEventListener("click", persistResult);
  byId("assessment-copy").addEventListener("click", async () => {
    const shareCodeField = byId("assessment-share-code");
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(shareCodeField.value);
    } else {
      shareCodeField.focus();
      shareCodeField.select();
      document.execCommand("copy");
    }
    byId("assessment-copy").textContent = "Copied";
  });
  const retakeDialog = byId("assessment-retake-dialog");
  byId("assessment-retake").addEventListener("click", () => retakeDialog.showModal());
  byId("assessment-retake-cancel").addEventListener("click", () => retakeDialog.close());
  retakeDialog.addEventListener("close", () => byId("assessment-retake").focus());
  byId("assessment-retake-confirm").addEventListener("click", () => {
    retakeDialog.close();
    localStorage.removeItem(storageKey);
    state = freshState();
    state.retake_started = true;
    order = assessment.display_order;
    startButton.textContent = "Begin assessment";
    byId("assessment-share").classList.add("hidden");
    saveLocal();
    show("intro");
  });

  document.addEventListener("keydown", (event) => {
    if (stages.quiz.classList.contains("hidden") || !byId("assessment-shortcuts").checked) return;
    if (!stages.quiz.contains(document.activeElement)) return;
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.isComposing || event.repeat) return;
    if (event.target.closest("input, textarea, select, [contenteditable='true']")) return;
    const itemId = order[state.index];
    const item = itemMap[itemId];
    if (["1", "2", "3", "4", "5"].includes(event.key)) {
      selectAnswer(itemId, Number(event.key));
      nextButton.click();
      event.preventDefault();
    } else if (
      (event.key === "n" || event.key === "N") &&
      item.allow_not_applicable
    ) {
      selectAnswer(itemId, "NA");
      nextButton.click();
      event.preventDefault();
    } else if (event.key === "ArrowLeft" && !backButton.disabled) {
      backButton.click();
      event.preventDefault();
    }
  });

  window.GroundedGrowthAssessmentApp = {
    completeWithState(nextState) {
      state = {
        ...freshState(),
        ...nextState,
        assessment_version: assessment.version,
      };
      showResults();
    },
    getState() {
      return JSON.parse(JSON.stringify(state));
    },
  };

  if (state.phase === "complete" && state.saved_run_id && app.dataset.runId &&
      state.saved_run_id !== app.dataset.runId) {
    state = freshState();
    order = assessment.display_order;
  }
  if (Object.keys(state.responses || {}).length) startButton.textContent = "Resume assessment";
  startButton.disabled = false;
  resetButton.disabled = false;
  importButton.disabled = false;
  byId("assessment-load-status").textContent = "Your progress saves on this device so you can return later.";
  if (state.phase === "complete" && state.last_result &&
      (!state.saved_run_id || state.saved_run_id === app.dataset.runId)) {
    renderResults(state.last_result, state.display_share_code);
    show("results", false);
    if (!state.saved_run_id) persistResult();
  } else if (app.dataset.completed === "true" && !state.retake_started) {
    show("results", false);
  } else {
    show("intro", false);
  }
})();
