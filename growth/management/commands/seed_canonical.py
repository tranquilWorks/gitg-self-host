from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from growth.services.canonical_import import CanonicalDataError, seed_canonical_data
from growth.services.library_import import seed_library_data


class Command(BaseCommand):
    help = "Validate and idempotently seed canonical curriculum, model, and Pilot 002 data."

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument(
            "--startup", action="store_true", help="Use the configured APP_SEED_DEMO choice."
        )
        mode.add_argument(
            "--without-demo", action="store_true", help="Preserve history without adding a demo."
        )

    def handle(self, *args, **options):
        include_demo = settings.SEED_DEMO if options["startup"] else not options["without_demo"]
        try:
            summary = seed_canonical_data() if include_demo else seed_library_data()
        except CanonicalDataError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            self.style.SUCCESS(
                "Canonical seed complete: "
                f"{summary.levers} levers, "
                f"{summary.competencies} competencies, "
                f"{summary.competency_lever_links} weighted links, "
                f"{summary.practice_protocols} practice protocols, "
                f"{summary.pilot_lever_baselines} Pilot 002 baselines."
            )
        )
