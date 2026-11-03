(() => {
  "use strict";
  document.querySelectorAll("[data-open-dialog]").forEach((button) => {
    const dialog = document.getElementById(button.dataset.openDialog);
    if (!dialog) return;
    button.addEventListener("click", () => dialog.showModal());
    dialog.addEventListener("close", () => button.focus());
  });
  const reveal = (element) => {
    for (let parent = element?.parentElement; parent; parent = parent.parentElement) {
      if (parent.matches("details")) parent.open = true;
    }
  };
  document.querySelectorAll('[aria-invalid="true"], .errorlist, .form-error').forEach((element) => {
    // Client-side error placeholders are not errors until populated and shown.
    // Opening their disclosures at startup defeats intentional collapsed controls.
    if (element.matches(".form-error") &&
        (!element.textContent.trim() || element.matches(".hidden, [hidden]"))) return;
    reveal(element);
  });
  const summary = document.getElementById("form-errors");
  if (summary) {
    summary.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener("click", (event) => {
        const target = document.getElementById(link.hash.slice(1));
        if (!target) return;
        event.preventDefault();
        reveal(target);
        const control = target.matches("input, select, textarea") ? target : target.querySelector("input, select, textarea");
        (control || target).focus();
      });
    });
    summary.focus();
  }
  document.querySelectorAll(".nav-more, .inline-help").forEach((menu) => {
    menu.addEventListener("focusout", (event) => {
      if (event.relatedTarget && !menu.contains(event.relatedTarget)) menu.open = false;
    });
    document.addEventListener("pointerdown", (event) => {
      if (!menu.contains(event.target)) menu.open = false;
    });
    menu.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && menu.open) {
        menu.open = false;
        menu.querySelector("summary").focus();
      }
    });
  });
})();
