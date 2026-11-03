(() => {
  "use strict";

  // Progressive enhancement: without JavaScript every field remains available.
  const guided = document.querySelector(".personal-os-form");
  if (guided) {
    const steps = [...guided.querySelectorAll(".reflection-fieldset")];
    guided.querySelectorAll("details").forEach((group) => { group.open = true; });
    const controls = document.createElement("div");
    controls.className = "button-row";
    const progress = document.createElement("p");
    progress.setAttribute("role", "status");
    const back = document.createElement("button");
    const next = document.createElement("button");
    back.type = next.type = "button";
    back.textContent = "Previous question";
    next.textContent = "Next question";
    back.className = next.className = "button button-secondary";
    controls.append(back, next);
    guided.append(progress, controls);
    let current = Math.max(0, steps.findIndex((step) => step.querySelector(".errorlist")));
    const show = (focus) => {
      steps.forEach((step, index) => { step.hidden = index !== current; });
      guided.querySelectorAll("details").forEach((group) => {
        group.hidden = !group.querySelector("fieldset:not([hidden])");
      });
      back.disabled = current === 0;
      next.disabled = current === steps.length - 1;
      progress.textContent = `Question ${current + 1} of ${steps.length}. Answers save only when you select Save.`;
      if (focus) steps[current].querySelector("select, textarea")?.focus();
    };
    back.addEventListener("click", () => { current--; show(true); });
    next.addEventListener("click", () => { current++; show(true); });
    show(false);
    // A server error summary can target any question, including a hidden one.
    document.getElementById("form-errors")?.addEventListener("click", (event) => {
      const link = event.target.closest("a[href^='#']");
      const target = link && document.getElementById(link.hash.slice(1));
      const index = steps.findIndex((step) => target && step.contains(target));
      if (index >= 0) {
        current = index;
        show(false);
        // Keep the exact error-summary destination, not the step's first select.
        target.focus();
      }
    });
  }

  const showForState = (stateControl, valueContainer) => {
    if (!stateControl || !valueContainer) return;
    const hasError = Boolean(valueContainer.querySelector(".errorlist"));
    valueContainer.hidden = stateControl.value !== "provided" && !hasError;
  };

  document.querySelectorAll("[data-personal-os-section]").forEach((container) => {
    const sectionId = container.dataset.personalOsSection;
    const state = document.querySelector(`#id_${sectionId}_state`);
    showForState(state, container);
    state?.addEventListener("change", () => showForState(state, container));
  });

  document.querySelectorAll("[data-state-value]").forEach((container) => {
    const factorId = container.dataset.stateValue;
    const state = document.querySelector(`#id_${factorId}_state`);
    showForState(state, container);
    state?.addEventListener("change", () => showForState(state, container));
  });

  const practiceForm = document.querySelector("[data-practice-context-form]");
  if (practiceForm) {
    const modeControls = [...practiceForm.querySelectorAll('input[name="mode"]')];
    const updateMode = () => {
      const selected = modeControls.find((control) => control.checked)?.value || "";
      practiceForm.querySelectorAll("[data-context-mode]").forEach((section) => {
        section.hidden = !section.dataset.contextMode.split(" ").includes(selected);
        section.querySelectorAll("input, select, textarea").forEach((control) => {
          control.disabled = section.hidden;
        });
        if (selected === "provide" && !section.hidden) {
          section.querySelectorAll("details").forEach((group) => { group.open = true; });
        }
      });
    };
    modeControls.forEach((control) => control.addEventListener("change", updateMode));
    updateMode();
  }

})();
