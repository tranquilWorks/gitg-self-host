"""Read-only discovery of public practice metadata, separate from ranking."""

from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Q

from growth.models import PracticeProtocol


def build_practice_explorer(params):
    query = params.get("q", "").strip()[:120]
    domain = params.get("domain", "").strip()[:8]
    browsing = params.get("browse") == "1" or bool(query or domain or params.get("page"))
    protocols = PracticeProtocol.objects.filter(
        availability=PracticeProtocol.Availability.ACTIVE
    ).select_related("parent_competency")
    domains = tuple(
        protocols.exclude(parent_competency__isnull=True)
        .order_by("parent_competency__domain_id")
        .values_list("parent_competency__domain_id", "parent_competency__domain_name")
        .distinct()
    )
    valid_domain = not domain or domain in {key for key, _name in domains}
    if domain:
        protocols = protocols.filter(parent_competency__domain_id=domain)
    if query:
        protocols = protocols.filter(
            Q(name__icontains=query)
            | Q(parent_competency__name__icontains=query)
            | Q(parent_competency__domain_name__icontains=query)
            | Q(parent_competency__stable_id__iexact=query)
        )
    page = (
        Paginator(protocols.order_by("display_order", "stable_id"), 12).get_page(params.get("page"))
        if browsing
        else None
    )
    filters = {"browse": "1", "q": query, "domain": domain}
    return {
        "query": query,
        "domain": domain,
        "domains": domains,
        "valid_domain": valid_domain,
        "page": page,
        "previous_query": (
            urlencode({**filters, "page": page.previous_page_number()})
            if page and page.has_previous()
            else ""
        ),
        "next_query": (
            urlencode({**filters, "page": page.next_page_number()})
            if page and page.has_next()
            else ""
        ),
    }
