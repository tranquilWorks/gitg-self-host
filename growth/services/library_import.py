"""Library-only startup while the historical importer remains byte-frozen.

The shared-table orchestration matches that importer; its validators, projections
and in-progress practice guard are reused, never replaced. Parity tests bind the
shared records. No demo seeding or temporary user filtering occurs here.
"""

from decimal import Decimal

from django.conf import settings
from django.db import transaction

from growth.domain.practice_content import PracticeContentError, load_practice_content_bundle
from growth.models import (
    Competency,
    CompetencyLeverLink,
    CurriculumVersion,
    Lever,
    PracticeProtocol,
)
from growth.services.canonical_import import (
    CanonicalDataError,
    ImportSummary,
    _competency_defaults,
    _mapping_weights,
    _seed_protocols,
    load_and_validate_bundle,
    validate_practice_content_mapping,
)


@transaction.atomic
def seed_library_data() -> ImportSummary:
    bundle = load_and_validate_bundle()
    try:
        practice_bundle = load_practice_content_bundle(settings.BASE_DIR)
    except PracticeContentError as exc:
        raise CanonicalDataError(f"Canonical practice content validation failed: {exc}") from exc
    validate_practice_content_mapping(practice_bundle, bundle)
    curriculum = bundle.curriculum
    model = bundle.model
    model_metadata = model["model"]
    version_id = f"CURRICULUM-{curriculum['version']}-MODEL-{model_metadata['version']}"
    version, _ = CurriculumVersion.objects.update_or_create(
        stable_id=version_id,
        defaults={
            "curriculum_version": curriculum["version"],
            "model_version": model_metadata["version"],
            "assessment_version": "1.1",
            "source_hash": bundle.source_hash,
            "active": True,
        },
    )

    family_by_slug = {family["slug"]: family for family in model.get("lever_families", [])}
    for lever in model["developmental_levers"]:
        family = family_by_slug[lever["family"]]
        Lever.objects.update_or_create(
            stable_id=lever["id"],
            defaults={
                "curriculum_version": version,
                "slug": lever["slug"],
                "name": lever["name"],
                "family_id": family["id"],
                "family_slug": family["slug"],
                "family_name": family["name"],
                "definition": lever["definition"],
                "orientation_composition": lever["orientation_composition"],
                "competency_count": lever["coverage"]["competency_count"],
                "total_competency_weight": Decimal(str(lever["coverage"]["total_weight"])),
            },
        )

    for domain in curriculum["domains"]:
        for competency in domain["competencies"]:
            Competency.objects.update_or_create(
                stable_id=competency["id"],
                defaults=_competency_defaults(domain, competency, version),
            )

    desired_links: set[tuple[str, str]] = set()
    for row in bundle.mapping_rows:
        competency_id = row["competency_id"].strip()
        for lever_id, weight in _mapping_weights(row).items():
            desired_links.add((competency_id, lever_id))
            CompetencyLeverLink.objects.update_or_create(
                competency_id=competency_id,
                lever_id=lever_id,
                defaults={"weight": weight},
            )
    stale_link_ids = [
        link.pk
        for link in CompetencyLeverLink.objects.all()
        if (link.competency_id, link.lever_id) not in desired_links
    ]
    CompetencyLeverLink.objects.filter(pk__in=stale_link_ids).delete()

    _seed_protocols(practice_bundle.runtime_protocols)
    from growth.services.composite_score_state import (
        synchronize_all_composite_score_states,
    )

    synchronize_all_composite_score_states()

    return ImportSummary(
        curriculum_versions=CurriculumVersion.objects.count(),
        levers=Lever.objects.count(),
        competencies=Competency.objects.count(),
        competency_lever_links=CompetencyLeverLink.objects.count(),
        practice_protocols=PracticeProtocol.objects.count(),
        pilot_assessment_runs=0,
        pilot_lever_baselines=0,
    )
