/* Deterministic DOM simulation of the real client, not a browser/visual pass. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = path.resolve(__dirname, "..");
const bundle = path.join(root, "data/assessment/v1.1_bundle/grounded_growth_assessment_v1_1");
const read = (name) => JSON.parse(fs.readFileSync(path.join(bundle, name), "utf8"));
const spec = read("assessment_spec_v1_1.json");
const model = read("grounded_growth_model_v1.json");
const display = JSON.parse(fs.readFileSync(0, "utf8"));

class Element {
  constructor(id = "", tag = "div") {
    this.id = id; this.tag = tag; this.children = []; this.listeners = {};
    this.dataset = {}; this.attributes = {}; this.classes = new Set(); this.style = {};
    this.disabled = false; this.checked = false; this.value = ""; this.open = false;
    this.classList = {
      add: (c) => this.classes.add(c), remove: (c) => this.classes.delete(c),
      contains: (c) => this.classes.has(c),
      toggle: (c, on) => on ? this.classes.add(c) : this.classes.delete(c),
    };
  }
  addEventListener(name, callback) { (this.listeners[name] ||= []).push(callback); }
  fire(name, event = {}) { for (const callback of this.listeners[name] || []) callback(event); }
  setAttribute(key, value) { this.attributes[key] = value; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  querySelectorAll() { return this.children.filter((c) => c instanceof Element); }
  querySelector(selector) {
    if (selector === "h2") return this.heading ||= new Element("", "h2");
    if (selector === ".assessment-import") return elements.get("import-panel");
    if (selector === "[name=csrfmiddlewaretoken]") return { value: "fixture-csrf" };
    throw Error(`Unimplemented selector ${selector}`);
  }
  focus() { document.activeElement = this; }
  contains(node) {
    return node === this || node === this.heading || this.children.some((c) => c instanceof Element && c.contains(node));
  }
  closest() { return ["input", "textarea", "select"].includes(this.tag) ? this : null; }
  click() { if (!this.disabled) this.fire("click"); }
  showModal() { this.open = true; elements.get("assessment-retake-cancel").focus(); }
  close() { this.open = false; this.fire("close"); }
}

const template = fs.readFileSync(path.join(root, "templates/growth/assessment.html"), "utf8");
const elements = new Map([...template.matchAll(/id="([^"]+)"/g)].map((match) => [match[1], new Element(match[1])]));
elements.set("import-panel", new Element());
for (const [id, value] of [["assessment-spec", spec], ["assessment-model", model], ["assessment-display", display]]) {
  elements.set(id, Object.assign(new Element(id), { textContent: JSON.stringify(value) }));
}
const get = (id) => { assert.ok(elements.has(id), `Missing actual template ID ${id}`); return elements.get(id); };
get("assessment-quiz").append(get("assessment-prompt"), get("assessment-scale"));
const app = get("assessment-app");
app.dataset = { storageKey: "fixture", saveUrl: "/assessment/runs/", completed: "false", runId: "" };
const document = {
  activeElement: null, listeners: {}, getElementById: get,
  createElement: (tag) => new Element("", tag), createTextNode: (value) => value,
  addEventListener(name, callback) { this.listeners[name] = callback; },
};
const local = new Map();
const localStorage = { getItem: (key) => local.get(key) || null, setItem: (key, value) => local.set(key, value), removeItem: (key) => local.delete(key) };
let payload;
const window = { crypto: { randomUUID: () => "simulation-submission-id" }, confirm: () => true };
class FixedDate extends Date {
  constructor(...args) { if (args.length) super(...args); else super("2026-11-02T00:00:00.000Z"); }
  static now() { return 1793577600000; }
}
const sandbox = vm.createContext({ window, document, localStorage, navigator: {}, performance: { now: () => 5000 },
  fetch: async (_url, options) => {
    payload = JSON.parse(options.body);
    return { ok: true, json: async () => ({ created: true, run_id: "saved", profile_url: "/profile/" }) };
  }, console, TextEncoder, TextDecoder, Buffer, Date: FixedDate,
  btoa: (value) => Buffer.from(value, "binary").toString("base64"),
  atob: (value) => Buffer.from(value, "base64").toString("binary"),
});
vm.runInContext(fs.readFileSync(path.join(bundle, "assessment_scoring_v1_1.js"), "utf8"), sandbox);
// The scorer's UMD global is globalThis in the isolated context.
window.GroundedGrowthAssessment = sandbox.GroundedGrowthAssessment;
vm.runInContext(fs.readFileSync(path.join(root, "growth/static/growth/assessment.js"), "utf8"), sandbox);
const state = () => window.GroundedGrowthAssessmentApp.getState();
const key = (value, extra = {}) => document.listeners.keydown({ key: value, target: document.activeElement, preventDefault() {}, ...extra });

get("assessment-start").click();
key("3");
assert.equal(state().index, 0, "shortcuts default off");
get("assessment-shortcuts").checked = true;
get("assessment-prompt").focus();
key("3", { repeat: true }); key("3", { ctrlKey: true });
assert.equal(state().index, 0, "modified/repeated keys cannot consume answers");
key("3");
assert.equal(state().index, 1, "one key advances without Next");
assert.equal(state().responses[spec.assessment.display_order[0]], 3);
document.activeElement = new Element("outside", "textarea"); key("5");
assert.equal(state().index, 1, "typing outside the question cannot answer");
get("assessment-prompt").focus();
key("ArrowLeft"); assert.equal(state().index, 0);
assert.equal(state().responses[spec.assessment.display_order[0]], 3);
for (let index = 0; index < 50; index++) {
  assert.equal(state().index, index);
  const id = spec.assessment.display_order[index];
  assert.equal(get("assessment-prompt").textContent, display.prompts[id]);
  key(index < 12 ? (index % 2 ? "5" : "1") : "4");
}
assert.equal(state().phase, "clarifier", "follow-ups start automatically");
const order = state().clarifier_order;
assert.equal(order.filter((id) => id.startsWith("C_")).length, 8);
assert.ok(order.length >= 8 && order.length <= 10);
key("ArrowLeft"); assert.equal(state().phase, "core"); assert.equal(state().index, 49);
key("4"); assert.deepEqual(state().clarifier_order, order);
for (const id of order) { assert.equal(get("assessment-prompt").textContent, display.prompts[id]); key("4"); }
assert.equal(state().phase, "complete");
assert.equal(payload.source, "application");
assert.equal(Object.keys(payload.responses).length, 50 + order.length);
assert.equal(Object.keys(payload.timings_seconds).length, 50 + order.length);
assert.ok(payload.share_code.startsWith("GGA11."));
assert.deepEqual(payload.result, JSON.parse(JSON.stringify(window.GroundedGrowthAssessment.scoreAssessment(spec, model, state()))));
get("assessment-retake").click();
assert.equal(get("assessment-retake-dialog").open, true);
get("assessment-retake-cancel").click();
assert.equal(state().phase, "complete", "cancel leaves completed answers intact");
get("assessment-retake").click(); get("assessment-retake-confirm").click();
assert.equal(state().phase, "core"); assert.equal(Object.keys(state().responses).length, 0);
assert.equal(state().retake_started, true);
console.log(JSON.stringify({ simulation: "passed", core_answers: 50, followups: order.length, direct_key_progression: true, scorer_parity: true }));
