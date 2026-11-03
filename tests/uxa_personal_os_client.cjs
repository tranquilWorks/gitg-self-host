// Deterministic execution of the real progressive form script, not a browser.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
let focused = null;
class Element {
  constructor() { this.children = []; this.listeners = {}; this.hidden = false; }
  append(...children) { this.children.push(...children); }
  setAttribute() {}
  addEventListener(name, callback) { this.listeners[name] = callback; }
  focus() { focused = this; }
}
const steps = [0, 1].map(() => {
  const step = new Element();
  step.state = new Element();
  step.value = new Element();
  step.value.value = "Retained private draft";
  step.querySelector = (selector) => selector === ".errorlist" ? null : step.state;
  step.contains = (target) => target === step.state || target === step.value;
  return step;
});
const groups = steps.map((step) => {
  const group = new Element();
  group.querySelector = () => step.hidden ? null : step;
  return group;
});
const form = new Element();
form.querySelectorAll = (selector) => selector === ".reflection-fieldset" ? steps : groups;
const summary = new Element();
const document = {
  querySelector: (selector) => selector === ".personal-os-form" ? form : null,
  querySelectorAll: () => [],
  createElement: () => new Element(),
  getElementById: (id) => id === "form-errors" ? summary : steps[1].value,
};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,
  "../growth/static/growth/personal_os.js"), "utf8"), { document });
assert.equal(steps[0].hidden, false);
assert.equal(steps[1].hidden, true);
const anchor = { hash: "#id_second_value", closest() { return this; } };
summary.listeners.click({ target: anchor });
assert.equal(steps[1].hidden, false);
assert.equal(steps[0].hidden, true);
assert.equal(focused, steps[1].value, "Error link must focus its exact textarea, not the select");
assert.equal(steps[1].value.value, "Retained private draft");
const controls = form.children[1];
controls.children[0].listeners.click();
assert.equal(steps[0].hidden, false);
assert.equal(focused, steps[0].state);
assert.equal(steps[1].value.value, "Retained private draft");
console.log("Progressive step/error focus and draft preservation passed (simulation only).");
