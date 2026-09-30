import uuid
from typing import ClassVar

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from growth.models import (
    AssessmentRun,
    ImmutablePersonalOSQuerySet,
    PersonalOSRevision,
    PracticeProtocol,
)


class PracticeDirectionRevision(models.Model):
    """Append-only owner choice, scoped to one assessment and protocol."""

    stable_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment_run = models.ForeignKey(AssessmentRun, on_delete=models.CASCADE)
    protocol = models.ForeignKey(PracticeProtocol, on_delete=models.PROTECT)
    personal_os = models.ForeignKey(
        PersonalOSRevision, on_delete=models.PROTECT, null=True, blank=True
    )
    revision = models.PositiveIntegerField()
    state = models.CharField(
        max_length=16,
        choices=(
            ("unknown", "Not sure yet"),
            ("declined", "Connection declined"),
            ("priority", "Saved priority"),
            ("outcome", "Intended outcome"),
        ),
    )
    priority_index = models.PositiveSmallIntegerField(null=True, blank=True)
    intended_outcome = models.CharField(max_length=500, blank=True)
    contract_version = models.CharField(max_length=40, default="GG-PRACTICE-DIRECTION-1.0")
    canonical_snapshot = models.JSONField()
    content_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = ImmutablePersonalOSQuerySet.as_manager()

    class Meta:
        base_manager_name = "objects"
        ordering = ("assessment_run_id", "protocol_id", "revision")
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("assessment_run", "protocol", "revision"),
                name="unique_practice_direction_revision",
            ),
            models.CheckConstraint(
                condition=models.Q(revision__gte=1), name="practice_direction_revision_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(state__in=("unknown", "declined", "priority", "outcome")),
                name="practice_direction_known_state",
            ),
            models.CheckConstraint(
                condition=models.Q(contract_version="GG-PRACTICE-DIRECTION-1.0"),
                name="practice_direction_known_version",
            ),
        ]

    def __str__(self):
        return f"Practice connection revision {self.revision}"

    def save(self, *args, **kwargs):
        if (
            not self._state.adding
            or kwargs.get("force_update")
            or type(self).objects.filter(pk=self.pk).exists()
        ):
            raise ValidationError("Practice connections are immutable; append a revision.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Practice connections are immutable.")

    @property
    def chosen_text(self):
        if self.state == "priority":
            return self.personal_os.priority_stack_value[self.priority_index]
        return self.intended_outcome

    def clean(self):
        from growth.domain.practice_direction import CONTRACT_VERSION, direction_snapshot

        super().clean()
        if self.contract_version != CONTRACT_VERSION or self.assessment_run.user_id != self.user_id:
            raise ValidationError("Practice connection version or ownership is invalid.")
        if self.state == "priority":
            if (
                not self.personal_os_id
                or self.personal_os.assessment_run_id != self.assessment_run_id
                or self.personal_os.user_id != self.user_id
            ):
                raise ValidationError("Choose a priority from this assessment period.")
            self.personal_os.full_clean()
            if (
                self.personal_os.priority_stack_state != "provided"
                or self.priority_index is None
                or not 0 <= self.priority_index < len(self.personal_os.priority_stack_value)
                or self.intended_outcome
            ):
                raise ValidationError("The selected priority is invalid.")
        elif self.personal_os_id or self.priority_index is not None:
            raise ValidationError("Only a saved priority can reference Personal OS.")
        if self.state == "outcome":
            if not self.intended_outcome.strip():
                raise ValidationError("Provide an intended outcome.")
        elif self.intended_outcome:
            raise ValidationError("This choice cannot contain an intended outcome.")
        payload, digest = direction_snapshot(self)
        if self.canonical_snapshot != payload or self.content_hash != digest:
            raise ValidationError("Practice connection snapshot does not verify.")
        if self._state.adding:
            previous = (
                type(self)
                .objects.filter(
                    assessment_run_id=self.assessment_run_id, protocol_id=self.protocol_id
                )
                .order_by("-revision")
                .first()
            )
            if self.revision != (previous.revision + 1 if previous else 1):
                raise ValidationError("Practice connection revision is not contiguous.")
