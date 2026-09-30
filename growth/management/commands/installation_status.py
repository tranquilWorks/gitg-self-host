import json

from django.core.management.base import BaseCommand, CommandError

from growth.installation import installation_diagnostics


class Command(BaseCommand):
    help = "Read local revision/configuration/database readiness without changing stored state."

    def add_arguments(self, parser):
        parser.add_argument("--check", action="store_true", help="Exit nonzero when not ready.")

    def handle(self, *args, **options):
        result = installation_diagnostics()
        self.stdout.write(json.dumps(result, sort_keys=True))
        if options["check"] and not result["ready"]:
            raise CommandError("Installation needs attention; see the reported issue codes.")
