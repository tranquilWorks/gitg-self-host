from django import template

from growth.views_instructional import guide_for_protocol

register = template.Library()


@register.simple_tag
def has_instructional_guide(protocol):
    return guide_for_protocol(protocol) is not None
