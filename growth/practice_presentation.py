"""Display-only work-loop language. No domain values or stored records change."""

from growth.domain.evidence import observation_fields_for_rules

CHOICE_COPY = {
    "evidence_direction": {
        "supports": "It went as expected",
        "mixed": "Some parts did; others did not",
        "contradicts": "It went against what I expected",
        "inconclusive": "Not enough happened to tell",
    },
    "context_comparison": {
        "first_record": "This is my first check-in for this practice",
        "same_context": "A similar setting or situation",
        "varied_context": "A meaningfully different setting or situation",
    },
    "support_level": {
        "independent": "I did it without help",
        "planning_aid": "I used a reminder or planning aid",
        "guided": "Someone prompted or guided me while I did it",
    },
}


def present_check_in_form(form):
    """Relabel existing choices without adding/removing values or validators."""
    for name, labels in CHOICE_COPY.items():
        form.fields[name].choices = [
            (value, labels.get(value, label)) for value, label in form.fields[name].choices
        ]
    form.fields["action"].label_from_instance = lambda action: (
        f"Action {action.sequence}: {display_action_title(action)}"
    )
    form.fields["evidence_direction"].label = "Did this go as you expected?"
    form.fields["evidence_direction"].help_text = "Choose what happened, including mixed results."
    form.fields["context_comparison"].help_text = "Compare with your earlier attempts, if any."
    for name, label in {
        "action_attempted": "I tried this action",
        "action_completed": "I completed this action",
        "contradictory_evidence": "What did not go as expected?",
        "internal_resistance": "How much resistance did you feel?",
        "expected_reciprocity": "How much response did you expect from the other person?",
        "observed_reciprocity": "How much response did you notice from the other person?",
    }.items():
        if name in form.fields:
            form.fields[name].label = label
    for name in ("internal_resistance", "expected_reciprocity", "observed_reciprocity"):
        if name in form.fields:
            form.fields[name].choices = [
                (value, label.split(" — ", 1)[-1]) for value, label in form.fields[name].choices
            ]
    state_labels = {
        "unknown": "I have not recorded this",
        "observed": "I observed it — add the result",
        "not_observed": "I did not observe it",
        "withheld": "I prefer not to record this",
        "not_applicable": "This does not apply",
        "deferred": "I will record this later",
    }
    for name, field in form.fields.items():
        if form.sprint.protocol.parent_competency_id == "26.13":
            field.label = field.label.replace(
                "return to what matters and keep the lesson proportionate",
                "return to the serious issue and review what helped",
            )
        if name.startswith("typed_") and name.endswith("_state"):
            field.label = field.label.replace(" — observation state", " — what did you notice?")
            field.choices = [(key, state_labels.get(key, label)) for key, label in field.choices]
        elif name.startswith("typed_") and name.endswith("_provenance"):
            field.label = field.label.replace(" — evidence source", " — how do you know?")
            source_labels = {
                "firsthand_self_report": "What I directly noticed",
                "reviewed_artifact": "Criteria checked in a work sample (not uploaded)",
                "objective_indicator": "A measured result",
                "consented_observer": "An observer who agreed to contribute",
                "qualified_attestation": "A qualified reviewer",
            }
            field.choices = [(key, source_labels.get(key, label)) for key, label in field.choices]
    return form


def display_action_title(action):
    if action.pk == "PRACTICE-COMP-2613-HUMOR-DELIGHT-AND-LIGHTNESS-01-A3":
        return "Return to the serious issue and review what helped"
    return action.title


def check_in_observations(check_in, event):
    """Only explicitly recorded useful fields; unknown is never turned into No."""
    labels = check_in.sprint.protocol.setup_copy.get("check_in_labels", {})
    # A completed protocol may be re-imported later. The immutable event keeps
    # the rules that applied to THIS observation, independently of that import.
    rules = event.input_snapshot.get("evidence_rules", {})
    fields = (
        observation_fields_for_rules(rules)
        if rules.get("schema_version") == "practice-observation-v1"
        else ()
    )
    rows = [
        {
            "label": labels.get(name, name.replace("_", " ").capitalize()),
            "value": "Yes" if getattr(check_in, name) else "Not marked",
        }
        for name in sorted(fields)
    ]
    for name in ("internal_resistance", "expected_reciprocity", "observed_reciprocity"):
        value = getattr(check_in, name)
        if value is not None:
            rows.append(
                {
                    "label": labels.get(name, name.replace("_", " ").capitalize()),
                    "value": ("None", "Low", "Moderate", "High", "Very high")[value],
                }
            )
    for observation in check_in.typed_observations:
        if observation["state"] == "unknown":
            continue
        measurement = observation["measurement_id"]
        rows.append(
            {
                "label": labels.get(measurement, measurement.replace("_", " ").capitalize()),
                "value": observation["state"].replace("_", " ").capitalize(),
                "result": readable_result(observation.get("value")),
            }
        )
    return rows


def readable_result(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, dict):
        if "numerator" in value and "denominator" in value:
            return f"{value['numerator']} of {value['denominator']} opportunities"
        if "amount" in value:
            return f"{value['amount']} {value.get('unit', '')}".strip()
        return "; ".join(
            f"{key.replace('_', ' ')}: {readable_result(item)}" for key, item in value.items()
        )
    if isinstance(value, list):
        return "; ".join(str(readable_result(item)) for item in value)
    return str(value).replace("_", " ")
