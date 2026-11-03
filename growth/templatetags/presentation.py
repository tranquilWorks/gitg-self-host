from django import forms, template
from django.urls import reverse

register = template.Library()

ORIENTATION_HELP = {
    "discernment": "You tend to look for reasons and check what is true before deciding.",
    "transcendence": "You tend to connect everyday choices with a larger sense of meaning.",
    "stewardship": "You tend to care for what others depend on and protect it over time.",
    "exploration": "You tend to learn by trying possibilities and meeting unfamiliar situations.",
    "agency": "You tend to set a direction and take initiative to move things forward.",
    "connection": ("You tend to begin with relationships and how people are affected."),
}


@register.filter
def orientation_help(slug):
    return ORIENTATION_HELP.get(slug, "This describes one way you approach choices.") + (
        " It describes a preference, not ability or an instruction for how you must act."
    )


@register.filter
def archetype_help(slugs):
    return " ".join(ORIENTATION_HELP.get(slug, "") for slug in slugs) + (
        " This name combines those two preferences as a reflection aid, not a fixed identity."
    )


@register.inclusion_tag("growth/partials/navigation.html", takes_context=True)
def application_navigation(context):
    request = context["request"]
    path = request.path
    entries = (
        ("Home", "growth:home", path == "/"),
        ("Personal OS", "growth:personal-os", path.startswith("/personal-os/")),
        ("Weekly", "growth:weekly-execution", path.startswith("/weekly/")),
        (
            "Practices",
            "growth:practice-list",
            path.startswith(("/practices/", "/practice-sprints/")),
        ),
        ("History", "history", path.startswith("/history/")),
        ("Profile", "growth:profile", path == "/profile/"),
        ("Assessment", "growth:assessment", path.startswith("/assessment/")),
        ("Evidence", "growth:evidence-ledger", path.startswith("/evidence/")),
        (
            "Account",
            "growth:data-management",
            path.startswith(("/account/", "/accounts/"))
            and not path.startswith("/account/pilot-feedback/"),
        ),
        ("Feedback", "growth:pilot-feedback", path.startswith("/account/pilot-feedback/")),
        ("Quick start", "quick-start", path == "/quick-start/"),
    )
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated and not user.assessment_runs.exists():
        entries = tuple(
            item for item in entries if item[0] in {"Home", "Assessment", "Account", "Quick start"}
        )
    links = [
        {"label": label, "url": reverse(name), "current": current}
        for label, name, current in entries
    ]
    split = 2 if len(links) == 4 else 6
    return {
        "primary": links[:split],
        "secondary": links[split:],
        "more_current": next((link["label"] for link in links[split:] if link["current"]), ""),
        "csrf_token": context.get("csrf_token"),
    }


@register.inclusion_tag("growth/partials/form_errors.html", takes_context=True)
def form_error_summary(context):
    errors = []
    seen = set()
    for form in context.flatten().values():
        if not isinstance(form, forms.BaseForm) or id(form) in seen or not form.is_bound:
            continue
        seen.add(id(form))
        for name, messages in form.errors.items():
            field = form[name] if name in form.fields else None
            target = field.auto_id if field and not field.is_hidden else ""
            label = field.label if field and not field.is_hidden else "Form"
            errors.extend(
                {"target": target, "label": label, "message": message} for message in messages
            )
    return {"form_errors": errors}
