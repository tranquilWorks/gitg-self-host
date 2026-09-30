from django.apps import AppConfig


class GrowthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "growth"

    def import_models(self) -> None:
        super().import_models()
        # Register additive models during Django's model-loading phase while
        # preserving the byte-pinned historical model module used by recovery.
        from . import models_direction  # noqa: F401

    def ready(self) -> None:
        from . import db  # noqa: F401
