"""Formatting, not a competing protocol or scoring source."""

import re

from django import template

from growth.practice_presentation import CHOICE_COPY, display_action_title

register = template.Library()


@register.filter
def plain_direction(value):
    return CHOICE_COPY["evidence_direction"].get(value, "No result recorded")


@register.filter
def action_title(action):
    return display_action_title(action)


@register.inclusion_tag("growth/partials/practice_actions.html")
def action_instructions(action):
    # Split only explicit author-supplied section boundaries. All instructions,
    # examples, adverse checks and reflection requirements remain in order.
    pieces = re.split(
        r"(Observation checks:|Observed checks:|Final review:|Examples:)",
        action.instructions.replace("the intervention", "the practice"),
    )
    sections = [{"heading": "", "body": pieces[0]}]
    for index in range(1, len(pieces), 2):
        heading = "Reflection" if pieces[index] == "Final review:" else pieces[index].rstrip(":")
        sections.append({"heading": heading, "body": pieces[index + 1]})
    return {"instruction_sections": sections}
