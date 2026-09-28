from django import template
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe
from markdown_it import MarkdownIt

from growth.views_instructional import guide_for_protocol

register = template.Library()
_markdown = MarkdownIt("js-default").disable("image")


def _table_open(_tokens, _index, _options, _env):
    return '<div class="guide-table" role="region" aria-label="Lesson table" tabindex="0"><table>\n'


def _table_close(_tokens, _index, _options, _env):
    return "</table></div>\n"


_markdown.renderer.rules.update(table_open=_table_open, table_close=_table_close)


@register.filter
def guide_body(value, body_format="plain"):
    # HTML is disabled, unsafe schemes rejected by the parser, and remote
    # images disabled. Plain legacy lessons keep their exact text semantics.
    if body_format == "markdown":
        return mark_safe(_markdown.render(value))
    return mark_safe(linebreaks(value, autoescape=True))


@register.simple_tag
def has_instructional_guide(protocol):
    return guide_for_protocol(protocol) is not None
