(() => {
  "use strict";
  const reveal = (element) => {
    for (let parent = element?.parentElement; parent; parent = parent.parentElement) {
      if (parent.matches("details")) parent.open = true;
    }
  };
  document.querySelectorAll('[aria-invalid="true"], .errorlist, .form-error').forEach(reveal);
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
  document.querySelectorAll(".nav-more").forEach((menu) => {
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
