from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from growth.installation import installation_information


@never_cache
@require_GET
def installation(request):
    return render(request, "growth/installation.html", installation_information())
