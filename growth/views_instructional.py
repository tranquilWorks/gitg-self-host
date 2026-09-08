from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from growth.domain.instructional_content import learner_projection, render_text
from growth.domain.practice_content import FROZEN_LEGACY_PROTOCOL_IDS, load_practice_content_bundle
from growth.models import PracticeProtocol


def guide_for_protocol(protocol):
    if protocol.stable_id in FROZEN_LEGACY_PROTOCOL_IDS:
        return load_practice_content_bundle(settings.BASE_DIR).instructional_guides.get(
            protocol.parent_competency_id
        )
    # Imported setup_copy is protected by the existing active/paused preflight.
    return protocol.setup_copy.get("instructional_content")


@login_required
@require_GET
def practice_guide(request, slug):
    protocol = get_object_or_404(PracticeProtocol, slug=slug)
    guide = guide_for_protocol(protocol)
    if guide is None:
        raise Http404("This practice has no learning guide.")
    attempt, check = request.GET.get("attempt"), request.GET.get("check")
    try:
        projection = learner_projection(
            guide, protocol.parent_competency_id, attempt=attempt, check=check
        )
    except ValueError as exc:
        raise Http404(str(exc)) from exc
    export = request.GET.get("format")
    if export and export not in {"txt", "md"}:
        raise Http404("Unknown guide format.")
    if export:
        response = HttpResponse(render_text(projection), content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{protocol.slug}-guide.{export}"'
    else:
        selection = QueryDict(mutable=True)
        if attempt:
            selection["attempt"] = attempt
        if check:
            selection["check"] = check
        response = render(
            request,
            "growth/practice_guide.html",
            {
                "protocol": protocol,
                "guide": projection,
                "selection_query": selection.urlencode(),
            },
        )
    response["Cache-Control"] = "private, no-store"
    return response
